use crate::{Kmer, Score};

pub fn parse_kmers(kmer_buf: &[u8], kmer_bytes: usize) -> Vec<Kmer> {
    kmer_buf.chunks(kmer_bytes).map(|bytes| {
        let mut kmer_array = [0u8; 8];
        kmer_array[8-kmer_bytes..].clone_from_slice(bytes);
        u64::from_be_bytes(kmer_array)
    }).collect::<Vec<Kmer>>()
}

pub fn parse_scores(score_buf: &[u8], score_bytes: usize) -> Vec<Score> {
    score_buf.chunks(score_bytes).map(|bytes| bytes.to_vec()).collect::<Vec<Score>>()
}