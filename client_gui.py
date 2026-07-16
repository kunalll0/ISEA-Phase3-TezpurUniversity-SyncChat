import socket
import threading
import time
import tkinter as tk
import csv
import hashlib
import os
import re
from datetime import datetime
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText


# ============================================
# User Database
# ============================================

USERS_FILE = "users.csv"

if not os.path.exists(USERS_FILE):

    with open(USERS_FILE, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "username",
            "password_hash"
        ])

# ============================================
# GUI LOGIN WINDOW - VERSION 1
# ============================================

root = tk.Tk()

root.title("SyncChat")
root.geometry("600x420")
root.resizable(False, False)


# Center Window
window_width = 560
window_height = 460

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))

root.geometry(f"{window_width}x{window_height}+{x}+{y}")


# ============================================
# Variables
# ============================================

username_var = tk.StringVar()
password_var = tk.StringVar()
signup_username_var = tk.StringVar()
signup_password_var = tk.StringVar()
signup_confirm_var = tk.StringVar()
signup_strength_var = tk.StringVar(value="")
server_ip_var = tk.StringVar(value="10.0.0.1")
PORT = 5000
MAX_MESSAGE_LENGTH = 500
SECURITY_LOG_FILE = "security_log.txt"
client = None
chat_window = None
chat_box = None
message_entry = None
online_users = None
status_label = None
failed_attempts = 0
lockout_until = 0
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = 30
SESSION_TIMEOUT = 600
last_activity_time = time.time()
timeout_job = None
# ============================================
# Functions
# ============================================

def connect_server():
    global client
    global failed_attempts
    global lockout_until
    global timeout_job
    username = username_var.get().strip()
    password = password_var.get()
    server_ip = server_ip_var.get().strip()
    password_hash = hash_password(password)

    current_time = time.time()
    if current_time < lockout_until:
        remaining = int(lockout_until - current_time)
        messagebox.showerror(
            "Login Temporarily Locked",
            f"Too many failed login attempts.\n\nPlease try again in {remaining} seconds."
        )

        return
    if username == "":
        messagebox.showerror(
            "Error",
            "Username cannot be empty."
        )
        return

    if password == "":
        messagebox.showerror(
            "Password Required",
            "Please enter your password."
        )
        return

    if server_ip == "":
        messagebox.showerror(
            "Error",
            "Server IP cannot be empty."
        )
        return
