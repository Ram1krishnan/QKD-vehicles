import numpy as np
import paho.mqtt.client as mqtt
import json
import time
from bob import BobQKD  # Import Bob's QKD module
from quantum_encryption1 import decrypt_data  # Import decryption function

# MQTT configuration
MQTT_BROKER = "localhost"
TOPIC_SEND_QUBITS = "quantum/send_qubits"
TOPIC_RECEIVE_BASIS = "quantum/receive_basis"
TOPIC_ENCRYPTED_DATA = "vehicle/encrypted_data"  # Topic for receiving encrypted data

# Initialize Bob's QKD system
bob = BobQKD(num_bits=256)

# Initialize MQTT client for RSU (Bob)
client = mqtt.Client()

# Variable to store the final key
final_key = None
key_established = False

def on_connect(client, userdata, flags, rc):
    print("RSU connected to MQTT Broker")
    client.subscribe(TOPIC_SEND_QUBITS)
    client.subscribe(TOPIC_ENCRYPTED_DATA)  # Subscribe to encrypted data topic

def on_qkd_message(client, userdata, msg):
    global final_key, key_established
    print("RSU received quantum data from vehicle")
    data = json.loads(msg.payload.decode())
    alice_bits = np.array(data["bits"])
    alice_bases = np.array(data["bases"])

    # Generate Bob's measurements and bases
    measured_bits, bob_bases = bob.generate_key(alice_bits, alice_bases)
    print("RSU (Bob) measured qubits with random bases")
    
    # Send Bob's basis choices back to Alice
    client.publish(TOPIC_RECEIVE_BASIS, json.dumps({"bases": bob_bases.tolist()}))
    print("RSU sent basis choices to vehicle")
    
    # Generate final key
    final_key = bob.get_final_key(alice_bases)
    key_established = True
    print(f"RSU final key: {final_key}")

    # Calculate statistics
    matching_bases = alice_bases == bob_bases
    print(f"Number of matching bases: {np.sum(matching_bases)} out of {len(alice_bases)}")

def on_encrypted_data_message(client, userdata, msg):
    if not key_established:
        print("Warning: Received encrypted data but key is not established yet.")
        return
        
    try:
        # Decode the JSON message
        encrypted_data = json.loads(msg.payload.decode())
        
        # Decrypt the data using the quantum key
        decrypted_data = decrypt_data(encrypted_data, final_key)
        
        if decrypted_data:
            print(f"RSU received and decrypted vehicle data: {decrypted_data}")
            
            # Parse the decrypted data
            parts = decrypted_data.split(',')
            if len(parts) >= 11:
                step = parts[0]
                vehicle_id = parts[1]
                x = float(parts[2])
                y = float(parts[3])
                speed = float(parts[4])
                acceleration = float(parts[5])
                lane=parts[6]
                
                print(f"Vehicle {vehicle_id} at step {step}:")
                print(f"\t Position: ({x}, {y})")
                print(f"\t Speed: {speed} m/s")
                print(f"\t Acceleration: {acceleration} m/s²")
                print(f"\t Lane: {lane}")
        else:
            print("Failed to decrypt data")
    except Exception as e:
        print(f"Error processing encrypted data: {e}")

def on_message(client, userdata, msg):
    if msg.topic == TOPIC_SEND_QUBITS:
        on_qkd_message(client, userdata, msg)
    elif msg.topic == TOPIC_ENCRYPTED_DATA:
        on_encrypted_data_message(client, userdata, msg)

client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker
client.connect(MQTT_BROKER, 1883)

# Start the MQTT loop
print("RSU starting MQTT client loop...")
client.loop_forever()