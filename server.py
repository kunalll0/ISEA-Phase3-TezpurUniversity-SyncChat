import socket
import threading
import csv
import os
from datetime import datetime

HOST="0.0.0.0"
PORT=5000

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

print("Advanced Chat Server started on port",PORT)



CHAT_HISTORY_FILE = "chat_history.csv"

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
        

def write_log(event,user="",detail=""):
    with open("chat_log.txt","a") as f:
        t=datetime.now().strftime("%H:%M:%S")
        f.write(f"{t},{event},{user},{detail}\n")

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
    for u,d in clients.items():
        if d["socket"]==sock:
            victim=u
            break
    if victim:
        del clients[victim]
        write_log("DISCONNECTED",victim)
        save_history("SYSTEM","SERVER","ALL",f"{victim} left the chat")
        broadcast(f"*** {victim} left the chat ***",system=True)
        stats()
        update_online_users()

def handle(sock,user):
    while True:
        try:
            text=sock.recv(1024).decode()
            if not text:
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

        except Exception as e :
            print(f"Handle Error : {e}")
            remove(sock)
            break

while True:
    sock,addr=server.accept()
    sock.send(b"USERNAME")
    user=sock.recv(1024).decode().strip()
    clients[user]={"socket":sock,"ip":addr[0],"port":addr[1],"login_time": datetime.now().strftime("%H:%M:%S"), "status": "Online"}
    write_log("CONNECTED",user,addr[0])
    save_history("SYSTEM", "SERVER" , "ALL" ,f"{user} joined the chat")
    broadcast(f"*** {user} joined the chat ***",exclude=user,system=True)
    stats()
    update_online_users()
    threading.Thread(target=handle,args=(sock,user),daemon=True).start()
