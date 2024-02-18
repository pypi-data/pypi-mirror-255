//==============================================================================
// lib.rs
//==============================================================================

// This is the high-level file defining the index crate & python module

// Modules =====================================================================
mod helpers;
mod mem_blocks; // Logic for dividing k-mer space into memory blocks
mod decompose_kmers; // Logic for decomposing a sequence into k-mers
mod get_kmers;
mod pkidx;
mod parse_kmers_scores;
mod adj_matrix;
mod metadata;
mod measure;
mod subset_index;
mod lower_bound;
mod anchor;

// Imports =====================================================================
use niffler::Level;
use pyo3::prelude::*;
// use pyo3::exceptions::Py<?>Error
use rustc_hash::FxHashMap as HashMap;
use crate::helpers::{print_err, genome_name, score_byte_to_blist};
use crate::metadata::{PKMeta, dump_metadata, load_metadata};
use crate::mem_blocks::generate_mem_blocks;
use crate::decompose_kmers::{decompose_kmers, break_seq};
use crate::pkidx::run_index;
use crate::adj_matrix::{add_score_mat_np, get_adjacency_matrix};
use crate::measure::measure_genomes;
use crate::subset_index::subset;
use crate::anchor::{get_sequence_kmerbits, get_kmer_scores,
                    get_sequence_scores, get_sorted_kmer_scores,
                    combined_kmers, get_sequences_scores};

// Constants ===================================================================
pub const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const GZIP_LEVELS: [Level; 10] = [
    Level::Zero,
    Level::One,
    Level::Two,
    Level::Three,
    Level::Four,
    Level::Five,
    Level::Six,
    Level::Seven,
    Level::Eight,
    Level::Nine
];

// Types =======================================================================
pub type Kmer = u64; // Integer representation of a k-mer
pub type Score = Vec<u8>; // Vector representation of a score
pub type PKTbl = HashMap<Kmer, Score>; // Map of k-mers to scores
pub type PKGenomes = Vec<String>; // Vector of genome names
pub type PKSizes = HashMap<String, usize>;
pub type MemBlocks = Vec<Vec<Kmer>>; // Vector of k-mer space breakpoints for memory blocks

// Functions ===================================================================
#[pyfunction]
pub fn version() -> PyResult<String> {
    Ok(String::from(VERSION))
}

// PyModule ====================================================================

// This function decorated with #[pymodule] defines the PyClasses and
// PyFunctions that will be included in the exported python module
#[pymodule]
fn index(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PKMeta>()?;
    m.add_function(wrap_pyfunction!(version, m)?)?;
    m.add_function(wrap_pyfunction!(print_err, m)?)?;
    m.add_function(wrap_pyfunction!(genome_name, m)?)?;
    m.add_function(wrap_pyfunction!(break_seq, m)?)?;
    m.add_function(wrap_pyfunction!(score_byte_to_blist, m)?)?;
    m.add_function(wrap_pyfunction!(generate_mem_blocks, m)?)?;
    m.add_function(wrap_pyfunction!(dump_metadata, m)?)?;
    m.add_function(wrap_pyfunction!(load_metadata, m)?)?;
    m.add_function(wrap_pyfunction!(measure_genomes, m)?)?;
    m.add_function(wrap_pyfunction!(run_index, m)?)?;
    m.add_function(wrap_pyfunction!(subset, m)?)?;
    m.add_function(wrap_pyfunction!(get_adjacency_matrix, m)?)?;
    m.add_function(wrap_pyfunction!(add_score_mat_np, m)?)?;
    m.add_function(wrap_pyfunction!(get_sequence_kmerbits, m)?)?;
    m.add_function(wrap_pyfunction!(get_kmer_scores, m)?)?;
    m.add_function(wrap_pyfunction!(get_sequence_scores, m)?)?;
    m.add_function(wrap_pyfunction!(get_sorted_kmer_scores, m)?)?;
    m.add_function(wrap_pyfunction!(combined_kmers, m)?)?;
    m.add_function(wrap_pyfunction!(get_sequences_scores, m)?)?;
    Ok(())
}

// Tests =======================================================================
fn test_decompose_kmers(){
    let corrects = [
        0b1110101010101010101010101010101010101010101010101010101010101010u64,
        0b1110101010101010101010101010101010101010101010101010101010101001u64,
        0b1111111111111111111111111111111111111111111111111111111111111111u64,
        0b1111111111111111111111111111111111111111111111111111111111111100u64,
        0b1111111111111111111111111111111111111111111111111111111111111000u64
    ];
    let result1 = decompose_kmers(b"CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCG", 31, Kmer::MAX, Kmer::MAX, 0);
    assert_eq!(result1[0], corrects[0]);
    assert_eq!(result1[1], corrects[1]);
    let result2 = decompose_kmers(b"CGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG", 31, Kmer::MAX, Kmer::MAX, 0);
    assert_eq!(result2[1], corrects[0]);
    assert_eq!(result2[0], corrects[1]);
    let result3 = decompose_kmers(b"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAT", 31, Kmer::MAX, Kmer::MAX, 0);
    assert_eq!(result3[0], corrects[2]);
    assert_eq!(result3[1], corrects[3]);
    let result4 = decompose_kmers(b"ATTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT", 31, Kmer::MAX, Kmer::MAX, 0);
    assert_eq!(result4[0], corrects[3]);
    assert_eq!(result4[1], corrects[2]);
    let result5 = decompose_kmers(b"AAANAAAAAAAAAAAAAAAAaAAAAAAAAAAAAAA", 31, Kmer::MAX, Kmer::MAX, 0);
    assert_eq!(result5[0], corrects[2]);
    let result6 = decompose_kmers(b"ACT", 3, Kmer::MAX, Kmer::MAX, 0);
    assert_eq!(result6[0], corrects[4]);
}

