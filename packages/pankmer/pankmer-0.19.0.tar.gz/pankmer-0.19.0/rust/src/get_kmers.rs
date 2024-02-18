//==============================================================================
// get_kmers.rs
//==============================================================================

// Logic for extracting k-mers from a set of genomes and creating the k-mer
// index

// Imports =====================================================================
use std::io::BufRead;
use std::iter::zip;
use bio::io::{fasta, fastq};
use niffler;
use rustc_hash::FxHashMap as HashMap;
use tar::Archive;
use crate::{Kmer, Score, PKTbl, PKGenomes};
use crate::helpers::{print_err, genome_name, has_fasta_ext, has_fastq_ext, any_are_fastq};
use crate::decompose_kmers::break_seq;
use crate::pkidx::PKIdx;

// Functions ===================================================================

// Genome index to byte index and bit mask
//
// From a genome's index in the genome list, get its byte index (the index of
// this genome's byte in the score list) and its bit mask (a byte with a 1 in
// the position of this genome)
//
// Parameters
// ----------
// i : usize
//    The genome's index in the genome list
//
// Returns
// -------
// usize, u8
//     byte index and bit mask
#[inline]
pub fn genome_index_to_byte_idx_and_bit_mask(i: usize, nbytes: usize) -> (usize, u8) {
    let byte_idx = nbytes - 1 - (i / 8);
    let bit_mask = match i%8 {
        0 => { 1u8 }
        1 => { 2u8 }
        2 => { 4u8 }
        3 => { 8u8 }
        4 => { 16u8 }
        5 => { 32u8 }
        6 => { 64u8 }
        7 => { 128u8 }
        _ => panic!("This ought to be impossible.")
    };
    return (byte_idx, bit_mask)
}

// Genome index to byte index and bit mask (filter)
//
// From a genome's index in the genome list, get its byte index (the index of
// this genome's byte in the score list) and its bit mask (a byte with a 1 in
// the position of this genome)
//
// Parameters
// ----------
// i : usize
//    The genome's index in the genome list
//
// Returns
// -------
// usize, u8
//     byte index and bit mask
#[inline]
pub fn genome_index_to_byte_idx_and_bit_mask_filter(i: usize, nbytes: usize) -> (usize, u8) {
    let byte_idx = 2*(nbytes - 1 - (i / 8));
    let bit_mask = match i%4 {
        0 => { 1u8 }
        1 => { 4u8 }
        2 => { 16u8 }
        3 => { 64u8 }
        _ => panic!("This ought to be impossible.")
    };
    return (byte_idx, bit_mask)
}

// Parse FASTA record
//
// Parameters
// ----------
// result : Result
//     the Result value wrapping a fasta::Record, the item of the
//     fasta::Reader.records() iterator
//
// Returns
// -------
// Vec<u8>
//     the (uppercase) sequence of the fasta::Record as ascii bytes
fn parse_record_fasta(result: Result<bio::io::fasta::Record, std::io::Error>) -> Vec<u8> {
    let record = result.expect("Error during fasta record parsing");
    record.seq().to_ascii_uppercase()
}

// Parse FASTQ record
//
// Parameters
// ----------
// result : Result
//     the Result value wrapping a fastq::Record, the item of the
//     fastq::Reader.records() iterator
//
// Returns
// -------
// Vec<u8>
//     the (uppercase) sequence of the fastq::Record as ascii bytes
fn parse_record_fastq(result: Result<bio::io::fastq::Record, bio::io::fastq::Error>) -> Vec<u8> {
    let record = result.expect("Error during fasta record parsing");
    record.seq().to_ascii_uppercase()
}

// Update a score in the k-mer table
//
// Check a new k-mer against a k-mer index. If an entry is already present,
// return an updated score including the current genome. If an entry is not
// already present, return an initializing score including only the current
// genome.
//
// Parameters
// ----------
// kmers : &PKTbl
//     table mapping k-mers to score indices
// kmer : &Kmer
//     the k-mer to be updated
// byte_idx : usize
//     the byte index of the current genome
// bit_mask : u8
//     the bit mask of the current genome
// nbytes : usize
//     number of bytes in the score vector
//
// Returns
// Score
//     updated score
fn update_score(kmers: &PKTbl, kmer: &Kmer, byte_idx: usize, bit_mask: u8,
                nbytes: usize) -> Score {
    let new_score: Score = match kmers.get(&kmer) {
        Some(s) => {
            let mut score: Score = s.to_vec();
            score[byte_idx] = score[byte_idx] | bit_mask;
            score
        },
        None => {
            let mut score: Score = vec![0; nbytes];
            score[byte_idx] = bit_mask;
            score
        }
    };
    new_score
}

