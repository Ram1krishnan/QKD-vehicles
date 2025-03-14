# bob_qkd.py
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class BobQKD:
    def __init__(self, num_bits=256):
        self.num_bits = num_bits
        self.bases = None
        self.measured_bits = None
        
    def measure_qubit(self, bit, sent_basis, measure_basis):
        """Simulate measuring a qubit"""
        qc = QuantumCircuit(1, 1)
        
        # Prepare state according to Alice's basis and bit
        if sent_basis == 0:  # Z-basis
            if bit == 1:
                qc.x(0)
        else:  # X-basis
            if bit == 1:
                qc.x(0)
            qc.h(0)
        
        # Measure in Bob's basis
        if measure_basis == 1:  # X-basis
            qc.h(0)
        qc.measure(0, 0)
        
        backend = Aer.get_backend('qasm_simulator')
        transpiled_qc = transpile(qc, backend)
        result = backend.run(transpiled_qc, shots=1).result()
        return int(list(result.get_counts(qc).keys())[0])
    
    def generate_key(self, alice_bits, alice_bases):
        """Generate key by measuring Alice's qubits"""
        self.bases = np.random.randint(2, size=self.num_bits)
        self.measured_bits = []
        
        for i in range(self.num_bits):
            measured_bit = self.measure_qubit(alice_bits[i], alice_bases[i], self.bases[i])
            self.measured_bits.append(measured_bit)
            
        self.measured_bits = np.array(self.measured_bits)
        return self.measured_bits, self.bases
    
    def get_final_key(self, alice_bases):
        """Generate final key using matching bases"""
        if self.measured_bits is None or self.bases is None:
            raise ValueError("Must measure qubits first")
            
        matching_bases = self.bases == alice_bases
        sifted_key = [str(self.measured_bits[i]) for i in range(self.num_bits) if matching_bases[i]]
        final_key = "".join(sifted_key)[:256]
        return final_key

# Example usage
if __name__ == "__main__":
    bob = BobQKD()
    # Would need Alice's bits and bases to actually generate a key
    print("Bob's QKD module loaded successfully")
