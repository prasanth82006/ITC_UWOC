import numpy as np

def bits_to_bpsk(bits):
    """
    Map bits {0, 1} to BPSK symbols {+1, -1}.
    0 -> +1
    1 -> -1
    Mathematical equation: s_i = 1 - 2*x_i
    """
    return 1 - 2 * bits

def calculate_llr(received_signal, irradiance_samples, sigma2):
    """
    Calculate LLR (Log-Likelihood Ratio) for BPSK in EGG channel.
    LLR_i = 2 * h_i * y_i / sigma2
    where h_i = sqrt(I_i)
    """
    h_i = np.sqrt(irradiance_samples)
    llr = 2 * h_i * received_signal / sigma2
    # Clip LLRs to prevent numerical overflow in subsequent operations
    llr = np.clip(llr, -50, 50) 
    return llr

def bpsk_to_bits(bpsk_symbols):
    """
    Hard decision mapping from BPSK symbols back to bits {0, 1}.
    For uncoded transmission comparison.
    +1 -> 0
    -1 -> 1
    """
    return (1 - np.sign(bpsk_symbols)) // 2
