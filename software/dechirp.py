import cacode
import matplotlib.pyplot as plt
import numpy as np

code = cacode.create_baseband_signal(
    prn = 17,
    shift = 0,
    length = 1023 * 200,
    sample_rate = 2.048e6,
    phase = 0,
    amplitude = 1,
    doppler = 1000,
    noise_mean = 0,
    noise_std = 0.1
)

code2 = cacode.create_baseband_signal(
    prn = 17,
    shift = 0,
    length = 1023 * 200,
    sample_rate = 2.048e6,
    phase = 0,
    amplitude = 1,
    doppler = 0,
    noise_mean = 0,
    noise_std = 0
)

# Create some random 'data'
# 10 symbols, 200 ms
data = np.ones(10) * -1
data[: 5] = np.ones(5)

np.random.shuffle(data)

sampled_data = cacode.sampled_signal(data, 2.048e6, 50)

code_with_data = code * sampled_data

code_stripped = code_with_data * code2
code_fft = np.fft.fft(code_stripped)

#plt.plot(20 * np.log10(np.abs(code_fft[: code_fft.size // 2])))
#print(np.mean(np.angle(code_cor, deg = True)))
#plt.plot(20 * np.log10(np.abs(code_fft)))
#plt.scatter(np.real(code_stripped), np.imag(code_stripped))
plt.show()