// Update a score in the k-mer table (filter)
//
// Check a new k-mer against a k-mer index. If an entry is already present,
// return an updated score including the current genome. If an entry is not
// already present, return an initializing score including only the current
// genome.
//
// Parameters
// ----------
// kmers : &PKTbl
//     table mapping k-mers to score indices
// kmer : &Kmer
//     the k-mer to be updated
// byte_idx : usize
//     the byte index of the current genome
// bit_mask : u8
//     the bit mask of the current genome
// nbytes : usize
//     number of bytes in the score vector
//
// Returns
// Score
//     updated score
fn update_score_filter(kmers: &PKTbl, kmer: &Kmer, byte_idx: usize,
                       bit_mask: u8, nbytes: usize) -> Score {
    let new_score: Score = match kmers.get(&kmer) {
        Some(s) => {
            let mut score: Score = s.to_vec();
            score[byte_idx] = score[byte_idx] + ((3*bit_mask)&(score[byte_idx]+bit_mask));
            score
        },
        None => {
            let mut score: Score = vec![0; 2*nbytes];
            score[byte_idx] = bit_mask;
            score
        }
    };
    new_score
}

fn break_seqs_fasta<B>(reader: fasta::Reader<B>, kmersize: usize, upper: Kmer,
                       lower: Kmer, cutoff: Kmer, byte_idx: usize,
                       bit_mask: u8, nbytes: usize,
                       kmers: &mut PKTbl) -> () where B: BufRead {
    for result in reader.records() {
        let seq = parse_record_fasta(result);
        for kmer in break_seq(&seq, kmersize, upper, lower, cutoff).expect("Error decomposing sequence") {
            let new_score: Score = update_score(&kmers, &kmer,
                byte_idx,  bit_mask, nbytes);
            kmers.insert(kmer, new_score);
        }
    }
}

fn break_seqs_fasta_filter<B>(reader: fasta::Reader<B>, kmersize: usize, upper: Kmer,
                              lower: Kmer, cutoff: Kmer, byte_idx:usize,
                              bit_mask: u8, nbytes: usize,
                              kmers: &mut PKTbl) -> () where B: BufRead {
    for result in reader.records() {
        let seq = parse_record_fasta(result);
        for kmer in break_seq(&seq, kmersize, upper, lower, cutoff).expect("Error decomposing sequence") {
            let new_score: Score = update_score_filter(&kmers, &kmer,
                byte_idx,  bit_mask, nbytes);
            kmers.insert(kmer, new_score);
        }
    }
}

fn break_seqs_fastq_filter<B>(reader: fastq::Reader<B>, kmersize: usize, upper: Kmer,
                              lower: Kmer, cutoff: Kmer, byte_idx: usize,
                              bit_mask: u8, nbytes: usize,
                              kmers: &mut PKTbl) -> () where B: BufRead {
    for result in reader.records() {
        let seq = parse_record_fastq(result);
        for kmer in break_seq(&seq, kmersize, upper, lower, cutoff).expect("Error decomposing sequence") {
            let new_score: Score = update_score_filter(&kmers, &kmer,
                byte_idx,  bit_mask, nbytes);
            kmers.insert(kmer, new_score);
        }
    }
}

fn commonprefix(pair: &[String]) -> String {
    let mut prefix = String::new();
    for (c0, c1) in zip(pair[0].chars(), pair[1].chars()) {
        if c0 == c1 {
            prefix.push(c0);
        } else {
            break
        }
    }
    prefix
}

