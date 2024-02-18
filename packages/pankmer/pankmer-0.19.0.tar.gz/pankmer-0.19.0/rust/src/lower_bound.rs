use pyo3::prelude::*;
use rustc_hash::FxHashMap as HashMap;
use crate::Kmer;

#[pyfunction]
pub fn get_lower_bound(positions: HashMap<Kmer, Kmer>, theo_bound: Kmer) -> PyResult<Kmer> {
    let mut lower_bound: Kmer = 0;
    for (kmer, pos) in positions.into_iter() {
        if kmer > theo_bound { return Ok(lower_bound); }
        lower_bound = pos;
    }
    Ok(0)
}
