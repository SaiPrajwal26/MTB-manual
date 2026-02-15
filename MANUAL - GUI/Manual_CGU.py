import tkinter as tk
from tkinter import messagebox
# import serial   # ← Uncomment when hardware is connected

# =====================================================
# 🔹 EDIT BELOW ONLY
# =====================================================

PAGE_TITLE = "Manual CGU Window"

LAYOUT = [

    [("lbl","SIG GEN VOLT"), ("ent","42"), ("lbl","SIG GEN POWER"), ("ent","")],
    [("lbl","CGU TX FREQ"), ("ent","42"), ("lbl","CGU TX POWER"), ("ent","")],

    [("sp",0.3), ("lbl","IP SET")],

    [("btn","IP VAL"), ("ent",""), ("lbl","STATUS"), ("ent","")],
    [("btn","FIN1"), ("lbl","Pamplitude"), ("lbl","OBP LINK"), ("ent","")],
    [("btn","FIN3"), ("lbl","Pwidth"), ("lbl","K1"), ("ent","")],
    [("btn","SIG RF ON"), ("lbl","Prise time"), ("lbl","K2"), ("ent","")],
    [("btn","SIG RF OFF"), ("lbl","Pfall time"), ("lbl","K3"), ("ent","")],
    [("btn","SPECTRUM P"), ("lbl","pulse char"), ("lbl","K4"), ("ent","")],
    [("btn","D-STC"), ("ent",0),("btn","SET U-STC"), ("lbl","K5"), ("ent","")],
    [("btn","D-STC"), ("ent",0),("btn","SET D-STC"), ("lbl","K6"), ("ent","")],

]

# =====================================================
# 🔹 HARDWARE INTERFACE (COMMENTED FOR NOW)
# =====================================================

class HardwareInterface:
    """
    This class will handle all hardware communication.
    Keep this clean and separate from GUI.
    """

    def __init__(self):
        # Uncomment when hardware ready
        # self.ser = serial.Serial("COM3", 9600, timeout=1)
        pass

    def read_value(self, command):
        """
        Send read command to hardware and return value.
        """
        # Example:
        # self.ser.write(command.encode())
        # return self.ser.readline().decode().strip()

        return "0.00"  # Dummy return for now

    def set_value(self, command, value):
        """
        Send set command with value to hardware.
        """
        # Example:
        # full_command = f"{command} {value}"
        # self.ser.write(full_command.encode())

        print(f"[SET COMMAND] {command} {value}")


# =====================================================
# 🔹 DO NOT TOUCH BELOW
# =====================================================


class IndustrialGUI:

    def __init__(self, root):
        self.root = root
        self.root.title(PAGE_TITLE)
        self.root.state("zoomed")
        self.root.configure(bg="#eef2f7")

        self.hardware = HardwareInterface()  # Ready but safe

        self.entry_widgets = {}  # store entries by row index

        self.build_ui()

    def build_ui(self):

        # ===== Header =====
        header = tk.Frame(self.root, bg="#1f2937", height=60)
        header.pack(fill="x")

        tk.Label(header,
                 text=PAGE_TITLE,
                 bg="#1f2937",
                 fg="white",
                 font=("Segoe UI", 18, "bold")
                 ).pack(pady=18)

        separator = tk.Frame(self.root, bg="#d1d5db", height=1)
        separator.pack(fill="x")

        # ===== Main Grid =====
        main = tk.Frame(self.root, bg="#eef2f7")
        main.pack(fill="both", expand=True, padx=40, pady=20)

        TOTAL_COLUMNS = 6

        # Spread horizontally
        for c in range(TOTAL_COLUMNS):
            main.grid_columnconfigure(c, weight=1)

        # Spread vertically
        for r in range(len(LAYOUT)):
            main.grid_rowconfigure(r, weight=1)

        # ===== Build Layout =====
        for r, row in enumerate(LAYOUT):

            col_index = 0

            for item in row:

                item_type, value = item

                if item_type == "sp":
                    col_index += int(value)
                    continue

                if item_type == "btn":
                    widget = tk.Button(main,
                                       text=value,
                                       bg="#1f2937",
                                       fg="white",
                                       font=("Segoe UI", 10, "bold"),
                                       relief="flat",
                                       height=1,
                                       command=lambda v=value: self.handle_button(v))
                    sticky_val = "nsew"

                elif item_type == "lbl":
                    widget = tk.Label(main,
                                      text=value,
                                      bg="#eef2f7",
                                      fg="#111827",
                                      font=("Segoe UI", 15, "bold"),
                                      anchor="e")
                    sticky_val = "e"

                elif item_type == "ent":
                    widget = tk.Entry(main,
                                      font=("Consolas", 14, "bold"),
                                      bg="#ffffff",
                                      justify="center",
                                      relief="solid",
                                      borderwidth=1)
                    widget.insert(0, value)
                    sticky_val = "nsew"

                widget.grid(row=r,
                            column=col_index,
                            padx=10,
                            pady=4,
                            sticky=sticky_val)

                col_index += 1

            # 🔥 Auto-fill remaining empty columns
            while col_index < TOTAL_COLUMNS:
                filler = tk.Label(main, bg="#eef2f7")
                filler.grid(row=r, column=col_index)
                col_index += 1

    # =====================================================
    # 🔹 BUTTON LOGIC (HARDWARE READY)
    # =====================================================

    def handle_button(self, button_name, row_index):

        print(f"[BUTTON PRESSED] {button_name}")

        # -------------------------------------------------
        # READ TYPE BUTTONS
        # Example: IP VAL → read from hardware
        # -------------------------------------------------
        if button_name == "IP VAL":

            # Uncomment when hardware connected
            # value = self.hardware.read_value("READ_IP")

            value = "192.168.0.10"  # Dummy for now

            # Update first entry in that row
            if row_index in self.entry_widgets:
                entry = self.entry_widgets[row_index][0]
                entry.delete(0, tk.END)
                entry.insert(0, value)

        # -------------------------------------------------
        # SET TYPE BUTTONS
        # Example: SET U-STC
        # -------------------------------------------------
        elif "SET" in button_name:

            if row_index in self.entry_widgets:
                entry = self.entry_widgets[row_index][0]
                value = entry.get()

                # Uncomment when hardware connected
                # self.hardware.set_value("SET_COMMAND", value)

                print(f"[SIMULATED SET] {button_name} → {value}")

        # -------------------------------------------------
        # ON/OFF TYPE BUTTONS
        # -------------------------------------------------
        elif "ON" in button_name:
            # self.hardware.set_value("RF_ON", 1)
            print("[SIMULATED] RF ON")

        elif "OFF" in button_name:
            # self.hardware.set_value("RF_OFF", 0)
            print("[SIMULATED] RF OFF")

        else:
            print("[NO HARDWARE ACTION DEFINED]")

    # =====================================================

    def safe_exit(self):
        if messagebox.askyesno("Confirm Exit", "Exit system?"):
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = IndustrialGUI(root)
    root.mainloop()
