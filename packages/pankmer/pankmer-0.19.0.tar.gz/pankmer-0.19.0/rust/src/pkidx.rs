//==============================================================================
// pkidx.rs
//==============================================================================

// High-level logic for indexing

// Imports =====================================================================
use std::{fs, str, io};
use std::fs::File;
use std::io::{Write, BufWriter};
use std::iter::zip;
use std::path::PathBuf;
use niffler;
use pyo3::prelude::*;
use rayon::iter::{IntoParallelRefIterator, ParallelIterator};
use rustc_hash::FxHashMap as HashMap;
use serde::{Serialize, Deserialize};
use crate::{Kmer, Score, PKTbl, PKGenomes, MemBlocks, GZIP_LEVELS};
use crate::helpers::{print_err, genomes_to_fastq_indicators, any_are_fastq, fastq_indicators_to_bitmask};
use crate::mem_blocks::generate_mem_blocks;
use crate::get_kmers::get_kmers;

// Structs =====================================================================

// A k-mer index
#[derive(Serialize, Deserialize, Debug)]
pub struct PKIdx {
    pub kmers: PKTbl,
    pub genomes: PKGenomes,
    pub k: usize,
    pub kmer_cutoff: Kmer
}

// Functions ===================================================================

/// Run indexing
///
/// Carry out the indexing algorithm on a set of input genomes. See complete
/// description of the algorithm at https://salk-tm.gitlab.io/pankmer/algorithm.html
/// 
/// Parameters
/// ----------
/// genomes_input : str
///     path to directory or tar file containing input genomes
/// genomes : list
///     list of paths to input genomes
/// genomes_paired : list
///     list of paths to input genomes with paired files
/// outdir : str
///     path to directory or tar file for output index
/// fraction : float
///     k-mer fraction for downsampling
/// gzip_level : int
///     gzip level for file compression
/// kmersize : int
///     k-mer size in bp for indexing
/// split_memory : int
///     number of memory blocks
/// threads : int
///     number of threads
/// index : str
///     path to preexisting index to update (not implemented yet)
/// input_is_tar : bool
///     if True, `genomes_input` will be treated as a tar file
/// 
/// Returns
/// -------
/// dict, list
///     positions dictionary, list of memory block bounds
#[pyfunction]
pub fn run_index(genomes_input: &str, genomes: PKGenomes, genomes_paired: PKGenomes,
                 outdir: &str, fraction: f64,
                 gzip_level: usize, kmersize: usize, split_memory: u64,
                 threads: usize, index: &str,
                 input_is_tar: bool) -> PyResult<(HashMap<Kmer, u64>, MemBlocks)>{
    let tar_file = match input_is_tar {
        true => String::from(genomes_input),
        false => String::from("")
    };
    print_err("Generating subindex scheme");
    let all_core_blocks: MemBlocks = generate_mem_blocks(split_memory, threads as u64)?;
    let mut positions_dictionary: HashMap<Kmer, u64> = HashMap::default();
    print_err("Indexing genomes.");
    let post_dict = index_genomes(&all_core_blocks, &genomes, &genomes_paired, kmersize,
        fraction, gzip_level, &outdir, threads, index, &tar_file).expect("couldn't index genomes");
    print_err("Finished Indexing.");
    print_err("Concatenating files.");
    concat_files(post_dict, &all_core_blocks, &outdir, &mut positions_dictionary)?;
    print_err("Finished concatenating.");
    Ok((positions_dictionary, all_core_blocks))
}