// fn download_test_data(){
//     eprintln!("Downloading and Unpacking Test Data...");
//     Command::new("wget")
//             .arg("-q")
//             .arg("https://salk-tm-pub.s3.us-west-2.amazonaws.com/PanKmer_example/PanKmer_test_data_1.tar.gz")
//             .arg("-O")
//             .arg("PanKmer_test_data_1.tar.gz")
//             .output()
//             .expect("Couldn't download test data");
//     Command::new("tar")
//             .arg("-zxf")
//             .arg("PanKmer_test_data_1.tar.gz")
//             .output()
//             .expect("Couldn't unpack test data");
//     return 
// }

// fn test_create_index(){
//     let result_idx1 = create_index(
//         vec![
//             "PanKmer_test_data_1/Sp_chr19/Sp7498_HiC_Chr19.fasta".to_string(),
//             "PanKmer_test_data_1/Sp_chr19/Sp9509_oxford_v3_Chr19.fasta".to_string(),
//             "PanKmer_test_data_1/Sp_chr19/Sp9512_a02_genome_Chr19.fasta".to_string()
//         ],
//         31,
//         1.0
//     );
//     assert_eq!(4764864, result_idx1.kmers.len());
//     let result_idx2 = create_index(vec!["PanKmer_test_data_1/smalls/test1.fasta".to_string()], 31, 1.0);
//     assert_eq!(1, result_idx2.kmers.len());
//     let kmer_poly_a = Kmer::MAX;
//     assert_eq!(vec![1u8],result_idx2.scores[*result_idx2.kmers.get(&kmer_poly_a).expect(
//         "Failed to find polyA kmer in result_idx2.kmers"
//     )]);
//     let result_idx3 = create_index(vec![
//         "PanKmer_test_data_1/smalls/test1.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test2.fasta".to_string(),
//     ], 31, 1.0);
//     assert_eq!(1, result_idx3.kmers.len());
//     let result_idx4 = create_index(vec![
//         "PanKmer_test_data_1/smalls/test1.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test3.fasta".to_string(),
//     ], 31, 1.0);
//     let i = 0b1110101010101010101010101010101010101010101010101010101010101010u64;
//     assert_eq!(vec![2u8], result_idx4.scores[*result_idx4.kmers.get(&i).unwrap()]);
//     let result_idx5 = create_index(vec![
//         "PanKmer_test_data_1/smalls/test1.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test2.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test3.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test4.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test5.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test6.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test7.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test8.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test9.fasta.gz".to_string(),
//     ], 31, 1.0);
//     assert_eq!(6, result_idx5.kmers.len());
//     let i = 0b1111100000000001010100001010111100111100110011010101101010111111u64;
//     assert_eq!(vec![0u8, 1u8], result_idx5.scores[*result_idx5.kmers.get(&i).expect(
//         "failed to find expected kmer in result_idx5"
//     )]);
//     assert_eq!(vec![0b11100011u8, 0u8], result_idx5.scores[*result_idx5.kmers.get(&kmer_poly_a).expect(
//         "Failed to find polyA kmer in results_idx5"
//     )]);
//     return
// }

// fn test_load_dump(){
//     let result_idx1 = create_index(vec![
//         "PanKmer_test_data_1/smalls/test1.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test2.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test3.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test4.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test5.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test6.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test7.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test8.fasta".to_string(),
//         "PanKmer_test_data_1/smalls/test9.fasta.gz".to_string(),
//     ], 31, 1.0);
//     let fpath = "temp.pkidx";
//     dump_pkidx(&result_idx1, &fpath);
//     let result_idx2 = load_pkidx(&fpath);
//     assert_eq!(result_idx1.kmers, result_idx2.kmers);
//     assert_eq!(result_idx1.genomes, result_idx2.genomes);
//     assert_eq!(result_idx1.k, result_idx2.k);
//     assert_eq!(result_idx1.scores, result_idx2.scores);
//     assert_eq!(result_idx1.score_map, result_idx2.score_map);
//     assert_eq!(result_idx1.kmer_cutoff, result_idx2.kmer_cutoff);
//     return
// }

// fn run_tests(){
//     test_decompose_kmers();
//     download_test_data();
//     test_create_index();
//     test_load_dump();
//     eprintln!("{}", "All tests passed.");
//     return
// }
