# Recommended IEEE Paper Structure & Results Mapping

**Title Idea:** *Performance Analysis of Polar-Coded Underwater Wireless Optical Communication over EGG Fading Channels*

To publish this project as an IEEE conference or journal paper, you must structure it professionally and include specific sets of results. I have generated all the necessary data for you in this folder.

---

## 1. Abstract & Introduction
*   **What to write:** Introduce UWOC, explain the fading problem caused by water turbulence, and propose Polar Coding as a mathematically proven capacity-achieving forward error correction (FEC) technique.
*   **Novelty:** Mention testing the state-of-the-art EGG (Exponential-Generalized Gamma) channel model with Soft-Decision Successive Cancellation decoding.

## 2. System Model (The Mathematics)
*   **Files to use:** Copy the equations directly from `Mathematical_Formulas.md`.
*   **What to include:**
    *   The EGG Probability Density Function (PDF) mixture equation.
    *   The BPSK Transmission equation ($y = \sqrt{I}s + n$).
    *   The exact Log-Likelihood Ratio (LLR) mapping equation.
    *   The Polar Code Generator Matrix ($G_N = F^{\otimes n}$) and Bhattacharyya bound polarization.

## 3. Results Section A: Standard BER Performance
*   **What to write:** Prove that Polar Coding vastly outperforms Uncoded transmission.
*   **Files to use:** `final_validation_results.csv`
*   **Graph to plot:** Plot *Uncoded BER* vs *Coded BER*. Show how the Polar code achieves a steep "waterfall" curve dropping to 0 errors around 8-10 dB, while uncoded BPSK struggles.

## 4. Results Section B: Impact of Turbulence Severity (Crucial for IEEE)
*   **What to write:** UWOC channels vary depending on water clarity and bubbles (weak, moderate, and strong fading). You must show how the Polar code performs across different EGG channel parameters.
*   **Files to use:** `ieee_fading_results.csv` and `ieee_fading_ber.png` (I am generating these for you right now).
*   **Graph to plot:** A single BER vs SNR graph with 3 curves: Weak Turbulence, Moderate Turbulence, and Strong Turbulence.

## 5. Results Section C: Source Corruption Bounds (Irreducible Error Floors)
*   **What to write:** Analyze what happens when the source information is degraded before transmission, demonstrating the strict theoretical bounds of channel coding capacity.
*   **Files to use:** `source_noise_results.csv` and `ber_vs_snr_source_noise.png`.
*   **Graph to plot:** Show how source noise $p$ creates an irreducible error floor exactly at $(1-p)$ accuracy.

## 6. Results Section D: Receiver Classification Performance
*   **What to write:** Frame the decoder's success in terms of receiver classification bounds to appeal to signal processing reviewers.
*   **Files to use:** `ml_metrics_results.csv`, `confusion_matrices.png`, and `roc_curve.png`.
*   **Graph to plot:** Place the ROC-AUC curve in the paper to prove the receiver efficiently utilizes the soft LLR information to approach a perfect True Positive Rate of $1.0$.

## 7. Conclusion
*   Summarize the maximum SNR coding gain achieved by Polar codes over uncoded systems in severe underwater turbulence.