// Run core cohort
// 
// This function is the item for the rayon parallel iterator. It mainly wraps
// create_index().
// 
// Parameters
// ----------
// args : (&Vec<Kmer>, &PKGenomes, usize, f64, usize, &str, &str, &str)
//     arguments to create_index()
//
// Returns
// -------
// String, PKTbl
//     the key for this memory block "{lower bound}_{upper bound}", this
//     block's entry for the positions dictionary
fn run_core_cohort(args: (&Vec<Kmer>, &PKGenomes, &PKGenomes, usize, f64, usize, &str, &str, &str)) -> (String, HashMap<Kmer, u64>) {
    let (limits, genomes, genomes_paired, kmersize, kmer_fraction, gzip_level, outdir, index, tar_file) = args;
    let (lower, upper) = (limits[0], limits[1]);
    let kmer_bytes: usize = (2 * kmersize + 7) / 8;
    let score_bytes = (genomes.len() + 7) / 8;
    let key = format!("{lower}_{upper}");
    let kmers_post = create_index(genomes, genomes_paired, kmersize, kmer_fraction, gzip_level, upper, lower,
        kmer_bytes, score_bytes,  &outdir, &tar_file).expect("Failed to run core cohort");
    (key, kmers_post)
}

// Index genomes
//
// Use rayon to iterate over memory blocks in parallel and generate temporary
// sub-indexes
//
// Parameters
// ----------
// all-core_blocks :  &[Vec<u64>]
//     array of memory blocks
// genomes : &PKGenomes
//     vector of genome paths
// genomes_paired : &PKGenomes
//     vector of genome paths for paired files
// kmersize : usize
//     k-mer size in bp
// kmer_fraction : f64
//     fraction of k-mers to keep when downsampling
// gzip_level : usize
//     gzip level for file compression
// outdir : &str
//     path to directory or tar file for output index
// threads : usize
//     number of threads
// index : str
//     preexisting index to update (not implemented yet)
// tar_file : &str
//     if input genomes are in a tar file, path to the tar file. Otherwise,
//     empty string
//
// Returns
// -------
/// dict
///     post dict
fn index_genomes(all_core_blocks: &Vec<Vec<u64>>, genomes: &PKGenomes, genomes_paired: &PKGenomes, kmersize: usize, kmer_fraction: f64,
                 gzip_level: usize, outdir: &str, threads: usize, index: &str,
                 tar_file: &str) -> PyResult<HashMap<String, HashMap<Kmer, u64>>> {
    let mut core_block_args: Vec<(&Vec<Kmer>, &PKGenomes, &PKGenomes, usize, f64, usize, &str, &str, &str)> = Vec::new();
    let rayon_num_threads: usize = rayon::current_num_threads();
    let results = match threads >= rayon_num_threads {
        true => {
            print_err(&format!("{threads} threads requested, using {rayon_num_threads} (entire global thread pool)"));
            for limits in all_core_blocks.iter() {
                core_block_args.push((limits, genomes, genomes_paired, kmersize, kmer_fraction, gzip_level, &outdir, &index, &tar_file));
            }
            core_block_args.par_iter().map(|args| run_core_cohort(*args)).collect::<Vec<(String, HashMap<Kmer, u64>)>>()
        },
        false => {
            print_err(&format!("{threads} threads requested, using {threads} (partial global thread pool)"));
            let mut results: Vec<(String, HashMap<Kmer, u64>)> = Vec::new();
            let cb_len = all_core_blocks.len();
            for (i, limits) in all_core_blocks.iter().enumerate() {
                core_block_args.push((limits, genomes, genomes_paired, kmersize, kmer_fraction, gzip_level, &outdir, &index, &tar_file));
                if (i+1)%threads==0 || (i+1)==cb_len {
                    results.extend(core_block_args.par_iter().map(|args| run_core_cohort(*args)).collect::<Vec<(String, HashMap<Kmer, u64>)>>());
                    core_block_args.clear();
                }
            }
            results
        }
    };
    let mut post_dict: HashMap<String, HashMap<Kmer, u64>> = HashMap::default();
    for result in results {
        post_dict.insert(result.0, result.1);
    }
    Ok(post_dict)
}

