import numpy as np
from scipy.stats import gengamma, expon

class EGGChannel:
    def __init__(self, omega=0.5, lambda_=1.0, a=1.0, d=2.0, p=1.0):
        """
        Initialize Exponential-Generalized Gamma (EGG) Channel Model.
        f_I(I) = omega * Exponential(lambda) + (1-omega) * GeneralizedGamma(a, d, p)
        
        Parameters:
        omega: Mixing weight (0 < omega < 1)
        lambda_: Parameter for Exponential distribution (scale)
        a: Scale parameter for Generalized Gamma
        d: Parameter for Generalized Gamma (relates to shape)
        p: Parameter for Generalized Gamma (relates to shape)
        """
        self.omega = omega
        self.lambda_ = lambda_
        self.a = a
        self.d = d
        self.p = p

    def generate_samples(self, size):
        """
        Generate random irradiance samples from EGG mixture.
        """
        # Generate uniform random variables to select between Exponential and GenGamma
        u = np.random.rand(size)
        
        samples = np.zeros(size)
        
        # Indices for Exponential and Generalized Gamma components
        idx_exp = u < self.omega
        idx_gg = ~idx_exp
        
        # Sample from Exponential
        if np.any(idx_exp):
            samples[idx_exp] = expon.rvs(scale=self.lambda_, size=np.sum(idx_exp))
            
        # Sample from Generalized Gamma
        # scipy.stats.gengamma parameters: a=d/p, c=p, scale=a
        if np.any(idx_gg):
            a_scipy = self.d / self.p
            c_scipy = self.p
            scale_scipy = self.a
            samples[idx_gg] = gengamma.rvs(a=a_scipy, c=c_scipy, scale=scale_scipy, size=np.sum(idx_gg))
            
        return samples

    def transmit(self, bpsk_symbols, snr_db):
        """
        Transmit BPSK symbols through EGG channel with AWGN.
        y_i = sqrt(I_i) * s_i + n_i
        
        bpsk_symbols: Transmitted symbols (+1, -1)
        snr_db: Signal-to-Noise Ratio in dB
        
        Returns:
        received_signal: y_i
        irradiance_samples: I_i (needed for LLR calculation at receiver)
        sigma2: Noise variance
        """
        size = len(bpsk_symbols)
        irradiance_samples = self.generate_samples(size)
        
        # Calculate noise variance based on SNR
        # E[s^2] = 1, so signal power is 1 (before channel).
        # Normalizing noise to the transmitted signal energy.
        snr_linear = 10 ** (snr_db / 10.0)
        sigma2 = 1.0 / (2.0 * snr_linear)
        sigma = np.sqrt(sigma2)
        
        # Generate AWGN
        noise = np.random.normal(0, sigma, size)
        
        # Baseband model
        h_i = np.sqrt(irradiance_samples)
        received_signal = h_i * bpsk_symbols + noise
        
        return received_signal, irradiance_samples, sigma2
