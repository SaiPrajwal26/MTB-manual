import tkinter as tk
from tkinter import messagebox
import subprocess
import time

# --- HARDWARE DISABLED FOR TESTING ---
# Uncomment these when deploying to the actual hardware
# import serial_api  # Mock representing your 'Serial' C++ object
# import ipcard_api  # Mock representing your 'Ip' C++ object
# import channel     # Mock representing your channel constants

# =====================================================
# CONFIGURATION & THEME ("Facebook / Elegant" Style)
# =====================================================
PAGE_TITLE = "PYRO CHECKS"

COLOR_BG_MAIN = "#F0F2F5"       
COLOR_PANEL_BG = "#FFFFFF"      
COLOR_HEADER = "#1877F2"        
COLOR_TEXT = "#1C1E21"          
COLOR_LABEL_TEXT = "#65676B"    
COLOR_ENTRY_BG = "#F0F2F5"      
COLOR_ACCENT = "#1877F2"        
COLOR_ACCENT_HOVER = "#166FE5"  

# Exact Colors from your C++ Code
# Note: In Pyro, ON/ARM = Danger (Red), OFF/SAFE = Safe (Green)
COLOR_SUCCESS = "#09B509"       # rgb(9, 181, 9) (OFF/SAFE/OPEN)
COLOR_FAIL = "#FF0000"          # rgb(255, 0, 0) (ON/ARM/CLOSE/FIRE)
COLOR_WHITE = "#FFFFFF"         # Default for Fire/Safe reset
COLOR_EXIT = "#FA383E"          

FONT_HEADER = ("Helvetica", 22, "bold")
FONT_PANEL_TITLE = ("Helvetica", 13, "bold")
FONT_LABEL = ("Helvetica", 11, "bold")
FONT_VALUE = ("Helvetica", 12, "bold")

