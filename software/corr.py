import cmath
import math
import numpy as np
import matplotlib.pyplot as plt
import cacode
import time

class satellite:
    def __init__(self, prn, chip_delay, doppler):
        self.chip = chip_delay
        self.doppler = doppler
        self.prn = prn
        # When the acquisition took place. Used for timeouts
        self.when = time.time()
        
    def lifetime():
        return time.time() - self.when

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
            self.sv_codes[sv] = np.conj(np.fft.fft(cacode.prn_code(sv, 0, 1023, sample_rate)))
            self.sv_bins[sv] = np.zeros((self.fsteps, self.samples_1ms))
            
    def set_threshold(db):
        self.threshold = db

    def run(self, buffer):
        sats = []
    
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
                
                sats.append(satellite(sv, chip_phase, doppler))                
        
        return sats