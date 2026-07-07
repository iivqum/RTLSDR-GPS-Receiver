import numpy as np
import multiprocessing
import ctypes

class is_full_except(Exception):
    pass

class is_empty_except(Exception):
    pass
 
class reader:
    def __init__(self):
        self.ptr = multiprocessing.RawValue(ctypes.c_size_t, 0)

class circular:
    def __init__(self, max_size = 32):
        self.lock = multiprocessing.Lock()
        self.readers = []
        self.write_ptr = multiprocessing.RawValue(ctypes.c_size_t, 0)
        self.size = max_size + 1
        self.buffer = multiprocessing.RawArray(ctypes.c_ubyte, self.size)
    
    def new_reader(self):
        rdr = reader()
        
        self.readers.append(rdr)
        
        return rdr
    
    def get_lock(self):
        self.lock.acquire()
        
    def release_lock(self):
        self.lock.release()
    
    def write(self, item, wait = False):
        if wait:
            # The slowest reader will prevent further writing.
            # If a reader hangs forever the writer will too.
            # Adding a timer seems appropriate so the user can decide
            # What to do
            # This is used for reading from files where the bottleneck are the readers
            for reader in self.readers:
                if self.available(reader) == 0:
                    return
    
        self.buffer[self.write_ptr.value] = item
        self.write_ptr.value = (self.write_ptr.value + 1) % self.size
        # Override behaviour
        for reader in self.readers:
            if self.available(reader) == 0:
                reader.ptr.value = (reader.ptr.value + 1) % self.size
            
    def write_block(self, buffer, wait = False):
        many = len(buffer)
        
        if many >= self.size:
            raise is_full_except

        if wait:
            # The slowest reader will prevent further writing.
            # If a reader hangs forever the writer will too.
            # Adding a timer seems appropriate so the user can decide
            # What to do
            # This is used for reading from files where the bottleneck are the readers
            for reader in self.readers:
                if self.available(reader) == 0:
                    return

        write_ptr = self.write_ptr.value
             
        for reader in self.readers:
            free = self.size - 1 - self.available(reader)
            
            if many > free:
                override = many - free
                reader.ptr.value = (reader.ptr.value + override) % self.size
        
        write = min(self.size - write_ptr, many)
        self.buffer[write_ptr : write_ptr + write] = buffer[: write]
        
        self.write_ptr.value = (write_ptr + many) % self.size

        remaining = many - write
        self.buffer[: remaining] = buffer[write : ]
        
    def available(self, reader):
        return (self.write_ptr.value - reader.ptr.value) % self.size
    
    def is_full(self):
        return self.available() == (self.size - 1)

    def is_empty(self, reader):
        return self.available(reader) == 0
        
    def get_size(self):
        return len(self.buffer)
        
    def read_block(self, buffer, reader):
        many = len(buffer)
        
        if many > self.available(reader):
            raise is_empty_except
            
        read_ptr = reader.ptr.value
        write_ptr = self.write_ptr.value

        if write_ptr < read_ptr:        
            read = min(self.size - read_ptr, many)
            buffer[: read] = self.buffer[read_ptr : read_ptr + read]
            
            if read < many:
                remaining = many - read
                buffer[read : ] = self.buffer[: remaining]

            reader.ptr.value = (read_ptr + many) % self.size
            
            return
            
        if write_ptr > read_ptr:
            buffer[:] = self.buffer[read_ptr : read_ptr + many]
            reader.ptr.value = (read_ptr + many) % self.size
        
    def read(self, reader):
        if self.is_empty(reader):
            raise is_empty_except
        
        item = self.buffer[reader.ptr.value]
        reader.ptr.value = (reader.ptr.value + 1) % self.size
 
        return item
        
if __name__ == '__main__':
    buf = circular(100)
    
    rdr = buf.new_reader()
    
    buf.read(rdr)