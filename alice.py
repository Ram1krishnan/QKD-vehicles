# alice_qkd.py
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class AliceQKD:
    def __init__(self, num_bits=256):
        self.num_bits = num_bits
        self.bits = None
        self.bases = None
        
    def generate_key(self):
        """Generate random bits and bases"""
        self.bits = np.random.randint(2, size=self.num_bits)
        self.bases = np.random.randint(2, size=self.num_bits)
        return self.bits, self.bases
    
    def get_final_key(self, bob_bases):
        """Generate final key using Bob's bases"""
        if self.bits is None or self.bases is None:
            raise ValueError("Must generate initial bits and bases first")
            
        matching_bases = self.bases == bob_bases
        sifted_key = [str(self.bits[i]) for i in range(self.num_bits) if matching_bases[i]]
        final_key = "".join(sifted_key)[:256]
        return final_key

# Example usage
if __name__ == "__main__":
    alice = AliceQKD()
    bits, bases = alice.generate_key()
    print("Alice's bits:", bits)
    print("Alice's bases:", bases)
