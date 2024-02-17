# atomicity

[![PyPI version](https://badge.fury.io/py/atomicity.svg)](https://badge.fury.io/py/atomicity)

Atomicity is a simple library that provides atomic operation to python's synchronization primitives used in multi-threading application.

*** Note: This is at a very early stage and is subject to changes.  Use at your own risk. ***

It includes an atomic lock and counter class, ensuring (somewhat) thread-safety and prevention of race conditions in concurrent programming. 
Everything is entirely lock-free and is backed by Rust's atomic types.


## Features
TBD

## Installation

Binary wheels are provided for Python 3.8 and above on Linux, macOS, and Windows:

```bash
pip install atomicity
```

## Usage

See the [documentation](DOCS.md) for more information. Here's a quick overview:

### Atomic Counter

```python
from atomicity import AtomicCounter

# Create an atomic integer with an initial value of 0
atom = AtomicCounter()

# Perform atomic operations
atom.set(10)
value = atom.get()
print(f"Value: {value}")

previous_value = atom.add( 20)
print(f"Previous Value: {previous_value}")

atom.sub(5)
print(f"Result after addition: {atom}")

# Increment and decrement operations
atom.increment()
atom.decrement()
```

### Atomic Lock

```python
from atomicity import AtomicLock

# Create an atomic boolean with an initial value of False
atom = AtomicLock( False)

# Perform atomic operations
atom.store(True)
value = atom.acquire()
previous_value = atom.release()
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The `atomicity` library is heavily dependent on and inspired by the Rust `std::sync::atomic` module.