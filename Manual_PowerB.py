import tkinter as tk
from tkinter import messagebox
import time

# --- HARDWARE DISABLED FOR TESTING ---
# Uncomment these when you are on the actual hardware machine
# from APCardManager import APCardManager
# import channel

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

COLOR_ON = "#42B72A"   # Green when ON
COLOR_OFF = "#FA383E"  # Red when OFF
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
        
        # --- HARDWARE DISABLED FOR TESTING ---
        # self.api = APCardManager()
        # self.api.ap_open() # Open connection to the card
        
        # Tracks current known UI state
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
        
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        self.build_control_panel(main_frame, 0, 0)
        self.build_analog_panel(main_frame, 0, 1)
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
            btn = tk.Button(card, text=f"{name} OFF", bg=COLOR_OFF, fg="white", font=FONT_LABEL, relief="flat", cursor="hand2", bd=0, 
                            command=lambda n=name: self.toggle_relay(n))
            btn.grid(row=i, column=0, sticky="nsew", padx=30, pady=8)
            self.buttons[name] = btn
            card.grid_rowconfigure(i, weight=1)
            
        # FIXED: Create subframe first, then parent the ASC/DSC buttons directly to the subframe
        self.tm_subframe = tk.Frame(card, bg=COLOR_PANEL_BG)
        
        self.btn_asc = tk.Button(self.tm_subframe, text="ASC", bg="#1877F2", fg="white", font=FONT_LABEL, relief="flat", command=self.send_asc)
        self.btn_dsc = tk.Button(self.tm_subframe, text="DSC", bg="#1877F2", fg="white", font=FONT_LABEL, relief="flat", command=self.send_dsc)
        
        self.btn_asc.pack(side="left", expand=True, fill="both", padx=(30, 5), pady=5)
        self.btn_dsc.pack(side="right", expand=True, fill="both", padx=(5, 30), pady=5)

    def build_analog_panel(self, parent, row_idx, col_idx):
        card = self.create_panel_frame(parent, row_idx, col_idx, "ANALOG SENSORS")
        card.grid_columnconfigure(0, weight=1); card.grid_columnconfigure(1, weight=1)
        
        analog_labels = ["EXT VOLTAGE", "EXT CURRENT", "SIM TB VOLTAGE", "SIM TB CURRENT", "TB MON VOLTAGE", "SUSTAINER RLY", "NOZZLE MATE", "WING CAGE"]
        
        for i, text in enumerate(analog_labels):
            self.add_entry_row(card, i, text, "0.00") 
            card.grid_rowconfigure(i, weight=1)

    def build_status_panel(self, parent, row_idx, col_idx):
        card = self.create_panel_frame(parent, row_idx, col_idx, "SYSTEM STATUS")
        card.grid_columnconfigure(0, weight=1); card.grid_columnconfigure(1, weight=1)
        
        status_labels = [
            "UMB1 STATUS", "UMB2 STATUS", "MSL TM STATUS", "OBP LINK", 
            "PRESSURE SW", "SAM RLY STATUS", "G SWITCH", "GND PYRO", 
            "NOZZLE RLY"
        ]
        
        for i, text in enumerate(status_labels):
            self.add_entry_row(card, i, text, "SAFE/OPEN") 
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
    # ⚙️ HARDWARE LOGIC & POLLING (DISABLED FOR UI TESTING)
    # ==============================================================================
    def init_hardware(self):
        print("[SYSTEM] Hardware disabled for UI testing. Loading defaults...")
        
        # --- HARDWARE DISABLED FOR TESTING ---
        # try:
        #     if hasattr(channel, 'SAM_COIL_STATUS'):
        #         self.set_btn_state("SAM COIL", self.api.ap_read_di(channel.SAM_COIL_STATUS) == 1)
        #     # ... other initial reads ...
        # except Exception as e:
        #     print(f"[WARN] Hardware initialization incomplete. Using defaults. Error: {e}")

        self.hardware_active = True
        self.hardware_polling_loop()

    def set_btn_state(self, name, is_on):
        self.button_states[name] = is_on
        btn = self.buttons[name]
        
        if is_on:
            btn.config(text=f"{name} ON", bg=COLOR_ON)
            if name == "TM":
                self.tm_subframe.grid(row=8, column=0, sticky="nsew") # Show ASC/DSC
        else:
            btn.config(text=f"{name} OFF", bg=COLOR_OFF)
            if name == "TM":
                self.tm_subframe.grid_forget() # Hide ASC/DSC

    def toggle_relay(self, name):
        intended_state = not self.button_states[name]
        
        # --- HARDWARE DISABLED FOR TESTING ---
        # We bypass the API entirely and just pretend the hardware successfully turned ON/OFF
        is_actually_on = intended_state 
        
        # Uncomment this block later to re-enable actual hardware control
        """
        actual_status = 0
        try:
            if name == "SAM COIL":
                actual_status = self.api.sam_coil_on() if intended_state else self.api.sam_coil_off()
            elif name == "OBP":
                actual_status = self.api.obp_on() if intended_state else self.api.obp_off()
            elif name == "SCU":
                actual_status = self.api.scu_on() if intended_state else self.api.scu_off()
            elif name == "CGU":
                actual_status = self.api.cgu_on() if intended_state else self.api.cgu_off()
            elif name == "RPF":
                actual_status = self.api.rpf_on() if intended_state else self.api.rpf_off()
            elif name == "TM":
                actual_status = self.api.tm_on() if intended_state else self.api.tm_off()
            elif name == "INT SUPPLY":
                actual_status = self.api.ips_on() if intended_state else self.api.ips_off()
            elif name == "EXT SUPPLY":
                actual_status = 1 if intended_state else 0 

            is_actually_on = (actual_status == 1)
        except Exception as e:
            messagebox.showerror("Hardware Error", f"Failed to send command to {name}.\nError: {e}")
            return
        """
        
        # For testing, we just link OBP state directly to the button state
        if name == "OBP":
            self.obpLink = 1 if is_actually_on else 0

        self.set_btn_state(name, is_actually_on)

    def hardware_polling_loop(self):
        if not self.hardware_active: return

        # --- HARDWARE DISABLED FOR TESTING ---
        # Bypassing the actual hardware read and just hardcoding the safe defaults
        u1Status, u2Status, mslTmStatus, pSwitchStatus = 0, 0, 0, 0
        samRelayStatus, gSwitchStatus, gndPyroStatus, nozzRelayStatus = 0, 0, 0, 0
        extVolt, extCurrent, intVolt, intCurrent, tbMonVolt, srVolt, neVolt, wcVolt = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

        """
        try:
            u1Status = self.api.ap_read_di(getattr(channel, 'UMB1_STATUS', 0)) or 0
            # ... other reads ...
        except Exception:
            pass
        """

        # 1. Analog Voltages Updates
        self.update_entry("EXT VOLTAGE", f"{extVolt:.2f} V")
        self.update_entry("EXT CURRENT", f"{extCurrent:.2f} A")
        self.update_entry("SIM TB VOLTAGE", f"{intVolt:.2f} V")
        self.update_entry("SIM TB CURRENT", f"{intCurrent:.2f} A")
        self.update_entry("TB MON VOLTAGE", f"{tbMonVolt:.2f} V")
        self.update_entry("SUSTAINER RLY", f"{srVolt:.2f} V")
        self.update_entry("NOZZLE MATE", f"{neVolt:.2f} V")
        self.update_entry("WING CAGE", f"{wcVolt:.2f} V")

        # 2. Digital Status Strings mapped from C++ logic
        self.update_entry("UMB1 STATUS", "MATED" if u1Status == 1 else "OPEN")
        self.update_entry("UMB2 STATUS", "MATED" if u2Status == 1 else "OPEN") 
        self.update_entry("MSL TM STATUS", "TM MSL" if mslTmStatus == 1 else "NON-TM")
        self.update_entry("OBP LINK", "UP" if self.obpLink == 1 else "DOWN")
        self.update_entry("PRESSURE SW", "CLOSED" if pSwitchStatus == 1 else "OPEN")
        self.update_entry("SAM RLY STATUS", "SAFE" if samRelayStatus == 1 else "ARM")
        self.update_entry("G SWITCH", "CLOSED" if gSwitchStatus == 1 else "OPEN")
        self.update_entry("GND PYRO", "ARM" if gndPyroStatus == 1 else "SAFE")
        self.update_entry("NOZZLE RLY", "ARM" if nozzRelayStatus == 1 else "SAFE")

        self.root.after(500, self.hardware_polling_loop)

    def update_entry(self, key, text):
        entry = self.entries.get(key)
        if entry:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, text)
            entry.config(state="readonly")

    def send_asc(self):
        if self.obpLink == 1:
            messagebox.showinfo("Success", "COMMAND SENT SUCCESSFULLY")
        else:
            messagebox.showwarning("Warning", "OBP LINK IS DOWN. Turn on OBP first.")

    def send_dsc(self):
        if self.obpLink == 1:
            messagebox.showinfo("Success", "COMMAND SENT SUCCESSFULLY")
        else:
            messagebox.showwarning("Warning", "OBP LINK IS DOWN. Turn on OBP first.")

    def open_dashboard(self):
        self.safe_exit(prompt=False)
        # subprocess.Popen(["python3", "ManualDashboard.py"])

    def safe_exit(self, prompt=True):
        if not prompt or messagebox.askyesno("Confirm Exit", "Shut down the system?"):
            self.hardware_active = False 
            # --- HARDWARE DISABLED FOR TESTING ---
            # self.api.ap_close() 
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PowerOnChecksGUI(root)
    root.mainloop()
