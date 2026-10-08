# Mathematical Formulas for Polar Coded EGG UWOC Simulation

This document contains all the mathematical models and equations implemented in the simulation. These can be presented to verify the mathematical soundness of the channel, modulation, and coding schemes.

---

## 1. Polar Code Construction
Polar codes rely on channel polarization. The block length $N$ and the number of information bits $K$ define the code rate $R$.
- **Block Length:** $N = 2^n$
- **Code Rate:** $R = \frac{K}{N}$

### Generator Matrix
The polar generator matrix $G_N$ is derived from the Kronecker power of the basic kernel $F$:
$$ F = \begin{bmatrix} 1 & 0 \\ 1 & 1 \end{bmatrix} $$
$$ G_N = F^{\otimes n} $$

### Encoding
A message vector $u$ (length $N$) is constructed by placing the $K$ information bits in the most reliable positions (information set) and setting the rest to $0$ (frozen set). The transmitted codeword $x$ is:
$$ x = u \cdot G_N \pmod 2 $$

### Bhattacharyya Parameter Update (AWGN Approximation)
To find the reliable bit channels, we calculate the Bhattacharyya parameter $Z(W)$. For an initial AWGN channel:
$$ Z(W) \approx \exp(-\text{SNR}_{\text{linear}}) $$

For the polarized channels (upper $W'$ and lower $W''$ branches):
$$ Z(W') \le 2Z(W) - Z(W)^2 $$
$$ Z(W'') = Z(W)^2 $$
The channels with the $K$ smallest $Z$ values are chosen for the information bits.

---

## 2. BPSK Modulation
The encoded binary bits $x_i \in \{0, 1\}$ are mapped to BPSK symbols $s_i \in \{+1, -1\}$:
$$ s_i = 1 - 2x_i $$

---

## 3. Exponential-Generalized Gamma (EGG) Channel
The underwater fading and turbulence are modeled using the EGG distribution, which is a mixture of an Exponential distribution and a Generalized Gamma distribution.

The Probability Density Function (PDF) of the irradiance $I$ is:
$$ f_I(I) = \frac{\omega}{\lambda} \exp\left(-\frac{I}{\lambda}\right) + (1-\omega) \frac{p I^{d-1}}{a^d \Gamma(d/p)} \exp\left(-\left(\frac{I}{a}\right)^p\right) $$
Where:
- $\omega$ : Mixing weight ($0 < \omega < 1$)
- $\lambda$ : Scale parameter for the Exponential component
- $a, d, p$ : Parameters for the Generalized Gamma component
- $\Gamma(\cdot)$ : Gamma function

---

## 4. Transmission Model
The baseband received signal $y_i$ after passing through the EGG channel and AWGN is:
$$ y_i = \sqrt{I_i} s_i + n_i $$
Where:
- $I_i$ : EGG irradiance/fading sample for the $i$-th symbol
- $s_i$ : Transmitted BPSK symbol
- $n_i$ : Additive White Gaussian Noise, $n_i \sim \mathcal{N}(0, \sigma^2)$

The noise variance $\sigma^2$ is determined by the Signal-to-Noise Ratio (SNR):
$$ \sigma^2 = \frac{1}{2 \cdot 10^{(\text{SNR}_{\text{dB}} / 10)}} $$

---

## 5. Log-Likelihood Ratio (LLR)
At the receiver, the soft information is computed as the Log-Likelihood Ratio. Given the channel state information $h_i = \sqrt{I_i}$:
$$ \text{LLR}_i = \ln \frac{P(x_i = 0 | y_i)}{P(x_i = 1 | y_i)} = \frac{2 \sqrt{I_i} y_i}{\sigma^2} $$

---

## 6. Successive Cancellation (SC) Decoder
The SC decoder traverses the polar code tree, estimating bits $\hat{u}_i$ sequentially using the soft LLR values.

For the upper branch (f-node):
$$ f(L_1, L_2) = 2 \text{arctanh}\left(\tanh\left(\frac{L_1}{2}\right) \tanh\left(\frac{L_2}{2}\right)\right) $$
*Implementation uses the hardware-friendly Min-Sum approximation for numerical stability:*
$$ f(L_1, L_2) \approx \text{sign}(L_1) \text{sign}(L_2) \min(|L_1|, |L_2|) $$

For the lower branch (g-node) given the previously decided bit $\hat{u}$:
$$ g(L_1, L_2, \hat{u}) = L_2 + (1 - 2\hat{u})L_1 $$

Decision at the leaf node for index $i$:
$$ 
\hat{u}_i = 
\begin{cases} 
0 & \text{if } i \text{ is a frozen bit} \\
0 & \text{if } \text{LLR}_i \ge 0 \text{ and } i \text{ is an info bit} \\
1 & \text{if } \text{LLR}_i < 0 \text{ and } i \text{ is an info bit}
\end{cases}
$$

---

## 7. Performance Metrics (BER)
The decoded information bits are compared to the originally transmitted bits to calculate the Bit Error Rate (BER):
$$ \text{BER} = \frac{N_{\text{errors}}}{K} = \frac{\sum_{i=1}^K (\hat{u}_i \oplus u_i)}{K} $$
