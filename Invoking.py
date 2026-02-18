import tkinter as tk
from tkinter import messagebox
import threading
import queue
# import serial   # Uncomment when hardware connected


PAGE_TITLE = "MANUAL POWER WINDOW"


LAYOUT = [
    [("btn","EXT SUPPLY"), ("lbl","Ext voltage(V)"), ("ent",""), ("lbl","UMB1 STATUS"), ("ent","open")],
    [("btn","SAM COIL"), ("lbl","Ext current(A)"), ("ent",""), ("lbl","SAM relay"), ("ent","open")],
    [("btn","OBP"), ("lbl","int voltage(V)"), ("ent",""), ("lbl","OBP LINK"), ("ent","down")],
    [("btn","CGU"), ("lbl","Pressure switch"), ("ent","")],
]


# =====================================================
# 🔹 HARDWARE INTERFACE (SAFE STRUCTURE)
# =====================================================

class HardwareInterface:

    def __init__(self):
        # self.ser = serial.Serial("COM3", 9600, timeout=1)
        pass

    def send_command(self, command):
        # Example:
        # self.ser.write(command.encode())
        # return self.ser.readline().decode().strip()
        print(f"[HARDWARE EXECUTED] {command}")
        return "123.45"   # Dummy return

    def close(self):
        print("[HARDWARE CLOSED]")


# =====================================================
# 🔹 GUI
# =====================================================

class IndustrialGUI:

    def __init__(self, root):

        self.root = root
        self.root.title(PAGE_TITLE)
        self.root.state("zoomed")
        self.root.configure(bg="#eef2f7")

        # Hardware
        self.hardware = HardwareInterface()

        # Thread communication
        self.command_queue = queue.Queue()

        # Store widgets
        self.buttons = {}
        self.entries = {}

        self.build_ui()

        # Start background worker
        self.start_worker_thread()


    # =====================================================
    # 🔹 BUILD UI
    # =====================================================

    def build_ui(self):

        header = tk.Frame(self.root, bg="#1f2937", height=60)
        header.pack(fill="x")

        tk.Label(header,
                 text=PAGE_TITLE,
                 bg="#1f2937",
                 fg="white",
                 font=("Segoe UI", 18, "bold")
                 ).pack(pady=15)

        main = tk.Frame(self.root, bg="#eef2f7")
        main.pack(fill="both", expand=True, padx=40, pady=20)

        TOTAL_COLUMNS = 6
        for c in range(TOTAL_COLUMNS):
            main.grid_columnconfigure(c, weight=1)

        for r, row in enumerate(LAYOUT):

            col = 0

            for item in row:

                item_type, value = item

                if item_type == "btn":
                    btn = tk.Button(main,
                                    text=value,
                                    bg="#1f2937",
                                    fg="white",
                                    font=("Segoe UI", 11, "bold"),
                                    command=lambda v=value: self.handle_button(v))
                    btn.grid(row=r, column=col, sticky="nsew", padx=10, pady=5)

                    # 🔹 STORE BUTTON FOR EXTERNAL ACCESS
                    self.buttons[value] = btn

                elif item_type == "lbl":
                    tk.Label(main,
                             text=value,
                             bg="#eef2f7",
                             fg="#111827",
                             font=("Segoe UI", 12, "bold"),
                             anchor="e"
                             ).grid(row=r, column=col, sticky="e", padx=10)

                elif item_type == "ent":
                    entry = tk.Entry(main,
                                     font=("Consolas", 14, "bold"),
                                     justify="center")
                    entry.insert(0, value)
                    entry.grid(row=r, column=col, sticky="nsew", padx=10)

                    # 🔹 STORE ENTRY BY LABEL NAME (FOR EXTERNAL WRITE)
                    self.entries[r] = entry

                col += 1

        footer = tk.Frame(self.root, bg="#111827", height=60)
        footer.pack(fill="x")

        tk.Button(footer,
                  text="EXIT",
                  bg="#7f1d1d",
                  fg="white",
                  command=self.safe_exit
                  ).pack(side="right", padx=20, pady=10)


    # =====================================================
    # 🔹 BUTTON CLICK → SEND TO THREAD
    # =====================================================

    def handle_button(self, name):

        print(f"[BUTTON CLICKED] {name}")

        # Instead of direct hardware call → send to queue
        self.command_queue.put(name)


    # =====================================================
    # 🔹 WORKER THREAD
    # =====================================================

    def start_worker_thread(self):

        threading.Thread(
            target=self.hardware_worker,
            daemon=True
        ).start()


    def hardware_worker(self):

        while True:

            command = self.command_queue.get()

            if command is None:
                break

            # 🔹 CALL HARDWARE
            result = self.hardware.send_command(command)

            # 🔹 UPDATE GUI SAFELY
            self.root.after(
                0,
                lambda r=result: self.update_entry(r)
            )


    # =====================================================
    # 🔹 SAFE GUI UPDATE
    # =====================================================

    def update_entry(self, value):

        # Example: update first entry
        first_entry = list(self.entries.values())[0]
        first_entry.delete(0, tk.END)
        first_entry.insert(0, value)


    # =====================================================
    # 🔹 EXTERNAL ACCESS METHODS
    # =====================================================

    def trigger_button(self, name):
        """
        Call this from another file to simulate button click.
        """
        self.root.after(0, lambda: self.buttons[name].invoke())


    def write_entry(self, row_index, value):
        """
        External hardware thread can write into entry safely.
        """
        self.root.after(
            0,
            lambda: self.entries[row_index].insert(0, value)
        )


    # =====================================================

    def safe_exit(self):
        self.command_queue.put(None)
        self.hardware.close()
        self.root.destroy()


# =====================================================
# 🔹 MAIN
# =====================================================

if __name__ == "__main__":

    root = tk.Tk()
    app = IndustrialGUI(root)

    # 🔹 EXAMPLE EXTERNAL CALL AFTER 3 SECONDS
    def external_demo():
        app.trigger_button("EXT SUPPLY")

    root.after(3000, external_demo)

    root.mainloop()
