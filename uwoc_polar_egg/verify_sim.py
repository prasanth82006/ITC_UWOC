import numpy as np
from backend.simulation import Simulation

def test_run():
    print("Testing Simulation...")
    polar_params = {'N': 64, 'K': 32, 'design_snr': 5.0}
    channel_params = {'omega': 0.5, 'lambda_': 1.0, 'a': 1.0, 'd': 2.0, 'p': 1.0}
    snr_range = np.arange(0, 10, 2)
    
    sim = Simulation(polar_params, channel_params, snr_range, num_frames=10)
    
    results = sim.run_simulation()
    
    print("Simulation completed successfully!")
    print(f"Tested SNRs: {results['snr_db']}")
    print(f"Coded BERs: {results['coded_ber']}")
    print(f"Uncoded BERs: {results['uncoded_ber']}")

if __name__ == "__main__":
    test_run()
