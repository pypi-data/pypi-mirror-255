use std::io::{Read, BufReader, ErrorKind, Error};
use std::path::PathBuf;
use std::iter::zip;
use pyo3::prelude::*;
use niffler;
use rustc_hash::FxHashMap as HashMap;
use rustc_hash::FxHashSet as HashSet;
use tar::Archive;
use itertools::Itertools;
use rayon::iter::{IntoParallelRefIterator, ParallelIterator};
use crate::{Kmer, Score, PKTbl, PKMeta};
use crate::decompose_kmers::break_seq;
use crate::metadata::load_metadata;
use crate::helpers::print_err;
use crate::parse_kmers_scores::{parse_kmers, parse_scores};

#[pyfunction]
pub fn get_sequences_scores(
    index: &str,
    tar_file: &str,
    k: usize,
    sequences: HashMap<(String, usize, usize), String>,
    threads: usize
) -> PyResult<HashMap<(String, usize, usize), Vec<Score>>> {
    let kmers: Vec<Kmer> = combined_kmers(sequences.clone().into_values().collect::<Vec<String>>(), k)?;
    let chunk_size: usize = (kmers.len() + threads - 1) / threads;
    let rayon_num_threads: usize = rayon::current_num_threads();
    let results: Vec<PKTbl> = match threads >= rayon_num_threads {
        true => {
            print_err(&format!("{threads} threads requested, using {rayon_num_threads} (entire global thread pool)"));
            let results = kmers.chunks(chunk_size).collect::<Vec<&[u64]>>().par_iter().map(|chunk| get_sorted_kmer_scores(index, tar_file, chunk.to_vec()).unwrap()).collect::<Vec<PKTbl>>();
            results
        },
        false => {
            print_err(&format!("{threads} threads requested, using {threads} (partial global thread pool)"));
            let mut results: Vec<PKTbl> = Vec::new();
            let all_kmer_chunks = kmers.chunks(chunk_size).collect::<Vec<&[u64]>>();
            let n_chunks = all_kmer_chunks.len();
            let mut kmer_chunks = Vec::new();
            for (i, kmer_chunk) in all_kmer_chunks.iter().enumerate() {
                kmer_chunks.push(kmer_chunk);
                if (i+1)%threads==0 || (i+1)==n_chunks {
                    results.extend(kmer_chunks.par_iter().map(|chunk| get_sorted_kmer_scores(index, tar_file, chunk.to_vec()).unwrap()).collect::<Vec<PKTbl>>());
                    kmer_chunks.clear();
                }
            }
            results
        }
    };
    let scored_kmers: PKTbl = results.into_iter().flatten().collect::<PKTbl>();
    Ok(sequences.into_iter().map(|(name, seq)| (name, get_sequence_scores(index, tar_file, k, &seq, scored_kmers.clone()).unwrap())).collect::<HashMap<(String, usize, usize),Vec<Score>>>())
}

#[pyfunction]
pub fn combined_kmers(sequences: Vec<String>, k: usize) -> PyResult<Vec<Kmer>> {
    Ok(sequences.iter().flat_map(|seq| get_sequence_kmerbits(seq, k, (1 << (k * 2)) - 1, 0)).flatten().unique().sorted().collect::<Vec<Kmer>>())
}

#[pyfunction]
pub fn get_sequence_scores(
    index: &str,
    tar_file: &str,
    k: usize,
    seq: &str,
    kmers: PKTbl
) -> PyResult<Vec<Score>> {
    let sequence_kmers = get_sequence_kmerbits(
        seq,
        k,
        (1u64 << (k as u64 * 2u64)) - 1u64,
        0u64
    )?;
    if kmers.is_empty() {
        let kmers = get_kmer_scores(
            index,
            tar_file,
            HashSet::from_iter(sequence_kmers.clone().into_iter())
        )?;
        return Ok(sequence_kmers.iter().map(|kmer| kmers.get(kmer).expect("could not get kmer").to_owned()).collect::<Vec<Score>>());
    } else {
        return Ok(sequence_kmers.iter().map(|kmer| kmers.get(kmer).expect("could not get kmer").to_owned()).collect::<Vec<Score>>());
    }
}

#[pyfunction]
pub fn get_sequence_kmerbits(seq: &str, k: usize, upper: Kmer, lower: Kmer) -> PyResult<Vec<Kmer>> {
    break_seq(seq.as_bytes(), k, upper, lower, Kmer::MAX)
}

fn initialize_index_read(index: &str, tar_file: &str) -> Result<(
    PKTbl, usize, usize, usize, usize, usize
), Error> {
    let meta: PKMeta = load_metadata(index, tar_file)?;
    let n_genomes: usize = meta.genomes.len();
    let kmer_bytes: usize =  (meta.kmer_size * 2 + 7) / 8;
    let kmer_bufsize: usize = 1000 * kmer_bytes;
    let score_bytes: usize = (n_genomes + 7) / 8;
    let score_bufsize: usize = 1000 * score_bytes;
    Ok((
        PKTbl::default(), n_genomes, kmer_bytes, kmer_bufsize, score_bytes,
        score_bufsize
    ))
}

