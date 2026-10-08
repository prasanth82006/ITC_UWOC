# Performance Analysis of Polar Coding over an Exponential-Generalized Gamma (EGG) Underwater Wireless Optical Communication Channel

## 1. Problem Statement
Underwater Wireless Optical Communication (UWOC) systems suffer from fading and turbulence, significantly degrading bit error rate (BER). Robust channel coding is required to mitigate these effects.

## 2. Objective
This simulation models an end-to-end UWOC system using Polar Channel Coding. The channel fading is modeled using the Exponential-Generalized Gamma (EGG) distribution, and AWGN is added.

## 3. Communication System
The system implements the following chain:
Information Bits -> Polar Encoder -> BPSK -> EGG Channel + AWGN -> LLR -> Polar SC Decoder -> BER.

## 4. Mathematical Details

### Polar Coding
N = 2^n, K = information length.
Code rate R = K/N.
Encoded as x = u * G_N.
Decoded using Successive Cancellation (SC) on LLRs.

### EGG Channel
The EGG probability density function is a mixture model:
f_I(I) = ω/λ * exp(-I/λ) + (1-ω) * [p * I^(d-1) / (a^d * Γ(d/p))] * exp(-(I/a)^p)

## 5. Installation
```bash
pip install -r requirements.txt
```

## 6. How to Run
```bash
streamlit run app.py
```

## 7. Limitations & Future Work
- Currently implements SC decoding. Future work can integrate CRC-aided SCL decoding for improved performance.
- EGG parameters should be sourced from experimental UWOC data to model specific underwater environments (e.g., clear ocean vs. coastal water).