# =====================================================
# MAIN GUI CLASS
# =====================================================
class PyroChecksGUI:

    def __init__(self, root):
        self.root = root
        self.root.title(PAGE_TITLE)
        
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg=COLOR_BG_MAIN)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        self.entries = {} 
        self.buttons = {}
        self.hardware_active = False
        
        # --- HARDWARE API INITIALIZATION (DISABLED FOR TESTING) ---
        # self.serial = serial_api.SerialManager()
        # self.ip = ipcard_api.IpCardManager()

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

        self.create_header_btn(header, "◀ Dashboard", self.open_dashboard, "#42B72A").grid(row=0, column=0, padx=20, sticky="w")
        tk.Label(header, text=PAGE_TITLE, bg=COLOR_HEADER, fg="white", font=FONT_HEADER).grid(row=0, column=1)
        self.create_header_btn(header, "Exit System ✖", self.safe_exit, COLOR_EXIT).grid(row=0, column=2, padx=20, sticky="e")

        # --- MAIN AREA ---
        main_frame = tk.Frame(self.root, bg=COLOR_BG_MAIN)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=30)
        
        # 3 Equal Columns
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Build Panels
        self.build_control_panel(main_frame, 0, 0)
        self.build_action_panel(main_frame, 0, 1)
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
        card = self.create_panel_frame(parent, row_idx, col_idx, "PYRO CONTROLS")
        
        # Paired ON/OFF Buttons mapped directly from XML
        self.add_dual_buttons(card, 0, "PYRO SUPPLY ON", "PYRO SUPPLY OFF", "PYRO_PS", COLOR_WHITE, self.on_pyroOnPushButton_clicked, self.on_pyroOffPushButton_clicked)
        self.add_dual_buttons(card, 1, "GND PYRO ARM", "GND PYRO SAFE", "GND_PYRO", COLOR_WHITE, self.on_gndPyroArmPushButton_clicked, self.on_gndPyroOffPushButton_clicked)
        self.add_dual_buttons(card, 2, "TH BATT ON", "TH BATT OFF", "TH_BATT", COLOR_WHITE, self.on_thbattOnPushButton_clicked, self.on_thbattOffPushButton_clicked)
        self.add_dual_buttons(card, 3, "NE PYRO ARM", "NE PYRO SAFE", "NE_PYRO", COLOR_WHITE, self.on_nePyroArmPushButton_clicked, self.on_nePyroOffPushButton_clicked)
        self.add_dual_buttons(card, 4, "PR SWITCH CLOSE", "PR SWITCH OPEN", "PR_SWITCH", COLOR_WHITE, self.on_psClosePushButton_clicked, self.on_psOpenPushButton_clicked)
        
        # The ALL SAFE override button
        self.buttons["ALL SAFE"] = self.add_single_btn(card, 5, "ALL SAFE", COLOR_WHITE, self.on_all_safe_clicked)

        for i in range(6): card.grid_rowconfigure(i, weight=1)

    def build_action_panel(self, parent, row_idx, col_idx):
        card = self.create_panel_frame(parent, row_idx, col_idx, "FIRING CONTROLS")
        
        # Fire buttons have a specific 5-second hold logic
        self.buttons["TH BATT FIRE"] = self.add_single_btn(card, 0, "TH BATT FIRE", COLOR_WHITE, lambda: self.fire_sequence("TH BATT FIRE", "THBATTERY_FIRE"))
        self.buttons["AIR BOTTLE FIRE"] = self.add_single_btn(card, 1, "AIR BOTTLE FIRE", COLOR_WHITE, lambda: self.fire_sequence("AIR BOTTLE FIRE", "AIRBOTTLE_FIRE"))
        self.buttons["BOOSTER FIRE"] = self.add_single_btn(card, 2, "BOOSTER FIRE", COLOR_WHITE, lambda: self.fire_sequence("BOOSTER FIRE", "BOOSTER_FIRE"))
        
        # Other actions
        self.buttons["VIBRATION"] = self.add_single_btn(card, 3, "VIBRATION", COLOR_WHITE, self.on_vibration_clicked)
        self.buttons["SUSTAINER FIRE"] = self.add_single_btn(card, 4, "SUSTAINER FIRE", COLOR_WHITE, self.on_sustainerFirePushButton_clicked)
        self.buttons["NOZZLE PYRO SAFE (OBP)"] = self.add_single_btn(card, 5, "NOZZLE PYRO SAFE (OBP)", COLOR_WHITE, self.on_nozzleSafePushButton_clicked)

        for i in range(6): card.grid_rowconfigure(i, weight=1)

    def build_status_panel(self, parent, row_idx, col_idx):
        card = self.create_panel_frame(parent, row_idx, col_idx, "ANALOG & STATUS")
        card.grid_columnconfigure(0, weight=1); card.grid_columnconfigure(1, weight=1)
        
        status_labels = [
            "SIM TB VOLTAGE", "SIM TB CURRENT", "EXT PS VOLTAGE", "EXT PS CURRENT", 
            "TB MON VOLTAGE", "PRESSURE SWITCH", "NOZZLE RLY STATUS", "GND PYRO R STATUS", "NE MATING STATUS"
        ]
        
        for i, text in enumerate(status_labels):
            self.add_entry_row(card, i, text, "0.00" if "V" in text or "A" in text else "SAFE/OPEN")
            card.grid_rowconfigure(i, weight=1)

    # =====================================================
    # UI HELPERS
    # =====================================================
    def add_entry_row(self, parent, row_idx, label_text, placeholder):
        lbl = tk.Label(parent, text=label_text, bg=COLOR_PANEL_BG, fg=COLOR_LABEL_TEXT, font=FONT_LABEL, anchor="e")
        lbl.grid(row=row_idx, column=0, sticky="e", padx=(10, 10), pady=4)
        
        entry = tk.Entry(parent, font=FONT_VALUE, bg=COLOR_ENTRY_BG, fg=COLOR_TEXT, justify="center", relief="flat", bd=5, highlightthickness=0, width=12)
        entry.grid(row=row_idx, column=1, sticky="w", padx=(0, 20), pady=4, ipady=4)
        entry.insert(0, placeholder)
        entry.config(state="readonly")
        
        self.entries[label_text] = entry

    def add_single_btn(self, parent, row_idx, text, color, cmd):
        btn = tk.Button(parent, text=text, bg=color, fg=COLOR_TEXT, font=FONT_LABEL, relief="ridge", bd=1, cursor="hand2", command=cmd)
        btn.grid(row=row_idx, column=0, columnspan=2, sticky="ew", padx=40, pady=8, ipady=4)
        return btn

    def add_dual_buttons(self, parent, row_idx, text_on, text_off, key, default_color, cmd_on, cmd_off):
        container = tk.Frame(parent, bg=COLOR_PANEL_BG)
        container.grid(row=row_idx, column=0, sticky="ew", padx=30, pady=8)
        container.grid_columnconfigure(0, weight=1); container.grid_columnconfigure(1, weight=1)

        btn_on = tk.Button(container, text=text_on, bg=default_color, fg=COLOR_TEXT, font=("Helvetica", 10, "bold"), relief="ridge", bd=1, cursor="hand2", command=cmd_on)
        btn_on.grid(row=0, column=0, sticky="ew", padx=(0, 5), ipady=4)

        btn_off = tk.Button(container, text=text_off, bg=default_color, fg=COLOR_TEXT, font=("Helvetica", 10, "bold"), relief="ridge", bd=1, cursor="hand2", command=cmd_off)
        btn_off.grid(row=0, column=1, sticky="ew", padx=(5, 0), ipady=4)

        # Store references to modify them later (like in ALL SAFE)
        self.buttons[f"{key}_ON"] = btn_on
        self.buttons[f"{key}_OFF"] = btn_off

    def create_header_btn(self, parent, text, command, color):
        return tk.Button(parent, text=text, bg=color, fg="white", font=("Helvetica", 11, "bold"), relief="flat", cursor="hand2", command=command, padx=20, bd=0)

    # ==============================================================================
    # ⚙️ HARDWARE LOGIC PORTED FROM C++
    # ==============================================================================
    def init_hardware(self):
        print("[SYSTEM] Starting Pyro Hardware Thread...")
        self.hardware_active = True
        self.hardware_polling_loop()

    # -------------------------------------------------------------
    # CONTROL PANEL COMMANDS (Dual Buttons)
    # -------------------------------------------------------------
    def _execute_dual_pulse(self, key, state, off_ch, on_ch, status_ch, success_val):
        """ Abstracted logic for writing OFF->ON->OFF and verifying state """
        hardware_success = False
        btn_on = self.buttons[f"{key}_ON"]
        btn_off = self.buttons[f"{key}_OFF"]

        # --- HARDWARE DISABLED FOR TESTING ---
        """
        try:
            if state == "ON":
                self.ip.writeDo_A(off_ch, 0)
                self.ip.writeDo_A(on_ch, 1)
                time.sleep(0.1)
                self.ip.writeDo_A(on_ch, 0)
            else:
                self.ip.writeDo_A(on_ch, 0)
                self.ip.writeDo_A(off_ch, 1)
                time.sleep(0.1)
                self.ip.writeDo_A(off_ch, 0)
            
            time.sleep(0.5) # Wait for hardware relay
            actual_status = self.ip.readDi_A(status_ch)
            if actual_status == success_val:
                hardware_success = True
        except Exception: pass
        """
        hardware_success = True # Bypass for UI Testing

        if hardware_success:
            btn_on.config(bg=COLOR_WHITE, fg=COLOR_TEXT)
            btn_off.config(bg=COLOR_WHITE, fg=COLOR_TEXT)
            if state == "ON":
                btn_on.config(bg=COLOR_FAIL, fg="white") # Mapped to C++ Red (Danger/Armed)
            else:
                btn_off.config(bg=COLOR_SUCCESS, fg="white") # Mapped to C++ Green (Safe)

    def on_pyroOnPushButton_clicked(self):
        # self._execute_dual_pulse("PYRO_PS", "ON", channel.PYRO_PS_OFF, channel.PYRO_PS_ON, channel.PYRO_PS_STATUS, 1)
        self._execute_dual_pulse("PYRO_PS", "ON", "PYRO_PS_OFF", "PYRO_PS_ON", "PYRO_PS_STATUS", 1)

    def on_pyroOffPushButton_clicked(self):
        self._execute_dual_pulse("PYRO_PS", "OFF", "PYRO_PS_OFF", "PYRO_PS_ON", "PYRO_PS_STATUS", 0)

    def on_thbattOnPushButton_clicked(self):
        self._execute_dual_pulse("TH_BATT", "ON", "IPS_OFF", "IPS_ON", "IPS_STATUS", 1)

    def on_thbattOffPushButton_clicked(self):
        self._execute_dual_pulse("TH_BATT", "OFF", "IPS_OFF", "IPS_ON", "IPS_STATUS", 0)

    def on_nePyroArmPushButton_clicked(self):
        self._execute_dual_pulse("NE_PYRO", "ON", "NOZZLE_PYRO_RELAY_SAFE", "NOZZLE_PYRO_RELAY_ARM", "NONE", 1)

    def on_nePyroOffPushButton_clicked(self):
        self._execute_dual_pulse("NE_PYRO", "OFF", "NOZZLE_PYRO_RELAY_SAFE", "NOZZLE_PYRO_RELAY_ARM", "NONE", 0)

    def on_psClosePushButton_clicked(self):
        self._execute_dual_pulse("PR_SWITCH", "ON", "PR_SWITCH_OFF", "PR_SWITCH_ON", "PR_SWITCH_STATUS", 1)

    def on_psOpenPushButton_clicked(self):
        self._execute_dual_pulse("PR_SWITCH", "OFF", "PR_SWITCH_OFF", "PR_SWITCH_ON", "PR_SWITCH_STATUS", 0)

    def on_gndPyroArmPushButton_clicked(self):
        hardware_success = False
        btn_on = self.buttons["GND_PYRO_ON"]
        btn_off = self.buttons["GND_PYRO_OFF"]
        
        # --- HARDWARE DISABLED FOR TESTING ---
        """
        try:
            self.ip.writeDo_A(channel.BOOSTER_GND_RELAY, 1)
            self.ip.writeDo_A(channel.THAB_GND_RELAY, 1)
            hardware_success = True
        except Exception: pass
        """
        hardware_success = True # Bypass for UI Testing
        
        if hardware_success:
            btn_on.config(bg=COLOR_FAIL, fg="white")
            btn_off.config(bg=COLOR_WHITE, fg=COLOR_TEXT)

    def on_gndPyroOffPushButton_clicked(self):
        hardware_success = False
        btn_on = self.buttons["GND_PYRO_ON"]
        btn_off = self.buttons["GND_PYRO_OFF"]
        
        # --- HARDWARE DISABLED FOR TESTING ---
        """
        try:
            self.ip.writeDo_A(channel.BOOSTER_GND_RELAY, 0)
            self.ip.writeDo_A(channel.THAB_GND_RELAY, 0)
            hardware_success = True
        except Exception: pass
        """
        hardware_success = True # Bypass for UI Testing
        
        if hardware_success:
            btn_off.config(bg=COLOR_SUCCESS, fg="white")
            btn_on.config(bg=COLOR_WHITE, fg=COLOR_TEXT)

    def on_all_safe_clicked(self):
        """ Executes the exact C++ ALL SAFE shutdown pulse sequence """
        print("[HW] Executing ALL SAFE sequence...")
        
        # --- HARDWARE DISABLED FOR TESTING ---
        """
        try:
            self.ip.writeDo_A(channel.BOOSTER_GND_RELAY, 0)
            self.ip.writeDo_A(channel.THAB_GND_RELAY, 0)

            self.ip.writeDo_A(channel.NOZZLE_PYRO_RELAY_ARM, 0)
            self.ip.writeDo_A(channel.NOZZLE_PYRO_RELAY_SAFE, 1)
            time.sleep(0.1)
            self.ip.writeDo_A(channel.NOZZLE_PYRO_RELAY_SAFE, 0)

            self.ip.writeDo_A(channel.PYRO_PS_ON, 0)
            self.ip.writeDo_A(channel.PYRO_PS_OFF, 1)
            time.sleep(0.1)
            self.ip.writeDo_A(channel.PYRO_PS_OFF, 0)

            self.ip.writeDo_A(channel.IPS_ON, 0)
            self.ip.writeDo_A(channel.IPS_OFF, 1)
            time.sleep(0.1)
            self.ip.writeDo_A(channel.IPS_OFF, 0)

            self.ip.writeDo_A(channel.PR_SWITCH_ON, 0)
            self.ip.writeDo_A(channel.PR_SWITCH_OFF, 1)
            time.sleep(0.1)
            self.ip.writeDo_A(channel.PR_SWITCH_OFF, 0)
        except Exception: pass
        """
        
        # Reset all paired button colors to white as instructed by C++
        for key, btn in self.buttons.items():
            if "_ON" in key or "_OFF" in key:
                btn.config(bg=COLOR_WHITE, fg=COLOR_TEXT)
                
        # Also reset single state buttons specified in C++
        self.buttons["SUSTAINER FIRE"].config(bg=COLOR_WHITE, fg=COLOR_TEXT)
        self.buttons["NOZZLE PYRO SAFE (OBP)"].config(bg=COLOR_WHITE, fg=COLOR_TEXT)

    # -------------------------------------------------------------
    # ACTION PANEL COMMANDS (Single Buttons)
    # -------------------------------------------------------------
    def fire_sequence(self, btn_name, cmd_string):
        """ Replicates the 5-second blocking delay for Fire commands from C++ without freezing the GUI """
        btn = self.buttons[btn_name]
        
        # --- HARDWARE DISABLED FOR TESTING ---
        """
        try:
            self.ip.writeDo_A(getattr(channel, cmd_string, 0), 1)
        except Exception: pass
        """
        
        print(f"[HW] SENDING COMMAND: Ip.writeDo_A({cmd_string}, 1)")
        btn.config(bg=COLOR_FAIL, fg="white") # Turns Red while firing
        
        # Schedule the OFF command after 5000ms
        self.root.after(5000, lambda: self.end_fire_sequence(btn, cmd_string))

    def end_fire_sequence(self, btn, cmd_string):
        """ Callback to end the 5-second fire sequence """
        # --- HARDWARE DISABLED FOR TESTING ---
        """
        try:
            self.ip.writeDo_A(getattr(channel, cmd_string, 0), 0)
        except Exception: pass
        """
        print(f"[HW] SENDING COMMAND: Ip.writeDo_A({cmd_string}, 0)")
        btn.config(bg=COLOR_WHITE, fg=COLOR_TEXT)

    def on_vibration_clicked(self):
        status = -1
        # --- HARDWARE DISABLED FOR TESTING ---
        # try: status = self.serial.actuatorVibration()
        # except: pass
        status = 0 # UI Bypass
        
        if status == 0:
            messagebox.showinfo("Success", "Vibration Command Sent Successfully")
        else:
            messagebox.showwarning("Error", "Vibration Command Unsuccessful")

    def on_sustainerFirePushButton_clicked(self):
        btn = self.buttons["SUSTAINER FIRE"]
        status = -1
        # --- HARDWARE DISABLED FOR TESTING ---
        # try: status = self.serial.relayOnCmd(2)
        # except: pass
        status = 1 # UI Bypass (1 is success in C++)
        
        if status == 1: btn.config(bg=COLOR_FAIL, fg="white") # Red for armed/fire
        else: btn.config(bg=COLOR_WHITE, fg=COLOR_TEXT)

    def on_nozzleSafePushButton_clicked(self):
        btn = self.buttons["NOZZLE PYRO SAFE (OBP)"]
        status = -1
        # --- HARDWARE DISABLED FOR TESTING ---
        # try: status = self.serial.relayOnCmd(7)
        # except: pass
        status = 1 # UI Bypass (1 is success in C++)
        
        if status == 1: btn.config(bg=COLOR_FAIL, fg="white") # Red
        else: btn.config(bg=COLOR_WHITE, fg=COLOR_TEXT)

    # -------------------------------------------------------------
    # POLLING LOOP
    # -------------------------------------------------------------
    def hardware_polling_loop(self):
        """ Replicates thread1 and sensor1 updating """
        if not self.hardware_active: return

        intVolt, intCurrent, extVolt, extCurrent, tbMonVolt, neVolt, psVolt = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        nozzRelayStatus, gndPyroStatus = 0, 0

        # --- HARDWARE DISABLED FOR TESTING ---
        """
        try:
            # Replicates fetching from Thread1
            extVolt = self.thread1.extVolt
            extCurrent = self.thread1.extCurrent
            intVolt = self.thread1.intVolt
            intCurrent = self.thread1.intCurrent
            tbMonVolt = self.thread1.tbMonVolt
            neVolt = self.thread1.neVolt
            nozzRelayStatus = self.thread1.nozzRelayStatus
            gndPyroStatus = self.thread1.gndPyroStatus
            
            # Replicates fetching from sensor1
            psVolt = self.sensor1.pressureswitchData
        except Exception: pass
        """

        # Analog Formatting
        self.update_entry("SIM TB VOLTAGE", f"{intVolt:.2f} V")
        self.update_entry("SIM TB CURRENT", f"{intCurrent:.2f} A")
        self.update_entry("EXT PS VOLTAGE", f"{extVolt:.2f} V")
        self.update_entry("EXT PS CURRENT", f"{extCurrent:.2f} A")
        self.update_entry("TB MON VOLTAGE", f"{tbMonVolt:.2f} V")
        self.update_entry("NE MATING STATUS", f"{neVolt:.2f} V")
        self.update_entry("PRESSURE SWITCH", f"{psVolt:.2f} V")

        # Digital Status Strings
        self.update_entry("NOZZLE RLY STATUS", "SAFE" if nozzRelayStatus == 0 else "ARM")
        self.update_entry("GND PYRO R STATUS", "SAFE" if gndPyroStatus == 0 else "ARM")

        self.root.after(500, self.hardware_polling_loop)

    def update_entry(self, key, text):
        entry = self.entries.get(key)
        if entry:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, text)
            entry.config(state="readonly")

    def open_dashboard(self):
        self.safe_exit(prompt=False)
        # subprocess.Popen(["python3", "ManualDashboard.py"])

    def safe_exit(self, prompt=True):
        if not prompt or messagebox.askyesno("Confirm Exit", "Shut down the system?"):
            self.hardware_active = False # Stop loop safely before destroying
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PyroChecksGUI(root)
    root.mainloop()
