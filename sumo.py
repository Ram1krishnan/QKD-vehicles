import traci
import time
import paho.mqtt.client as mqtt
import json
import numpy as np
from alice import AliceQKD  # Import Alice's QKD module
from quantum_encryption1 import encrypt_data  # Import encryption function

# Path to SUMO binary
SUMO_BINARY = "sumo"

# Path to SUMO configuration file
SUMO_CONFIG = "../sumo_network/sumo_config.sumocfg"

# Output file for saving vehicle data
OUTPUT_FILE = "vehicle_data.json"

# MQTT configuration
MQTT_BROKER = "localhost"
TOPIC_SEND_QUBITS = "quantum/send_qubits"
TOPIC_RECEIVE_BASIS = "quantum/receive_basis"
TOPIC_ENCRYPTED_DATA = "vehicle/encrypted_data"  # New topic for encrypted data

# Initialize MQTT client for the vehicle (Alice)
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, 1883)
mqtt_client.loop_start()

# Initialize Alice's QKD system
alice = AliceQKD(num_bits=256)

# Variable to store the final key
final_key = None
key_established = False  # Flag to track key establishment
vehicle_data = []  # Collection for storing vehicle data

# MQTT callback for receiving Bob's bases
def on_message(client, userdata, msg):
    global final_key, key_established
    data = json.loads(msg.payload.decode())
    bob_bases = np.array(data["bases"])
    
    # Generate final key using Bob's bases
    final_key = alice.get_final_key(bob_bases)
    key_established = True
    #print(f"Vehicle received basis from RSU")
    #print(f"Vehicle final key: {final_key}")
    #print(f"Quantum key established, now starting to collect vehicle data...")

# Set up MQTT callbacks
mqtt_client.on_message = on_message
mqtt_client.subscribe(TOPIC_RECEIVE_BASIS)

# Generate quantum key at the beginning
alice_bits, alice_bases = alice.generate_key()
#print("Vehicle generated quantum bits and bases")

# Send quantum bits and bases to RSU (Bob)
mqtt_client.publish(TOPIC_SEND_QUBITS, json.dumps({
    "bits": alice_bits.tolist(),
    "bases": alice_bases.tolist()
}))
#print("Vehicle sent quantum data to RSU")
print("Waiting for key establishment before collecting vehicle data...")

# Wait for key to be established (with timeout)
key_wait_start = time.time()
timeout = 30  # 30 seconds timeout
while not key_established:
    time.sleep(0.5)
    if time.time() - key_wait_start > timeout:
        print("Timeout waiting for key establishment. Exiting...")
        mqtt_client.loop_stop()
        exit(1)

# Start SUMO with TraCI after key is established
#print("Starting SUMO simulation now that the key is established...")
traci.start([SUMO_BINARY, "-c", SUMO_CONFIG, "--step-length", "0.1"])

# Run simulation
SIMULATION_TIME = 1000
step = 0

while step < SIMULATION_TIME:
    traci.simulationStep()  # Advance SUMO simulation
    vehicles = traci.vehicle.getIDList()  # Get active vehicles

    print(f"Step {step}: {len(vehicles)} vehicles detected.")

    # Process each vehicle and encrypt the data
    for vehicle_id in vehicles:
        position = traci.vehicle.getPosition(vehicle_id)  # (x, y) position
        speed = traci.vehicle.getSpeed(vehicle_id)  # Speed in m/s
        acceleration = traci.vehicle.getAcceleration(vehicle_id)  # Acceleration in m/s²
        lane = traci.vehicle.getLaneID(vehicle_id)  # Current lane
        lane_position = traci.vehicle.getLanePosition(vehicle_id)  # Position in the lane
        angle = traci.vehicle.getAngle(vehicle_id)  # Heading angle in degrees
        co2_emission = traci.vehicle.getCO2Emission(vehicle_id)  # CO2 emissions in mg/s
        fuel_consumption = traci.vehicle.getFuelConsumption(vehicle_id)  # Fuel consumption in mL/s

        # Print to console
        print(f"Vehicle {vehicle_id}:")
        print(f"\t Position: {position}")
        print(f"\t Speed: {speed:.2f} m/s")
        print(f"\t Acceleration: {acceleration:.2f} m/s²")
        print(f"\t Lane: {lane}")

        # Format data as string for encryption and transmission
        data_string = f"{step},{vehicle_id},{position[0]:.2f},{position[1]:.2f},{speed:.2f},{acceleration:.2f},{lane},{lane_position:.2f},{angle:.2f},{co2_emission:.2f},{fuel_consumption:.2f}"
        
        # Store for local logging
        vehicle_data.append(data_string)
        
        # Encrypt the data with the quantum key
        encrypted_data = encrypt_data(data_string, final_key)
        print(encrypted_data)
        # Send encrypted data to RSU
        mqtt_client.publish(TOPIC_ENCRYPTED_DATA, json.dumps(encrypted_data))
        print(f"Sent encrypted data for vehicle {vehicle_id}")

    step += 1
    time.sleep(0.1)

# Write collected data to JSON file
with open(OUTPUT_FILE, 'w') as f:
    json.dump(vehicle_data, f, indent=2)

# Clean up
mqtt_client.loop_stop()
traci.close()
print(f"Simulation Ended. Data saved in {OUTPUT_FILE}")
#print(f"Final Quantum Key Used: {final_key}")