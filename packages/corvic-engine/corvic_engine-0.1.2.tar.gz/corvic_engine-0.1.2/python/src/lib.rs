use numpy::ndarray::{ArrayView1, ArrayViewMut1, ArrayViewMut2};
use numpy::{PyArrayLike2, PyReadonlyArray1, TypeMustMatch};
use pyo3::prelude::*;
use std::cmp::{max, min};

const SIGMOID_TABLE_SIZE: usize = 1000;
const SIGMOID_MAX_EXP: f32 = 6.;
static mut SIGMOID_TABLE: [f32; SIGMOID_TABLE_SIZE] = [0.; SIGMOID_TABLE_SIZE];

/// sigmoid(x) = 1 / (exp(-x) + 1)
fn init_sigmoid_table() {
    unsafe {
        for (i, entry) in SIGMOID_TABLE.iter_mut().enumerate() {
            let p = i as f64 / SIGMOID_TABLE_SIZE as f64 * 2. - 1.;
            let exp = (p * SIGMOID_MAX_EXP as f64).exp();
            let value = exp / (exp + 1.);
            *entry = value as f32;
        }
    }
}

fn next_random(cur_random: u64) -> u64 {
    (cur_random.wrapping_mul(25214903917u64).wrapping_add(11)) & 281474976710655u64
}

fn sigmoid(x: f32) -> f32 {
    let p = (x + SIGMOID_MAX_EXP) * (SIGMOID_TABLE_SIZE as f32 / SIGMOID_MAX_EXP / 2.);
    return *unsafe { SIGMOID_TABLE.get_unchecked(p as usize) };
}

fn saxpy(a: f32, x: &ArrayView1<'_, f32>, y: &mut ArrayViewMut1<'_, f32>) {
    let n = x.len();
    unsafe {
        for i in 0..n {
            *y.uget_mut(i) = a * x.uget(i) + y.uget(i);
        }
    }
}

fn bisect_left(a: ArrayView1<u32>, x: u32, mut low: usize, mut hi: usize) -> usize {
    while hi > low {
        let mid = (low + hi) >> 1;
        if *unsafe { a.uget(mid) } >= x {
            hi = mid;
        } else {
            low = mid + 1;
        }
    }

    low
}

#[allow(clippy::too_many_arguments)]
fn train_node2vec_word(
    num_negative: usize,
    cumulative: ArrayView1<u32>,
    embeddings: &mut ArrayViewMut2<f32>,
    hidden_layer: &mut ArrayViewMut2<f32>,
    current_word: u32,
    context_word: u32,
    alpha: f32,
    work: &mut ArrayViewMut1<f32>,
    mut cur_random: u64,
    lock_factors: ArrayView1<f32>,
) -> u64 {
    work.fill(0.);

    let cumulative_last = match cumulative.last() {
        Some(value) => *value,
        _ => 0u32,
    };

    for count_neg in 0..num_negative + 1 {
        let mut target_index = current_word as usize;
        let mut label = 1.;
        if count_neg != 0 {
            let random_target = (cur_random >> 16) as u32;

            target_index = bisect_left(
                cumulative,
                random_target % cumulative_last,
                0usize,
                cumulative.len(),
            );
            cur_random = next_random(cur_random);
            label = 0.;
            if target_index == (current_word as usize) {
                continue;
            }
        }

        let error = embeddings
            .row(context_word as usize)
            .dot(&hidden_layer.row(target_index));
        if error <= -SIGMOID_MAX_EXP || error >= SIGMOID_MAX_EXP {
            continue;
        }
        let f = sigmoid(error);
        let g = (label - f) * alpha;

        saxpy(g, &hidden_layer.row(target_index), work);
        saxpy(
            g,
            &embeddings.row(context_word as usize),
            &mut hidden_layer.row_mut(target_index),
        );
    }

    let lock_index = context_word % lock_factors.len() as u32;
    saxpy(
        lock_factors[lock_index as usize],
        &work.view(),
        &mut embeddings.row_mut(context_word as usize),
    );

    cur_random
}

/// Trains a batch of data for node2vec
#[allow(clippy::too_many_arguments)]
fn train_node2vec_batch_array(
    sentences: ArrayView1<u32>,
    words: ArrayView1<u32>,
    window: i32,
    reduced_windows: ArrayView1<i32>,
    num_negative: usize,
    cumulative: ArrayView1<u32>,
    mut embeddings: ArrayViewMut2<f32>,
    mut hidden_layer: ArrayViewMut2<f32>,
    alpha: f32,
    mut work: ArrayViewMut1<f32>,
    mut cur_random: u64,
    lock_factors: ArrayView1<f32>,
) {
    for sidx in 0..sentences.len() - 1 {
        let sentence_start = sentences[sidx] as i64;
        let sentence_end = sentences[sidx + 1] as i64;

        for cur in sentence_start..sentence_end {
            let begin = max(
                cur - window as i64 + *unsafe { reduced_windows.uget(cur as usize) } as i64,
                sentence_start,
            );
            let end = min(
                cur + window as i64 + 1 - *unsafe { reduced_windows.uget(cur as usize) } as i64,
                sentence_end,
            );
            for idx in begin..end {
                if cur == idx {
                    continue;
                }
                cur_random = train_node2vec_word(
                    num_negative,
                    cumulative,
                    &mut embeddings,
                    &mut hidden_layer,
                    words[cur as usize],
                    words[idx as usize],
                    alpha,
                    &mut work,
                    cur_random,
                    lock_factors,
                )
            }
        }
    }
}

/// Trains a batch of data for node2vec
#[pyfunction]
#[pyo3(
    text_signature = "(*, sentences, words, window, num_negative, cumulative, embeddings, hidden_layer, alpha, work, next_random, lock_factors)"
)]
#[allow(clippy::too_many_arguments)]
fn train_node2vec_batch(
    sentences: PyReadonlyArray1<u32>,
    words: PyReadonlyArray1<u32>,
    window: i32,
    reduced_windows: PyReadonlyArray1<i32>,
    num_negative: usize,
    cumulative: PyReadonlyArray1<u32>,
    embeddings: PyArrayLike2<f32, TypeMustMatch>,
    hidden_layer: PyArrayLike2<f32, TypeMustMatch>,
    alpha: f32,
    work: PyReadonlyArray1<f32>,
    next_random: u64,
    lock_factors: PyReadonlyArray1<f32>,
) {
    train_node2vec_batch_array(
        sentences.as_array(),
        words.as_array(),
        window,
        reduced_windows.as_array(),
        num_negative,
        cumulative.as_array(),
        unsafe { embeddings.as_array_mut() },
        unsafe { hidden_layer.as_array_mut() },
        alpha,
        unsafe { work.as_array_mut() },
        next_random,
        lock_factors.as_array(),
    );
}

/// A Python module implemented in Rust.
#[pymodule]
#[pyo3(name = "_native")]
fn engine(_py: Python, m: &PyModule) -> PyResult<()> {
    init_sigmoid_table();
    m.add_function(wrap_pyfunction!(train_node2vec_batch, m)?)?;
    Ok(())
}
