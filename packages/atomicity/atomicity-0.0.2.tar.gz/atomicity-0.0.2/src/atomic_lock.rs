use pyo3::prelude::*;
use std::sync::atomic::{ AtomicBool, Ordering};


#[pyclass(name = "AtomicLock")]
pub struct AtomicLock {
    _lock: AtomicBool,
}

#[pymethods]
impl AtomicLock {

    #[new]
    fn new( value: bool) -> Self {
        Self {
            _lock: AtomicBool::new( value),
        }
    }

    fn get( &self) -> bool {
        self._lock.load( Ordering::SeqCst)
    }

    fn set( &self, value: bool)-> PyResult<()> {
        self._lock.store( value, Ordering::SeqCst);
        Ok(())
    }

    fn acquire( &self) -> PyResult<bool> {
        let res = self._lock.compare_exchange( false, true, Ordering::SeqCst, Ordering::SeqCst);
        Ok(res.is_ok())
    }

    fn release( &self) -> PyResult<()> {
        self._lock.store( false, Ordering::SeqCst);
        Ok(())
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(self._lock.load( Ordering::SeqCst).to_string())
    }
}


