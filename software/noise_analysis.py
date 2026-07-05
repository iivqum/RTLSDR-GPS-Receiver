import cmath
import math
import numpy as np
import matplotlib.pyplot as plt
import cacode

samples = []

try:
    with open("noise_1.57G_2.4GBW.txt", "r") as f:

        while True:
            real = f.readline()
            imag = f.readline()
        
            if len(real) == 0 or len(imag) == 0:
                break
                
            real = float(real)
            imag = float(imag)
            
            theta = np.tan(imag / real)
            amp = np.sqrt(real ** 2 + imag ** 2)
            
            samples.append(np.cos(theta) * amp)
except FileNotFoundError:
    print("Could not open IQ data file, not found")
except IOError:
    print("Could not open IQ data file, IO error")

"""
Provides an estimation for the noise in the receiver.
Looking at the histogram, it's not exactly gaussian but
close enough.
"""

mean = np.mean(samples) / np.sqrt(2) 
sigma = np.std(samples) / np.sqrt(2)

print(f"Noise mean = {mean} ({20 * np.log10(mean)} dBfs)")  
print(f"Noise STD = {sigma} ({20 * np.log10(sigma)} dBfs)")  
    
plt.hist(samples)

plt.show()