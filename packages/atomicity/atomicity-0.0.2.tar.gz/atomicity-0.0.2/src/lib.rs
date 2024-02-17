mod atomic_lock;
use atomic_lock::{AtomicLock};
mod atomic_counter;
use atomic_counter::{AtomicCounter};
use pyo3::prelude::*;

/// A Python module implemented in Rust.
#[pymodule]
fn atomicity(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<AtomicCounter>()?;
    m.add_class::<AtomicLock>()?;
    Ok(())
}