#[pyfunction]
pub fn get_kmer_scores(index: &str, tar_file: &str, target_kmer_set: HashSet<Kmer>) -> PyResult<PKTbl> {
    let target_kmers_empty = target_kmer_set.is_empty();
    let (
        mut kmer_scores, _, kmer_bytes, kmer_bufsize, score_bytes,
        score_bufsize,
    ) = initialize_index_read(index, tar_file)?;
    let mut kmer_buf = vec![0; kmer_bytes];
    let mut score_buf = vec![0; score_bytes];
    if tar_file.len() == 0 {
        let mut kmers_in_path: PathBuf = PathBuf::from(&index);
        kmers_in_path.push("kmers.bgz");
        let mut scores_in_path: PathBuf = PathBuf::from(&index);
        scores_in_path.push("scores.bgz");
        let (kmers_reader, _format) = niffler::from_path(&kmers_in_path).expect("File not found");
        let (scores_reader, _format) = niffler::from_path(&scores_in_path).expect("File not found");
        let mut kmers_in = BufReader::with_capacity(kmer_bufsize, kmers_reader);
        let mut scores_in = BufReader::with_capacity(score_bufsize, scores_reader);
        loop {
            let kmers = match kmers_in.read_exact(&mut kmer_buf) {
                Ok(_) => parse_kmers(&kmer_buf, kmer_bytes),
                Err(ref e) if e.kind() == ErrorKind::UnexpectedEof => break,
                // Err(ref e) if e.kind() == ErrorKind::Interrupted => continue,
                Err(e) => panic!("{:?}", e),
            };
            let scores = match scores_in.read_exact(&mut score_buf) {
                Ok(_) => score_buf.chunks(score_bytes).map(|bytes| bytes.to_vec()).collect::<Vec<Score>>(),
                Err(ref e) if e.kind() == ErrorKind::UnexpectedEof => break,
                // Err(ref e) if e.kind() == ErrorKind::Interrupted => continue,
                Err(e) => panic!("{:?}", e),
            };
            let iter = zip(kmers, scores);
            if target_kmers_empty {
                for (kmer, score) in iter {
                    kmer_scores.insert(kmer, score);
                }
            } else {
                for (kmer, score) in iter {
                    if target_kmer_set.contains(&kmer) {
                        kmer_scores.insert(kmer, score);
                    }
                }
            }
        }
    } else {
        let (tar_k, _format) = niffler::from_path(tar_file).expect(
            &format!("File not found: {}", tar_file));
        for kmers_entry in Archive::new(tar_k).entries().expect("Can't read tar file") {
            let k = kmers_entry.expect("Error reading tar archive");
            let k_in_path = k.path().expect("Error reading tar archive");
            let k_in_str = k_in_path.to_str().unwrap().to_owned();
            if (&k_in_str).ends_with("kmers.bgz") {
                let (kmers_reader, _format) = niffler::get_reader(Box::new(k)).expect("Can't read from tar archive");
                let (tar_s, _format) = niffler::from_path(tar_file).expect(
                    &format!("File not found: {}", tar_file));
                for scores_entry in Archive::new(tar_s).entries().expect("Can't read tar file") {
                    let s = scores_entry.expect("Error reading tar archive");
                    let s_in_path = s.path().expect("Error reading tar archive");
                    let s_in_str = s_in_path.to_str().unwrap().to_owned();
                    if (&s_in_str).ends_with("scores.bgz") {
                        let (scores_reader, _format) = niffler::get_reader(Box::new(s)).expect("Can't read from tar archive");
                        let mut kmers_in = BufReader::with_capacity(kmer_bufsize, kmers_reader);
                        let mut scores_in = BufReader::with_capacity(score_bufsize, scores_reader);
                        loop {
                            let kmers = match kmers_in.read_exact(&mut kmer_buf) {
                                Ok(_) => parse_kmers(&kmer_buf, kmer_bytes),
                                Err(ref e) if e.kind() == ErrorKind::UnexpectedEof => break,
                                // Err(ref e) if e.kind() == ErrorKind::Interrupted => continue,
                                Err(e) => panic!("{:?}", e),
                            };
                            let scores = match scores_in.read_exact(&mut score_buf) {
                                Ok(_) => score_buf.chunks(score_bytes).map(|bytes| bytes.to_vec()).collect::<Vec<Score>>(),
                                Err(ref e) if e.kind() == ErrorKind::UnexpectedEof => break,
                                // Err(ref e) if e.kind() == ErrorKind::Interrupted => continue,
                                Err(e) => panic!("{:?}", e),
                            };
                            let iter = zip(kmers, scores);
                            if target_kmers_empty {
                                for (kmer, score) in iter {
                                    kmer_scores.insert(kmer, score);
                                }
                            } else {
                                for (kmer, score) in iter {
                                    if target_kmer_set.contains(&kmer) {
                                        kmer_scores.insert(kmer, score);
                                    }
                                }
                            }
                        }
                        break;
                    }
                }
                break;
            }
        }
    }
    Ok(kmer_scores)
}

