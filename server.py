import socket
import threading
import csv
import os
import json
from datetime import datetime

with open("config.json", "r") as config_file:
    config = json.load(config_file)

HOST = config["server"]["host"]
PORT = config["server"]["port"]
BUFFER_SIZE = config["server"]["buffer_size"]
clients={}
statistics={
    "connected_users":0,
    "messages_processed":0,
    "broadcast_messages":0,
    "private_messages":0,
    "system_messages":0
}
server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
server.bind((HOST,PORT))
server.listen()
server.settimeout(1)
print("Advanced Chat Server started on port",PORT)
CHAT_HISTORY_FILE = config["files"]["chat_history"]

if not os.path.exists(CHAT_HISTORY_FILE):
    with open(CHAT_HISTORY_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Timestamp",
            "Type",
            "Sender",
            "Receiver",
            "Message"
        ])
SECURITY_LOG_FILE = config["files"]["security_log"]

if not os.path.exists(SECURITY_LOG_FILE):
    with open(SECURITY_LOG_FILE, "w") as file:
        file.write("=" * 60 + "\n")
        file.write("SYNCCHAT SECURITY LOG\n")
        file.write("=" * 60 + "\n\n")

def save_history(message_type,
                 sender,
                 receiver,
                 message):
    with open(CHAT_HISTORY_FILE,
              "a",
              newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            message_type,
            sender,
            receiver,
            message
        ])

def write_log(event, user="", detail=""):
    with open(config["files"]["chat_log"], "a") as f:
        t=datetime.now().strftime("%H:%M:%S")
        f.write(f"{t},{event},{user},{detail}\n")

# ==========================================================
# SECURITY LOG
# ==========================================================