// Concatenate and/or merge sub-index files
//
// k-mer files (kmers.bgz) and score files (scores.bgz) are directly concatenated
// 
// Parameters
// ----------
// post_dict : HashMap<String, HashMap<Kmer, u64>>
//     post_dict returned by index_genomes
// all_core_blocks : &[Vec<u64>]
//     array of memory blocks
// outdir : &str
//     path to output directory
// positions_dict :  &mut HashMap<Kmer, u64>
//     positions dictionary
//
// Returns
// -------
// positions_dict
//     positions dictionary for metadata
fn concat_files(post_dict: HashMap<String, HashMap<Kmer, u64>>,
                all_core_blocks: &[Vec<u64>], outdir: &str,
                positions_dict: &mut HashMap<Kmer, u64>) -> PyResult<()> {
    let mut num: u64 = 0;
    let mut kmers_out_path = PathBuf::from(&outdir);
    kmers_out_path.push("kmers.bgz");
    let mut scores_out_path = PathBuf::from(&outdir);
    scores_out_path.push("scores.bgz");
    let mut kmers_out = File::create(&kmers_out_path)?;
    let mut scores_out = File::create(&scores_out_path)?;
    for limits in all_core_blocks {
        let lower = limits[0];
        let upper = limits[1];
        let key  = format!("{lower}_{upper}");
        let temp_dict = post_dict.get(&key).unwrap();
        let mut sorted_temp: Vec<(&Kmer, &u64)> = temp_dict.iter().collect();
        sorted_temp.sort_unstable();
        for (kmer, cur) in sorted_temp {
            num = cur + num;
            positions_dict.insert(*kmer, num);
        }
        num += 1;
        let mut kmers_in_path: PathBuf = PathBuf::from(&outdir);
        kmers_in_path.push(format!("{lower}_{upper}_kmers.bgz"));
        let mut kmers_in = File::open(&kmers_in_path)?;
        io::copy(&mut kmers_in, &mut kmers_out)?;
        fs::remove_file(&kmers_in_path)?;
        let mut scores_in_path: PathBuf = PathBuf::from(&outdir);
        scores_in_path.push(format!("{lower}_{upper}_scores.bgz"));
        let mut scores_in = File::open(&scores_in_path)?;
        io::copy(&mut scores_in, &mut scores_out)?;
        fs::remove_file(&scores_in_path)?;
    }
    Ok(())
}

fn score_filter(
    score: &Score,
    fastq_bitmask: &Vec<u8>
) -> Score {
    let mut filtered_score = vec![0u8; score.len() / 2];
    for (i, (bytes, mask)) in zip(score.chunks(2), fastq_bitmask.chunks(2)).enumerate() {
        let masked = [bytes[0] & mask[0], bytes[1] & mask[1]];
        filtered_score[i] = (0..4).map(|bit| ((masked[0]>>bit)|(masked[0]>>(bit+1)))&(1<<bit)).sum::<u8>()
                         | ((0..4).map(|bit| ((masked[1]>>bit)|(masked[1]>>(bit+1)))&(1<<bit)).sum::<u8>()<<4)
    }
    filtered_score
}

fn write_kmers_any_fastq(
    sorted_kmers: Vec<(u64, Vec<u8>)>,
    kmer_bytes: usize,
    kmers_out: &mut BufWriter<Box<dyn Write>>,
    scores_out: &mut BufWriter<Box<dyn Write>>,
    filter_threshold: usize,
    fastq_bitmask: &Vec<u8>,
    kmers_post: &mut HashMap<Kmer, u64>
) -> u64 {
    let mut count: u64 = 0;
    for (kmer, score) in sorted_kmers {
        let filtered_score = score_filter(&score, fastq_bitmask);
        if filtered_score.iter().all(|&i| i==0u8) {continue}
        kmers_out.write_all(&kmer.to_be_bytes()[8-kmer_bytes..]).unwrap();
        scores_out.write_all(&filtered_score).unwrap();
        if count%10000000 == 0 && count != 0 {
            kmers_post.insert(kmer, count);
            count = 0;
        }
        count += 1;
    }
    count
}

fn write_kmers_all_fasta(
    sorted_kmers: Vec<(u64, Vec<u8>)>,
    kmer_bytes: usize,
    kmers_out: &mut BufWriter<Box<dyn Write>>,
    scores_out: &mut BufWriter<Box<dyn Write>>,
    kmers_post: &mut HashMap<Kmer, u64>
) -> u64 {
    let mut count: u64 = 0;
    for (kmer, score) in sorted_kmers {
        kmers_out.write_all(&kmer.to_be_bytes()[8-kmer_bytes..]).unwrap();
        scores_out.write_all(&score).unwrap();
        if count%10000000 == 0 && count != 0 {
            kmers_post.insert(kmer, count);
            count = 0;
        }
        count += 1;
    }
    count
}

