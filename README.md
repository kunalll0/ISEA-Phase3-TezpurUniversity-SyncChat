# SyncChat

SyncChat is a GUI-based Multi-Client TCP Chat Application developed using Python Socket Programming and Tkinter. The project demonstrates reliable communication over TCP sockets inside a Mininet network topology while providing a modern graphical interface for real-time messaging.

---

## Features

- Multi-client TCP communication
- GUI built using Tkinter
- Public (broadcast) messaging
- Private messaging between users
- Real-time online users list
- Join and leave notifications
- Thread-based communication for responsive GUI
- TCP packet verification using Wireshark
- Tested in Mininet virtual network

---

## Technologies Used

- Python 3
- Socket Programming
- TCP Protocol
- Tkinter
- Threading
- Mininet
- Wireshark
- Ubuntu (WSL)

---

## Project Structure

```
SyncChat/
│
├── client_gui.py
├── server.py
├── README.md
├── LICENSE
├── report.pdf
└── screenshots/
```

---

## How to Run

### 1. Start Mininet

```bash
sudo mn --topo single,5
```

### 2. Start the Server

```bash
python3 server.py
```

### 3. Launch Client GUI

```bash
python3 client_gui.py
```

Connect using the server IP (for example `10.0.0.1`) and enter a username.

---

## Application Screenshots

- Login Window
- Chat Interface
- User Join Notification
- Broadcast Messaging
- Private Messaging
- User Leave Notification
- Online Users Panel

---

## Network Verification

The communication was verified using **Wireshark** by capturing TCP packets on port **5000**.

Verified operations include:

- TCP Connection Establishment
- Broadcast Message Transmission
- Private Message Transmission
- TCP Acknowledgements
- Connection Termination

---

## Learning Outcomes

This project demonstrates practical implementation of:

- TCP Socket Programming
- Client-Server Architecture
- Multi-threading
- GUI Development with Tkinter
- Network Packet Analysis
- Multi-client Communication
- Mininet Network Emulation

---

## Author

**Kunal Prajapati**

BCA (Cyber Security)

University Assignment – GUI Based Multi-Client TCP Chat Application

---

## License

This project is licensed under the MIT License.
