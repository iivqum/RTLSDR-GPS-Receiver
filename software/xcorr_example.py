"""
   Author: Josh McGuigan
   Description: 
        The code here demonstrates the autocorrelation properties of the satellite C/A code.
        This code is multiplied with the data to encode the NAV message, and used
        to pick out the desired signal from all other signals transmitting on the
        CDMA channel.
        
        The C/A code is 1023 bits (chips) long sequenced at 1.023 MHz, therefore 
        the code takes 1023 / (1.023 * 10^6) seconds, or 1 ms. The NAV message data
        transitions every 20 ms, so the C/A code repeats 20 times between any NAV data bit.
"""

import numpy as np
import matplotlib.pyplot as plt

import cacode

sv17 = cacode.ca_sequence(17)

cor = np.correlate(sv17, sv17, mode = "full")
lag = list(range(-cor.size // 2, cor.size // 2))

plt.title("Autocorrelation properties of SV17 coarse aquistion code")
plt.xlabel("Code delay")
plt.ylabel("Correlation")
plt.plot(lag, cor)
plt.show()