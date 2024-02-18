use std::fs;
use std::io::{Read, Write, BufReader, BufWriter, ErrorKind};
use std::path::{Path, PathBuf};
use std::iter::zip;
use niffler;
use pyo3::prelude::*;
use tar::Archive;
use crate::helpers::score_byte_to_blist;
use crate::{Kmer, PKGenomes, GZIP_LEVELS, Score};
use crate::metadata::{PKMeta, load_metadata};
use crate::get_kmers::genome_index_to_byte_idx_and_bit_mask;
use crate::parse_kmers_scores::parse_kmers;

fn compress_score(superset_score: Score, n_superset_genomes: usize, n_subset_bytes: usize, memberships: &Vec<usize>, exclusions: &Vec<usize>, exclusive: bool) -> Score {
    let expanded_score: Vec<usize> = score_byte_to_blist(&superset_score, n_superset_genomes).expect("could not expand score");
    if exclusive {
        for j in exclusions.iter() {
            if expanded_score[*j] == 1 {
                return vec![0u8; n_subset_bytes]
            }
        }
    }
    let mut compressed_score: Score = vec![0u8; n_subset_bytes];
    for (i, j) in memberships.iter().enumerate() {
        if expanded_score[*j] == 1 {
            let (byte_idx, bit_mask) = genome_index_to_byte_idx_and_bit_mask(i, n_subset_bytes);
            compressed_score[byte_idx] = compressed_score[byte_idx] | bit_mask;
        }
    }
    return compressed_score
}

fn subset_loop(idx_dir: &str, kmer_buf: &mut [u8], score_buf: &mut Vec<u8>,
               kmers_out: &mut BufWriter<Box<dyn Write>>,
               scores_out: &mut BufWriter<Box<dyn Write>>,
               metadata: &mut PKMeta, kmer_bufsize: usize,
               kmer_bytes: usize,
               n_superset_genomes: usize, superset_score_bufsize: usize,
               n_superset_bytes: usize,
               n_subset_bytes: usize, memberships: Vec<usize>,
               exclusions: Vec<usize>, exclusive: bool,
               sorted_temp: &mut Vec<(Kmer, u64)>) -> (u64, Kmer) {
    let mut count: u64 = 0;
    let mut kmer_end: Kmer = 0;
    let mut kmers_in_path: PathBuf = PathBuf::from(&idx_dir);
    kmers_in_path.push("kmers.bgz");
    let mut scores_in_path: PathBuf = PathBuf::from(&idx_dir);
    scores_in_path.push("scores.bgz");
    let (kmers_reader, _format) = niffler::from_path(&kmers_in_path).expect("File not found");
    let (scores_reader, _format) = niffler::from_path(&scores_in_path).expect("File not found");
    let mut kmers_in = BufReader::with_capacity(kmer_bufsize, kmers_reader);
    let mut scores_in = BufReader::with_capacity(superset_score_bufsize, scores_reader);
    loop {
        let kmers = match kmers_in.read_exact(kmer_buf) {
            Ok(_) => parse_kmers(&kmer_buf, kmer_bytes),
            Err(ref e) if e.kind() == ErrorKind::UnexpectedEof => break,
            // Err(ref e) if e.kind() == ErrorKind::Interrupted => continue,
            Err(e) => panic!("{:?}", e),
        };
        let scores = match scores_in.read_exact(score_buf) {
            Ok(_) => score_buf.chunks(n_superset_bytes).map(
                |bytes| compress_score(bytes.to_vec(), n_superset_genomes, n_subset_bytes, &memberships, &exclusions, exclusive)).collect::<Vec<Score>>(),
            Err(ref e) if e.kind() == ErrorKind::UnexpectedEof => break,
            // Err(ref e) if e.kind() == ErrorKind::Interrupted => continue,
            Err(e) => panic!("{:?}", e),
        };
        let iter = zip(kmers, scores);
        for (kmer, score) in iter {
            match score.iter().any(|&i| i>0u8) {
                true => {
                    kmers_out.write(&kmer.to_be_bytes()[8-kmer_bytes..]).unwrap();
                    scores_out.write(&score).unwrap();
                    if count % 10000000 == 0 && count != 0 {
                        sorted_temp.push((kmer, count));
                        count = 0;
                    }
                    count += 1;
                    kmer_end = kmer;
                },
                false => { continue; }
            };
        }
    }
    (count, kmer_end)
}

