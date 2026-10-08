import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from backend.simulation import Simulation

st.set_page_config(page_title="Polar Coded EGG UWOC Simulation", layout="wide")

st.title("Performance Analysis of Polar Coding over an EGG Underwater Wireless Optical Communication Channel")

# Sidebar for parameters
st.sidebar.header("1. Polar Code Parameters")
N = st.sidebar.selectbox("Block Length (N)", [32, 64, 128, 256, 512, 1024], index=2)
K = st.sidebar.number_input("Information Bits (K)", min_value=1, max_value=N-1, value=N//2)
design_snr = st.sidebar.slider("Design SNR (dB) for Polar Code", -5.0, 15.0, 0.0)

st.sidebar.header("2. EGG Channel Parameters")
st.sidebar.markdown("*Ideally selected from an experimental UWOC scenario.*")
omega = st.sidebar.slider("Mixing Weight (omega)", 0.01, 0.99, 0.5)
lambda_ = st.sidebar.number_input("Exponential Scale (lambda)", value=1.0)
a_param = st.sidebar.number_input("Gen. Gamma Scale (a)", value=1.0)
d_param = st.sidebar.number_input("Gen. Gamma Shape (d)", value=2.0)
p_param = st.sidebar.number_input("Gen. Gamma Shape (p)", value=1.0)

st.sidebar.header("3. Simulation Parameters")
snr_min = st.sidebar.number_input("Min SNR (dB)", value=0.0)
snr_max = st.sidebar.number_input("Max SNR (dB)", value=20.0)
snr_step = st.sidebar.number_input("SNR Step (dB)", value=2.0)
num_frames = st.sidebar.number_input("Monte Carlo Frames per SNR", value=1000)

snr_range = np.arange(snr_min, snr_max + snr_step, snr_step)

# System Architecture
st.header("Communication Block Diagram")
st.markdown("""
```mermaid
graph TD
    A[Random Information Bits] --> B[Polar Encoder]
    B --> C[BPSK Modulator]
    C --> D[EGG UWOC Channel]
    D -->|EGG fading + AWGN| E[BPSK Soft Demodulator]
    E --> F[LLR Calculation]
    F --> G[Polar SC Decoder]
    G --> H[Recovered Information Bits]
    H --> I[BER Calculation]
```
""")

run_button = st.button("Run Simulation")

progress_bar = st.progress(0)
status_text = st.empty()

if run_button:
    polar_params = {'N': N, 'K': K, 'design_snr': design_snr}
    channel_params = {'omega': omega, 'lambda_': lambda_, 'a': a_param, 'd': d_param, 'p': p_param}
    
    sim = Simulation(polar_params, channel_params, snr_range, num_frames=num_frames)
    
    def update_progress(snr_idx, total_snrs, frame, total_frames, current_snr):
        overall_progress = (snr_idx + frame / total_frames) / total_snrs
        progress_bar.progress(overall_progress)
        status_text.text(f"Running SNR: {current_snr} dB | Frame: {frame}/{total_frames}")

    start_time = time.time()
    results = sim.run_simulation(progress_callback=update_progress)
    end_time = time.time()
    
    progress_bar.progress(1.0)
    status_text.text(f"Simulation completed in {end_time - start_time:.2f} seconds.")
    
    # Extract example frame for visualization
    coded_err, uncoded_err, info_bits, encoded_bits, rx_signal, decoded_bits = sim.run_frame(snr_range[-1])
    
    st.header("BER vs SNR Graph")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.semilogy(results['snr_db'], results['coded_ber'], 'o-', label=f'Polar ({N},{K}) + BPSK', linewidth=2)
    ax.semilogy(results['snr_db'], results['uncoded_ber'], 's--', label='Uncoded BPSK', linewidth=2)
    ax.set_xlabel('SNR (dB)')
    ax.set_ylabel('Bit Error Rate (BER)')
    ax.set_title('BER Performance over EGG UWOC Channel')
    ax.grid(True, which="both", ls="--")
    ax.legend()
    st.pyplot(fig)
    
    st.header("Results Table")
    df = pd.DataFrame(results)
    st.dataframe(df)
    
    csv = df.to_csv(index=False)
    st.download_button("Download Results (CSV)", csv, "ber_results.csv", "text/csv")
    
    st.header("Original vs Recovered Bits (Example Frame at Highest SNR)")
    st.markdown(f"**Original Information:** {list(info_bits[:32])}...")
    st.markdown(f"**Decoded Information:**  {list(decoded_bits[:32])}...")
    st.markdown(f"**Bit Errors in this frame:** {coded_err} out of {K} bits")
    st.markdown(f"**Frame Bit Error Rate (BER):** {coded_err / K:.6f}")
