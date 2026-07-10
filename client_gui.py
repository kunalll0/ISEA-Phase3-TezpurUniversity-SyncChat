import socket
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

# ============================================
# GUI LOGIN WINDOW - VERSION 1
# ============================================

root = tk.Tk()

root.title("SyncChat")
root.geometry("600x420")
root.resizable(False, False)


# Center Window
window_width = 500
window_height = 350

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))

root.geometry(f"{window_width}x{window_height}+{x}+{y}")


# ============================================
# Variables
# ============================================

username_var = tk.StringVar()
server_ip_var = tk.StringVar(value="10.0.0.1")
PORT = 5000
client = None
chat_window = None
chat_box = None
message_entry = None
online_users = None
status_label = None

# ============================================
# Functions
# ============================================

def connect_server():

    global client

    username = username_var.get().strip()
    server_ip = server_ip_var.get().strip()

    if username == "":
        messagebox.showerror(
            "Error",
            "Username cannot be empty."
        )
        return

    if server_ip == "":
        messagebox.showerror(
            "Error",
            "Server IP cannot be empty."
        )
        return

    try:

        client = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        client.connect(
            (server_ip, PORT)
        )

        response = client.recv(1024).decode()

        if response == "USERNAME":

            client.send(
                username.encode()
            )

        messagebox.showinfo("Connected", 
        f"Successfully connected to \n {server_ip}:5000" )

        root.withdraw()

        open_chat_window(username)
        threading.Thread(
            target=receive,
            daemon=True
        ).start()

    except Exception as e:

        messagebox.showerror(
            "Connection Failed",
            str(e)
        )

def open_chat_window(username):

    global chat_window
    global chat_box
    global message_entry
    global online_users 
    global status_label

    chat_window = tk.Toplevel()

    chat_window.title("SyncChat")

    chat_window.geometry("1050x750")
    chat_window.minsize(1050, 750)
    chat_window.configure(bg="#f4f6f9")
    chat_window.resizable(True, True)
    window_width = 1050
    window_height = 750

    screen_width = chat_window.winfo_screenwidth()
    screen_height = chat_window.winfo_screenheight()

    x = int((screen_width - window_width) / 2)
    y = int((screen_height - window_height) / 2)

    chat_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    chat_window.minsize(window_width, window_height)
    # =====================================
# HEADER
# =====================================

    header_frame = tk.Frame(chat_window, bg="#f4f6f9")
    header_frame.pack(fill="x", pady=(12,5))

    title = tk.Label(
        header_frame,
        text="SYNCCHAT",
        font=("Segoe UI",24,"bold"),
        fg="#0d47a1",
        bg="#f4f6f9"
    )

    title.pack(pady=(5,0))

    subtitle = tk.Label(
        header_frame,
        text="Powered by TCP Socket Programming",
        font=("Segoe UI",10),
        fg="gray40",
        bg="#f4f6f9"
    )

    subtitle.pack(pady=(3,8))

# =====================================
# STATUS BAR
# =====================================

    status_frame = tk.Frame(chat_window, bg="#f4f6f9")
    status_frame.pack(fill="x", padx=25, pady=(2,10))

    status_label = tk.Label(
        status_frame,
        text="🟢 Connected",
        font=("Segoe UI",10,"bold"),
        fg="green",
        bg="#f4f6f9"
    )

    status_label.pack(side="left")

    user_label = tk.Label(
        status_frame,
        text=f"👤 @{username}",
        font=("Segoe UI",10,"bold"),
        fg="#1565c0",
        bg="#f4f6f9"
    )

    user_label.pack(side="right")

    main_frame = tk.Frame(chat_window, bg="#f4f6f9")

    main_frame.pack(fill="both",expand=True,padx=10,pady=10)

    conversation_frame = tk.LabelFrame(main_frame,text=" Conversation ", font=("Segoe UI",10,"bold"),padx=5,pady=5)

    conversation_frame.pack(side="left",fill="both",expand=True,padx=(0,8), pady=(0,5))

    users_frame = tk.LabelFrame(main_frame,text=" Online Users ",font=("Segoe UI",10,"bold"),width=170,padx=5,pady=5)
    users_frame.pack(side="right",fill="y",padx=(10,0))

    users_frame.pack_propagate(False)

    chat_box = ScrolledText(conversation_frame,font=("Consolas",12),wrap="word", state="disabled", relief="flat",borderwidth=0)
    chat_box.pack(fill="both",expand=True, padx=5, pady=5)