# ============================================
# Authenticate User
# ============================================

    authenticated = False
    with open(USERS_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if (
                row["username"].lower() == username.lower()
                and
                row["password_hash"] == password_hash
            ):
                authenticated = True
                break
    if not authenticated:
        failed_attempts += 1
        if failed_attempts >= MAX_FAILED_ATTEMPTS:
            lockout_until = time.time() + LOCKOUT_DURATION
            failed_attempts = 0
            write_security_log(event="ACCOUNT LOCKED",username=username,details=f"{MAX_FAILED_ATTEMPTS} failed login attempts")
            messagebox.showerror(
                "Too Many Login Attempts",
                f"PLease try again in {LOCKOUT_DURATION} seconds."
            )
        else:
            remaining = MAX_FAILED_ATTEMPTS - failed_attempts
            write_security_log(event="FAILED LOGIN",username=username,details="Invalid username or password")
            messagebox.showerror(
            "Login Failed",
            f"Invalid username or password.\n\nRemaining attempts: {remaining}"
            )
        password_var.set("")
        password_entry.focus()
        return

    failed_attempts = 0
    try:
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.connect((server_ip, PORT))
        response = client.recv(1024).decode()

        if response == "USERNAME":
            client.send(username.encode())
            response = client.recv(1024).decode()

            if response == "DUPLICATE_LOGIN":
                messagebox.showerror(
                    "Already Logged In",
                    "This account is already logged in.\n\nPlease logout first."
                )
                username_var.set("")
                password_var.set("")
                password_entry.focus()
                client.close()
                return

        elif response != "LOGIN_SUCCESS":
                messagebox.showerror(
                    "Login Failed",
                    "Unexpected server response."
                )
                client.close()
                return


        messagebox.showinfo("Connected",
        f"Successfully connected to \n {server_ip}:5000" )
        root.withdraw()
        update_activity()
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
    chat_window.protocol(
        "WM_DELETE_WINDOW",
        exit_application
    )
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
    message_entry.bind("<Key>",lambda event: update_activity())
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

def toggle_password():

    if password_entry.cget("show") == "*":

        password_entry.config(show="")

        eye_button.config(text="Hide")

    else:

        password_entry.config(show="*")

        eye_button.config(text="Show")

def update_activity():
    global last_activity_time
    last_activity_time = time.time()

def check_session_timeout():

    global last_activity_time
    global chat_window

    try:

        if chat_window is not None and chat_window.winfo_exists():

            current_time = time.time()

            if current_time - last_activity_time >= SESSION_TIMEOUT:
                update_activity()      # Prevent repeated popups
                write_security_log( event="SESSION TIMEOUT",username=username_var.get().strip(),details="Logged out due to inactivity")          
                messagebox.showwarning(
                    "Session Expired",
                    "You have been logged out due to inactivity."
                )

                exit_application()

    except tk.TclError:
        pass

    root.after(1000, check_session_timeout)

def send_message(event=None):

    global client
    global message_entry
    msg = message_entry.get().strip()
    username = username_var.get().strip()
    # Empty message
    if msg == "":
        return
    # Placeholder text
    if msg == "Type a message...":
        return
# Maximum length check
    if len(msg) > MAX_MESSAGE_LENGTH:
        messagebox.showerror(
            "Message Too Long",
            f"The Maximum allowed message length is {MAX_MESSAGE_LENGTH} characters."
        )
        message_entry.focus()
        return

    try:
        update_activity()
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


def hash_password(password):

    return hashlib.sha256(password.encode()).hexdigest()

# ============================================
# SECURITY LOG
# ============================================

def write_security_log(event,username="",details=""):
    with open(SECURITY_LOG_FILE, "a") as file:
        file.write(
            f"Time      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        file.write(
            "Source    : CLIENT\n"
        )
        file.write(
            f"Event     : {event}\n"
        )
        if username:
            file.write(
                f"Username  : {username}\n"
            )
        if details:
            file.write(
                f"Details   : {details}\n"
            )
        file.write("=" * 60 + "\n")

def signup_window():

    signup = tk.Toplevel(root)
    signup.title("Create SyncChat Account")
    signup.geometry("560x460")
    signup.resizable(False, False)
    signup.configure(bg="#f4f6f9")
    signup.transient(root)
    signup.grab_set()

    # ----------------------------
    # Center Window
    # ----------------------------
    window_width = 560
    window_height = 460

    screen_width = signup.winfo_screenwidth()
    screen_height = signup.winfo_screenheight()

    x = int((screen_width - window_width) / 2) 
    y = int((screen_height - window_height) / 2)

    signup.geometry(f"{window_width}x{window_height}+{x}+{y}")


    def create_account():
        username = signup_username_var.get().strip()
        password = signup_password_var.get()
        confirm_password = signup_confirm_var.get()
        if username == "":
             messagebox.showerror("Username Required","Please enter a username.")
             return
        if not re.fullmatch(r"[A-Za-z0-9_.]+", username):
            messagebox.showerror(
                "Invalid Username",
                "Username can contain only:\n\n"
                "• Letters (A-Z, a-z)\n"
                "• Numbers (0-9)\n"
                "• Underscore (_)\n"
                "• Dot (.)"
            )
            return
        if password == "":
            messagebox.showerror(
                "Password Required",
                "Please enter a password."
            )
            return
        if confirm_password == "":
            messagebox.showerror(
                "Confirm Password",
                "Please confirm your password."
            )
            return
        if password != confirm_password:
            messagebox.showerror(
                "Password Mismatch",
                "Password and Confirm Password do not match."
            )
            return
        with open(USERS_FILE, "r", newline="") as file:

            reader = csv.DictReader(file)
            for row in reader:
                if row["username"].lower() == username.lower():
                   messagebox.showerror(
                       "Username Already Exists",
                       "This username is already registered.\n\nPlease choose a different username."
                   )
                   return

        password_hash = hash_password(password)
        with open(USERS_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                username,
                password_hash
            ])
        write_security_log(event="ACCOUNT CREATED",username=username)
        messagebox.showinfo(
            "Account Created",
            "Your SyncChat account has been created successfully!"
        )
        signup_username_var.set("")
        signup_password_var.set("")
        signup_confirm_var.set("")
        signup_strength_var.set("")
        signup.destroy()
    # ----------------------------
    # Local Toggle Functions
    # ----------------------------

    def toggle_signup_password():

        if signup_password_entry.cget("show") == "*":
            signup_password_entry.config(show="")
            signup_show_btn.config(text="Hide")
        else:
            signup_password_entry.config(show="*")
            signup_show_btn.config(text="Show")

    def toggle_confirm_password():

        if signup_confirm_entry.cget("show") == "*":
            signup_confirm_entry.config(show="")
            signup_confirm_show_btn.config(text="Hide")
        else:
            signup_confirm_entry.config(show="*")
            signup_confirm_show_btn.config(text="Show")

    def check_password_strength(event=None):

        password = signup_password_var.get()

        if password == "":
            signup_strength_var.set("")
            return

        password = signup_password_var.get()

        score = 0

        if len(password) >= 8:
            score += 1

        if any(c.isupper() for c in password):
            score += 1

        if any(c.islower() for c in password):
            score += 1

        if any(c.isdigit() for c in password):
            score += 1

        if any(c in "!@#$%^&*()_+-=[]{}|;:',.<>?/`~" for c in password):
            score += 1

        if score <= 2:
            signup_strength_var.set("Weak Password")
            strength_label.config(fg="red")

        elif score == 3 or score == 4:
            signup_strength_var.set("Medium Password")
            strength_label.config(fg="orange")

        else:
            signup_strength_var.set("Strong Password")
            strength_label.config(fg="green")


    # ----------------------------
    # Heading
    # ----------------------------

    title = tk.Label(
        signup,
        text="Create SyncChat Account",
        font=("Segoe UI",22,"bold"),
        fg="navy",
        bg="#f4f6f9"
    )

    title.pack(pady=(28,8))

    subtitle = tk.Label(
        signup,
        text="Create a new account to access SyncChat",
        font=("Segoe UI",10),
        fg="gray40",
        bg="#f4f6f9"
    )

    subtitle.pack(pady=(0,28))

    # ----------------------------
    # Form
    # ----------------------------

    form = tk.Frame(signup,bg="#f4f6f9")
    form.pack(pady=10, padx=15)

    # Username
    tk.Label(
        form,
        text="Username :",
        font=("Segoe UI",10),
        bg="#f4f6f9"
    ).grid(row=0,column=0,padx=10,pady=10,sticky="e")

    signup_username_entry = tk.Entry(
        form,
        width=34,
        font=("Segoe UI",10),
        textvariable=signup_username_var,
        bg="#fcfcfc",
        highlightthickness=0
    )

    signup_username_entry.grid(row=0,column=1,sticky="w")

    # Password

    tk.Label(
        form,
        text="Password :",
        font=("Segoe UI",10),
        bg="#f4f6f9"
    ).grid(row=1,column=0,padx=10,pady=10,sticky="e")

    signup_password_entry = tk.Entry(
        form,
        width=34,
        font=("Segoe UI",10),
        textvariable=signup_password_var,
        show="*",
        bg="#fcfcfc",
        highlightthickness=0
    )

    signup_password_entry.grid(row=1,column=1,sticky="w")
    signup_password_entry.bind("<KeyRelease>",check_password_strength)
    signup_show_btn = tk.Button(
        form,
        text="Show",
        width=4,
        font=("Segoe UI",9),
        bg="#f0f0f0",
        fg="black",
        activebackground="#d9d9d9",
        cursor="hand2",
        command=toggle_signup_password
    )

    signup_show_btn.grid(row=1,column=2,padx=(8,0))

    strength_label = tk.Label(
        form,
        textvariable=signup_strength_var,
        font=("Segoe UI",9,"bold"),
        fg="red",
        bg="#f4f6f9"
    )

    strength_label.grid(
        row=2,
        column=1,
        sticky="w",
        padx=(15,0),
        pady=(3,8)
    )

    # ============================================
