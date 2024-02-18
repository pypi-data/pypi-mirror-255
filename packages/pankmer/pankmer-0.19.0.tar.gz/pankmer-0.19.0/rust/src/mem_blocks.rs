//==============================================================================
// mem_blocks.rs
//==============================================================================

// Logic for dividing the k-mer space into discrete blocks, accounting for a
// biased distribution of canonical k-mers

// Imports =====================================================================
use pyo3::prelude::*;
use crate::MemBlocks;

// Functions ===================================================================

/// Generate memory blocks
/// 
/// Generate a list of blocks representing division of k-mer space. The total
/// number of blocks will be a multiple of the number of threads. Since the
/// distribution of canonical k-mers is biased towards lexically primary
/// values, (e.g. starting with "AA"), smaller blocks are used for those values.
/// See also in online documentation: https://salk-tm.gitlab.io/pankmer/algorithm.html
/// 
/// Parameters
/// ----------
/// mem_split : int
///     number of blocks per thread
/// threads : int
///     number of threads
/// 
/// Returns
/// -------
/// list
///     list of start-end pairs representing blocks of k-mer space.
#[pyfunction]
pub fn generate_mem_blocks(mem_split: u64, threads: u64) -> PyResult<MemBlocks> {
    let split_num = mem_split * (threads as u64);
    let mut all_core_blocks: MemBlocks = Vec::new();
    if split_num % 4 == 0 {
        let sm_block_size = ((1<<63)-1)/(4*split_num);
        let md_block_size = 2*sm_block_size;
        let lg_block_size = 2*md_block_size;
        let n_sm_blocks = split_num/2;
        let n_md_blocks = split_num/4;
        let n_lg_blocks = split_num/4;
        let md_block_start = lg_block_size * n_lg_blocks;
        let sm_block_start = md_block_start + md_block_size * n_md_blocks;
        let blocks_end = sm_block_start + sm_block_size * n_sm_blocks;
        for x in 0..n_lg_blocks {
            all_core_blocks.push(vec![x*lg_block_size, (x+1)*lg_block_size]);
        }
        for x in 0..n_md_blocks {
            all_core_blocks.push(vec![md_block_start+x*md_block_size,
                md_block_start+(x+1)*md_block_size]);
        }
        for x in 0..n_sm_blocks {
            all_core_blocks.push(vec![sm_block_start+x*sm_block_size,
                sm_block_start+(x+1)*sm_block_size]);
        }
        all_core_blocks.push(vec![blocks_end, (1<<63)-1]);
    } else {
        let block_size = ((1<<63)-1)/(2*split_num);
        for x in 0..split_num {
            all_core_blocks.push(vec![x*block_size, (x+1)*block_size]);
        }
        all_core_blocks.push(vec![split_num*block_size, (1<<63)-1]);
    }
    Ok(all_core_blocks)
}
