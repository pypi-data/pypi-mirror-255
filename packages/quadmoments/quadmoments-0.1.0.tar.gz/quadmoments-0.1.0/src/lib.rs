use numpy::{ndarray::Array2, ndarray::ArrayView1, IntoPyArray, PyArray2};
use pyo3::prelude::{pymodule, PyModule, PyResult, Python};
use rayon::prelude::*;

fn beta(m: usize, beta_above: Vec<u64>) -> Vec<u64> {
    match m {
        0 => vec![1],
        1 => vec![2, 1],
        2 => vec![8, 4, 1],
        3 => vec![48, 24, 6, 1],
        _ => {
            let mult_factor = 2 * m as u64;
            let mut result: Vec<u64> = Vec::with_capacity(m + 1);
            beta_above
                .par_iter()
                .map(|x| mult_factor * x)
                .chain(vec![1])
                .collect_into_vec(&mut result);
            result
        }
    }
}

fn build_matrix(n: usize) -> Array2<u64> {
    if n == 0 {
        Array2::<u64>::zeros((0, 0))
    } else {
        let mut betas: Array2<u64> = Array2::<u64>::zeros((0, n - 1));
        let mut row: Vec<u64> = Vec::<u64>::new();
        let mut fullrow: Vec<u64> = vec![0; n - 1];

        for m in 0..(n - 1) {
            row = beta(m, row);
            fullrow[0..=m].copy_from_slice(&row[..]);
            betas.push_row(ArrayView1::from(&fullrow)).unwrap();
        }
        betas
    }
}

#[pymodule]
#[pyo3(name = "coefs")]
fn coefs<'py>(_py: Python<'py>, m: &'py PyModule) -> PyResult<()> {
    fn beta_coefs(n: usize) -> Array2<u64> {
        build_matrix(n)
    }

    #[pyfn(m)]
    #[pyo3(name = "beta_coefs")]
    fn beta_coefs_py<'py>(py: Python<'py>, n: usize) -> &'py PyArray2<u64> {
        beta_coefs(n).into_pyarray(py)
    }

    // m.add_function(wrap_pyfunction!(beta_coefs, m)?)?;
    Ok(())
}
