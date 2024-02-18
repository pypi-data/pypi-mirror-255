//==============================================================================
// measure.rs
//==============================================================================

// Logic for measuring genome sizes in bp

// Imports =====================================================================
use std::io::BufRead;
use pyo3::prelude::*;
use bio::io::{fasta, fastq};
use niffler;
use rayon::iter::{IntoParallelRefIterator, ParallelIterator};
use rustc_hash::FxHashMap as HashMap;
use tar::Archive;
use crate::helpers::{print_err, genome_name, has_fasta_ext, has_fastq_ext};
use crate::PKGenomes;

// Functions ===================================================================

fn measure_records_fasta<B>(reader: fasta::Reader<B>) -> usize where B: BufRead {
    let mut size: usize = 0;
    for result in reader.records() {
        let record = result.expect("Error during fasta record parsing");
        size += record.seq().len();
    }
    size
}

fn measure_records_fastq<B>(reader: fastq::Reader<B>) -> usize where B: BufRead {
    let mut size: usize = 0;
    for result in reader.records() {
        let record = result.expect("Error during fastq record parsing");
        size += record.seq().len();
    }
    size
}

// Measure a genome
//
// Parameters
// ----------
// f
//    path to genome file
//
// Returns
// -------
// &str, usize
//     path to genome file, genome size
fn measure_genome(f: &str) -> (&str, usize) {
    let (reader, _format) = niffler::from_path(f).expect(&format!("File not found: {}", f));
    print_err(&format!("Measuring {0}", genome_name(f).expect("Error inferring genome name")));
    let size = match (has_fasta_ext(&f), has_fastq_ext(&f)) {
        (true, false) => measure_records_fasta(fasta::Reader::new(reader)),
        (false, true) => measure_records_fastq(fastq::Reader::new(reader)),
        (false, false) => panic!("not a genome"),
        (true, true) => panic!("not possible")
    };
    (f, size)
}

/// Measure genomes
/// 
/// Compute the size of each of a set of genomes
/// 
/// Parameters
/// ----------
/// genomes
///     iterable of genome file paths
/// tar_file : str
///     if genomes are provided as a tar file, path to the file. Otherwise,
///     empty string
/// 
/// Returns
/// -------
/// dict
///     map from genome file to genome size
#[pyfunction]
pub fn measure_genomes(genomes: PKGenomes, tar_file: &str) -> PyResult<HashMap<String, usize>> {
    let mut genome_sizes: HashMap<String, usize> = HashMap::default();
    if tar_file.len() > 0 {
        let (tar, _format) = niffler::from_path(tar_file).expect(
            &format!("File not found: {}", tar_file));
        for f in Archive::new(tar).entries().expect("Can't read tar file") {
            let f = f.expect("Error reading tar archive");
            let genome_path = f.header().path().expect("Error reading tar archive");
            let genome_str = genome_path.to_str().unwrap().to_owned();
            if !(has_fasta_ext(&genome_str) || has_fastq_ext(&genome_str)) { continue; }
            print_err(&format!("Measuring {0}.", genome_name(&genome_str).expect("Error inferring genome name")));
            let (reader, _format) = niffler::get_reader(Box::new(f)).expect("Can't read from tar archive");
            let size = match (has_fasta_ext(&genome_str), has_fastq_ext(&genome_str)) {
                (true, false) => measure_records_fasta(fasta::Reader::new(reader)),
                (false, true) => measure_records_fastq(fastq::Reader::new(reader)),
                (false, false) => panic!("not a genome"),
                (true, true) => panic!("not possible")
            };
            genome_sizes.insert(genome_str, size);
        }
    } else {
        for (file, size) in genomes.par_iter().map(|f| measure_genome(f)).collect::<Vec<(&str, usize)>>() {
            genome_sizes.insert(file.to_owned(), size);
        }
    }
    Ok(genome_sizes)
}
