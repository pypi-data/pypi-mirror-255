use pyo3::prelude::*;

mod cap;

#[pymodule]
fn windows_cap(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<cap::WindowCapture>()?;
    Ok(())
}
