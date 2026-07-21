# SyncChat

A GUI-based Multi-Client TCP Chat Application built with Python Socket Programming featuring user authentication, real-time messaging, performance optimization, scalability evaluation, and network traffic analysis.

---

## Overview

SyncChat is a desktop-based client-server chat application developed using Python. It enables multiple authenticated users to communicate over a TCP network through an intuitive graphical interface while providing real-time messaging, user management, and reliable communication.

The project combines concepts from computer networks, socket programming, cybersecurity, operating systems, and software engineering into a single application. Beyond implementing a multi-client chat system, the latest version focuses on improving application reliability, optimizing performance, evaluating scalability, and simplifying deployment through centralized configuration management.

The application was developed and tested using Mininet for network emulation and Wireshark for packet inspection, with performance benchmarking carried out under multiple client workloads.

---

# Features

## Communication

- Multi-client TCP communication
- Real-time broadcast messaging
- Private messaging using `/msg`
- Live online user management
- User join and leave notifications
- Built-in server commands
- Multi-threaded client handling

---

## User Management

- User registration
- Login authentication
- Duplicate username prevention
- Duplicate login prevention
- Password strength validation
- Login attempt restriction
- Temporary account lockout
- Automatic session timeout

---

## Reliability

- Graceful client disconnection
- Improved exception handling
- Automatic session cleanup
- Stable multi-threaded communication
- Continuous server availability
- Connection monitoring

---

## Performance & Scalability

- Centralized configuration management
- Automated benchmark testing
- Scalability evaluation
- Throughput measurement
- Average message delay analysis
- CPU usage monitoring
- Memory usage monitoring
- Performance report generation
- Automatic graph generation

---

## Network Analysis

- Mininet virtual network testing
- Wireshark packet analysis
- TCP connection verification
- Multi-client traffic analysis

---

# Technologies Used

| Technology | Purpose |
|------------|---------|
| Python 3 | Programming Language |
| Socket | TCP Communication |
| Tkinter | GUI Development |
| Threading | Multi-client Support |
| Hashlib | Password Hashing |
| CSV | Data Storage |
| JSON | Configuration Management |
| Mininet | Network Emulation |
| Wireshark | Packet Analysis |
| Matplotlib | Performance Visualization |

---

# Project Structure

```text
SyncChat/
│
├── client_gui.py
├── server.py
├── performance_test.py
├── config.json
├── users.csv
├── chat_history.csv
├── security_log.txt
├── performance_results.csv
│
├── graphs/
│   ├── cpu.png
│   ├── delay.png
│   ├── memory.png
│   └── throughput.png
│
├── Screenshots/
│
├── Reports/
│   ├── Assignment8_Report.docx
│   └── Assignment8_Report.pdf
│
├── README.md
└── LICENSE
```

---

# Getting Started

Clone the repository.

```bash
git clone https://github.com/kunalll0/ISEA-Phase3-TezpurUniversity-SyncChat.git
```

Move into the project directory.

```bash
cd ISEA-Phase3-TezpurUniversity-SyncChat
```

---

# Running the Application

Start the server.

```bash
python3 server.py
```

Launch one or more client instances.

```bash
python3 client_gui.py
```

Log in using registered credentials and begin chatting.

---

# Performance Benchmark

Run the benchmark tool.

```bash
python3 performance_test.py
```

The benchmark evaluates the application using:

- 5 Clients
- 8 Clients
- 10 Clients

The following metrics are recorded:

- Average Message Delay
- Throughput
- CPU Usage
- Memory Usage

Benchmark results are saved in:

```text
performance_results.csv
```

Performance graphs are generated inside:

```text
graphs/
```

---

# Configuration

All application settings are managed through:

```text
config.json
```

The configuration file allows modification of:

- Server IP Address
- Port Number
- Buffer Size
- Maximum Client Limit
- Session Timeout
- Login Attempt Limit
- Maximum Message Length

No source code modifications are required when changing deployment settings.

---

# Available Commands

| Command | Description |
|---------|-------------|
| Normal Message | Send a broadcast message |
| `/msg username message` | Send a private message |
| `/list` | Display online users |
| `/info` | Display server statistics |
| `/history` | View recent chat history |
| `/help` | Display all available commands |

---

# Performance Evaluation

The latest version introduces performance benchmarking and scalability testing to evaluate application behavior under increasing workloads.

Performance evaluation includes:

- Multi-client benchmark execution
- Resource utilization monitoring
- Throughput analysis
- Message delay measurement
- Scalability testing
- Performance graph generation

---

# Packet Analysis

Network communication was verified using Wireshark.

Captured operations include:

- TCP Three-Way Handshake
- User Authentication
- Broadcast Messaging
- Private Messaging
- User Connection
- User Disconnection
- TCP Connection Termination

---

# Screenshots

The repository contains screenshots demonstrating:

- User Registration
- Login Interface
- Chat Window
- Broadcast Messaging
- Private Messaging
- Online User Management
- Session Timeout
- Configuration Management
- Benchmark Execution
- Performance Results
- Wireshark Analysis
- Performance Graphs

---

# Future Scope

Possible future enhancements include:

- TLS/SSL Communication
- End-to-End Encryption
- Database Integration
- Cloud Deployment
- Load Balancing
- Asynchronous Networking
- Mobile Application
- File Sharing
- Voice Communication
- Video Communication

---

# About the Project

This project was developed during the Information Security Education and Awareness (ISEA) Phase-III Summer Internship under the Ministry of Electronics and Information Technology (MeitY) in affiliation with Tezpur University.

The project demonstrates practical implementation of:

- Python Programming
- Socket Programming
- Computer Networks
- GUI Development
- Authentication
- Performance Optimization
- Scalability
- Distributed Systems

---

# Author

**Kunal Prajapati**

Bachelor of Computer Applications (Cyber Security)

GitHub: https://github.com/kunalll0

---

# License

This project is licensed under the MIT License.
