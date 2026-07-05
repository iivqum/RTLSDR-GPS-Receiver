import buffer
from rtlsdr import RtlSdr
import time
import asyncio
import threading
import numpy
import corr
import multiprocessing as mp
import ctypes
import cacode
import signal
import sys
import sampler

# 1ms
num_samples = 2048
num_bytes = num_samples * 2

if __name__ == '__main__':
    #cbuf = buffer.circular(204800)
    # Store 100 ms of samples
    cbuf = buffer.circular(num_bytes * 100)
    
    print(f"Allocated {cbuf.get_size() / 1e3} Kb")
    
    byte_buf2 = numpy.empty(num_bytes * 10, dtype = numpy.dtype('B'))
    
    proc = mp.Process(target = sampler.main, args = (
        cbuf, # Circular buffer reference
        2.048e6, # Sample frequency
        1575.42e6, # Center frequency
        50, # Gain
        True, # Bias tee enable
        2048 * 2 * 10 # Block size
    ), daemon = True)
    
    saq = corr.correlator(sample_rate = 2.0480e6, integrations = 10)

    def sigint_handle(sig, frame):
        sys.exit()

    signal.signal(signal.SIGINT, sigint_handle)

    proc.start()

    while True:
        handover = False
        
        cbuf.get_lock()
        
        try:
            if cbuf.available() >= (num_bytes * 10):
                cbuf.read_block(byte_buf2)
                handover = True
        except buffer.is_empty_except:
            print("Empty buffer violation!")
        finally:
            cbuf.release_lock()

        if handover:
            data = byte_buf2.astype(numpy.float64)
            data = (data - 127.5) / 127.5
            saq.run(data.view(numpy.complex128))