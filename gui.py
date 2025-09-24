import cv2
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from PIL import Image, ImageTk
import pandas as pd
import os
import main  # backend with process_frame

SNAPSHOT_FOLDER = "logs"  # Folder to store snapshots
ArgusLog_FILE = "assets/ArgusLog.csv"  # Path to ArgusLog CSV

class ArgusGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Argus - Live Feed")  # Window title
        self.root.minsize(1200, 700)  # Fixed minimum size, prevents resizing smaller
        self.running = False  # Webcam running state
        self.cap = cv2.VideoCapture(0)  # Default webcam, initialized on Start

        # ---------------- Top Camera Selection ----------------
        cam_frame = tk.Frame(root, bg="#2e2e2e")  # Camera selection frame background
        cam_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)  # Pack at top, fill X
        tk.Label(cam_frame, text="Select Camera:", bg="#2e2e2e", fg="white").pack(side=tk.LEFT)  # Label
        self.cam_index = tk.IntVar(value=0)  # Default camera index
        self.cam_dropdown = ttk.Combobox(cam_frame, values=[0,1,2,3], width=5, textvariable=self.cam_index)
        self.cam_dropdown.pack(side=tk.LEFT, padx=5)  # Dropdown for camera selection
        tk.Button(cam_frame, text="Set Camera", command=self.set_camera, bg="#3b3b3b", fg="white",
                  font=("Arial",10,"bold")).pack(side=tk.LEFT)  # Button to apply selected camera

        # ---------------- Main Content ----------------
        main_frame = tk.Frame(root, bg="#1e1e1e")  # Main container frame
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  # Fill both directions

        # --- Webcam frame (2/3 width) ---
        video_frame = tk.Frame(main_frame, bg="black")  # Video container
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)  # Pack left, expand
        video_frame.pack_propagate(False)  # Reserve space before Start
        self.display_width = 800  # Width of webcam display
        self.display_height = 600  # Height of webcam display
        self.video_label = tk.Label(video_frame, bg="black")  # Label to display webcam frames
        self.video_label.pack(fill=tk.BOTH, expand=True)  # Expand to fill video_frame

        # --- Logs panel (1/3 width) ---
        side_panel = tk.Frame(main_frame, width=400, bg="#2e2e2e")  # Logs container
        side_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)  # Pack right, vertical fill
        side_panel.pack_propagate(False)  # Fix width
        tk.Label(side_panel, text="Detection Logs:", bg="#2e2e2e", fg="white").pack()  # Logs label
        self.log_text = scrolledtext.ScrolledText(side_panel, width=50, height=35,
                                                  bg="#1e1e1e", fg="white", font=("Consolas", 10),  # Font can be adjusted here
                                                  state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True)  # Fill panel
        self.status_canvas = tk.Canvas(side_panel, width=20, height=20, highlightthickness=0, bg="#2e2e2e")
        self.status_canvas.pack(pady=5)  # Status dot canvas
        self.status_dot = self.status_canvas.create_oval(5,5,15,15, fill="red")  # Red dot indicates paused

        # ---------------- Bottom Buttons ----------------
        btn_frame = tk.Frame(root, bg="#2e2e2e")  # Bottom buttons container
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)  # Pack bottom, fill X
        for txt, cmd in [("Start", self.start), ("Pause", self.pause),
                         ("Open Snapshots", self.open_snapshots), ("Open ArgusLog CSV", self.open_ArgusLog),
                         ("Clear Logs", self.clear_logs), ("Exit", self.exit)]:
            tk.Button(btn_frame, text=txt, command=cmd, bg="#3b3b3b", fg="white",
                      font=("Arial",10,"bold")).pack(side=tk.LEFT, padx=5)  # Buttons in bottom frame

        # ---------------- Start CSV Auto Refresh ----------------
        self.update_logs_from_csv()  # Automatically refresh log panel every 2 seconds

    # ---------------- Camera Control ----------------
    def set_camera(self):
        index = self.cam_index.get()
        self.cap.release()
        self.cap = cv2.VideoCapture(index)  # Switch to selected camera
        self.log(f"Switched to camera {index}")  # Log change

    # ---------------- Start / Pause / Exit ----------------
    def start(self):
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.cam_index.get())  # Initialize webcam if not open
        self.running = True
        self.status_canvas.itemconfig(self.status_dot, fill="green")  # Green dot for running
        self.update_frame()
        self.log("\nWebcam started")  # Log action

    def pause(self):
        self.running = False
        self.status_canvas.itemconfig(self.status_dot, fill="red")  # Red dot for paused
        self.log("\nWebcam paused")

    def exit(self):
        self.running = False
        self.cap.release()  # Release webcam
        self.root.destroy()  # Close window

    # ---------------- Open Files ----------------
    def open_snapshots(self):
        path = os.path.abspath(SNAPSHOT_FOLDER)  # Absolute path
        if os.path.exists(path):
            os.startfile(path)  # Open folder
        else:
            self.log(f"Snapshots folder not found: {path}")

    def open_ArgusLog(self):
        path = os.path.abspath(ArgusLog_FILE)  # Absolute path
        if os.path.exists(path):
            os.startfile(path)  # Open CSV
        else:
            self.log(f"ArgusLog file not found: {path}")

    # ---------------- Logging ----------------
    def log(self, text):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{text}\n")  # Append log
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def clear_logs(self):
        import csv
        with open(ArgusLog_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Name","Timestamp","Confidence"])  # Reset CSV header
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.insert(tk.END, "Logs cleared (header preserved).\n")  # GUI log reset
        self.log_text.config(state='disabled')
        self.update_logs_from_csv()  # Refresh logs

    # ---------------- Frame Update ----------------
    def update_frame(self):
        if self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = main.process_frame(frame)  # Process frame from backend
                h, w = frame.shape[:2]
                scale = min(self.display_width/w, self.display_height/h)  # Keep aspect ratio
                frame = cv2.resize(frame, (int(w*scale), int(h*scale)))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk  # Assign to label
                self.video_label.config(image=imgtk)
            self.video_label.after(15, self.update_frame)  # Refresh every ~15ms

    # ---------------- CSV Auto Refresh ----------------
    def update_logs_from_csv(self):
        try:
            df = pd.read_csv(ArgusLog_FILE)  # Read CSV
            self.log_text.config(state='normal')
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, df.to_string(index=False))  # Display CSV in log panel
            self.log_text.config(state='disabled')
        except Exception as e:
            self.log_text.config(state='normal')
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, f"⚠ Error loading ArgusLog.csv\n{e}")  # Error display
            self.log_text.config(state='disabled')
        self.root.after(2000, self.update_logs_from_csv)  # Refresh every 2s

    def pause(self):
        self.running = False
        self.status_canvas.itemconfig(self.status_dot, fill="red")
        main.stop_alarm()  # 🔴 force stop alarm when webcam is paused
        self.log("\nWebcam paused")

    def exit(self):
        self.running = False
        main.stop_alarm()  # 🔴 also stop alarm before closing
        self.cap.release()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ArgusGUI(root)
    root.mainloop()
