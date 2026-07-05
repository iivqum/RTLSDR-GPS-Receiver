import cmath
import math
import numpy as np
import matplotlib.pyplot as plt
import cacode
from rtlsdr import RtlSdr
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class correlator:
    def __init__(self, sample_rate = 2.4e6, frequency_deviation = 20e3, 
        frequency_resolution = 1e3, integrations = 10):
        
        self.sample_rate = sample_rate
        self.fdev = frequency_deviation
        self.fres = frequency_resolution
        
        self.fsteps = int(frequency_deviation / frequency_resolution)
        self.integrations = int(integrations)

        self.samples_1ms = round(1e-3 * sample_rate)
        self.samples = self.samples_1ms * integrations
                
        self.sv_codes = dict()
        self.sv_bins = dict()
        self.ifs = dict()
        
        self.time = np.arange(self.samples) / sample_rate
        
        self.threshold = 8
        
        for sv in range(1 , 33):
            #code = cacode.prn_code(sv, 0, 1023, sample_frequency)
            #ca_fft = np.conj(np.fft.fft(code))
            
            self.sv_codes[sv] = np.conj(np.fft.fft(cacode.prn_code(sv, 0, 1023, sample_rate)))
            self.sv_bins[sv] = np.zeros((self.fsteps, self.samples_1ms))
            
    def set_threshold(db):
        self.threshold = db

    def run(self, buffer):
        for freq in range(self.fsteps):
            f = (freq - self.fsteps * 0.5) * self.fres
            self.ifs[freq] = buffer[0 : self.samples] * np.exp(2j * np.pi * f * self.time)

        for sv in range(1, 33):
            for freq in range(self.fsteps):
                self.sv_bins[sv][freq] = 0;
                
                for i in range(self.integrations):
                    block = self.ifs[freq][i * self.samples_1ms : (i + 1) * self.samples_1ms]
                    iq_fft = np.fft.fft(block)
                    result = np.abs(np.fft.ifft(iq_fft * self.sv_codes[sv])) ** 2               
                    self.sv_bins[sv][freq] += result

            peak = float(np.max(self.sv_bins[sv]))
            mean = float(np.mean(self.sv_bins[sv]))
            
            try:
                peak_to_mean = round(10 * np.log10(peak / mean), 2)
            except ZeroDivisionError:
                peak_to_mean = 100
                
            if peak_to_mean >= self.threshold:
                index = np.unravel_index(self.sv_bins[sv].argmax(), self.sv_bins[sv].shape)
                doppler = round((index[0] - (self.fsteps / 2)) / self.fsteps * self.fdev, 2)
                chip_phase = round(index[1] / self.sample_rate * 1.023 * 10**6, 2)
                
                print(f"DETECTION SV{sv}: {peak_to_mean} dB peak-to-mean, doppler {doppler} Hz, chip {chip_phase}")
                

"""
sample_frequency = 2.4 * 10 ** 6

sdr = RtlSdr()
sdr.sample_rate = sample_frequency
sdr.center_freq = 1575.42e6
sdr.gain = 50
sdr.set_bias_tee(True)

frequency_deviation = 20e3
frequency_resolution = 1000
frequency_steps = int(frequency_deviation / frequency_resolution)
# 1 ms, or one code sequence
integrations = 10
num_samples_1ms = round(1e-3 * sample_frequency)
num_samples = num_samples_1ms * integrations

t_sample = 1 / sample_frequency
freq = np.linspace(-frequency_deviation * 0.5, frequency_deviation * 0.5, frequency_steps)
shift = np.linspace(0, 1023, num_samples_1ms)
FREQ, SHIFT = np.meshgrid(freq, shift)
t = np.arange(num_samples) * t_sample

sv_codes = dict()
sv_bins = dict()
mixed_in = dict()

for sv in range(1 , 33):
    #code = cacode.prn_code(sv, 0, 1023, sample_frequency)
    #ca_fft = np.conj(np.fft.fft(code))
    
    sv_codes[sv] = np.conj(np.fft.fft(cacode.prn_code(sv, 0, 1023, sample_frequency)))
    sv_bins[sv] = np.zeros((frequency_steps, num_samples_1ms))

fig, ax = plt.subplots()
im = ax.imshow(sv_bins[24], aspect='auto', extent=[0, 1023, -5000, 5000])

plt.show(block=False)


while 1:
    start = time.perf_counter()
    samples = sdr.read_samples(num_samples)
    
    for freq in range(frequency_steps):
        f = (freq - frequency_steps * 0.5) * frequency_resolution
        mixed_in[freq] = samples[0 : num_samples] * np.exp(2j * np.pi * f * t)

    for sv in range(1, 33):
        for freq in range(frequency_steps):
            sv_bins[sv][freq] = 0;
            
            for i in range(integrations):
                block = mixed_in[freq][i * num_samples_1ms : (i + 1) * num_samples_1ms]
                iq_fft = np.fft.fft(block)
                result = np.abs(np.fft.ifft(iq_fft * sv_codes[sv])) ** 2               
                sv_bins[sv][freq] += result

        peak = float(np.max(sv_bins[sv]))
        mean = float(np.mean(sv_bins[sv]))
        peak_to_mean = round(10 * np.log10(peak / mean), 2)
    
        if peak_to_mean >= 8:
            print(f"DETECTION SV{sv}: {peak_to_mean} dB PTM") 
    
    #print(f"{round(time.perf_counter() - start, 2)}")

    #im.set_data(sv_bins[sv])
    #im.autoscale()
    #fig.canvas.draw_idle()
    #fig.canvas.flush_events()
"""

if __name__ == '__main__':
    sdr = RtlSdr()
    sdr.sample_rate = 2.048e6
    sdr.center_freq = 1575.42e6
    sdr.gain = 50
    sdr.set_bias_tee(True)
    
    saq = correlator(sample_rate = 2.048e6)

    while 1:
        samples = sdr.read_samples(24000)
        saq.run(samples)
    