import socket
import threading
import time
import csv
import json
import psutil
import os
import matplotlib.pyplot as plt

# ==========================
# LOAD CONFIG
# ==========================

with open("config.json", "r") as file:
    config = json.load(file)

SERVER_IP = config["client"]["default_server_ip"]
SERVER_PORT = config["server"]["port"]
BUFFER_SIZE = config["server"]["buffer_size"]
MAX_CLIENTS = config["server"]["max_clients"]

USERS_FILE = config["files"]["users"]

RESULT_FILE = "performance_results.csv"

GRAPH_FOLDER = "graphs"

if not os.path.exists(GRAPH_FOLDER):
    os.makedirs(GRAPH_FOLDER)

CLIENT_COUNTS = [5, 8, 10]

MESSAGES_PER_CLIENT = 20

MESSAGE_DELAY = 0.05

results = []


# ==========================
# LOAD USERNAMES
# ==========================

def load_users():

    usernames = []

    with open(USERS_FILE, "r", newline="") as file:

        reader = csv.DictReader(file)

        for row in reader:

            usernames.append(row["username"])

    return usernames


# ==========================
# FIND SERVER PROCESS
# ==========================

def find_server_process():

    for process in psutil.process_iter(["pid", "name", "cmdline"]):

        try:

            cmdline = process.info["cmdline"]

            if cmdline:

                command = " ".join(cmdline)

                if "server.py" in command:

                    return process

        except Exception:
            pass

    return None


# ==========================
# CLIENT CLASS
# ==========================

class TestClient:

    def __init__(self, username):

        self.username = username

        self.socket = None

        self.connected = False

        self.sent = 0

        self.received = 0

        self.total_delay = 0

        self.running = False

        self.receiver = None


    def connect(self):

        try:

            self.socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            self.socket.connect(
                (SERVER_IP, SERVER_PORT)
            )

            response = self.socket.recv(BUFFER_SIZE).decode()

            if response != "USERNAME":
                return False

            self.socket.send(
                self.username.encode()
            )

            response = self.socket.recv(BUFFER_SIZE).decode()

            if response != "LOGIN_SUCCESS":
                return False

            self.connected = True

            self.running = True

            self.receiver = threading.Thread(
                target=self.receive_loop,
                daemon=True
            )

            self.receiver.start()

            return True

        except Exception as e:

            print("Connection Error:", e)

            return False


    def receive_loop(self):

        while self.running:

            try:

                data = self.socket.recv(BUFFER_SIZE)

                if not data:
                    break

                self.received += 1

            except Exceptiion:

                break

        # ==========================
    # SEND BENCHMARK MESSAGES
    # ==========================

    def run_test(self):

        for i in range(MESSAGES_PER_CLIENT):

            if not self.connected:
                break

            message = f"TEST_MESSAGE_{i}"

            start = time.perf_counter()

            try:

                self.socket.send(message.encode())

                self.sent += 1

            except:

                break

            end = time.perf_counter()

            self.total_delay += (end - start)

            time.sleep(MESSAGE_DELAY)


    def average_delay(self):

        if self.sent == 0:

            return 0

        return (self.total_delay / self.sent) * 1000


    def disconnect(self):

        try:

            self.running = False

            self.socket.send(b"LOGOUT")

            self.socket.close()

        except Exception:

            pass
# ==========================
# BENCHMARK FUNCTION
# ==========================