# Buttons
# ============================================
    # Confirm Password

    tk.Label(
        form,
        text="Confirm Password :",
        font=("Segoe UI",10),
        bg="#f4f6f9"
    ).grid(row=3,column=0,padx=10,pady=10,sticky="e")

    signup_confirm_entry = tk.Entry(
        form,
        width=34,
        font=("Segoe UI",10),
        textvariable=signup_confirm_var,
        show="*",
        bg="#fcfcfc",
        highlightthickness=0
    )

    signup_confirm_entry.grid(row=3,column=1,sticky="w")

    signup_confirm_show_btn = tk.Button(
        form,
        text="Show",
        width=4,
        font=("Segoe UI",9),
        bg="#f0f0f0",
        fg="black",
        activebackground="#d9d9d9",
        cursor="hand2",
        command=toggle_confirm_password
    )

    signup_confirm_show_btn.grid(row=3,column=2,padx=(8,0))
    # ============================================
# Buttons
# ============================================

    button_frame = tk.Frame(
        signup,
        bg="#f4f6f9"
    )

    button_frame.pack(pady=(15,12))
    footer = tk.Label(
        signup,
        text="SyncChat v2.0 – Secure Edition • © 2026 Kunal Prajapati",
        font=("Arial",9),
        fg="gray",
        bg="#f4f6f9"
    )

    footer.pack(side="bottom", pady=(8,10))

    create_btn = tk.Button(
        button_frame,
        text="Create Account",
        width=16,
        font=("Segoe UI",10,"bold"),
        pady=4,
        bg="#1565c0",
        fg="white",
        activebackground="#0d47a1",
        activeforeground="white",
        cursor="hand2",
        command=create_account
    )

    create_btn.grid(row=0,column=0,padx=8)

    cancel_btn = tk.Button(
        button_frame,
        text="Cancel",
        width=16,
        font=("Segoe UI",10,"bold"),
        pady=4,
        bg="#e0e0e0",
        activebackground="#cfcfcf",
        cursor="hand2",
        command=signup.destroy
    )

    cancel_btn.grid(row=0,column=1,padx=8)

    signup_username_entry.focus()
    signup.bind("<Return>",lambda event: create_account())
    signup.bind("<Escape>",lambda event: signup.destroy())

