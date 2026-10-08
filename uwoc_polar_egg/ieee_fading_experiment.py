import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from backend.polar import PolarCode
from backend.egg_channel import EGGChannel
from backend.modulation import bits_to_bpsk, calculate_llr

def run_ieee_turbulence_experiment():
    np.random.seed(42)
    N, K = 128, 64
    polar = PolarCode(N, K, design_snr_db=0.0)
    
    # EGG parameters for different turbulence conditions (Standard literature approximations)
    # The variance of irradiance dictates turbulence strength.
    turbulence_models = {
        'Weak':   {'omega': 0.1, 'lambda_': 1.0, 'a': 3.0, 'd': 5.0, 'p': 2.0},
        'Moderate':{'omega': 0.5, 'lambda_': 1.0, 'a': 1.0, 'd': 2.0, 'p': 1.0},
        'Strong': {'omega': 0.9, 'lambda_': 0.5, 'a': 0.5, 'd': 1.0, 'p': 0.5}
    }
    
    snr_list = np.arange(-2, 16, 2)
    num_frames = 2000
    
    all_results = []
    
    plt.figure(figsize=(10, 6))
    
    for label, params in turbulence_models.items():
        print(f"Simulating {label} Turbulence...")
        channel = EGGChannel(**params)
        
        ber_list = []
        for snr in snr_list:
            total_errors = 0
            
            for _ in range(num_frames):
                info_bits = np.random.randint(0, 2, K)
                encoded = polar.encode(info_bits)
                tx_symbols = bits_to_bpsk(encoded)
                rx_signal, irradiance, sigma2 = channel.transmit(tx_symbols, snr)
                llr = calculate_llr(rx_signal, irradiance, sigma2)
                decoded = polar.decode_sc(llr)
                total_errors += np.sum(info_bits != decoded)
                
            ber = total_errors / (num_frames * K)
            ber_list.append(ber)
            all_results.append({
                'Turbulence': label,
                'SNR (dB)': snr,
                'Coded BER': ber
            })
            
        plt.semilogy(snr_list, ber_list, 'o-', label=f'{label} Turbulence', linewidth=2)
        
    plt.xlabel('SNR (dB)')
    plt.ylabel('Bit Error Rate (BER)')
    plt.title('Polar Coded UWOC Performance under varying EGG Turbulence')
    plt.grid(True, which="both", ls="--")
    plt.legend()
    plt.savefig('ieee_fading_ber.png')
    
    df = pd.DataFrame(all_results)
    df.to_csv("ieee_fading_results.csv", index=False)
    print("Exported ieee_fading_results.csv and ieee_fading_ber.png")

if __name__ == "__main__":
    run_ieee_turbulence_experiment()