pub fn get_kmers(kmersize: usize, kmer_fraction: f64,
                 upper: Kmer, lower: Kmer, genomes: PKGenomes,
                 genomes_paired: PKGenomes, tar_file: &str) -> PKIdx {
    let mut kmers: PKTbl = HashMap::default();
    let mut prefixes = Vec::new();
    let cutoff = (kmer_fraction * Kmer::MAX as f64) as Kmer;
    let gnum: usize = genomes.len();
    let gnum_paired: usize = genomes_paired.len() / 2;
    let gnum_total = gnum + gnum_paired;
    let nbytes = (gnum_total + 7) / 8;
    let any_fastq = any_are_fastq(&genomes, &genomes_paired);
    // unpaired
    if gnum > 0 && tar_file.len() > 0 {
        let (tar, _format) = niffler::from_path(tar_file).expect(
            &format!("File not found: {}", tar_file));
        let mut i = 0;
        for f in Archive::new(tar).entries().expect("Can't read tar file") {
            let f = f.expect("Error reading tar archive");
            let genome_path = f.header().path().expect("Error reading tar archive");
            let genome_str = genome_path.to_str().unwrap().to_owned();
            if !(has_fasta_ext(&genome_str) || has_fastq_ext(&genome_str)) { continue; }
            print_err(&format!("Scoring {0} ({1}/{2}).", genome_name(&genome_str).expect("Error inferring genome name"), i+1, gnum_total));
            let (byte_idx, bit_mask) = match any_fastq {
                true => genome_index_to_byte_idx_and_bit_mask_filter(i, nbytes),
                false => genome_index_to_byte_idx_and_bit_mask(i, nbytes)
            };
            i += 1;
            let (reader, _format) = niffler::get_reader(Box::new(f)).expect("Can't read from tar archive");
            match (has_fasta_ext(&genome_str), has_fastq_ext(&genome_str), any_fastq) {
                (true, false, false) => break_seqs_fasta(fasta::Reader::new(reader),
                                                  kmersize, upper, lower, cutoff,
                                                  byte_idx, bit_mask, nbytes,
                                                  &mut kmers),
                (true, false, true) => break_seqs_fasta_filter(fasta::Reader::new(reader),
                                                  kmersize, upper, lower, cutoff,
                                                  byte_idx, bit_mask, nbytes,
                                                  &mut kmers),
                (false, true, true) => break_seqs_fastq_filter(fastq::Reader::new(reader),
                                                  kmersize, upper, lower, cutoff,
                                                  byte_idx, bit_mask, nbytes,
                                                  &mut kmers),
                _ => panic!("should not be possible")
            };
            print_err(&format!("Finished scoring {0}.", genome_name(&genome_str).expect("Error inferring genome name")));
        }
    } else if gnum > 0 {
        for (i, f) in genomes.iter().enumerate() {
            let (byte_idx, bit_mask) = genome_index_to_byte_idx_and_bit_mask(i, nbytes);
            print_err(&format!("Scoring {0} ({1}/{2}).", genome_name(f).expect("Error inferring genome name"), i+1, gnum_total));
            let (reader, _format) = niffler::from_path(f).expect(&format!("File not found: {}", f));
            match (has_fasta_ext(&f), has_fastq_ext(&f), any_fastq) {
                (true, false, false) => break_seqs_fasta(fasta::Reader::new(reader),
                                                  kmersize, upper, lower, cutoff,
                                                  byte_idx, bit_mask, nbytes,
                                                  &mut kmers),
                (true, false, true) => break_seqs_fasta_filter(fasta::Reader::new(reader),
                                                  kmersize, upper, lower, cutoff,
                                                  byte_idx, bit_mask, nbytes,
                                                  &mut kmers),
                (false, true, true) => break_seqs_fastq_filter(fastq::Reader::new(reader),
                                                  kmersize, upper, lower, cutoff,
                                                  byte_idx, bit_mask, nbytes,
                                                  &mut kmers),
                _ => panic!("should not be possible")
            };
            print_err(&format!("Finished scoring {0}.", genome_name(f).expect("Error inferring genome name")));
        }
    }

    // paired
    if gnum_paired > 0 {
        for (i, pair) in genomes_paired.chunks(2).enumerate() {
            let prefix = commonprefix(&pair);
            print_err(&format!("Scoring {0} ({1}/{2}).", genome_name(&prefix).expect("Error inferring genome name"), i+gnum+1, gnum_total));
            let (byte_idx, bit_mask) = genome_index_to_byte_idx_and_bit_mask(i+gnum, nbytes);
            for f in pair {
                let (reader, _format) = niffler::from_path(f).expect(&format!("File not found: {}", f));
                match (has_fasta_ext(&f), has_fastq_ext(&f), any_fastq) {
                    (true, false, false) => break_seqs_fasta(fasta::Reader::new(reader),
                                                    kmersize, upper, lower, cutoff,
                                                    byte_idx, bit_mask, nbytes,
                                                    &mut kmers),
                    (true, false, true) => break_seqs_fasta_filter(fasta::Reader::new(reader),
                                                    kmersize, upper, lower, cutoff,
                                                    byte_idx, bit_mask, nbytes,
                                                    &mut kmers),
                    (false, true, true) => break_seqs_fastq_filter(fastq::Reader::new(reader),
                                                    kmersize, upper, lower, cutoff,
                                                    byte_idx, bit_mask, nbytes,
                                                    &mut kmers),
                    _ => panic!("should not be possible")
                };
            }
            print_err(&format!("Finished scoring {0}.", genome_name(&prefix).expect("Error inferring genome name")));
            prefixes.push(prefix);
        }
    }
    PKIdx {
        kmers: kmers, 
        genomes: genomes.into_iter().chain(prefixes.into_iter()).collect(),
        k: kmersize,
        kmer_cutoff: cutoff
    }
}
