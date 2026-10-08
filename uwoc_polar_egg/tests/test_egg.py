import numpy as np
from backend.egg_channel import EGGChannel

def test_egg_channel_samples():
    channel = EGGChannel(omega=0.5, lambda_=1.0, a=1.0, d=2.0, p=1.0)
    samples = channel.generate_samples(1000)
    
    assert len(samples) == 1000
    assert np.all(samples >= 0), "Irradiance samples must be non-negative"

def test_egg_transmission():
    channel = EGGChannel()
    bpsk = np.array([1, -1, 1, -1])
    rx, I, sigma2 = channel.transmit(bpsk, snr_db=10)
    
    assert len(rx) == 4
    assert len(I) == 4
    assert sigma2 > 0
