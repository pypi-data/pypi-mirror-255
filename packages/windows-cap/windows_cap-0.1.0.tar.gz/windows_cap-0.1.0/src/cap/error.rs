use pyo3::{prelude::*, create_exception};

#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("Win32 error: {0}")]
    Windows(#[from] windows::core::Error),
    #[error("Window not found")]
    WindowNotFound,
}


create_exception!(module, WindowsCapError, pyo3::exceptions::PyException);

impl From<Error> for PyErr {
    fn from(err: Error) -> PyErr {
        WindowsCapError::new_err(err.to_string())
    }
}