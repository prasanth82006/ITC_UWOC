
import numpy as np
import math

class PolarCode:
    def __init__(self, N, K, design_snr_db=0.0):
        self.N = N
        self.K = K
        self.n = int(np.log2(N))
        self.design_snr_db = design_snr_db
        
        # Determine information and frozen sets
        self.info_bits_indices, self.frozen_bits_indices = self._construct_polar_code(design_snr_db)
        
    def _construct_polar_code(self, design_snr_db):
        """
        Constructs the Polar code using Bhattacharyya bounds for an AWGN channel.
        """
        design_snr_linear = 10 ** (design_snr_db / 10.0)
        # Initial Bhattacharyya parameter for AWGN
        z = np.zeros(self.N)
        z[0] = np.exp(-design_snr_linear)
        
        # Calculate Z values for polarized channels
        for step in range(self.n):
            stride = 1 << step
            for j in range(0, 1 << (step + 1)):
                if j < stride:
                    # Upper branch (worse channel): 2Z - Z^2 (bounded to 1.0 for numerical stability)
                    val = 2 * z[j] - z[j]**2
                    z[j] = min(val, 1.0)
                else:
                    # Lower branch (better channel): Z^2
                    z[j] = z[j - stride]**2
                    
        # Sort indices by reliability (smaller Z means more reliable)
        sorted_indices = np.argsort(z)
        info_indices = sorted_indices[:self.K]
        frozen_indices = sorted_indices[self.K:]
        
        return np.sort(info_indices), np.sort(frozen_indices)

    def encode(self, info_bits):
        """
        Polar encoding.
        info_bits: Array of size K with values in {0, 1}
        Returns: Encoded codeword of size N
        """
        u = np.zeros(self.N, dtype=int)
        u[self.info_bits_indices] = info_bits
        
        x = np.copy(u)
        # Polar transform
        for step in range(self.n):
            stride = 1 << step
            for i in range(0, self.N, 2 * stride):
                for j in range(stride):
                    x[i + j] = (x[i + j] + x[i + j + stride]) % 2
        return x

    def decode_sc(self, llr):
        """
        Successive Cancellation (SC) Decoding.
        llr: Received LLR values of size N
        Returns: Decoded information bits of size K
        """
        # Node values in the SC decoding tree
        # LLR arrays for each stage
        node_llrs = [np.zeros(self.N) for _ in range(self.n + 1)]
        node_llrs[0] = np.copy(llr)
        
        # Bit estimates for each stage
        node_ucap = [np.zeros(self.N, dtype=int) for _ in range(self.n + 1)]
        
        def f(l1, l2):
            # Min-Sum approximation for numerical stability
            return np.sign(l1) * np.sign(l2) * np.minimum(np.abs(l1), np.abs(l2))
        
        def g(l1, l2, u_hat):
            return l2 + (1 - 2 * u_hat) * l1

        # Recursive SC decoding function
        def recursively_calc_llr(stage, index):
            if stage == 0:
                return
            
            stride = 1 << (stage - 1)
            
            # Left child
            if index % 2 == 0:
                recursively_calc_llr(stage - 1, index // 2)
                # Compute LLR for left branch
                for i in range(stride):
                    l1 = node_llrs[stage - 1][(index // 2) * 2 * stride + i]
                    l2 = node_llrs[stage - 1][(index // 2) * 2 * stride + stride + i]
                    node_llrs[stage][index * stride + i] = f(l1, l2)
            # Right child
            else:
                # Left child bit estimates are ready
                # Compute LLR for right branch
                for i in range(stride):
                    l1 = node_llrs[stage - 1][(index // 2) * 2 * stride + i]
                    l2 = node_llrs[stage - 1][(index // 2) * 2 * stride + stride + i]
                    u_hat = node_ucap[stage][(index - 1) * stride + i]
                    node_llrs[stage][index * stride + i] = g(l1, l2, u_hat)
                    
            if stage == self.n:
                # Leaf node: make decision
                if index in self.frozen_bits_indices:
                    node_ucap[self.n][index] = 0
                else:
                    node_ucap[self.n][index] = 0 if node_llrs[self.n][index] >= 0 else 1
            else:
                # Continue recursion for children
                recursively_calc_llr(stage + 1, 2 * index)
                recursively_calc_llr(stage + 1, 2 * index + 1)
                
                # Combine bit estimates to pass up
                for i in range(stride):
                    u_left = node_ucap[stage + 1][2 * index * stride // 2 + i]
                    u_right = node_ucap[stage + 1][(2 * index + 1) * stride // 2 + i]
                    node_ucap[stage][index * stride + i] = (u_left + u_right) % 2
                    node_ucap[stage - 1][(index // 2) * 2 * stride + stride + i] = u_right # Wait, this structure is complex.
                    
        # We will use an iterative or simpler recursive approach for SC.
        # Iterative SC is often easier to implement correctly in Python.
        
        # Let's implement standard recursive SC decoder tree traversal
        u_hat = np.zeros(self.N, dtype=int)
        
        # The LLRs at each stage. l[st][node]
        l = np.zeros((self.n + 1, self.N))
        l[0] = llr
        # The partial sums at each stage. p[st][node]
        b = np.zeros((self.n + 1, self.N), dtype=int)
        
        def sc_decode_recursive(stage, node_idx):
            if stage == self.n:
                # Leaf node
                if node_idx in self.frozen_bits_indices:
                    b[stage, node_idx] = 0
                else:
                    b[stage, node_idx] = 0 if l[stage, node_idx] >= 0 else 1
                return b[stage, node_idx]
            
            # Non-leaf node
            length = 1 << (self.n - stage)
            half_len = length // 2
            
            # Left child (f function)
            node_llrs = l[stage, node_idx * length : (node_idx + 1) * length]
            l1 = node_llrs[:half_len]
            l2 = node_llrs[half_len:]
            l[stage + 1, 2 * node_idx * half_len : (2 * node_idx + 1) * half_len] = f(l1, l2)
            
            sc_decode_recursive(stage + 1, 2 * node_idx)
            
            u_left = b[stage + 1, 2 * node_idx * half_len : (2 * node_idx + 1) * half_len]
            
            # Right child (g function)
            l[stage + 1, (2 * node_idx + 1) * half_len : (2 * node_idx + 2) * half_len] = g(l1, l2, u_left)
            
            sc_decode_recursive(stage + 1, 2 * node_idx + 1)
            
            u_right = b[stage + 1, (2 * node_idx + 1) * half_len : (2 * node_idx + 2) * half_len]
            
            # Combine bit estimates
            b[stage, node_idx * length : node_idx * length + half_len] = (u_left + u_right) % 2
            b[stage, node_idx * length + half_len : (node_idx + 1) * length] = u_right
            
        sc_decode_recursive(0, 0)
        
        # Extract info bits from leaves
        return b[self.n, self.info_bits_indices]