fn subset_loop_tar(idx_dir: &str, tar_file: &str,
                   kmer_buf: &mut [u8], score_buf: &mut Vec<u8>,
                   kmers_out: &mut BufWriter<Box<dyn Write>>,
                   scores_out: &mut BufWriter<Box<dyn Write>>,
                   metadata: &mut PKMeta, kmer_bufsize: usize,
                   kmer_bytes: usize,
                   n_superset_genomes: usize, superset_score_bufsize: usize,
                   n_superset_bytes: usize,
                   n_subset_bytes: usize, memberships: Vec<usize>,
                   exclusions: Vec<usize>, exclusive: bool,
                   sorted_temp: &mut Vec<(Kmer, u64)>) -> (u64, Kmer) {
    let mut count: u64 = 0;
    let mut kmer_end: Kmer = 0;
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
                    let mut scores_in = BufReader::with_capacity(superset_score_bufsize, scores_reader);
                    loop {
                        let kmers = match kmers_in.read_exact(kmer_buf) {
                            Ok(_) => parse_kmers(&kmer_buf, kmer_bytes),
                            Err(ref e) if e.kind() == ErrorKind::UnexpectedEof => break,
                            // Err(ref e) if e.kind() == ErrorKind::Interrupted => continue,
                            Err(e) => panic!("{:?}", e),
                        };
                        let scores = match scores_in.read_exact(score_buf) {
                            Ok(_) => score_buf.chunks(n_superset_bytes).map(
                                |bytes| compress_score(bytes.to_vec(), n_superset_genomes, n_subset_bytes, &memberships, &exclusions, exclusive)).collect::<Vec<Score>>(),
                            Err(ref e) if e.kind() == ErrorKind::UnexpectedEof => break,
                            // Err(ref e) if e.kind() == ErrorKind::Interrupted => continue,
                            Err(e) => panic!("{:?}", e),
                        };
                        let iter = zip(kmers, scores);
                        for (kmer, score) in iter {
                            match score.iter().any(|&i| i>0u8) {
                                true => {
                                    kmers_out.write(&kmer.to_be_bytes()[8-kmer_bytes..]).unwrap();
                                    scores_out.write(&score).unwrap();
                                    if count % 10000000 == 0 && count != 0 {
                                        sorted_temp.push((kmer, count));
                                        count = 0;
                                    }
                                    count += 1;
                                    kmer_end = kmer;
                                },
                                false => { continue; }
                            };
                        }
                    }
                    break;
                }
            }
            break;
        }
    }
    (count, kmer_end)
}

