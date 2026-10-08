import numpy as np
import pandas as pd
from backend.polar import PolarCode
from backend.egg_channel import EGGChannel
from backend.modulation import bits_to_bpsk, calculate_llr

def get_ml_metrics():
    # Setup
    N = 128
    K = 64
    polar = PolarCode(N, K, design_snr_db=0.0)
    channel = EGGChannel(omega=0.5, lambda_=1.0, a=1.0, d=2.0, p=1.0)
    
    snr_list = [0, 4, 8, 12, 16]
    num_frames = 100
    
    results = []
    
    print("Calculating ML metrics...")
    
    for snr in snr_list:
        all_true = []
        all_pred = []
        all_scores = [] # For ROC-AUC, we need a continuous score. We can use the LLRs of the info bits, but SC decoder output is hard bits. 
        # Actually, if we just want ROC-AUC, we can use the hard bits or we can extract the soft LLRs at the leaves if we modified the decoder.
        # Since SC decoder gives hard bits, we'll just report ROC-AUC based on the hard predictions, which is equivalent to (TPR - FPR + 1)/2
        
        for _ in range(num_frames):
            clean_source = np.random.randint(0, 2, K)
            encoded_bits = polar.encode(clean_source)
            tx_symbols = bits_to_bpsk(encoded_bits)
            rx_signal, irradiance, sigma2 = channel.transmit(tx_symbols, snr)
            llr = calculate_llr(rx_signal, irradiance, sigma2)
            decoded_bits = polar.decode_sc(llr)
            
            all_true.extend(clean_source)
            all_pred.extend(decoded_bits)
            
        # Calculate metrics manually
        all_true = np.array(all_true)
        all_pred = np.array(all_pred)
        
        TP = np.sum((all_true == 1) & (all_pred == 1))
        TN = np.sum((all_true == 0) & (all_pred == 0))
        FP = np.sum((all_true == 0) & (all_pred == 1))
        FN = np.sum((all_true == 1) & (all_pred == 0))
        
        acc = (TP + TN) / len(all_true)
        prec = TP / (TP + FP) if (TP + FP) > 0 else 0
        rec = TP / (TP + FN) if (TP + FN) > 0 else 0
        f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0
        
        # Specificity (True Negative Rate)
        specificity = TN / (TN + FP) if (TN + FP) > 0 else 0
        
        # ROC-AUC for hard binary predictions is (TPR + TNR)/2
        roc = (rec + specificity) / 2
        
        results.append({
            'SNR (dB)': snr,
            'Accuracy': acc,
            'Precision': prec,
            'Recall': rec,
            'F1-score': f1,
            'ROC-AUC': roc
        })
        
    df = pd.DataFrame(results)
    print(df.to_string(index=False))
    df.to_csv("ml_metrics_results.csv", index=False)

if __name__ == "__main__":
    get_ml_metrics()
