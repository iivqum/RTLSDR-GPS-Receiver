"""
   Author: Josh McGuigan
   Description: 
        This file contains a function that generates a full CA code sequence
        for any of the 32 legacy GPS satellites.
"""
import math
import numpy as np
import matplotlib.pyplot as plt

taps = (
    None,
    (2, 6), (3, 7), (4, 8), (5, 9), 
    (1, 9), (2, 10), (1, 8), (2, 9), 
    (3, 10), (2, 3), (3, 4), (5, 6), 
    (6, 7), (7, 8), (8, 9), (9, 10), 
    (1, 4), (2, 5), (3, 6), (4, 7), 
    (5, 8), (6, 9), (1, 3), (4, 6), 
    (5, 7), (6, 8), (7, 9), (8, 10), 
    (1, 6), (2, 7), (3, 8), (4, 9))
    
def dbfs_to_amplitude(db : float):
    """
    RMS dBfs to amplitude
    """
    return 10 ** (db / 20) * math.sqrt(2)
    
def bit(x: int, n: int) -> int:
    """
    Get n'th bit, zero starting
    x: input
    n: n'th bit
    """
    return (x >> n) & 1

def gold_sequence(prn: int) -> list[int]:
    """
    Generates 1023 chip satellite CA sequence
    prn: Satellite PRN number
    """
    g1 = 0x3FF
    g2 = 0x3FF
    
    p0 = taps[prn][0] - 1
    p1 = taps[prn][1] - 1
    
    chips = np.empty(1023)
    
    for i in range(1023):
        g1_out = bit(g1, 9)
        g1_in = bit(g1, 9) ^ bit(g1, 2)
        
        g2_out = bit(g2, p0) ^ bit(g2, p1)
        g2_in = bit(g2, 1) ^ bit(g2, 2) ^ bit(g2, 5) ^ bit(g2, 7) ^ bit(g2, 8) ^ bit(g2, 9)
        
        out = g1_out ^ g2_out
    
        chips[i] = (2 * (out) - 1)
        
        g1 = ((g1 << 1) + g1_in) & 0x3FF
        g2 = ((g2 << 1) + g2_in) & 0x3FF
    
    return chips
    
satellite_cache = [gold_sequence(x) for x in range(1, 33)]
    
def prn_code(prn: int, shift : float, length : int, sample_rate : float) -> list[int]:
    """
    Generates a desired satellite code with shifting, length and sample rate options.
    prn: Satellite PRN number
    shift: Code shift amount in chips
    length: Length in chips
    sample_rate: Sampling rate in hertz
    """
    
    if sample_rate < 2.046 * 10**6:
        print("Sample rate too low. Needs to be at least 2.046 MHz")
        return []

    sequence = satellite_cache[prn - 1]
    # Time of a single chip
    sequence_position = shift % 1023
    # Current length of code in chips
    code_length = 0
    t_sample = 1 / sample_rate
    t_symbol = 1 / (1.023 * 10 ** 6)
    samples = round(length * t_symbol / t_sample)
    code = np.empty(samples)
    
    for i in range(samples):
        code[i] = sequence[int(sequence_position)]
        sequence_position += t_sample / t_symbol
        
        if sequence_position >= 1023:
            sequence_position = sequence_position - 1023

    return code
  
def create_baseband_signal(prn : int, shift : float, length : int, sample_rate : float, 
    phase : float, amplitude : float, doppler : float, noise_mean : float, noise_std : float) -> list[int]:
    """
    Create a complex baseband L1 signal with phase shift, doppler, amplitude and phase shift.
    Does not include navigation bits.
    """
    # -1 and 1 PRN signal
    code = prn_code(prn, shift, length, sample_rate) * amplitude
    t = np.arange(len(code)) / sample_rate
    # Doppler shift
    code = code * np.exp(2j * np.pi * doppler * t)
    # The carrier phase which is kept after downconversion
    code = code * np.exp(1j * np.deg2rad(phase))
    """
    Adding non-zero mean noise to the signal can be problematic and will
    likely result in ridges in the doppler/shift plot.
    
    This is because DC energy is shifted up (or down) the spectrum and will correlate
    with the periodicity of the code sequence (1 KHz). Therefore you will get ridges/fringes
    at multiples of 1 KHz.
    """
    noise_i = np.random.normal(noise_mean, noise_std, len(code))
    noise_q = np.random.normal(noise_mean, noise_std, len(code))
    
    return code + (noise_i + 1j * noise_q)