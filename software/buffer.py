import numpy as np
import multiprocessing
import ctypes

class is_full_except(Exception):
    pass

class is_empty_except(Exception):
    pass
 
class circular:
    def __init__(self, max_size = 32):
        self.lock = multiprocessing.Lock()
        self.read_ptr =  multiprocessing.RawValue(ctypes.c_size_t, 0)
        self.write_ptr = multiprocessing.RawValue(ctypes.c_size_t, 0)
        self.size = max_size + 1
        self.buffer = multiprocessing.RawArray(ctypes.c_ubyte, self.size)
        
    def get_lock(self):
        self.lock.acquire()
        
    def release_lock(self):
        self.lock.release()
    
    def write(self, item):
        self.buffer[self.write_ptr.value] = item
        self.write_ptr.value = (self.write_ptr.value + 1) % self.size
        # Override behaviour
        if self.write_ptr.value == self.read_ptr.value:
            self.read_ptr.value = (self.read_ptr.value + 1) % self.size
            
    def write_block(self, buffer):
        many = len(buffer)
        
        if many >= self.size:
            raise is_full_except

        read_ptr = self.read_ptr.value
        write_ptr = self.write_ptr.value
        # Number of bytes that can be written without overriding old data
        free = self.size - 1 - self.available()
        
        if many > free:
            override = many - free
            self.read_ptr.value = (self.read_ptr.value + override) % self.size
        
        write = min(self.size - write_ptr, many)
        self.buffer[write_ptr : write_ptr + write] = buffer[: write]
        
        wrap = write < many
        self.write_ptr.value = (write_ptr + many) % self.size

        remaining = many - write
        self.buffer[: remaining] = buffer[write : ]

        
        
    def available(self):
        return (self.write_ptr.value - self.read_ptr.value) % self.size
    
    def is_full(self):
        return self.available() == (self.size - 1)

    def is_empty(self):
        return self.available() == 0
        
    def get_size(self):
        return len(self.buffer)
        
    def read_block(self, buffer):
        many = len(buffer)
        
        if many > self.available():
            raise is_empty_except
            
        read_ptr = self.read_ptr.value
        write_ptr = self.write_ptr.value

        if write_ptr < read_ptr:        
            read = min(self.size - read_ptr, many)
            buffer[: read] = self.buffer[read_ptr : read_ptr + read]
            
            if read < many:
                remaining = many - read
                buffer[read : ] = self.buffer[: remaining]

            self.read_ptr.value = (read_ptr + many) % self.size
            
            return
            
        if write_ptr > read_ptr:
            buffer[:] = self.buffer[read_ptr : read_ptr + many]
            self.read_ptr.value = (read_ptr + many) % self.size
        
    def read(self):
        if self.is_empty():
            raise is_empty_except
        
        item = self.buffer[self.read_ptr.value]
        self.read_ptr.value = (self.read_ptr.value + 1) % self.size
 
        return item
        
if __name__ == '__main__':
    pass