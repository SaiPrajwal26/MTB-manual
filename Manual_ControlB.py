import tkinter as tk
from tkinter import ttk, messagebox
import subprocess

# --- HARDWARE DISABLED FOR TESTING ---
# Uncomment these when deploying to the actual hardware
# import serial_api  # Mock representing your 'Serial' C++ object
# import ipcard_api  # Mock representing your 'Ip' C++ object

# =====================================================
# CONFIGURATION & THEME ("Facebook / Elegant" Style)
# =====================================================
PAGE_TITLE = "CONTROL CHECKS"

COLOR_BG_MAIN = "#F0F2F5"       
COLOR_PANEL_BG = "#FFFFFF"      
COLOR_HEADER = "#1877F2"        
COLOR_TEXT = "#1C1E21"          
COLOR_LABEL_TEXT = "#65676B"    
COLOR_ENTRY_BG = "#F0F2F5"      
COLOR_ACCENT = "#1877F2"        

# Standard Toggle Colors matching C++ logic
COLOR_ON = "#42B72A"            # Green for Success / ON / Free
COLOR_OFF = "#FA383E"           # Red for Fail / OFF / Locked
COLOR_WHITE = "#FFFFFF"         # White for inactive states (like Stop Data)
COLOR_EXIT = "#FA383E"          

FONT_HEADER = ("Helvetica", 22, "bold")
FONT_PANEL_TITLE = ("Helvetica", 13, "bold")
FONT_LABEL = ("Helvetica", 11, "bold")
FONT_VALUE = ("Helvetica", 12, "bold")