# =====================================
# Chat Styles
# =====================================

    chat_box.tag_config(
        "system",
        foreground="green",
        font=("Arial",11,"bold")
    )

    chat_box.tag_config(
        "private",
        foreground="purple",
        font=("Arial",11,"bold")
    )

    chat_box.tag_config(
        "normal",
        foreground="blue",
        font=("Arial",11,"bold")
    )

    chat_box.tag_config(
        "message",
        foreground="black",
        font=("Consolas",11)
    )

    chat_box.tag_config(
        "space",
        spacing3=8
    )

#    tk.Label(

#        users_frame,

#        text="Online Users",

#        font=("Arial",12,"bold")

#    ).pack(pady=5)

    online_users = tk.Listbox(
        users_frame,
        width=18,
        height=20,
        font=("Segoe UI",10),
        activestyle="none",
        relief="flat",
        borderwidth=0,
        exportselection=False,
        selectbackground="#dbeafe",
        selectforeground="black"
    )

    online_users.pack(
        fill="both",
        expand=True,
        padx=5,
        pady=5
    )

    online_users.insert(tk.END,username)

    bottom = tk.Frame(chat_window, bg="#f4f6f9")

    bottom.pack(fill="x",padx=10,pady=10)

    message_entry = tk.Entry(

        bottom,

        font=("Arial",11),

        fg="gray"

    )

    message_entry.insert(0, "Type a message...")

    message_entry.pack(side="left",fill="x",expand=True,padx=5, ipady=6)
    message_entry.bind("<FocusIn>", clear_placeholder)
    message_entry.bind("<FocusOut>", add_placeholder)

    send_btn = tk.Button(
        bottom,
        text="Send",
        width=12,
        font=("Segoe UI",10),
        padx=10,
        pady=2,
        command = send_message
    )

    message_entry.bind("<Return>", send_message)
    send_btn.pack(side="left",padx=6)

    disconnect_btn = tk.Button(
        bottom,
        text="Disconnect",
        width=12,
        font=("Segoe UI",10),
        padx=10,
        pady=2,
        command=exit_application
    )
    disconnect_btn.pack(side="left", padx=6)

# ============================================
# Chat Window Footer
# ============================================

    footer_frame = tk.Frame(chat_window, bg="#f4f6f9")
    footer_frame.pack(fill="x")

    footer = tk.Label(
        footer_frame,
        text="SyncChat v1.0 • © 2026 Kunal Prajapati",
        font=("Segoe UI",8),
        fg="gray50",
        bg="#f4f6f9"
    )

    footer.pack(pady=(3,5))

def clear_placeholder(event):

    if message_entry.get() == "Type a message...":

        message_entry.delete(0, tk.END)

        message_entry.config(fg="black")

def add_placeholder(event):

    if message_entry.get().strip() == "":

        message_entry.delete(0, tk.END)

        message_entry.insert(0, "Type a message...")

        message_entry.config(fg="gray")


def send_message(event=None):

    global client
    global message_entry

    msg = message_entry.get().strip()
    username = username_var.get().strip()
    if msg == "" or msg == "Enter your message...":
        return

    try:
        client.send(msg.encode())

        message_entry.delete(0, tk.END)
        message_entry.focus()

    except Exception as e:

        print("Send Error :", e)

def receive():

    global chat_box
    global client
    global online_users
    global status_label

    while True:

        try:

            msg = client.recv(4096).decode()
            if msg.startswith("USERS:"):

                users = msg.replace("USERS:", "").split(",")
                current_user = username_var.get().strip()

                if current_user in users:
                   users.remove(current_user)

                users.insert(0, current_user)
                online_users.delete(0, tk.END)

                for user in users:

                    if user.strip():

                        online_users.insert(tk.END, user)
                online_users.selection_clear(0, tk.END)
                online_users.selection_set(0)
                online_users.activate(0)
                online_users.see(0)
                continue

            if not msg:
                break

            current_time = datetime.now().strftime("%H:%M:%S")

            chat_box.config(state="normal")

