import numpy as np
from .polar import PolarCode
from .egg_channel import EGGChannel
from .modulation import bits_to_bpsk, calculate_llr, bpsk_to_bits

class Simulation:
    def __init__(self, polar_params, channel_params, snr_range, num_frames=1000):
        self.N = polar_params['N']
        self.K = polar_params['K']
        self.polar_code = PolarCode(self.N, self.K, design_snr_db=polar_params.get('design_snr', 0.0))
        
        self.channel = EGGChannel(
            omega=channel_params['omega'],
            lambda_=channel_params['lambda_'],
            a=channel_params['a'],
            d=channel_params['d'],
            p=channel_params['p']
        )
        
        self.snr_range = snr_range
        self.num_frames = num_frames
        
        self.results = {
            'snr_db': [],
            'coded_ber': [],
            'uncoded_ber': [],
            'total_bits': [],
            'coded_errors': [],
            'uncoded_errors': []
        }
        
    def run_frame(self, snr_db):
        """
        Run a single Monte Carlo frame.
        """
        # 1. Generate random information bits
        info_bits = np.random.randint(0, 2, self.K)
        
        # 2. Polar encode
        encoded_bits = self.polar_code.encode(info_bits)
        
        # 3. BPSK modulate
        tx_symbols = bits_to_bpsk(encoded_bits)
        
        # Uncoded for comparison (transmit info bits directly)
        uncoded_tx_symbols = bits_to_bpsk(info_bits)
        
        # 4 & 5. Transmit through EGG channel
        rx_signal, irradiance, sigma2 = self.channel.transmit(tx_symbols, snr_db)
        uncoded_rx_signal, uncoded_irradiance, uncoded_sigma2 = self.channel.transmit(uncoded_tx_symbols, snr_db)
        
        # 6. Calculate LLR
        llr = calculate_llr(rx_signal, irradiance, sigma2)
        
        # 7. Polar decode
        decoded_bits = self.polar_code.decode_sc(llr)
        
        # Uncoded decoding (hard decision)
        uncoded_rx_bits = bpsk_to_bits(uncoded_rx_signal)
        
        # 8 & 9. Compare and accumulate errors
        coded_errors = np.sum(info_bits != decoded_bits)
        uncoded_errors = np.sum(info_bits != uncoded_rx_bits)
        
        return coded_errors, uncoded_errors, info_bits, encoded_bits, rx_signal, decoded_bits

    def run_simulation(self, progress_callback=None):
        """
        Run Monte Carlo simulation over SNR range.
        """
        for i, snr in enumerate(self.snr_range):
            total_coded_errors = 0
            total_uncoded_errors = 0
            total_bits = 0
            
            # For stopping criterion
            min_errors = 100
            
            for frame in range(self.num_frames):
                coded_err, uncoded_err, _, _, _, _ = self.run_frame(snr)
                
                total_coded_errors += coded_err
                total_uncoded_errors += uncoded_err
                total_bits += self.K
                
                # Optional progress callback
                if progress_callback:
                    progress_callback(i, len(self.snr_range), frame, self.num_frames, snr)
            coded_ber = total_coded_errors / total_bits
            uncoded_ber = total_uncoded_errors / total_bits
            
            self.results['snr_db'].append(snr)
            self.results['coded_ber'].append(coded_ber)
            self.results['uncoded_ber'].append(uncoded_ber)
            self.results['total_bits'].append(total_bits)
            self.results['coded_errors'].append(total_coded_errors)
            self.results['uncoded_errors'].append(total_uncoded_errors)
            
        return self.results
