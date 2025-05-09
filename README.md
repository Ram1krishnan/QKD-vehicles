# QKD-vehicles
## Project Description

This project demonstrates **Quantum Key Distribution (QKD)** integrated with **Vehicular Ad-hoc Networks (VANETs)** to ensure secure communication between vehicles and roadside infrastructure.

We built an IoT communication prototype where:

- **SUMO (Simulation of Urban Mobility)** acts as a vehicle simulator that collects traffic-related data.
- The collected data is **encrypted using a quantum key** generated through the **BB84 QKD protocol**.
- This quantum key exchange simulates **SUMO** and **RSU** exchanging qubits and bases to derive a shared secret key.
- The encrypted data is transmitted over MQTT to **Road Side Units (RSUs)**.
- RSUs use the agreed quantum key to **decrypt the data securely**, ensuring end-to-end confidentiality and robustness against classical eavesdropping attacks.

The system showcases the feasibility of quantum-enhanced security in future intelligent transportation systems and lays the groundwork for incorporating QKD in real-world IoT-based smart city infrastructures.