# -------------------------------
# SYSTEM MESSAGE
# -------------------------------

            if msg.startswith("***") or msg.startswith("SERVER"):

                 chat_box.insert(
                     "end",
                     f"SYSTEM  |  {current_time}\n",
                     "system"
                 )

                 chat_box.insert(
                     "end",
                     msg + "\n\n",
                     "message"
                 )

# -------------------------------
# PRIVATE MESSAGE
# -------------------------------

            elif msg.startswith("[PRIVATE]"):

                sender = msg.replace("[PRIVATE]", "").split(":", 1)[0].strip()

                text = msg.split(":", 1)[1].strip()

                chat_box.insert(
                    "end",
                    f"PRIVATE ← {sender}  |  {current_time}\n",
                    "private"
                )

                chat_box.insert(
                    "end",
                    text + "\n\n",
                    "message"
                )

            elif msg.startswith("[PRIVATE to"):

                receiver = msg.split("]")[0].replace("[PRIVATE to", "").strip()

                text = msg.split("]", 1)[1].strip()

                chat_box.insert(
                    "end",
                    f"PRIVATE → {receiver}  |  {current_time}\n",
                    "private"
                )

                chat_box.insert(
                    "end",
                    text + "\n\n",
                    "message"
                )

# -------------------------------
# NORMAL CHAT MESSAGE
# -------------------------------

            elif msg.startswith("["):

                sender = msg.split("]")[0].replace("[", "").strip()

                text = msg.split("]", 1)[1].strip()
                display_name = sender
                if sender == username_var.get().strip():
                    display_name = "You"

                chat_box.insert(
                    "end",
                    f"{display_name}  |  {current_time}\n",
                    "normal"
                )

                chat_box.insert(
                    "end",
                     text + "\n\n",
                    "message"
                )

# -------------------------------
# OTHER OUTPUT
# -------------------------------

            else:

                chat_box.insert(
                    "end",
                    msg + "\n\n"
                )

            chat_box.see("end")

            chat_box.config(state="disabled")

        except Exception as e:

            print("Receive Error :", e)
            if status_label:
                status_label.config(
                    text="Status : Disconnected",
                    fg="red"
                )
            client.close()
            break


def exit_application():

    global client

    try:
        if client:
            client.close()
    except:
        pass

    root.destroy()

# ============================================
# Title
# ============================================

title = tk.Label(
    root,
    text= "SYNCCHAT",
    font=("Arial", 18, "bold"),
    fg="navy"
)

title.pack(pady=20)


subtitle = tk.Label(
    root,
    text="Powered by TCP Socket Programming",
    font=("Arial", 11)
)

subtitle.pack()

# ============================================
# Login Frame
# ============================================

frame = tk.Frame(root)

frame.pack(pady=25)


tk.Label(
    frame,
    text="Username :",
    font=("Arial", 11)
).grid(row=0, column=0, padx=10, pady=10, sticky="e")

username_entry = tk.Entry(
    frame,
    width=28,
    textvariable=username_var
)

username_entry.grid(row=0, column=1)



tk.Label(
    frame,
    text="Server IP :",
    font=("Arial", 11)
).grid(row=1, column=0, padx=10, pady=10, sticky="e")

server_entry = tk.Entry(
    frame,
    width=32,
    textvariable=server_ip_var
)

server_entry.grid(row=1, column=1)


# ============================================
# Buttons
# ============================================

button_frame = tk.Frame(root)

button_frame.pack(pady=35)


connect_button = tk.Button(
    button_frame,
    text="Connect",
    width=18,
    command=connect_server
)

connect_button.grid(row=0, column=0, padx=10)


exit_button = tk.Button(
    button_frame,
    text="Exit",
    width=18,
    command=exit_application
)

exit_button.grid(row=0, column=1, padx=10)

root.bind("<Return>", lambda event: connect_server())

# ============================================
# Footer
# ============================================

footer = tk.Label(
    root,
    text="SyncChat v1.0 • © 2026 Kunal Prajapati",
    font=("Arial", 9),
    fg="gray"
)

footer.pack(side="bottom", pady=12)


username_entry.focus()

root.mainloop()
