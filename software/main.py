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
import acquire
import tracking

# 1ms
num_samples = 2048
num_bytes = num_samples * 2

if __name__ == '__main__':
    #cbuf = buffer.circular(204800)
    # Store 100 ms of samples
    cbuf = buffer.circular(num_bytes * 100)

    sample_proc = mp.Process(target = sampler.main, args = (
        cbuf, # Circular buffer reference
        2.048e6, # Sample frequency
        1575.42e6, # Center frequency
        50, # Gain
        True, # Bias tee enable
        2048 * 2 * 10 # Block size
    ), daemon = True)
    
    acquire_reader = cbuf.new_reader()
    track_reader = cbuf.new_reader()
    track_rx, track_tx = mp.Pipe(duplex = False)
    
    acquire_proc = mp.Process(target = acquire.main, args = (
        cbuf,
        acquire_reader,
        track_tx
    ), daemon = True)

    track_proc = mp.Process(target = tracking.main, args = (
        cbuf,
        track_reader,
        track_rx
    ), daemon = True)

    sample_proc.start()
    acquire_proc.start()
    track_proc.start()
    
    def sigint_handle(sig, frame):
        sys.exit()

    signal.signal(signal.SIGINT, sigint_handle)    

    while True:
        pass