def write_security_log(event,
                       username="",
                       ip="",
                       details=""):

    with open(SECURITY_LOG_FILE, "a") as file:

        file.write(f"Time      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write("Source    : SERVER\n")
        file.write(f"Event     : {event}\n")

        if username:
            file.write(f"Username  : {username}\n")

        if ip:
            file.write(f"IP        : {ip}\n")

        if details:
            file.write(f"Details   : {details}\n")

        file.write("-" * 60 + "\n")

def stats():
    statistics["connected_users"]=len(clients)
    print("\n"+"="*50)
    print("ADVANCED MULTI CLIENT TCP CHAT SERVER")
    print("="*50)
    print(f"Online Users       : {statistics['connected_users']}")
    print(f"Messages Processed : {statistics['messages_processed']}")
    print(f"Broadcast Messages : {statistics['broadcast_messages']}")
    print(f"Private Messages   : {statistics['private_messages']}")
    print(f"System Messages    : {statistics['system_messages']}")
    print("="*50)

def broadcast(msg,exclude=None,system=False):
    for u,i in list(clients.items()):
        if exclude and u.lower()==exclude.lower():
            continue
        try:
            i["socket"].send(msg.encode())
        except Exception as e:
            print(f"Broadcast Error : {e}")
    if system:
        statistics["system_messages"]+=1
    else:
        statistics["broadcast_messages"]+=1

def find_user(name):
    for u in clients:
        if u.lower()==name.lower():
            return u
    return None
# ==========================================================
# SEND UPDATED ONLINE USERS TO EVERY CLIENT
# ==========================================================
def update_online_users():
    users = ",".join(clients.keys())
    message = "USERS:" + users
    for user in list(clients.values()):
        try:
            user["socket"].send(message.encode())
        except:
            pass

def send_list(sock):
    lines=["\n========== ONLINE USERS =========="]
    for i,u in enumerate(clients,1):
        lines.append(f"{i}. {u}")
    lines.append(f"\nTotal Online : {len(clients)}")
    lines.append("="*32)
    sock.send("\n".join(lines).encode())

def send_help(sock):
    txt="""
==============================
AVAILABLE COMMANDS
==============================
Normal Message:
Hello everyone

Private Message:
/msg username message

Online Users:
/list

Server Information:
/info

History:
/history

Help:
/help
==============================
"""
    sock.send(txt.encode())

def send_info(sock):
    history_records = 0
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r") as file:
            history_records = max(0,sum(1 for _ in file) - 1)
    txt = f"""
==============================
SERVER INFORMATION
==============================

Online Users       : {len(clients)}
Messages Processed : {statistics['messages_processed']}
Broadcast Messages : {statistics['broadcast_messages']}
Private Messages   : {statistics['private_messages']}
System Messages    : {statistics['system_messages']}
History Records    : {history_records}
==============================
"""
    sock.send(txt.encode())

def send_history(sock, limit=10):
    if not os.path.exists(CHAT_HISTORY_FILE):
        sock.send(b"History file not found.")
        return
    history = []
    with open(CHAT_HISTORY_FILE, "r", newline="") as file:
        reader = list(csv.reader(file))
        if len(reader) <= 1:
            sock.send(b"No chat history available.")
            return
        rows = reader[1:]
        rows = rows[-limit:]
    history.append("\n========== RECENT CHAT HISTORY ==========\n")
    for row in rows:
        if len(row) != 5:
            continue
        timestamp, msg_type, sender, receiver, message = row
        history.append(f"[{timestamp}]")
        history.append(f"Type     : {msg_type}")
        history.append(f"Sender   : {sender}")
        history.append(f"Receiver : {receiver}")
        history.append(f"Message  : {message}")
        history.append("-" * 40)
    sock.send("\n".join(history).encode())

def private_message(sender,target,msg):
    user=find_user(target)
    if not user:
        clients[sender]["socket"].send(f"[SERVER] User '{target}' not found.".encode())
        return
    clients[user]["socket"].send(f"[PRIVATE] {sender}: {msg}".encode())
    clients[sender]["socket"].send(f"[PRIVATE to {user}] {msg}".encode())
    statistics["private_messages"]+=1
    write_log( "PRIVATE", sender,f"{user}:{msg}")
    save_history("PRIVATE",sender,user,msg)
    stats()

def remove(sock):
    victim=None
    victim_data= None
    for u,d in clients.items():
        if d["socket"]==sock:
            victim=u
            victim_data=d
            break
    if victim:
        write_log("DISCONNECTED",victim)
        write_security_log(event="LOGOUT",username=victim, ip=victim_data["ip"])
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

        try:
            sock.close()
        except OSError:
            pass
        del clients[victim]
        save_history("SYSTEM","SERVER","ALL",f"{victim} left the chat")
        broadcast(f"*** {victim} left the chat ***",system=True)
        stats()
        update_online_users()

def handle(sock,user):
    while True:
        try:
            text=sock.recv(BUFFER_SIZE).decode()
            if not text:
                remove(sock)
                break
            if text == "LOGOUT":
                remove(sock)
                break
            if text.startswith("/"):
                if text.startswith("/msg "):
                    p=text.split(" ",2)
                    if len(p)==3:
                        private_message(user,p[1],p[2])
                    else:
                        sock.send(b"Usage: /msg username message")
                elif text=="/list":
                    send_list(sock)
                elif text=="/help":
                    send_help(sock)
                elif text=="/info":
                    send_info(sock)
                elif text=="/history":
                    send_history(sock)
                else:
                    sock.send(b"Unknown command. Type /help")
                continue

            statistics["messages_processed"]+=1
            write_log("MESSAGE",user,text)

            save_history("BROADCAST", user, "ALL",text)
            broadcast(f"[{user}] {text}")
            stats()

        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            print(f"{user} disconnected unexpectedly.")
            remove(sock)
            break

        except Exception as e:
            print(f"Unexpected Handle Error: {e}")
            remove(sock)
            break
while True:
    try:
        sock, addr = server.accept()

    except socket.timeout:
        continue

    except KeyboardInterrupt:

        print("\nServer shutting down...")

        # Notify all connected clients
        for data in list(clients.values()):
            try:
                data["socket"].send(
                    b"SERVER_SHUTDOWN"
                )
            except:
                pass

        # Close all client sockets
        for data in list(clients.values()):
            try:
                data["socket"].shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            try:
                data["socket"].close()
            except OSError:
                pass

        server.close()
        break
    # ============================================
    # Maximum Client Limit
    # ============================================
    if len(clients) >= config["server"]["max_clients"]:
        sock.send(b"SERVER_FULL")
        sock.close()
        continue
    sock.send(b"USERNAME")
    user=sock.recv(BUFFER_SIZE).decode().strip()
# ============================================
# Prevent Duplicate Login
# ============================================
    if find_user(user):
       write_security_log(event="DUPLICATE LOGIN BLOCKED",username=user,ip=addr[0])
       sock.send(b"DUPLICATE_LOGIN")
       sock.close()
       continue

    sock.send(b"LOGIN_SUCCESS")
    clients[user]={"socket":sock,"ip":addr[0],"port":addr[1],"login_time":datetime.now().strftime("%H:%M:%S"),"status":"Online"}
    write_security_log(event="LOGIN SUCCESS",username=user,ip=addr[0])
    write_log("CONNECTED",user,addr[0])
    save_history("SYSTEM", "SERVER" , "ALL" ,f"{user} joined the chat")
    broadcast(f"*** {user} joined the chat ***",exclude=user,system=True)
    stats()
    update_online_users()
    threading.Thread(target=handle,args=(sock,user),daemon=True).start()