# =====================================================
# MAIN GUI CLASS
# =====================================================
class ControlChecksGUI:

    def __init__(self, root):
        self.root = root
        self.root.title(PAGE_TITLE)
        
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg=COLOR_BG_MAIN)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        self.entries = {} 
        self.buttons = {}
        self.lockable_buttons = [] # Group of buttons disabled during TM polling
        
        # --- Backend State Variables ---
        self.hardware_active = False
        self.polling_sensors = False
        self.polling_actuators = False
        self.obpLink = 0

        # --- HARDWARE API INITIALIZATION (DISABLED FOR TESTING) ---
        # self.serial = serial_api.SerialManager()
        # self.ip = ipcard_api.IpCardManager()

        self.build_ui()
        
        # Start the background analog polling immediately (matches C++ thread1.start())
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
        main_frame.grid_columnconfigure(0, weight=1); main_frame.grid_columnconfigure(1, weight=1); main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Build Panels
        self.build_dynamic_control_panel(main_frame, 0, 0) # Left Column
        self.build_dynamic_data_panel(main_frame, 0, 1)    # Middle Column
        self.build_analog_panel(main_frame, 0, 2)          # Right Column

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
    # PANEL 1: COMMAND CONSOLE (Left Column)
    # =====================================================
    def build_dynamic_control_panel(self, parent, row_idx, col_idx):
        card = self.create_panel_frame(parent, row_idx, col_idx, "COMMAND CONSOLE")
        
        # Container for the stacked menus
        self.control_stack = tk.Frame(card, bg=COLOR_PANEL_BG)
        self.control_stack.grid(row=0, column=0, sticky="nsew")
        self.control_stack.grid_rowconfigure(0, weight=1); self.control_stack.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)

        # -------------------------------------
        # FRAME A: Less Frame (Basic)
        # -------------------------------------
        self.less_frame = tk.Frame(self.control_stack, bg=COLOR_PANEL_BG)
        self.less_frame.grid(row=0, column=0, sticky="nsew")
        self.less_frame.grid_columnconfigure(0, weight=1)

        self.btn_uncage = self.add_single_btn(self.less_frame, 0, "WING UNCAGE", COLOR_ACCENT, self.on_winguncagePushButton_clicked)
        self.btn_cage = self.add_single_btn(self.less_frame, 1, "WING CAGE", COLOR_ACCENT, self.on_wingcagePushButton_clicked)
        self.btn_null = self.add_single_btn(self.less_frame, 2, "ACTUATOR NULL", COLOR_ACCENT, self.on_actuatorNullPushButton_clicked)
        self.btn_cycle = self.add_single_btn(self.less_frame, 3, "CYCLING", COLOR_ACCENT, self.on_cyclingPushButton_clicked)
        self.btn_sensor_sign = self.add_single_btn(self.less_frame, 4, "SENSOR SIGN", COLOR_ACCENT, self.on_sensorsignPushButton_clicked)
        
        self.btn_more = tk.Button(self.less_frame, text="ADVANCED MENU ➔", bg="#65676B", fg="white", font=FONT_LABEL, bd=0, cursor="hand2", command=self.on_morePushButton_clicked)
        self.btn_more.grid(row=5, column=0, sticky="ew", padx=40, pady=15, ipady=4)

        # Map to lockable buttons array so we can disable them when reading TM
        self.lockable_buttons.extend([self.btn_uncage, self.btn_cage, self.btn_null, self.btn_cycle, self.btn_more])
        for i in range(6): self.less_frame.grid_rowconfigure(i, weight=1)

        # -------------------------------------
        # FRAME B: More Frame (Advanced)
        # -------------------------------------
        self.more_frame = tk.Frame(self.control_stack, bg=COLOR_PANEL_BG)
        self.more_frame.grid(row=0, column=0, sticky="nsew")
        self.more_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure('TCombobox', font=FONT_VALUE)

        tk.Label(self.more_frame, text="STEP COMMAND", bg=COLOR_PANEL_BG, font=("Helvetica", 10, "bold"), fg=COLOR_LABEL_TEXT).grid(row=0, pady=(15, 0))
        
        combo_frame = tk.Frame(self.more_frame, bg=COLOR_PANEL_BG)
        combo_frame.grid(row=1, padx=40, pady=5, sticky="ew")
        combo_frame.grid_columnconfigure(0, weight=1); combo_frame.grid_columnconfigure(1, weight=1)
        
        self.step_combo = ttk.Combobox(combo_frame, values=["TCP1", "TCP2", "TCP3", "TCP4", "WING1", "WING2"], state="readonly")
        self.step_combo.current(0)
        self.step_combo.grid(row=0, column=0, padx=(0,5), sticky="ew")
        
        self.val_combo = ttk.Combobox(combo_frame, values=["0.0 V", "5.0 V", "9.0 V", "-5.0 V", "-9.0 V"], state="readonly")
        self.val_combo.current(0)
        self.val_combo.grid(row=0, column=1, padx=(5,0), sticky="ew")

        self.btn_step = self.add_single_btn(self.more_frame, 2, "APPLY STEP", COLOR_ACCENT, self.on_stepPushButton_clicked)
        self.btn_feedback = self.add_single_btn(self.more_frame, 3, "FEEDBACK", COLOR_ACCENT, self.on_feedbackPushButton_clicked)

        tk.Label(self.more_frame, text="LINEARITY TEST", bg=COLOR_PANEL_BG, font=("Helvetica", 10, "bold"), fg=COLOR_LABEL_TEXT).grid(row=4, pady=(15, 0))
        
        self.lin_combo = ttk.Combobox(self.more_frame, values=["TCP1", "TCP2", "TCP3", "TCP4", "WING1", "WING2"], state="readonly")
        self.lin_combo.current(0)
        self.lin_combo.grid(row=5, padx=40, pady=5, sticky="ew")
        
        self.btn_linearity = self.add_single_btn(self.more_frame, 6, "CHECK LINEARITY", COLOR_ACCENT, self.on_linearityPushButton_clicked)
        self.add_entry_row(self.more_frame, 7, "Non-Linearity %", "0.00 %")

        self.btn_less = tk.Button(self.more_frame, text="⬅ BACK TO MAIN", bg="#65676B", fg="white", font=FONT_LABEL, bd=0, cursor="hand2", command=self.on_lessPushButton_clicked)
        self.btn_less.grid(row=8, sticky="ew", padx=40, pady=15, ipady=4)

        for i in range(9): self.more_frame.grid_rowconfigure(i, weight=1)
        self.less_frame.tkraise()

    # =====================================================
    # PANEL 2: TELEMETRY (Middle Column)
    # =====================================================
    def build_dynamic_data_panel(self, parent, row_idx, col_idx):
        card = self.create_panel_frame(parent, row_idx, col_idx, "TELEMETRY MONITORING")
        
        btn_bar = tk.Frame(card, bg=COLOR_PANEL_BG)
        btn_bar.grid(row=0, column=0, pady=10, sticky="ew")
        btn_bar.grid_columnconfigure(0, weight=1); btn_bar.grid_columnconfigure(1, weight=1); btn_bar.grid_columnconfigure(2, weight=1)

        tk.Button(btn_bar, text="SENSORS", bg=COLOR_ACCENT, fg="white", font=("Helvetica", 10, "bold"), bd=0, cursor="hand2", command=self.on_sensorPushButton_clicked).grid(row=0, column=0, padx=5, ipady=4, sticky="ew")
        tk.Button(btn_bar, text="ACTUATORS", bg=COLOR_ACCENT, fg="white", font=("Helvetica", 10, "bold"), bd=0, cursor="hand2", command=self.on_actuatorPushButton_clicked).grid(row=0, column=1, padx=5, ipady=4, sticky="ew")
        
        self.btn_stop = tk.Button(btn_bar, text="STOP DATA", bg=COLOR_WHITE, fg=COLOR_TEXT, font=("Helvetica", 10, "bold"), bd=1, relief="solid", cursor="hand2", command=self.on_stopDataPushButton_clicked)
        self.btn_stop.grid(row=0, column=2, padx=5, ipady=4, sticky="ew")

        stack_container = tk.Frame(card, bg=COLOR_PANEL_BG)
        stack_container.grid(row=1, column=0, sticky="nsew")
        stack_container.grid_columnconfigure(0, weight=1); stack_container.grid_rowconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        # 1. Sensor Frame
        self.sensor_frame = tk.Frame(stack_container, bg=COLOR_PANEL_BG)
        self.sensor_frame.grid(row=0, column=0, sticky="nsew")
        self.sensor_frame.grid_columnconfigure(0, weight=1); self.sensor_frame.grid_columnconfigure(1, weight=1)
        
        sens_labels = ["PITCH (V)", "ROLL (V)", "YAW (V)", "AX (mV)", "AY (mV)", "AZ (mV)", "LIFT OFF (V)", "PR SWITCH (V)"]
        for i, text in enumerate(sens_labels):
            self.add_entry_row(self.sensor_frame, i, text, "0.00")
            self.sensor_frame.grid_rowconfigure(i, weight=1)

        # 2. Actuator Frame
        self.actuator_frame = tk.Frame(stack_container, bg=COLOR_PANEL_BG)
        self.actuator_frame.grid(row=0, column=0, sticky="nsew")
        self.actuator_frame.grid_columnconfigure(0, weight=1); self.actuator_frame.grid_columnconfigure(1, weight=1)
        
        act_labels = ["WING 1 (V)", "WING 2 (V)", "TCP 1 (V)", "TCP 2 (V)", "TCP 3 (V)", "TCP 4 (V)"]
        for i, text in enumerate(act_labels):
            self.add_entry_row(self.actuator_frame, i, text, "0.00")
            self.actuator_frame.grid_rowconfigure(i, weight=1)

        self.sensor_frame.tkraise()

    # =====================================================
    # PANEL 3: ANALOG & STATUS (Right Column)
    # =====================================================
    def build_analog_panel(self, parent, row_idx, col_idx):
        card = self.create_panel_frame(parent, row_idx, col_idx, "ANALOG & STATUS")
        card.grid_columnconfigure(0, weight=1); card.grid_columnconfigure(1, weight=1)
        
        labels = [
            "EXT VOLTAGE", "EXT CURRENT", "SIM TB VOLTAGE", "SIM TB CURRENT", 
            "TB MON VOLTAGE", "UMBILICAL 1", "UMBILICAL 2", "WING STATUS", "OBP LINK"
        ]
        for i, text in enumerate(labels):
            self.add_entry_row(card, i, text, "0.00" if "V" in text or "A" in text else "OPEN/DOWN")
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
        btn = tk.Button(parent, text=text, bg=color, fg="white", font=FONT_LABEL, relief="ridge", bd=0, cursor="hand2", command=cmd)
        btn.grid(row=row_idx, column=0, columnspan=2, sticky="ew", padx=40, pady=8, ipady=4)
        return btn

    def create_header_btn(self, parent, text, command, color):
        return tk.Button(parent, text=text, bg=color, fg="white", font=("Helvetica", 11, "bold"), relief="flat", cursor="hand2", command=command, padx=20, bd=0)

    # ==============================================================================
    # ⚙️ BACKEND LOGIC PORTED FROM C++
    # ==============================================================================
    def init_hardware(self):
        """ Replicates the constructor and updateManualControlWindow """
        print("[SYSTEM] Hardware disabled for UI testing. Loading defaults...")
        self.hardware_active = True
        
        # This replicates thread1.start()
        self.analog_polling_loop()

    def on_morePushButton_clicked(self):
        self.less_frame.grid_remove() # Hide
        self.actuator_frame.tkraise()
        self.more_frame.tkraise()

    def on_lessPushButton_clicked(self):
        self.more_frame.grid_remove() # Hide
        self.less_frame.tkraise()

    def on_sensorsignPushButton_clicked(self):
        self.on_stopDataPushButton_clicked() # Ensure threads are dead before opening new window
        print("[UI] Opening Sensor Sign Window...")
        # sensorSignSubWindow = sensorSignWindow() 
        # sensorSignSubWindow.showFullScreen()

    # -------------------------------------------------------------
    # RELAY COMMANDS
    # -------------------------------------------------------------
    def on_winguncagePushButton_clicked(self):
        status = -1
        # --- HARDWARE DISABLED FOR TESTING ---
        # try: status = self.serial.wingUncage()
        # except: pass
        status = 0 # UI Bypass
        
        if status == 0: self.btn_uncage.config(bg=COLOR_ON)
        else: self.btn_uncage.config(bg=COLOR_OFF)

    def on_wingcagePushButton_clicked(self):
        status = -1
        # --- HARDWARE DISABLED FOR TESTING ---
        # try: status = self.serial.wingCage()
        # except: pass
        status = 0 # UI Bypass
        
        if status == 0: self.btn_cage.config(bg=COLOR_ON)
        else: self.btn_cage.config(bg=COLOR_OFF)

    def on_actuatorNullPushButton_clicked(self):
        # --- HARDWARE DISABLED FOR TESTING ---
        # try: self.serial.actuatorNull()
        # except: pass
        self.btn_null.config(bg=COLOR_ON)

    def on_cyclingPushButton_clicked(self):
        status = -1
        # --- HARDWARE DISABLED FOR TESTING ---
        # try: status = self.serial.actuatorCycling()
        # except: pass
        status = 0 # UI Bypass
        
        if status == 0: self.btn_cycle.config(bg=COLOR_ON)
        else: self.btn_cycle.config(bg=COLOR_OFF)

    # -------------------------------------------------------------
    # ADVANCED COMMANDS
    # -------------------------------------------------------------
    def on_stepPushButton_clicked(self):
        tcpIndex = self.step_combo.current()
        stepIndex = self.val_combo.current()
        
        # Match C++ switch logic
        val_map = {0: 0.0, 1: 5.0, 2: 9.0, 3: -5.0, 4: -9.0}
        val = val_map.get(stepIndex, 0.0)

        # --- HARDWARE DISABLED FOR TESTING ---
        # try: self.serial.tcpWriteChannel(tcpIndex, val)
        # except: pass
        print(f"[HW TX] Serial.tcpWriteChannel(Index: {tcpIndex}, Value: {val})")

    def on_feedbackPushButton_clicked(self):
        """ Replicates on_pushButton_clicked() - fetches feedback outside of threads """
        # --- HARDWARE DISABLED FOR TESTING ---
        # try: self.serial.actuatorFeedback()
        # except: pass
        
        tcp1Data, tcp2Data, tcp3Data, tcp4Data = 0.0, 0.0, 0.0, 0.0
        wing1Data, wing2Data = 0.0, 0.0
        linkData = 1 # Bypass
        
        self.update_entry("TCP 1 (V)", f"{tcp1Data:.3f}")
        self.update_entry("TCP 2 (V)", f"{tcp2Data:.3f}")
        self.update_entry("TCP 3 (V)", f"{tcp3Data:.3f}")
        self.update_entry("TCP 4 (V)", f"{tcp4Data:.3f}")
        self.update_entry("WING 1 (V)", f"{wing1Data:.3f}")
        self.update_entry("WING 2 (V)", f"{wing2Data:.3f}")
        self.obpLink = linkData

    def on_linearityPushButton_clicked(self):
        self.update_entry("Non-Linearity %", "0.00 %")
        tcpIndex = self.lin_combo.current()
        linIndex = tcpIndex + 1
        
        status = -1
        nonLinVal = 0.0
        # --- HARDWARE DISABLED FOR TESTING ---
        # try: 
        #     status = self.serial.checkLinearity(linIndex)
        #     nonLinVal = self.serial.nonLinearityVal
        # except: pass
        
        status = 0 # Bypass
        if status == 0:
            self.update_entry("Non-Linearity %", f"{nonLinVal:.2f} %")

    # -------------------------------------------------------------
    # TELEMETRY CONTROLS
    # -------------------------------------------------------------
    def on_sensorPushButton_clicked(self):
        self.lock_controls()
        self.btn_stop.config(bg=COLOR_OFF, fg="white") # Turns Red in C++ when active
        
        self.actuator_frame.grid_remove()
        self.sensor_frame.tkraise()
        
        self.polling_actuators = False
        self.polling_sensors = True
        self.sensor_polling_loop() # Replicates sensor1.start()

    def on_actuatorPushButton_clicked(self):
        self.lock_controls()
        self.btn_stop.config(bg=COLOR_OFF, fg="white") # Turns Red in C++ when active
        
        self.sensor_frame.grid_remove()
        self.actuator_frame.tkraise()
        
        self.polling_sensors = False
        self.polling_actuators = True
        self.actuator_polling_loop() # Replicates actuator1.start()

    def lock_controls(self):
        """ Replicates setEnabled(false) on control buttons """
        for btn in self.lockable_buttons:
            btn.config(state=tk.DISABLED, bg="#9CA3AF")

    def on_stopDataPushButton_clicked(self):
        """ Replicates on_stopDataPushButton_clicked() """
        self.btn_stop.config(bg=COLOR_WHITE, fg=COLOR_TEXT, relief="solid")
        
        self.polling_sensors = False
        self.polling_actuators = False
        
        # Restore control buttons
        for btn in self.lockable_buttons:
            # We don't restore btn_more since it's gray by design, handled uniquely if needed
            if btn != self.btn_more: 
                btn.config(state=tk.NORMAL, bg=COLOR_ACCENT)
        self.btn_more.config(state=tk.NORMAL, bg="#65676B")
        
        messagebox.showinfo("Link Free", "Serial Link Free\nNow you can send commands")

    # -------------------------------------------------------------
    # POLLING THREADS
    # -------------------------------------------------------------
    def analog_polling_loop(self):
        """ Replicates thread1 (updateAnalog) """
        if not self.hardware_active: return

        extVolt, extCurrent, intVolt, intCurrent, tbMonVolt, wcVolt = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        u1Status, u2Status = 0, 0

        # --- HARDWARE DISABLED FOR TESTING ---
        """
        try:
            # Replicate fetching from hardware
            extVolt = self.api.ap_read_ai(channel.EXT_VOLT)
            # ... fetches ...
            wcVolt = self.api.ap_read_ai(channel.WING_CAGE)
        except Exception: pass
        """

        self.update_entry("EXT VOLTAGE", f"{extVolt:.2f} V")
        self.update_entry("EXT CURRENT", f"{extCurrent:.2f} A")
        self.update_entry("SIM TB VOLTAGE", f"{intVolt:.2f} V")
        self.update_entry("SIM TB CURRENT", f"{intCurrent:.2f} A")
        self.update_entry("TB MON VOLTAGE", f"{tbMonVolt:.2f} V")

        self.update_entry("UMBILICAL 1", "MATED" if u1Status == 1 else "OPEN")
        self.update_entry("UMBILICAL 2", "MATED" if u2Status == 1 else "OPEN")
        self.update_entry("WING STATUS", "UNCAGED" if wcVolt > 5.0 else "CAGED")
        self.update_entry("OBP LINK", "UP" if self.obpLink == 1 else "DOWN")

        self.root.after(500, self.analog_polling_loop)

    def sensor_polling_loop(self):
        """ Replicates sensor1 (updateSensorData) """
        if not self.polling_sensors: return

        pitch, roll, yaw, ax, ay, az, ps, liftoff = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        
        # --- HARDWARE DISABLED FOR TESTING ---
        """
        try:
            # Replicate hardware fetching
            pitch = self.serial.pitchData
            self.obpLink = self.serial.obpLink
            # ...
        except Exception: pass
        """

        self.update_entry("PITCH (V)", f"{pitch:.3f}")
        self.update_entry("ROLL (V)", f"{roll:.3f}")
        self.update_entry("YAW (V)", f"{yaw:.3f}")
        self.update_entry("AX (mV)", f"{ax:.1f}")
        self.update_entry("AY (mV)", f"{ay:.1f}")
        self.update_entry("AZ (mV)", f"{az:.1f}")
        self.update_entry("LIFT OFF (V)", f"{liftoff:.2f}")
        self.update_entry("PR SWITCH (V)", f"{ps:.2f}")

        self.root.after(500, self.sensor_polling_loop)

    def actuator_polling_loop(self):
        """ Replicates actuator1 (updateActuatorData) """
        if not self.polling_actuators: return

        tcp1, tcp2, tcp3, tcp4, wing1, wing2 = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        
        # --- HARDWARE DISABLED FOR TESTING ---
        """
        try:
            # Replicate hardware fetching
            tcp1 = self.serial.tcp1Data
            self.obpLink = self.serial.obpLink
            # ...
        except Exception: pass
        """

        self.update_entry("TCP 1 (V)", f"{tcp1:.3f}")
        self.update_entry("TCP 2 (V)", f"{tcp2:.3f}")
        self.update_entry("TCP 3 (V)", f"{tcp3:.3f}")
        self.update_entry("TCP 4 (V)", f"{tcp4:.3f}")
        self.update_entry("WING 1 (V)", f"{wing1:.3f}")
        self.update_entry("WING 2 (V)", f"{wing2:.3f}")

        self.root.after(500, self.actuator_polling_loop)

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
            self.hardware_active = False 
            self.polling_sensors = False
            self.polling_actuators = False
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ControlChecksGUI(root)
    root.mainloop()
