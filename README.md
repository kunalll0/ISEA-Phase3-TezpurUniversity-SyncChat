#  SyncChat v2.0 - Secure Multi-Client TCP Chat Application

<p align="center">
  <b>GUI-Based Secure Multi-Client TCP Chat Application</b><br>
  Developed using Python Socket Programming, Tkinter, Mininet & Wireshark
</p>

---

##  Project Overview

**SyncChat v2.0** is a secure GUI-based Multi-Client TCP Chat Application developed as part of the **ISEA Phase-III Cyber Security Internship (Tezpur University)**.

The application enables multiple users to communicate simultaneously over a TCP network while incorporating authentication, secure account management, duplicate login prevention, activity timeout, chat history logging, security logging, and real-time GUI updates.

The project was developed and tested inside a Mininet virtual network and validated using Wireshark packet analysis.

---

#  Features

## Communication Features

- Multi-client TCP socket communication
- Real-time broadcast messaging
- Private messaging using `/msg`
- Live online users panel
- User join and leave notifications
- Server statistics monitoring
- Multi-threaded client handling

---

## GUI Features

- Modern Tkinter GUI
- Secure Login Window
- User Registration Window
- Responsive Chat Interface
- Online Users Panel
- Status Indicator
- Password Show/Hide functionality
- Password Strength Indicator
- Session Timeout Warning Dialogs

---

## Security Features

- User Authentication
- SHA-256 Password Hashing
- Secure User Registration
- Duplicate Login Prevention
- Login Attempt Limiter
- Temporary Account Lockout
- Session Timeout (Automatic Logout)
- Security Event Logging
- Chat History Logging
- Username Validation
- Password Validation
- Maximum Message Length Validation

---

# Technologies Used

- Python 3
- TCP Socket Programming
- Tkinter
- Threading
- CSV
- SHA-256 Hashing
- Mininet
- Wireshark
- Ubuntu (WSL)
- Linux Networking

---

#  Project Structure

```
SyncChat/
│
├── client_gui.py
├── server.py
├── users.csv
├── chat_history.csv
├── security_log.txt
├── README.md
├── LICENSE
│
├── Report/
│   ├── Assignment7_Report.docx
│   └── Assignment7_Report.pdf
│
└── Screenshots/
    ├── Login Window
    ├── Signup Window
    ├── Chat Interface
    ├── Wireshark Captures
    ├── Security Logs
    ├── Chat History
    └── Server Statistics
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/kunalll0/ISEA-Phase3-TezpurUniversity-SyncChat.git
```

Go inside the project

```bash
cd ISEA-Phase3-TezpurUniversity-SyncChat
```

---

#  Running the Application

## Step 1

Start Mininet

```bash
sudo mn --topo single,5
```

---

## Step 2

Run the Server

```bash
python3 server.py
```

---

## Step 3

Launch Client GUI

```bash
python3 client_gui.py
```

---

## Step 4

Connect using the Server IP

Example

```
10.0.0.1
```

Login using your registered credentials.

---

#  Supported Commands

| Command | Description |
|----------|-------------|
| Normal Message | Broadcast to all users |
| `/msg username message` | Private Messaging |
| `/list` | Display Online Users |
| `/info` | Server Information |
| `/history` | Recent Chat History |
| `/help` | Available Commands |

---

#  Screenshots Included

The repository contains screenshots demonstrating:

- Login Window
- User Registration
- Password Validation
- Duplicate Login Prevention
- Login Attempt Lockout
- Session Timeout
- Successful Login
- Chat Window
- Broadcast Messaging
- Private Messaging
- Online Users Panel
- Help Command
- Server Information
- Chat History
- User Disconnection
- Server Console
- Chat History Log
- Security Log
- User Database
- Wireshark TCP Analysis

---

#  Wireshark Packet Analysis

The application traffic was verified using Wireshark by monitoring TCP communication on **Port 5000**.

Captured operations include:

- TCP Three-Way Handshake
- Broadcast Message Transmission
- Private Message Transmission
- TCP ACK Packets
- User Logout
- TCP FIN Termination

---

#  Security Mechanisms

Implemented security controls include:

- Password Hashing (SHA-256)
- Secure User Authentication
- Duplicate Login Detection
- Login Attempt Restriction
- Temporary Account Lockout
- Automatic Session Timeout
- Security Event Logging
- Chat History Logging
- Username Validation
- Password Strength Validation
- Message Length Validation

---

#  Learning Outcomes

This project provided practical experience in:

- Client-Server Architecture
- TCP Socket Programming
- Multi-threaded Network Applications
- GUI Development using Tkinter
- Authentication Mechanisms
- Password Hashing
- Secure Programming Practices
- Mininet Network Emulation
- Wireshark Packet Analysis
- Network Security Fundamentals

---

#  Internship Information

**Program:** Information Security Education and Awareness (ISEA) Phase-III

**University:** Tezpur University

**Project:** Assignment 7 - Secure GUI-Based Multi-Client TCP Chat Application

---

# 💻 Author

**Kunal Prajapati**

BCA (Cyber Security)

ISEA Phase-III Cyber Security Internship

Tezpur University

GitHub: https://github.com/kunalll0

---

#  License

This project is released under the **MIT License**.
