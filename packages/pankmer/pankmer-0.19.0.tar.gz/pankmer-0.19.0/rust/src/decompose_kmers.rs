//==============================================================================
// decomp0ose_kmers.rs
//==============================================================================

// Logic for decomposing a sequence into k-mers

// Imports =====================================================================
use pyo3::prelude::*;
use crate::{Kmer};
use crate::helpers::mix64;

// Functions ===================================================================

// Decompose a sequence into k-mers
//
// Each 31-bp k-mer is efficiently represented as a 64-bit integer
//
// Parameters
// ----------
// seq : &[u8]
//     nucleotide sequence
// ksize : usize
//     k-mer size
// cutoff : Kmer
//     cutoff value for mix64 downsampling
// upper : Kmer
//     upper limit of current memory block
// lower : Kmer
//     lower limit of current memory block
//
// Returns
// -------
// Vec<Kmer>
//     vector of all (non-N) k-mers observed in seq
pub fn decompose_kmers(seq: &[u8], ksize: usize, cutoff: Kmer, upper: Kmer, lower: Kmer) -> Vec<Kmer> {
    let kmermask = !(Kmer::MAX << (2 * ksize));
    let rev_comp_shift = Kmer::BITS as usize - (2 * ksize);
    let mut most_recent_n = 1;
    let mut kmercis: Kmer = 0;
    let mut kmercomp: Kmer = 0;
    let mut digimax_vec: Vec<Kmer> = Vec::new();
    let a_val: Kmer = 3;
    let c_val: Kmer = 2;
    let g_val: Kmer = 1;
    let t_val: Kmer = 0;
    let _a_rev = t_val.reverse_bits();
    let c_rev = c_val.reverse_bits();
    let g_rev = g_val.reverse_bits();
    let t_rev = a_val.reverse_bits();

    for base in seq {
        match base {
            b'A'=> { kmercis = (kmercis << 2) + a_val; kmercomp = kmercomp >> 2; }
            b'C'=> { kmercis = (kmercis << 2) + c_val; kmercomp = (kmercomp >> 2) + c_rev; }
            b'G'=> { kmercis = (kmercis << 2) + g_val; kmercomp = (kmercomp >> 2) + g_rev; }
            b'T'=> { kmercis = kmercis << 2; kmercomp = (kmercomp >> 2) + t_rev; }
            b'a'=> { kmercis = (kmercis << 2) + a_val; kmercomp = kmercomp >> 2; }
            b'c'=> { kmercis = (kmercis << 2) + c_val; kmercomp = (kmercomp >> 2) + c_rev; }
            b'g'=> { kmercis = (kmercis << 2) + g_val; kmercomp = (kmercomp >> 2) + g_rev; }
            b't'=> { kmercis = kmercis << 2; kmercomp = (kmercomp >> 2) + t_rev; }
            _=> { most_recent_n = 0; }
        }
        most_recent_n += 1;
        if most_recent_n > ksize {
            let rckmer = (kmercomp >> rev_comp_shift) & kmermask;
            let forkmer = kmercis & kmermask;
            let digimax = match forkmer >= rckmer {
                true => forkmer, false => rckmer
            };
            if mix64(digimax) < cutoff && (digimax >= lower) && (digimax < upper) {
                digimax_vec.push(digimax);
            }
        }
    }
    return digimax_vec
}

/// Decompose a sequence into k-mers
/// 
/// Each 31-bp k-mer is efficiently represented as a 64-bit integer
///
/// Parameters
/// ----------
/// seq : str
///     nucleotide sequence
/// ksize : int
///     k-mer size
/// upper : int
///     upper limit of current memory block
/// lower : int
///     lower limit of current memory block
/// cutoff : int
///     cutoff value for mix64 downsampling
/// 
/// Returns
/// -------
/// list
///     list of all (non-N) k-mers observed in seq
#[pyfunction]
pub fn break_seq(seq: &[u8], ksize: usize, upper: Kmer, lower: Kmer, cutoff: Kmer) -> PyResult<Vec<Kmer>> {
    let digimax_vec = decompose_kmers(seq, ksize, cutoff, upper, lower);
    Ok(digimax_vec)
}
