import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, roc_curve, auc
from backend.polar import PolarCode
from backend.egg_channel import EGGChannel
from backend.modulation import bits_to_bpsk, calculate_llr

def generate_ml_graphs():
    np.random.seed(42)
    N = 128
    K = 64
    polar = PolarCode(N, K, design_snr_db=0.0)
    channel = EGGChannel(omega=0.5, lambda_=1.0, a=1.0, d=2.0, p=1.0)
    
    # We will test two SNRs: 0 dB (Noisy) and 8 dB (Good)
    snrs_to_test = [0, 8]
    num_frames = 100
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: Confusion Matrices
    for i, snr in enumerate(snrs_to_test):
        all_true = []
        all_pred = []
        
        # We also want to gather continuous LLRs for ROC
        all_uncoded_true = []
        all_uncoded_llrs = []
        
        for _ in range(num_frames):
            clean_source = np.random.randint(0, 2, K)
            encoded_bits = polar.encode(clean_source)
            tx_symbols = bits_to_bpsk(encoded_bits)
            rx_signal, irradiance, sigma2 = channel.transmit(tx_symbols, snr)
            llr = calculate_llr(rx_signal, irradiance, sigma2)
            decoded_bits = polar.decode_sc(llr)
            
            all_true.extend(clean_source)
            all_pred.extend(decoded_bits)
            
            all_uncoded_true.extend(encoded_bits)
            # The channel LLR represents the log-likelihood ratio for bit=0 vs bit=1
            # A positive LLR means bit 0 is more likely. A negative means bit 1.
            # For sklearn roc_curve, higher score = positive class (which we'll define as bit 0)
            all_uncoded_llrs.extend(llr)
            
        # Confusion Matrix
        cm = confusion_matrix(all_true, all_pred, labels=[0, 1])
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Bit 0', 'Bit 1'])
        disp.plot(ax=axes[i], cmap='Blues')
        axes[i].set_title(f'Polar Decoder Confusion Matrix\nSNR = {snr} dB')
        
    plt.tight_layout()
    plt.savefig('confusion_matrices.png')
    print("Saved confusion_matrices.png")
    plt.clf()
    
    # Plot 2: ROC Curve (Uncoded Soft Information)
    plt.figure(figsize=(8, 8))
    for snr in [0, 4, 8]:
        all_uncoded_true = []
        all_uncoded_llrs = []
        for _ in range(num_frames):
            clean_source = np.random.randint(0, 2, K)
            encoded_bits = polar.encode(clean_source)
            tx_symbols = bits_to_bpsk(encoded_bits)
            rx_signal, irradiance, sigma2 = channel.transmit(tx_symbols, snr)
            llr = calculate_llr(rx_signal, irradiance, sigma2)
            
            # Map true bits: we treat '0' as the positive class (1) and '1' as negative class (0)
            # because LLR is positive when bit is 0.
            mapped_true = [1 if b == 0 else 0 for b in encoded_bits]
            
            all_uncoded_true.extend(mapped_true)
            all_uncoded_llrs.extend(llr)
            
        fpr, tpr, _ = roc_curve(all_uncoded_true, all_uncoded_llrs)
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=2, label=f'SNR = {snr} dB (AUC = {roc_auc:.3f})')
        
    plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate (FPR)')
    plt.ylabel('True Positive Rate (TPR)')
    plt.title('Receiver Operating Characteristic (ROC) Curve\nSoft Information from EGG Channel')
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.savefig('roc_curve.png')
    print("Saved roc_curve.png")

if __name__ == "__main__":
    generate_ml_graphs()
