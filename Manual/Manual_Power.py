import tkinter as tk
from tkinter import messagebox
import subprocess
import random  # Used ONLY to simulate hardware data

# =====================================================
# CONFIGURATION & THEME ("Facebook / Elegant" Style)
# =====================================================
PAGE_TITLE = "POWER ON CHECKS"

COLOR_BG_MAIN = "#F0F2F5"       
COLOR_PANEL_BG = "#FFFFFF"      
COLOR_HEADER = "#1877F2"        
COLOR_TEXT = "#1C1E21"          
COLOR_LABEL_TEXT = "#65676B"    
COLOR_ENTRY_BG = "#F0F2F5"      
COLOR_ACCENT = "#1877F2"        

# Standardized Toggle Colors
COLOR_ON = "#42B72A"            # Green for ON
COLOR_OFF = "#FA383E"           # Red for OFF
COLOR_EXIT = "#FA383E"          

FONT_HEADER = ("Helvetica", 22, "bold")
FONT_PANEL_TITLE = ("Helvetica", 13, "bold")
FONT_LABEL = ("Helvetica", 11, "bold")
FONT_VALUE = ("Helvetica", 12, "bold")

# =====================================================
# MAIN GUI CLASS
# =====================================================
class PowerOnChecksGUI:

    def __init__(self, root):
        self.root = root
        self.root.title(PAGE_TITLE)
        
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg=COLOR_BG_MAIN)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        self.entries = {} 
        self.buttons = {}
        
        # --- Backend State Variables ---
        self.button_states = {
            "EXT SUPPLY": False,
            "SAM COIL": False,
            "OBP": False,
            "SCU": False,
            "CGU": False,
            "RPF": False,
            "TM": False,
            "INT SUPPLY": False
        }
        self.obpLink = 0
        self.hardware_active = False

        self.build_ui()
        self.init_hardware()

    # =====================================================
    # BUILD UI
    # =====================================================
    def build_ui(self):
        self.root.grid_rowconfigure(1, weight=1) 
        self.root.grid_columnconfigure(0, weight=1) 

        # --- HEADER ---
        header = tk.Frame(self.root, bg=COLOR_HEADER, height=70)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1); header.grid_columnconfigure(1, weight=2); header.grid_columnconfigure(2, weight=1)
        header.grid_propagate(False)

        btn_dash = self.create_header_btn(header, "◀ Dashboard", self.open_dashboard, "#42B72A")
        btn_dash.grid(row=0, column=0, padx=20, sticky="w")
        tk.Label(header, text=PAGE_TITLE, bg=COLOR_HEADER, fg="white", font=FONT_HEADER).grid(row=0, column=1)
        btn_exit = self.create_header_btn(header, "Exit System ✖", self.safe_exit, COLOR_EXIT)
        btn_exit.grid(row=0, column=2, padx=20, sticky="e")

        # --- MAIN AREA ---
        main_frame = tk.Frame(self.root, bg=COLOR_BG_MAIN)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=30)
        
        # 3 Equal Columns
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Build the 3 Panels
        self.build_control_panel(main_frame, 0, 0)
        self.build_analog_panel(main_frame, 0, 1)  # Analog now gets the full middle column
        self.build_status_panel(main_frame, 0, 2)

    def create_panel_frame(self, parent, row_idx, col_idx, title):
        container = tk.Frame(parent, bg=COLOR_BG_MAIN)
        container.grid(row=row_idx, column=col_idx, sticky="nsew", padx=15)
        container.grid_columnconfigure(0, weight=1); container.grid_rowconfigure(1, weight=1)
        
        tk.Label(container, text=title, bg=COLOR_BG_MAIN, fg=COLOR_TEXT, font=FONT_PANEL_TITLE, anchor="center").grid(row=0, column=0, pady=(0, 8))
        
        card = tk.Frame(container, bg=COLOR_PANEL_BG, highlightbackground="#DADDDF", highlightthickness=1)
        card.grid(row=1, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        return card

    # =====================================================
    # PANELS
    # =====================================================
    def build_control_panel(self, parent, row_idx, col_idx):
        card = self.create_panel_frame(parent, row_idx, col_idx, "CONTROL RELAYS")
        
        controls = ["EXT SUPPLY", "SAM COIL", "OBP", "SCU", "CGU", "RPF", "TM", "INT SUPPLY"]

        for i, name in enumerate(controls):
            # All buttons default to OFF (Red)
            btn = tk.Button(card, text=f"{name} OFF", bg=COLOR_OFF, fg="white", font=FONT_LABEL, relief="flat", cursor="hand2", bd=0, 
                            command=lambda n=name: self.toggle_relay(n))
            btn.grid(row=i, column=0, sticky="nsew", padx=30, pady=8)
            self.buttons[name] = btn
            card.grid_rowconfigure(i, weight=1)

    def build_analog_panel(self, parent, row_idx, col_idx):
        card = self.create_panel_frame(parent, row_idx, col_idx, "ANALOG SENSORS")
        card.grid_columnconfigure(0, weight=1); card.grid_columnconfigure(1, weight=1)
        
        analog_labels = ["EXT VOLTAGE", "EXT CURRENT", "SIM TB VOLTAGE", "SIM TB CURRENT", "TB MON VOLTAGE"]
        
        for i, text in enumerate(analog_labels):
            self.add_entry_row(card, i, text, "")
            card.grid_rowconfigure(i, weight=1)

    def build_status_panel(self, parent, row_idx, col_idx):
        card = self.create_panel_frame(parent, row_idx, col_idx, "SYSTEM STATUS")
        card.grid_columnconfigure(0, weight=1); card.grid_columnconfigure(1, weight=1)
        
        status_labels = [
            "UMB1 STATUS", "UMB2 STATUS", "MSL TM STATUS", "OBP LINK", 
            "PRESSURE SW", "SAM RLY STATUS", "G SWITCH", "GND PYRO", 
            "NOZZLE RLY", "SUSTAINER RLY", "NOZZLE MATE", "WING CAGE"
        ]
        
        for i, text in enumerate(status_labels):
            self.add_entry_row(card, i, text, "")
            card.grid_rowconfigure(i, weight=1)

    # =====================================================
    # UI HELPERS
    # =====================================================
    def add_entry_row(self, parent, row_idx, label_text, placeholder):
        lbl = tk.Label(parent, text=label_text, bg=COLOR_PANEL_BG, fg=COLOR_LABEL_TEXT, font=FONT_LABEL, anchor="e")
        lbl.grid(row=row_idx, column=0, sticky="e", padx=(10, 10), pady=2)
        
        entry = tk.Entry(parent, font=FONT_VALUE, bg=COLOR_ENTRY_BG, fg=COLOR_TEXT, justify="center", relief="flat", bd=5, highlightthickness=0, width=14)
        entry.grid(row=row_idx, column=1, sticky="w", padx=(0, 20), pady=2, ipady=2)
        entry.insert(0, placeholder)
        entry.config(state="readonly")
        
        self.entries[label_text] = entry

    def create_header_btn(self, parent, text, command, color):
        return tk.Button(parent, text=text, bg=color, fg="white", font=("Helvetica", 11, "bold"), relief="flat", cursor="hand2", command=command, padx=20, bd=0)

    # ==============================================================================
    # ⚙️ HARDWARE LOGIC & POLLING
    # ==============================================================================
    def init_hardware(self):
        print("[SYSTEM] Reading initial relay states...")
        self.hardware_active = True
        self.hardware_polling_loop()

    def toggle_relay(self, name):
        """ Handles ON/OFF button clicks """
        new_state = not self.button_states[name]
        self.button_states[name] = new_state
        btn = self.buttons[name]
        
        if new_state:
            # Turned ON -> Make it Green
            btn.config(text=f"{name} ON", bg=COLOR_ON)
            print(f"[HW] Sending Command: {name}_ON")
            if name == "OBP":
                self.obpLink = 1
        else:
            # Turned OFF -> Make it Red
            btn.config(text=f"{name} OFF", bg=COLOR_OFF)
            print(f"[HW] Sending Command: {name}_OFF")
            if name == "OBP":
                self.obpLink = 0

    def hardware_polling_loop(self):
        """ Background loop that runs every 500ms to update entries dynamically """
        if not self.hardware_active: return

        # -------------------------------------------------------------
        # REPLACE THESE RANDOM VALUES WITH YOUR ACTUAL SERIAL READINGS
        # -------------------------------------------------------------
        u1Status = random.choice([0, 1])
        mslTmStatus = random.choice([0, 1])
        wcVolt = random.uniform(2.0, 7.0)
        extVolt = random.uniform(24.0, 24.5)  # Slight flutter to show it's dynamic
        
        # 1. Analog Voltages (Formatted to 2 decimal places)
        self.update_entry("EXT VOLTAGE", f"{extVolt:.2f} V")
        self.update_entry("EXT CURRENT", "1.20 A")
        self.update_entry("SIM TB VOLTAGE", "28.00 V")
        self.update_entry("SIM TB CURRENT", "0.50 A")
        self.update_entry("TB MON VOLTAGE", "5.00 V")

        # 2. Digital Status Strings mapped from C++ conditions
        self.update_entry("UMB1 STATUS", "MATED" if u1Status == 1 else "OPEN")
        self.update_entry("UMB2 STATUS", "MATED") 
        self.update_entry("MSL TM STATUS", "TM MSL" if mslTmStatus == 1 else "NON-TM")
        self.update_entry("OBP LINK", "UP" if self.obpLink == 1 else "DOWN")
        
        self.update_entry("PRESSURE SW", "CLOSED")
        self.update_entry("SAM RLY STATUS", "SAFE")
        self.update_entry("G SWITCH", "OPEN")
        self.update_entry("GND PYRO", "SAFE")
        self.update_entry("NOZZLE RLY", "ARM")
        
        self.update_entry("SUSTAINER RLY", "0.00 V")
        self.update_entry("NOZZLE MATE", "0.00 V")
        self.update_entry("WING CAGE", f"{wcVolt:.2f} V")

        # Call itself again in 500ms
        self.root.after(500, self.hardware_polling_loop)

    def update_entry(self, key, text):
        """ Helper to safely update a readonly Entry without freezing the UI """
        entry = self.entries.get(key)
        if entry:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, text)
            entry.config(state="readonly")

    def open_dashboard(self):
        self.safe_exit(prompt=False)
        subprocess.Popen(["python3", "ManualDashboard.py"])

    def safe_exit(self, prompt=True):
        if not prompt or messagebox.askyesno("Confirm Exit", "Shut down the system?"):
            self.hardware_active = False # Stop loop safely before destroying
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PowerOnChecksGUI(root)
    root.mainloop()
