import asyncio
from rtlsdr import RtlSdr

async def sample(sdr, buf, block_size):
    async for samples in sdr.stream(block_size, format = "bytes"):
        buf.get_lock()
        try:
            buf.write_block(samples)
        finally:
            buf.release_lock()

def main(buf, sample_frequency, center_frequency, gain, bias_tee, block_size):
    sdr = RtlSdr()
    sdr.sample_rate = sample_frequency
    sdr.center_freq = center_frequency
    sdr.gain = gain
    sdr.set_bias_tee(bias_tee)
    
    asyncio.run(sample(sdr, buf, block_size))
    
    sdr.close()