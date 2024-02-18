//==============================================================================
// helpers.rs
//==============================================================================

// small helper functions for use in other modules (or in Python code)

// Imports =====================================================================
use pyo3::prelude::*;
use time::OffsetDateTime;
use std::path::Path;
use crate::{Kmer, PKGenomes};

// Functions ===================================================================

/// Print to stderr with a timestamp
/// 
/// Parameters
/// ----------
/// message : str
///     a message to print
#[pyfunction]
pub fn print_err(message: &str) {
    let date_time = OffsetDateTime::now_utc();
    eprintln!("{date_time}: {message}");
}

/// Genome name
/// 
/// Parameters
/// ----------
/// genome : str
///     path to a genome file
/// 
/// Returns
/// -------
/// str
///     name of genome extracted from path
#[pyfunction]
pub fn genome_name(genome: &str) -> PyResult<&str> {
    let file_stem = Path::new(genome).file_stem().expect("could not get genome file stem");
    let file_stem_str = file_stem.to_str().expect("could not stringify genome file stem");
    Ok(file_stem_str)
}

/// Convert score in bytes to list of binary values
/// 
/// Parameters
/// ----------
/// b : bytes
///     bytes representation of a k-mer score
/// sz : int
///     length of score (number of genomes in index)
/// 
/// Returns
/// -------
/// list
///     the score represented as a list of binary values
#[pyfunction]
pub fn score_byte_to_blist(b: &[u8], sz: usize) -> PyResult<Vec<usize>> {
    let s = b.len();
    let vec: Vec<usize> = (0..sz).map(|k| (b[s - (k/8) - 1] & (1<<(k%8)) > 0) as usize).collect();
    Ok(vec)
}

// mix64
// 
// Pseudo-randomize a k-mer
// 
// Parameters
// ----------
// x : Kmer
//     a k-mer (u64)
//
// Returns
// -------
// Kmer
//     pseudo-randomized value using input k-mer as seed
#[inline]
pub fn mix64(mut x: Kmer) -> Kmer {
    x ^= x >> 32;
    x = x.wrapping_mul(0xbea225f9eb34556d);
    x ^= x >> 29;
    x = x.wrapping_mul(0xbea225f9eb34556d);
    x ^= x >> 32;
    x = x.wrapping_mul(0xbea225f9eb34556d);
    x ^ (x >> 29)
}

pub fn has_fasta_ext(genome_str: &str) -> bool {
    (genome_str).ends_with("fasta")
    || (genome_str).ends_with("fa")
    || (genome_str).ends_with("fna")
    || (genome_str).ends_with("fasta.gz")
    || (genome_str).ends_with("fa.gz")
    || (genome_str).ends_with("fna.gz")
}

pub fn has_fastq_ext(genome_str: &str) -> bool {
    (genome_str).ends_with("fastq")
    || (genome_str).ends_with("fq")
    || (genome_str).ends_with("fastq.gz")
    || (genome_str).ends_with("fq.gz")
}

fn has_fastq_ext_paired(pair: &[String]) -> bool {
    return match (has_fastq_ext(&pair[0]), has_fastq_ext(&pair[1])) {
        (true, true) => true,
        (false, false) => false,
        _ => panic!("mismatched file extensions")
    }
}

pub fn genomes_to_fastq_indicators(genomes: &PKGenomes, genomes_paired: &PKGenomes) -> Vec<bool> {
    let mut fastq_indicators: Vec<bool> = genomes.iter().map(|g| has_fastq_ext(g)).collect();
    let fastq_indicators_paired: Vec<bool> = genomes_paired.chunks(2).map(|g| has_fastq_ext_paired(g)).collect();
    fastq_indicators.extend(fastq_indicators_paired);
    fastq_indicators
}

pub fn fastq_indicators_to_bitmask(fastq_indicators: &Vec<bool>) -> Vec<u8> {
    let nbytes = (fastq_indicators.len() + 3) / 4;
    let mut fastq_bitmask = vec![0u8; nbytes];
    for (i, fourbools) in fastq_indicators.chunks(4).enumerate() {
        fastq_bitmask[nbytes - 1 - i] = fourbools.iter().enumerate().map(
            |(j, b)| match b {true => 2u8<<(2*j), false => 3u8<<(2*j)}).sum()
    }
    fastq_bitmask
}

pub fn any_are_fastq(genomes: &PKGenomes, genomes_paired: &PKGenomes) -> bool {
    genomes_to_fastq_indicators(&genomes, &genomes_paired).iter().any(|&is_fastq| is_fastq)
}