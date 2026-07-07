import corr
import ctypes
import cacode
import signal
import numpy as np

def main(buf, reader, transmitter):
    saq = corr.correlator(sample_rate = 2.0480e6, integrations = 10, frequency_resolution = 500)
    samples = np.empty(2048 * 10 * 2, dtype = np.dtype('B'))
    
    while True:
        handover = False
        buf.get_lock()
        
        try:
            if buf.available(reader) >= (2048 * 10 * 2):
                buf.read_block(samples, reader)
                handover = True
        except buffer.is_empty_except:
            print("ACQUISITION Empty buffer violation!")
        finally:
            buf.release_lock()

        if handover:
            data = samples.astype(np.float64)
            data = (data - 127.5) / 127.5
            
            for sat in saq.run(data.view(np.complex128)):
                transmitter.send(sat)