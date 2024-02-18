use std::io::{Read, BufReader, ErrorKind};
use std::path::PathBuf;
use pyo3::prelude::*;
use ndarray::s;
use numpy::{ToPyArray,PyArray1,PyArray2};
use rustc_hash::FxHashMap as HashMap;
use niffler;
use crate::{Score, PKMeta, PKGenomes};
use crate::metadata::load_metadata;
use crate::helpers::score_byte_to_blist;
use tar::Archive;
use crate::parse_kmers_scores::parse_scores;

#[pyfunction]
pub fn add_score_mat_np<'py>(py: Python<'py>, score_multi: &PyArray1<usize>, mat: &PyArray2<usize>) -> PyResult<&'py PyArray2<usize>> {
    let size = score_multi.len();
    let score_multi = score_multi.readwrite().as_array().to_owned();
    let mut mat = mat.readwrite().as_array_mut().to_owned();
    for count in 0..size {
        if score_multi[count] != 0 {
            let sum = &mat.slice(s![count, ..]) + &score_multi;
            mat.slice_mut(s![count, ..]).assign(&sum)
        }
    }
    Ok(mat.to_pyarray(py))
}

#[pyfunction]
pub fn get_adjacency_matrix<'py>(py: Python<'py>, idx_dir: &str, tar_file: &str,
) -> PyResult<(&'py PyArray2<usize>, PKGenomes)> {
    let meta: PKMeta = load_metadata(idx_dir, tar_file)?;
    let n_genomes: usize = meta.genomes.len();
    let score_counts = match tar_file.len() > 0 {
        true => count_scores_tar(idx_dir, n_genomes, tar_file),
        false => count_scores(idx_dir, n_genomes)
    };
    let mut mat: &PyArray2<usize> = PyArray2::zeros(py, [n_genomes, n_genomes], false);
    for (score, count) in score_counts.iter() {
        let score_multi: &PyArray1<usize> = score_byte_to_blist(score, n_genomes)?.iter().map(|x| x * count).collect::<Vec<usize>>().to_pyarray(py);
        let mat_updated = add_score_mat_np(py, score_multi, &mut mat).expect("could not add score");
        mat = mat_updated;
    }
    let mut genomes: PKGenomes = Vec::new();
    for i in 0..n_genomes {
        let genome = meta.genomes.get(&i).expect("could not get genome name");
        genomes.push(genome.to_string());
    }
    Ok((mat, genomes))
}

fn count_scores(idx_dir: &str, n_genomes: usize) -> HashMap<Score, usize> {
    let mut score_counts = HashMap::default();
    let score_bytes: usize = (n_genomes + 7) / 8;
    let mut score_buf = vec![0; score_bytes];
    let score_bufsize: usize = 1000 * score_bytes;
    let mut scores_in_path: PathBuf = PathBuf::from(&idx_dir);
    scores_in_path.push("scores.bgz");
    let (scores_reader, _format) = niffler::from_path(&scores_in_path).expect("File not found");
    let mut scores_in = BufReader::with_capacity(score_bufsize, scores_reader);
    loop {
        let scores = match scores_in.read_exact(&mut score_buf) {
            Ok(_) => parse_scores(&score_buf, score_bytes),
            Err(ref e) if e.kind() == ErrorKind::UnexpectedEof => break,
            // Err(ref e) if e.kind() == ErrorKind::Interrupted => continue,
            Err(e) => panic!("{:?}", e),
        };
        for score in scores.iter() {
            *score_counts.entry(score.to_owned()).or_default() += 1;
        }
    }
    score_counts
}

fn count_scores_tar(idx_dir: &str, n_genomes: usize, tar_file: &str) -> HashMap<Score, usize> {
    let mut score_counts = HashMap::default();
    let score_bytes: usize = (n_genomes + 7) / 8;
    let mut score_buf = vec![0; score_bytes];
    let score_bufsize: usize = 1000 * score_bytes;
    let (tar, _format) = niffler::from_path(tar_file).expect(
        &format!("File not found: {}", tar_file));
    for entry in Archive::new(tar).entries().expect("Can't read tar file") {
        let s = entry.expect("Error reading tar archive");
        let s_in_path = s.path().expect("Error reading tar archive");
        let s_in_str = s_in_path.to_str().unwrap().to_owned();
        if (&s_in_str).ends_with("scores.bgz") {
            let (scores_reader, _format) = niffler::get_reader(Box::new(s)).expect("Can't read from tar archive");
            let mut scores_in = BufReader::with_capacity(score_bufsize, scores_reader);
            loop {
                let scores = match scores_in.read_exact(&mut score_buf) {
                    Ok(_) => score_buf.chunks(score_bytes).map(|bytes| bytes.to_vec()).collect::<Vec<Score>>(),
                    Err(ref e) if e.kind() == ErrorKind::UnexpectedEof => break,
                    // Err(ref e) if e.kind() == ErrorKind::Interrupted => continue,
                    Err(e) => panic!("{:?}", e),
                };
                for score in scores.iter() {
                    *score_counts.entry(score.to_owned()).or_default() += 1;
                }
            }
        }
    }
    score_counts
}

// fn compute_jaccards(pkidx: &PKIdx) -> HashMap<String, HashMap<String, f64>> {
//     let score_counts = count_scores(&pkidx);
//     let mut table =  HashMap::default();
//     for (i1, f1) in pkidx.genomes.iter().enumerate() {
//         let mut row: HashMap<String, f64> = HashMap::default();
//         let (byte_idx1, bit_mask1) = genome_index_to_byte_idx_and_bit_mask(i1);
//         for (i2, f2) in pkidx.genomes.iter().enumerate() {        
//             let (byte_idx2, bit_mask2) = genome_index_to_byte_idx_and_bit_mask(i2);
//             let (mut i, mut u) = (0, 0);
//             for (score, c) in score_counts.iter(){
//                 let flag1 = (score[byte_idx1] & bit_mask1) > 0u8;
//                 let flag2 = (score[byte_idx2] & bit_mask2) > 0u8;
//                 if flag1 | flag2 { u += c };
//                 if flag1 & flag2 { i += c };
//             }
//             row.insert(f2.clone(), i as f64 / u as f64);
//         }
//         table.insert(f1.clone(), row);
//     }
//     return table
// }
