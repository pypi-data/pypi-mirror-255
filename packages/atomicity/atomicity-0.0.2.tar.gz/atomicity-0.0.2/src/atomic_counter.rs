use pyo3::prelude::*;
use std::{isize};
use std::sync::atomic::{AtomicIsize, Ordering};


#[pyclass(name = "AtomicCounter")]
pub struct AtomicCounter {
    _count: AtomicIsize,
}

#[pymethods]
impl AtomicCounter {

    #[new]
    fn new( value: isize) -> Self {
        Self {
            _count: AtomicIsize::new( value),
        }
    }

    // Loads a value from the atomic integer
    fn get( &self) -> isize {
        self._count.load( Ordering::SeqCst)
    }

    // Stores a value into the atomic integer.
    fn set( &mut self, value: isize)-> PyResult<()> {
        self._count.store( value, Ordering::SeqCst);
        Ok(())
    }

    // Increment the current value, returning the previous value. This operation wraps around on overflow.
    fn increment( &self)-> isize {
        self._count.fetch_add( 1, Ordering::SeqCst)
    }

    // Decrement the current value, returning the previous value. This operation wraps around on overflow.
    fn decrement( &self)-> isize {
        self._count.fetch_sub( 1, Ordering::SeqCst)
    }

    // Adds to the current value, returning the previous value. This operation wraps around on overflow.
    fn add( &self, value: isize)-> isize {
        self._count.fetch_add( value, Ordering::SeqCst)
    }

    // Subtracts from the current value, returning the previous value.  This operation wraps around on overflow.
    fn sub( &self, value: isize)-> isize {
        self._count.fetch_sub( value, Ordering::SeqCst)
    }

    // Stores a value into the atomic integer, returning the previous value.
    fn swap( &self, value: isize)-> isize {
        self._count.swap( value, Ordering::SeqCst)
    }

    // Stores a value into the atomic integer if the current value is the same as the current value.
    // Returns the previous value.
    fn test_and_set( &self, curr: isize, value: isize) -> (bool, isize) {
        let res = self._count.compare_exchange( curr, value, Ordering::SeqCst, Ordering::SeqCst);
        (
            res.is_ok(),
            match res { Ok(v) => v, Err(v) => v }
        )
    }

    // Stores a value into the atomic integer if the current value is less than current value.
    // Returns the previous value.  Note that This method is subject to the ABA Problem.
    fn less_and_set( &self, value: isize) -> PyResult<isize> {
        Ok(self._count.fetch_max( value, Ordering::SeqCst))
    }

    // Stores a value into the atomic integer if the current value is greater than the current value.
    // Returns the previous value.  Note that This method is subject to the ABA Problem.
    fn greater_and_set( &self, value: isize) -> PyResult<isize> {
        Ok( self._count.fetch_min( value, Ordering::SeqCst))
    }

    fn __str__( &self) -> PyResult<String> {
        Ok( self._count.load( Ordering::SeqCst).to_string())
    }
}
