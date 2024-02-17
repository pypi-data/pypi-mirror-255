import threading
from atomicity import AtomicCounter

COUNT:int = 1000
nbTH:int = 10

def test_atomic_counter_increment():
    atom = AtomicCounter( 0)
    
    def function_thread():
        for _ in range(COUNT): atom.increment()
            
    # Create multiple threads to increment the atomic integer concurrently
    threads = []
    for _ in range(nbTH):
        t = threading.Thread( target=function_thread)
        threads.append(t)
        t.start()
          
    # Wait for all threads to complete
    for t in threads: t.join()
    # The expected value should be the number of threads multiplied by the number of increments per thread
    expected_value = nbTH * COUNT
    assert atom.get() == expected_value
    
    
def test_atomic_counter_decrement():
    atom = AtomicCounter( nbTH * COUNT * 2 )
    
    def function_thread():
        for _ in range(COUNT): atom.decrement()
            
    # Create multiple threads to increment the atomic integer concurrently
    threads = []
    for _ in range(nbTH):
        t = threading.Thread( target=function_thread)
        threads.append(t)
        t.start()
        
    # Wait for all threads to complete
    for t in threads:
        t.join()
    # The expected value should be the number of threads multiplied by the number of increments per thread
    expected_value = nbTH * COUNT
    assert atom.get() == expected_value
    

def test_atomic_counter_add_race_condition():
    atom = AtomicCounter(0)

    def function_thread(value):
        for _ in range(COUNT): atom.add( value)

    # Create multiple threads to concurrently add to the atomic integer
    threads = []
    for i in range(nbTH):
        t = threading.Thread( target=function_thread, args=(i,))
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:   t.join()

    # The expected value should be the sum of 0 + 1 + 2 + ... + 9 multiplied by the number of increments per thread
    expected_value = sum(range(nbTH)) * COUNT
    assert atom.get() == expected_value


def test_atomic_counter_race_condition_with_non_atomic_operations():
    atom = AtomicCounter(0)

    def function_thread():
        for _ in range(COUNT):
            current_value = atom.get()
            # Simulate a non-atomic operation (e.g., time-consuming calculation)
            # before updating the atomic integer
            result = current_value * 2
            atom.set( result)

    # Create multiple threads to perform non-atomic operations and update the atomic integer concurrently
    threads = []
    for _ in range(nbTH):
        t = threading.Thread( target=function_thread)
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:    t.join()
    # The expected value should be the result of the non-atomic operation applied multiple times
    expected_value = 0
    for _ in range(COUNT):
        expected_value = expected_value * 2
    assert atom.get() == expected_value


def test_atomic_bool_test_and_set_successful():
    atom = AtomicCounter(0)
    # Perform compare and exchange operation where the current value matches
    result = atom.test_and_set(0, 8888)
    # The swap should be successful, and the previous value should be True
    assert result == (True, 0)
    assert atom.get() == 8888


def test_atomic_bool_test_and_set_unsuccessful():
    atom = AtomicCounter(0)
    # Perform compare and exchange operation where the current value doesn't match
    result = atom.test_and_set(1, 8888)
    # The swap should be unsuccessful, and the previous value should be False
    assert result == (False, 0)
    assert atom.get() == 0


if __name__ == "__main__":
    test_atomic_counter_increment()
    test_atomic_counter_decrement()
    test_atomic_counter_add_race_condition()
    test_atomic_counter_race_condition_with_non_atomic_operations()
    test_atomic_bool_test_and_set_successful()
    test_atomic_bool_test_and_set_unsuccessful()
    print( "Done!")