def exit_application():
    global client
    global chat_window
    global timeout_job
    try:
        if client:
            # Tell server we are logging out
            client.send(b"LOGOUT")
            client.shutdown(socket.SHUT_RDWR)
            client.close()
    except:
        pass
    # Close chat window
    if timeout_job:
        root.after_cancel(timeout_job)
        timeout_job = None
    chat_window.destroy()
    # Show login window again
    root.deiconify()
    # Clear login fields
    password_var.set("")
    username_entry.focus()

# ============================================
# Title
# ============================================

title = tk.Label(
    root,
    text= "SYNCCHAT",
    font=("Segoe UI",22,"bold"),
    fg="navy"
)

title.pack(pady=(25,10))


subtitle = tk.Label(
    root,
    text="Powered by TCP Socket Programming",
    font=("Segoe UI", 10)
)

subtitle.pack(pady=(0,20))

# ============================================
# Login Frame
# ============================================

frame = tk.Frame(root)

frame.pack(pady=10)

tk.Label(
    frame,
    text="Username :",
    font=("Segoe UI", 10)
).grid(row=0, column=0, padx=10, pady=10, sticky="e")

username_entry = tk.Entry(
    frame,
    width=34,
    textvariable=username_var,
    font=("Segoe UI",10)
)

username_entry.grid(row=0, column=1)


tk.Label(
    frame,
    text="Password :",
    font=("Segoe UI", 10)).grid(row=1, column=0, padx=10, pady=10, sticky="e")

password_entry = tk.Entry(
    frame,
    width=34,
    textvariable=password_var,
    show="*",
    font=("Segoe UI",10)
)

password_entry.grid(row=1, column=1)

eye_button = tk.Button(
    frame,
    text="Show",
    width=4,
    font=("Segoe UI",9),
    command=toggle_password
)

eye_button.grid(row=1,column=2,padx=(1,0), sticky="w")

tk.Label(
    frame,
    text="Server IP :",
    font=("Segoe UI",10)
).grid(row=2, column=0, padx=10, pady=10, sticky="e")

server_entry = tk.Entry(
    frame,
    width=34,
    textvariable=server_ip_var,
    font=("Segoe UI",10)
)

server_entry.grid(row=2, column=1)


# ============================================
# Buttons
# ============================================

button_frame = tk.Frame(root)

button_frame.pack(pady=35)


connect_button = tk.Button(
    button_frame,
    text="Login",
    width=16,
    font=("Segoe UI",10,"bold"),
    pady=4,
    bg="#1565c0",
    fg="white",
    activebackground="#0d47a1",
    activeforeground="white",
    cursor="hand2",
    command=connect_server
)

connect_button.grid(row=0, column=0, padx=10)


signup_button = tk.Button(
    button_frame,
    text="Sign Up",
    width=16,
    font=("Segoe UI",10,"bold"),
    pady=4,
    bg="#2e7d32",
    fg="white",
    activebackground="#1b5e20",
    activeforeground="white",
    cursor="hand2",
    command=signup_window
)

signup_button.grid(row=0, column=1, padx=10)

root.bind("<Return>", lambda event: connect_server())

# ============================================
# Footer
# ============================================

footer = tk.Label(
    root,
    text="SyncChat v2.0 – Secure Edition • © 2026 Kunal Prajapati",
    font=("Arial", 9),
    fg="gray"
)

footer.pack(side="bottom", pady=12)


username_entry.focus()
check_session_timeout()
root.mainloop()