#[pyfunction]
pub fn get_sorted_kmer_scores(
    index: &str, tar_file: &str, target_kmers: Vec<Kmer>
) -> PyResult<PKTbl> {
    let upper = target_kmers.last().expect("couldnt get last item of vec").to_owned();
    let target_kmer_set: HashSet<Kmer> = HashSet::from_iter(target_kmers.into_iter());
    let (
        _, _, kmer_bytes, kmer_bufsize, score_bytes, score_bufsize
    ) = initialize_index_read(index, tar_file)?;
    let mut kmer_scores: PKTbl = HashMap::default();
    let mut kmer_buf = vec![0u8; kmer_bytes];
    let mut score_buf = vec![0u8; score_bytes];
    if tar_file.len() == 0 {
        let mut kmers_in_path: PathBuf = PathBuf::from(&index);
        kmers_in_path.push("kmers.bgz");
        let mut scores_in_path: PathBuf = PathBuf::from(&index);
        scores_in_path.push("scores.bgz");
        let (kmers_reader, _format) = niffler::from_path(&kmers_in_path).expect("File not found");
        let (scores_reader, _format) = niffler::from_path(&scores_in_path).expect("File not found");
        let mut kmers_in = BufReader::with_capacity(kmer_bufsize, kmers_reader);
        let mut scores_in = BufReader::with_capacity(score_bufsize, scores_reader);
        loop {
            let kmers = match kmers_in.read_exact(&mut kmer_buf) {
                Ok(_) => parse_kmers(&kmer_buf, kmer_bytes),
                Err(ref e) if e.kind() == ErrorKind::UnexpectedEof => break,
                Err(e) => panic!("{:?}", e),
            };
            let scores = match scores_in.read_exact(&mut score_buf) {
                Ok(_) => score_buf.chunks(score_bytes).map(|bytes| bytes.to_vec()).collect::<Vec<Score>>(),
                Err(ref e) if e.kind() == ErrorKind::UnexpectedEof => break,
                Err(e) => panic!("{:?}", e),
            };
            for (kmer, score) in zip(kmers, scores) {
                if kmer > upper { break; }
                if target_kmer_set.contains(&kmer) {
                    kmer_scores.insert(kmer, score);
                }
            }
        }
    } else {
        let (tar_k, _format) = niffler::from_path(tar_file).expect(
            &format!("File not found: {}", tar_file));
        for kmers_entry in Archive::new(tar_k).entries().expect("Can't read tar file") {
            let k = kmers_entry.expect("Error reading tar archive");
            let k_in_path = k.path().expect("Error reading tar archive");
            let k_in_str = k_in_path.to_str().unwrap().to_owned();
            if (&k_in_str).ends_with("kmers.bgz") {
                let (kmers_reader, _format) = niffler::get_reader(Box::new(k)).expect("Can't read from tar archive");
                let (tar_s, _format) = niffler::from_path(tar_file).expect(
                    &format!("File not found: {}", tar_file));
                for scores_entry in Archive::new(tar_s).entries().expect("Can't read tar file") {
                    let s = scores_entry.expect("Error reading tar archive");
                    let s_in_path = s.path().expect("Error reading tar archive");
                    let s_in_str = s_in_path.to_str().unwrap().to_owned();
                    if (&s_in_str).ends_with("scores.bgz") {
                        let (scores_reader, _format) = niffler::get_reader(Box::new(s)).expect("Can't read from tar archive");
                        let mut kmers_in = BufReader::with_capacity(kmer_bufsize, kmers_reader);
                        let mut scores_in = BufReader::with_capacity(score_bufsize, scores_reader);
                        loop {
                            let kmers = match kmers_in.read_exact(&mut kmer_buf) {
                                Ok(_) => parse_kmers(&kmer_buf, kmer_bytes),
                                Err(ref e) if e.kind() == ErrorKind::UnexpectedEof => break,
                                Err(e) => panic!("{:?}", e),
                            };
                            let scores = match scores_in.read_exact(&mut score_buf) {
                                Ok(_) => parse_scores(&score_buf, score_bytes),
                                Err(ref e) if e.kind() == ErrorKind::UnexpectedEof => break,
                                Err(e) => panic!("{:?}", e),
                            };
                            for (kmer, score) in zip(kmers, scores) {
                                if kmer > upper { break; }
                                if target_kmer_set.contains(&kmer) {
                                    kmer_scores.insert(kmer, score);
                                }
                            }
                        }
                        break;
                    }
                }
                break;
            }
        }
    }
    for kmer in target_kmer_set.into_iter() {
        if !kmer_scores.contains_key(&kmer) {
            kmer_scores.insert(kmer, vec![0u8; score_bytes]);
        }
    }
    Ok(kmer_scores)
}