#[pyfunction]
pub fn subset(idx_dir: &str, tar_file: &str, subset_genomes: PKGenomes,
              outdir: &str, gzip_level: usize, exclusive: bool) -> PyResult<()> {
    let mut metadata = PKMeta::new();
    let mut subset_genomes_ordered = Vec::new();
    let output_is_tar: bool = outdir.ends_with(".tar");
    match fs::create_dir(outdir) {
        Ok(_) => (),
        Err(_) => match Path::new(outdir).is_dir() {
            true => (),
            false => panic!("Could not create dir and dir does not exist")
        }
    };
    let superset_meta: PKMeta = load_metadata(idx_dir, tar_file)?;
    metadata.kmer_size = superset_meta.kmer_size;
    metadata.mem_blocks = superset_meta.mem_blocks;
    let n_superset_genomes = superset_meta.genomes.len();
    let mut superset_genomes: PKGenomes = Vec::new();
    for i in 0..n_superset_genomes {
        let genome = superset_meta.genomes.get(&i).expect("could not get genome name");
        superset_genomes.push(genome.to_string());
        if subset_genomes.contains(genome) {
            subset_genomes_ordered.push(genome.to_string());
        }
    }
    for (i, g) in subset_genomes_ordered.iter().enumerate() {
        let size = superset_meta.genome_sizes.get(g).expect("could not get genome size");
        metadata.genome_sizes.insert(g.to_string(), *size);
        metadata.genomes.insert(i, g.to_string());
    }
    let n_superset_genomes: usize = superset_genomes.len();
    let n_subset_genomes: usize = subset_genomes.len();
    let mut memberships: Vec<usize> = Vec::new();
    let mut exclusions: Vec<usize> = Vec::new();
    for (i, genome) in superset_genomes.iter().enumerate() {
        if subset_genomes.contains(&genome) {
            memberships.push(i);
        } else {
            exclusions.push(i);
        }
    }
    let kmer_bytes: usize =  (metadata.kmer_size * 2 + 7) / 8;
    let kmer_bufsize: usize = 1000 * kmer_bytes;
    let n_subset_bytes: usize = (n_subset_genomes + 7) / 8;
    let n_superset_bytes: usize = (n_superset_genomes + 7) / 8;
    let superset_score_bufsize: usize = 1000*n_superset_bytes;
    let subset_score_bufsize: usize = 1000*n_subset_bytes;
    let mut kmers_out_path = PathBuf::from(&outdir);
    kmers_out_path.push("kmers.bgz");
    let mut scores_out_path = PathBuf::from(&outdir);
    scores_out_path.push("scores.bgz");
    let mut kmer_buf = vec![0; kmer_bytes];
    let mut score_buf = vec![0; n_superset_bytes];
    let mut kmers_out = BufWriter::with_capacity(kmer_bufsize, niffler::to_path(kmers_out_path, niffler::compression::Format::Gzip, GZIP_LEVELS[gzip_level]).expect("Can't open file for writing"));
    let mut scores_out = BufWriter::with_capacity(subset_score_bufsize, niffler::to_path(scores_out_path, niffler::compression::Format::Gzip, GZIP_LEVELS[gzip_level]).expect("Can't open file for writing"));
    let mut sorted_temp = Vec::new();
    let (count, kmer_end) = match tar_file.len() > 0 {
        true => subset_loop_tar(&idx_dir, &tar_file,&mut kmer_buf, &mut score_buf,
                        &mut kmers_out, &mut scores_out, &mut metadata,
                        kmer_bufsize, kmer_bytes, n_superset_genomes,
                        superset_score_bufsize, n_superset_bytes,
                        n_subset_bytes, memberships, exclusions, exclusive,
                        &mut sorted_temp),
        false => subset_loop(&idx_dir,&mut kmer_buf, &mut score_buf, &mut kmers_out,
                    &mut scores_out, &mut metadata,
                    kmer_bufsize, kmer_bytes, n_superset_genomes,
                    superset_score_bufsize, n_superset_bytes, n_subset_bytes,
                    memberships, exclusions, exclusive,
                    &mut sorted_temp),
    };
    kmers_out.flush().unwrap();
    scores_out.flush().unwrap();
    if count > 0 {
        sorted_temp.push((kmer_end, count-1));
    }
    let mut num: u64 = 0;
    for (kmer, cur) in sorted_temp.iter() {
        num = cur + num;
        metadata.positions.insert(*kmer, num);
    }
    let mut meta_out_path = PathBuf::from(&outdir);
    meta_out_path.push("metadata.json");
    let meta_out = fs::File::create(&meta_out_path).expect(
        "Can't open file for writing"
    );
    serde_json::to_writer(&meta_out, &metadata).expect(
        "Couldn't write PKMeta to file"
    );
    Ok(())
}