def run_benchmark(client_count):

    print("\n==============================")
    print(f"Running Test with {client_count} Clients")
    print("==============================")

    usernames = load_users()

    clients = []

    server_process = find_server_process()

    if server_process:

        server_process.cpu_percent()

    # --------------------------
    # Connect Clients
    # --------------------------

    for username in usernames[:client_count]:

        client = TestClient(username)

        if client.connect():

            clients.append(client)

            print(username, "Connected")

        else:

            print(username, "Failed")

    time.sleep(2)

    # --------------------------
    # Start Benchmark
    # --------------------------

    start_time = time.perf_counter()

    threads = []

    for client in clients:

        thread = threading.Thread(
            target=client.run_test
        )

        threads.append(thread)

        thread.start()

    for thread in threads:

        thread.join()

    end_time = time.perf_counter()

    elapsed = end_time - start_time

    total_sent = sum(client.sent for client in clients)

    average_delay = sum(
        client.average_delay()
        for client in clients
    ) / len(clients)

    throughput = total_sent / elapsed

    cpu = 0

    memory = 0

    if server_process:

        cpu = server_process.cpu_percent()

        memory = (
            server_process.memory_info().rss
            / 1024
            / 1024
        )

    results.append({

        "clients": client_count,

        "delay": round(average_delay, 2),

        "throughput": round(throughput, 2),

        "cpu": round(cpu, 2),

        "memory": round(memory, 2)

    })

    print("Average Delay :", round(average_delay, 2), "ms")

    print("Throughput    :", round(throughput, 2), "msg/sec")

    print("CPU Usage     :", round(cpu, 2), "%")

    print("Memory Usage  :", round(memory, 2), "MB")

    # --------------------------
    # Disconnect Clients
    # --------------------------

    for client in clients:

        client.disconnect()

    time.sleep(2)

# ==========================
# SAVE RESULTS
# ==========================

def save_results():

    with open(RESULT_FILE, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "Clients",
            "Average Delay (ms)",
            "Throughput (msg/sec)",
            "CPU Usage (%)",
            "Memory Usage (MB)"
        ])

        for row in results:

            writer.writerow([
                row["clients"],
                row["delay"],
                row["throughput"],
                row["cpu"],
                row["memory"]
            ])

    print("\nResults saved to", RESULT_FILE)


# ==========================
# GRAPHS
# ==========================

def generate_graphs():

    clients = [r["clients"] for r in results]

    delays = [r["delay"] for r in results]

    throughput = [r["throughput"] for r in results]

    cpu = [r["cpu"] for r in results]

    memory = [r["memory"] for r in results]


    # Delay Graph

    plt.figure(figsize=(6,4))

    plt.plot(clients, delays, marker="o")

    plt.title("Average Delay")

    plt.xlabel("Number of Clients")

    plt.ylabel("Delay (ms)")

    plt.grid(True)

    plt.savefig(os.path.join(GRAPH_FOLDER, "delay.png"))

    plt.close()


    # Throughput Graph

    plt.figure(figsize=(6,4))

    plt.plot(clients, throughput, marker="o")

    plt.title("Throughput")

    plt.xlabel("Number of Clients")

    plt.ylabel("Messages / Second")

    plt.grid(True)

    plt.savefig(os.path.join(GRAPH_FOLDER, "throughput.png"))

    plt.close()


    # CPU Graph

    plt.figure(figsize=(6,4))

    plt.plot(clients, cpu, marker="o")

    plt.title("CPU Usage")

    plt.xlabel("Number of Clients")

    plt.ylabel("CPU %")

    plt.grid(True)

    plt.savefig(os.path.join(GRAPH_FOLDER, "cpu.png"))

    plt.close()


    # Memory Graph

    plt.figure(figsize=(6,4))

    plt.plot(clients, memory, marker="o")

    plt.title("Memory Usage")

    plt.xlabel("Number of Clients")

    plt.ylabel("Memory (MB)")

    plt.grid(True)

    plt.savefig(os.path.join(GRAPH_FOLDER, "memory.png"))

    plt.close()

    print("Graphs generated successfully.")


# ==========================
# MAIN
# ==========================

if __name__ == "__main__":

    print("=" * 50)

    print("SYNCCHAT PERFORMANCE TEST")

    print("=" * 50)

    for count in CLIENT_COUNTS:

        run_benchmark(count)

    save_results()

    generate_graphs()

    print("\nPerformance Testing Completed.")
