import numpy as np
from backend.polar import PolarCode

def test_polar_noiseless():
    N = 128
    K = 64
    pc = PolarCode(N, K)
    
    info_bits = np.random.randint(0, 2, K)
    encoded = pc.encode(info_bits)
    
    # Simulate noiseless BPSK
    tx = 1 - 2 * encoded
    llr = 20 * tx # High LLR implies high certainty
    
    decoded = pc.decode_sc(llr)
    
    assert np.array_equal(info_bits, decoded), "Noiseless decoding failed"

def test_polar_all_zeros():
    N = 64
    K = 32
    pc = PolarCode(N, K)
    info_bits = np.zeros(K, dtype=int)
    encoded = pc.encode(info_bits)
    assert np.all(encoded == 0), "All zero info bits should yield all zero codeword"
