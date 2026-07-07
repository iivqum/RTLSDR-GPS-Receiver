import cmath
import math
import numpy as np
import matplotlib.pyplot as plt
import cacode


baseband = []

try:
    with open("data.txt", "r") as f:

        while True:
            real = f.readline()
            imag = f.readline()
        
            if len(real) == 0 or len(imag) == 0:
                break
            
            baseband.append(complex(float(real), float(imag)))
except FileNotFoundError:
    print("Could not open IQ data file, not found")
except IOError:
    print("Could not open IQ data file, IO error")

baseband = baseband - np.mean(baseband)

#baseband = np.fromfile("GPS_L1_recording_10ms_4MHz_cf32.iq", dtype = np.complex64)

"""
# Synthesize a signal to test aquisition

baseband = cacode.create_baseband_signal(
    prn = 17,
    shift = 512,
    length = 1023 * 10,
    sample_rate = sample_frequency,
    phase = 0,
    # RMS
    amplitude = cacode.dbfs_to_amplitude(-56),
    doppler = 500,
    # RMS noise measured in noise_analysis.py
    # -38 dBfs mean
    noise_mean = 0,
    noise_std = cacode.dbfs_to_amplitude(-34),
)
"""
"""
fig, axs = plt.subplots(2)
axs[0].scatter(baseband.real, baseband.imag)
axs[0].axis("equal")
axs[0].set_title("Constellation")
axs[1].plot(baseband.real)
axs[1].set_title("PRN Code")
plt.show()
"""

sample_frequency = 2.4 * 10 ** 6
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

print(len(baseband))

for sv in range(1, 33):
    code = cacode.prn_code(sv, 0, 1023, sample_frequency)
    ca_fft = np.conj(np.fft.fft(code))
    z = np.zeros((frequency_steps, num_samples_1ms))
    
    for freq in range(frequency_steps):
        f = (freq - frequency_steps * 0.5) * frequency_resolution
        iq_shifted = baseband[0 : num_samples] * np.exp(2j * np.pi * f * t)
        
        for i in range(integrations):
            block = iq_shifted[i * num_samples_1ms : (i + 1) * num_samples_1ms]
            iq_fft = np.fft.fft(block)
            result = np.abs(np.fft.ifft(iq_fft * ca_fft)) ** 2
            
            z[freq] += result

    peak = float(np.max(z))
    mean = float(np.mean(z))

    print(f"SV {sv}: Max XCOR is {peak}, {10 * np.log10(peak / mean)} peak to mean level")


idx = np.unravel_index(np.argmax(z), z.shape)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.plot_surface(FREQ, SHIFT, np.transpose(z), cmap = 'viridis', linewidth = 8, antialiased = True)
ax.set_xlabel('Doppler')
ax.set_ylabel('Code Shift')
ax.set_zlabel('Correlation')

plt.show()