// Create an index (sub-index)
//
// this function is called to create a sub-index during indexing, essentially
// wrapped by run_core_cohort
//
// Parameters
// ----------
// genomes : &PKGenomes
//     vector of paths to input genomes
// genomes_paired : &PKGenomes
//     vector of paths to input genomes with paired files
// kmersize : usize
//     k-mer size in bp
// kmer_fraction : f64
//     k-mer fraction for downsampling
// gzip_level : usize
//     gzip level for file compression
// upper : Kmer
//     upper bound of current memory block
// lower : Kmer
//     lower bound of current memory block
// kmer_bytes : usize
//     number of bytes required to contain a Kmer (always 8 for 31-mers)
// score_bytes : usize
//     number of bytes per Score ((n_genomes + 7) / 8)
// outdir : &str
//     path to output index directory
// tar_file : &str
//     if the input genomes are in a tar file, path to the file. Otherwise empty
//     string
// tar_file : &str
//     if the paired input genomes are in a tar file, path to the file.
//     Otherwise empty string
fn create_index(genomes: &PKGenomes, genomes_paired: &PKGenomes, kmersize: usize, kmer_fraction: f64,
                gzip_level: usize,
                upper: Kmer, lower: Kmer, kmer_bytes: usize,
                score_bytes: usize, outdir: &str, tar_file: &str) -> PyResult<HashMap<Kmer, u64> > {
    let filter_threshold = 2;
    let idx: PKIdx = get_kmers(kmersize, kmer_fraction, upper, lower,
                               genomes.to_vec(), genomes_paired.to_vec(),
                               tar_file);
    let mut kmers_out_path = PathBuf::from(&outdir);
    kmers_out_path.push(format!("{lower}_{upper}_kmers.bgz"));
    let mut scores_out_path = PathBuf::from(&outdir);
    scores_out_path.push(format!("{lower}_{upper}_scores.bgz"));
    let kmer_bufsize: usize = 1000 * kmer_bytes;
    let score_bufsize: usize = 1000 * score_bytes;
    let mut kmers_out = BufWriter::with_capacity(kmer_bufsize, niffler::to_path(kmers_out_path, niffler::compression::Format::Gzip, GZIP_LEVELS[gzip_level]).expect("Can't open file for writing"));
    let mut scores_out = BufWriter::with_capacity(score_bufsize, niffler::to_path(scores_out_path, niffler::compression::Format::Gzip, GZIP_LEVELS[gzip_level]).expect("Can't open file for writing"));
    let kmers: PKTbl = idx.kmers;
    let kmer_none: bool = kmers.is_empty();
    let mut sorted_kmers: Vec<(Kmer, Score)> = kmers.into_iter().collect();
    sorted_kmers.sort_unstable();
    let kmer_end: Kmer = match kmer_none {
        true => 0,
        false => sorted_kmers[sorted_kmers.len()-1].0
    };
    let mut kmers_post: HashMap<Kmer, u64> = HashMap::default();
    let fastq_indicators = genomes_to_fastq_indicators(genomes, genomes_paired);
    let fastq_bitmask = fastq_indicators_to_bitmask(&fastq_indicators);
    let count = match any_are_fastq(genomes, genomes_paired) {
        true => write_kmers_any_fastq(sorted_kmers, kmer_bytes, &mut kmers_out,
            &mut scores_out, filter_threshold, &fastq_bitmask,
            &mut kmers_post),
        false => write_kmers_all_fasta(sorted_kmers, kmer_bytes, &mut kmers_out,
            &mut scores_out, &mut kmers_post)
    };
    kmers_out.flush().unwrap();
    scores_out.flush().unwrap();
    if !kmer_none && !kmers_post.contains_key(&kmer_end) {
        kmers_post.insert(kmer_end, count-1);
    }
    Ok(kmers_post)
}
