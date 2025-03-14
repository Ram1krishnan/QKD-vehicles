import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib

def prepare_key(quantum_key, key_size=32):
    """
    Prepare a quantum key for use with AES encryption.
    - If binary string, convert to bytes
    - Hash the key to get a fixed length suitable for AES
    - AES-256 requires a 32-byte key
    """
    # If key is a binary string, convert to bytes
    if isinstance(quantum_key, str) and all(bit in '01' for bit in quantum_key):
        # Convert binary string to bytes
        # First ensure length is a multiple of 8
        padded_key = quantum_key.ljust((len(quantum_key) + 7) // 8 * 8, '0')
        key_bytes = bytes(int(padded_key[i:i+8], 2) for i in range(0, len(padded_key), 8))
    else:
        # Otherwise assume it's already bytes
        key_bytes = quantum_key if isinstance(quantum_key, bytes) else quantum_key.encode()
    
    # Use SHA-256 to get a fixed length key
    return hashlib.sha256(key_bytes).digest()[:key_size]

def encrypt_data(data, quantum_key):
    """
    Encrypt data with a quantum key using AES-GCM.
    
    Args:
        data (str): The data to encrypt
        quantum_key (str/bytes): Quantum key (will be properly formatted)
        
    Returns:
        dict: Dictionary with ciphertext, nonce, and tag
    """
    # Prepare the key for AES
    key = prepare_key(quantum_key)
    
    # Create cipher
    cipher = AES.new(key, AES.MODE_GCM)
    nonce = cipher.nonce
    
    # Encrypt the data
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())
    
    # Format for transmission
    encrypted_data = {
        'ciphertext': base64.b64encode(ciphertext).decode(),
        'nonce': base64.b64encode(nonce).decode(),
        'tag': base64.b64encode(tag).decode()
    }
    return encrypted_data

def decrypt_data(encrypted_data, quantum_key):
    """
    Decrypt data with a quantum key using AES-GCM.
    
    Args:
        encrypted_data (dict): Dictionary with ciphertext, nonce, and tag
        quantum_key (str/bytes): Quantum key (will be properly formatted)
        
    Returns:
        str: Decrypted data string or None if decryption fails
    """
    # Prepare the key for AES
    key = prepare_key(quantum_key)
    
    try:
        # Decode the encrypted components
        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
        nonce = base64.b64decode(encrypted_data['nonce'])
        tag = base64.b64decode(encrypted_data['tag'])
        
        # Create cipher for decryption
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        
        # Decrypt and verify
        decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
        
        return decrypted_data.decode()
    except Exception as e:
        print(f"Error: Decryption failed. {e}")
        return None

# Test function
def test_encryption():
    """Test the encryption and decryption functions"""
    test_key = "010101010101010101010101"  # Example quantum key (binary string)
    test_data = "This is a secret message from the vehicle"
    
    print(f"Original key (binary): {test_key}")
    print(f"Prepared key (hex): {prepare_key(test_key).hex()}")
    
    encrypted = encrypt_data(test_data, test_key)
    print(f"Encrypted: {encrypted}")
    
    decrypted = decrypt_data(encrypted, test_key)
    print(f"Decrypted: {decrypted}")
    
    assert decrypted == test_data, "Decryption failed to match original"
    print("Test passed: encryption and decryption working correctly")

if __name__ == "__main__":
    test_encryption()