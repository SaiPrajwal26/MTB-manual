import tkinter as tk
from tkinter import messagebox
import subprocess
import time

# --- HARDWARE DISABLED FOR TESTING ---
# Uncomment these when deploying to the actual hardware
# import serial_api  # Mock representing your 'Serial' C++ object
# import ipcard_api  # Mock representing your 'Ip' C++ object
# import gpib_api    # Mock representing your 'Gpib' C++ object
# import channel     # Mock representing your channel constants

# =====================================================
# CONFIGURATION & THEME ("Facebook / Elegant" Style)
# =====================================================
PAGE_TITLE = "RPF CHECKS"

COLOR_BG_MAIN = "#F0F2F5"       
COLOR_PANEL_BG = "#FFFFFF"      
COLOR_HEADER = "#1877F2"        
COLOR_TEXT = "#1C1E21"          
COLOR_LABEL_TEXT = "#65676B"    
COLOR_ENTRY_BG = "#F0F2F5"      
COLOR_ACCENT = "#1877F2"        
COLOR_ACCENT_HOVER = "#166FE5"  

# Strict Toggle Colors based on requirements
COLOR_ON = "#42B72A"            # Green for ON / CLOSE / SUCCESS
COLOR_OFF = "#FA383E"           # Red for OFF / OPEN / FAIL
COLOR_WHITE = "#FFFFFF"         
COLOR_EXIT = "#FA383E"          

FONT_HEADER = ("Helvetica", 22, "bold")
FONT_PANEL_TITLE = ("Helvetica", 13, "bold")
FONT_LABEL = ("Helvetica", 11, "bold")
FONT_VALUE = ("Helvetica", 12, "bold")

# =====================================================
# MAIN GUI CLASS
# =====================================================
class RPFChecksGUI:

    def __init__(self, root):
        self.root = root
        self.root.title(PAGE_TITLE)
        
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg=COLOR_BG_MAIN)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        self.entries = {} 
        self.buttons = {}
        
        # --- Backend State Variables ---
        self.hardware_active = False
        self.attn = 0  # Master attenuator value from C++
        self.obpLink = 0
        self.samCoilButtonStatus = 0

        # --- HARDWARE API INITIALIZATION (DISABLED FOR TESTING) ---
        # self.serial = serial_api.SerialManager()
        # self.ip = ipcard_api.IpCardManager()
        # self.gpib = gpib_api.GpibManager()

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
        main_frame.grid_columnconfigure(0, weight=1); main_frame.grid_columnconfigure(1, weight=1); main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Build Panels
        self.build_dynamic_control_panel(main_frame, 0, 0) # Left Column (Stacked Menus)
        self.build_action_panel(main_frame, 0, 1)          # Middle Column
        self.build_status_panel(main_frame, 0, 2)          # Right Column

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
    # PANEL 1: DYNAMIC CONTROLS (Left Column)
    # =====================================================
    def build_dynamic_control_panel(self, parent, row_idx, col_idx):
        card = self.create_panel_frame(parent, row_idx, col_idx, "RPF CONTROLS")
        
        # Container for the stacked frames
        self.control_stack = tk.Frame(card, bg=COLOR_PANEL_BG)
        self.control_stack.grid(row=0, column=0, sticky="nsew")
        self.control_stack.grid_rowconfigure(0, weight=1)
        self.control_stack.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)

        # -------------------------------------
        # FRAME A: Less Frame (Main Menu)
        # -------------------------------------
        self.less_frame = tk.Frame(self.control_stack, bg=COLOR_PANEL_BG)
        self.less_frame.grid(row=0, column=0, sticky="nsew")
        self.less_frame.grid_columnconfigure(0, weight=1)

        self.buttons["SAM COIL"] = self.add_single_btn(self.less_frame, 0, "SAM COIL OFF", COLOR_WHITE, self.on_samCoilPushButton_clicked)
        self.add_dual_buttons(self.less_frame, 1, "TX1", "TX2", "TX_SEL", COLOR_WHITE, self.on_tx1PushButton_clicked, self.on_tx2PushButton_clicked)
        self.add_dual_buttons(self.less_frame, 2, "K8 LNA ON", "K8 LNA OFF", "K8_LNA", COLOR_WHITE, self.on_k8onPushButton_clicked, self.on_k8offPushButton_clicked)
        self.add_dual_buttons(self.less_frame, 3, "AWG CONT ON", "AWG CONT OFF", "AWG", COLOR_WHITE, self.on_contPushButton_clicked, self.on_contoffPushButton_clicked)
        self.add_single_btn(self.less_frame, 5, "AWG TRG", COLOR_WHITE, self.on_trgPushButton_clicked)
        
        tk.Button(self.less_frame, text="ATTENUATOR MENU ▶", bg="#65676B", fg="white", font=FONT_LABEL, bd=0, cursor="hand2", command=self.show_more_frame).grid(row=6, sticky="ew", padx=40, pady=10, ipady=4)
        tk.Button(self.less_frame, text="SAM CHECK MENU ▶", bg="#65676B", fg="white", font=FONT_LABEL, bd=0, cursor="hand2", command=lambda: self.sam_frame.tkraise()).grid(row=7, sticky="ew", padx=40, pady=10, ipady=4)
        
        for i in range(8): self.less_frame.grid_rowconfigure(i, weight=1)

        # -------------------------------------
        # FRAME B: More Frame (Attenuator)
        # -------------------------------------
        self.more_frame = tk.Frame(self.control_stack, bg=COLOR_PANEL_BG)
        self.more_frame.grid(row=0, column=0, sticky="nsew")
        self.more_frame.grid_columnconfigure(0, weight=1)

        self.add_dual_buttons(self.more_frame, 0, "1 dB ON", "1 dB OFF", "1DB", COLOR_WHITE, lambda: self.attn_math(1, "ON", "1DB"), lambda: self.attn_math(1, "OFF", "1DB"))
        self.add_dual_buttons(self.more_frame, 1, "2 dB ON", "2 dB OFF", "2DB", COLOR_WHITE, lambda: self.attn_math(2, "ON", "2DB"), lambda: self.attn_math(2, "OFF", "2DB"))
        self.add_dual_buttons(self.more_frame, 2, "4 dB ON", "4 dB OFF", "4DB", COLOR_WHITE, lambda: self.attn_math(4, "ON", "4DB"), lambda: self.attn_math(4, "OFF", "4DB"))
        self.add_dual_buttons(self.more_frame, 3, "4 dB (2) ON", "4 dB (2) OFF", "4DB2", COLOR_WHITE, lambda: self.attn_math(4, "ON", "4DB2"), lambda: self.attn_math(4, "OFF", "4DB2"))
        self.add_dual_buttons(self.more_frame, 4, "10 dB ON", "10 dB OFF", "10DB", COLOR_WHITE, lambda: self.attn_math(10, "ON", "10DB"), lambda: self.attn_math(10, "OFF", "10DB"))
        self.add_dual_buttons(self.more_frame, 5, "20 dB ON", "20 dB OFF", "20DB", COLOR_WHITE, lambda: self.attn_math(20, "ON", "20DB"), lambda: self.attn_math(20, "OFF", "20DB"))
        self.add_dual_buttons(self.more_frame, 6, "30 dB ON", "30 dB OFF", "30DB", COLOR_WHITE, lambda: self.attn_math(30, "ON", "30DB"), lambda: self.attn_math(30, "OFF", "30DB"))
        self.add_dual_buttons(self.more_frame, 7, "30 dB (2) ON", "30 dB (2) OFF", "30DB2", COLOR_WHITE, lambda: self.attn_math(30, "ON", "30DB2"), lambda: self.attn_math(30, "OFF", "30DB2"))
        
        tk.Button(self.more_frame, text="◀ BACK TO MAIN", bg="#65676B", fg="white", font=FONT_LABEL, bd=0, cursor="hand2", command=lambda: self.less_frame.tkraise()).grid(row=8, sticky="ew", padx=40, pady=10, ipady=4)
        for i in range(9): self.more_frame.grid_rowconfigure(i, weight=1)

        # -------------------------------------
        # FRAME C: SAM Frame (Switches & Relays)
        # -------------------------------------
        self.sam_frame = tk.Frame(self.control_stack, bg=COLOR_PANEL_BG)
        self.sam_frame.grid(row=0, column=0, sticky="nsew")
        self.sam_frame.grid_columnconfigure(0, weight=1)

        self.add_dual_buttons(self.sam_frame, 0, "G SWITCH CLOSE", "G SWITCH OPEN", "G_SW", COLOR_WHITE, self.on_gSwitchOnPushButton_clicked, self.on_gSwitchOffPushButton_clicked)
        self.add_dual_buttons(self.sam_frame, 1, "SAM K8 ON", "SAM K8 OFF", "SAM_K8", COLOR_WHITE, self.on_samk8onPushButton_clicked, self.on_samk8offPushButton_clicked)
        self.add_dual_buttons(self.sam_frame, 2, "SAM K9 ON", "SAM K9 OFF", "SAM_K9", COLOR_WHITE, self.on_samk9onPushButton_clicked, self.on_samk9offPushButton_clicked)
        
        tk.Button(self.sam_frame, text="◀ BACK TO MAIN", bg="#65676B", fg="white", font=FONT_LABEL, bd=0, cursor="hand2", command=lambda: self.less_frame.tkraise()).grid(row=3, sticky="ew", padx=40, pady=10, ipady=4)
        for i in range(4): self.sam_frame.grid_rowconfigure(i, weight=1)

        # Default View
        self.less_frame.tkraise()

    # =====================================================
    # PANEL 2: DELAYS & MEASUREMENTS (Middle Column)
    # =====================================================
    def build_action_panel(self, parent, row_idx, col_idx):
        card = self.create_panel_frame(parent, row_idx, col_idx, "DELAYS & MEASUREMENTS")
        
        # Delay Buttons
        self.add_single_btn(card, 0, "100 ns DELAY", COLOR_WHITE, lambda: self.set_delay(100))
        self.add_single_btn(card, 1, "150 ns DELAY", COLOR_WHITE, lambda: self.set_delay(150))
        self.add_single_btn(card, 2, "250 ns DELAY", COLOR_WHITE, lambda: self.set_delay(250))
        
        # Spectrum
        self.add_single_btn(card, 3, "TX S_POWER", COLOR_ACCENT, self.on_measPowerSpectrumPushButton_clicked)

        # Read-Only Entries
        self.add_entry_row(card, 4, "DELAY", "100 ns")
        self.add_entry_row(card, 5, "NET ATTN", "0 dB")
        self.add_entry_row(card, 6, "TX S_POWER", "0.00 dBm")
        self.add_entry_row(card, 7, "PULSE AMP1", "0.00 V")
        self.add_entry_row(card, 8, "PULSE WIDTH", "0.00 mS")

        for i in range(9): card.grid_rowconfigure(i, weight=1)

    # =====================================================
    # PANEL 3: STATUS (Right Column)
    # =====================================================
    def build_status_panel(self, parent, row_idx, col_idx):
        card = self.create_panel_frame(parent, row_idx, col_idx, "ANALOG & STATUS")
        card.grid_columnconfigure(0, weight=1); card.grid_columnconfigure(1, weight=1)
        
        status_labels = [
            "EXT VOLTAGE", "EXT CURRENT", "SIM TB VOLTAGE", "SIM TB CURRENT", 
            "TB MON VOLTAGE", "OBP LINK", "G SWITCH STATUS", "K1", "K2", "K3", "K4", "K5", "K6", "K7"
        ]
        
        for i, text in enumerate(status_labels):
            self.add_entry_row(card, i, text, "0.00" if "V" in text or "A" in text else "OPEN")
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
        if color == COLOR_ACCENT:
            btn.config(fg="white", bd=0)
            btn.bind("<Enter>", lambda e: btn.config(bg=COLOR_ACCENT_HOVER))
            btn.bind("<Leave>", lambda e: btn.config(bg=COLOR_ACCENT))
        self.buttons[text] = btn
        return btn

    def add_dual_buttons(self, parent, row_idx, text_on, text_off, key, default_color, cmd_on, cmd_off):
        container = tk.Frame(parent, bg=COLOR_PANEL_BG)
        container.grid(row=row_idx, column=0, sticky="ew", padx=30, pady=8)
        container.grid_columnconfigure(0, weight=1); container.grid_columnconfigure(1, weight=1)

        btn_on = tk.Button(container, text=text_on, bg=default_color, fg=COLOR_TEXT, font=("Helvetica", 9, "bold"), relief="ridge", bd=1, cursor="hand2", command=cmd_on)
        btn_on.grid(row=0, column=0, sticky="ew", padx=(0, 3), ipady=4)

        btn_off = tk.Button(container, text=text_off, bg=default_color, fg=COLOR_TEXT, font=("Helvetica", 9, "bold"), relief="ridge", bd=1, cursor="hand2", command=cmd_off)
        btn_off.grid(row=0, column=1, sticky="ew", padx=(3, 0), ipady=4)

        self.buttons[f"{key}_ON"] = btn_on
        self.buttons[f"{key}_OFF"] = btn_off

    def create_header_btn(self, parent, text, command, color):
        return tk.Button(parent, text=text, bg=color, fg="white", font=("Helvetica", 11, "bold"), relief="flat", cursor="hand2", command=command, padx=20, bd=0)

    # ==============================================================================
    # ⚙️ HARDWARE LOGIC PORTED FROM C++
    # ==============================================================================
    def init_hardware(self):
        print("[SYSTEM] Hardware disabled for UI testing. Loading defaults...")
        
        # --- HARDWARE DISABLED FOR TESTING ---
        """
        try:
            self.gpib.initSaRpf()
            # Opto and attenuator reset sequence would go here...
            
            # Read SAM Coil Status
            status = self.ip.readDi_A(channel.SAM_COIL_STATUS)
            if status == 1:
                self.samCoilButtonStatus = -1
                self.buttons["SAM COIL"].config(text="SAM COIL ON", bg=COLOR_ON, fg="white")
            else:
                self.samCoilButtonStatus = 0
                self.buttons["SAM COIL"].config(text="SAM COIL OFF", bg=COLOR_WHITE, fg=COLOR_TEXT)
        except Exception as e:
            print(f"Init Error: {e}")
        """
        
        self.hardware_active = True
        self.hardware_polling_loop()
        self.set_delay(100)

    def show_more_frame(self):
        self.more_frame.tkraise()
        self.update_entry("NET ATTN", f"{self.attn} dB")

    def attn_math(self, val, state, key):
        """ Handles the complex addition/subtraction of attenuator values """
        btn_on = self.buttons[f"{key}_ON"]
        btn_off = self.buttons[f"{key}_OFF"]
        
        hardware_success = False

        # --- HARDWARE DISABLED FOR TESTING ---
        """
        try:
            # Replicates: Ip.writeDo_A(AXDB_OFF, 0); Ip.writeDo_A(AXDB_ON, 1); delay(100); Ip.writeDo_A(AXDB_ON, 0);
            if state == "ON":
                self.ip.writeDo_A(getattr(channel, f"A{val}DB_OFF", 0), 0)
                self.ip.writeDo_A(getattr(channel, f"A{val}DB_ON", 0), 1)
                time.sleep(0.1)
                self.ip.writeDo_A(getattr(channel, f"A{val}DB_ON", 0), 0)
            else:
                self.ip.writeDo_A(getattr(channel, f"A{val}DB_ON", 0), 0)
                self.ip.writeDo_A(getattr(channel, f"A{val}DB_OFF", 0), 1)
                time.sleep(0.1)
                self.ip.writeDo_A(getattr(channel, f"A{val}DB_OFF", 0), 0)
            hardware_success = True
        except Exception: pass
        """
        hardware_success = True # Bypass for UI Testing
        
        if not hardware_success: 
            return messagebox.showerror("Hardware Error", f"Failed to switch {val}dB Attenuator.")

        if state == "ON":
            self.attn += val
            btn_on.config(bg=COLOR_ON, fg="white", state=tk.DISABLED)
            btn_off.config(bg=COLOR_WHITE, fg=COLOR_TEXT, state=tk.NORMAL)
        else:
            if self.attn > 0: self.attn -= val
            btn_on.config(bg=COLOR_WHITE, fg=COLOR_TEXT, state=tk.NORMAL)
            btn_off.config(bg=COLOR_OFF, fg="white", state=tk.NORMAL)
            # Clear color back to white after visual feedback
            self.root.after(300, lambda: btn_off.config(bg=COLOR_WHITE, fg=COLOR_TEXT))

        self.update_entry("NET ATTN", f"{self.attn} dB")

    def set_delay(self, val):
        hardware_success = False
        
        # --- HARDWARE DISABLED FOR TESTING ---
        """
        try:
            for p in range(8):
                self.ip.writeOptoDo_A(p, 1)
            time.sleep(0.1)
            self.ip.writeOptoDo_A(getattr(channel, f"DL{val}", 0), 0)
            hardware_success = True
        except Exception: pass
        """
        hardware_success = True # Bypass for UI Testing

        if hardware_success:
            self.update_entry("DELAY", f"{val} ns")

    def on_samCoilPushButton_clicked(self):
        btn = self.buttons["SAM COIL"]
        intended_state = 1 if self.samCoilButtonStatus == 0 else 0
        hardware_success = False
        
        # --- HARDWARE DISABLED FOR TESTING ---
        """
        try:
            if intended_state == 1:
                self.ip.writeDo_A(channel.SAM_COIL_OFF, 0)
                self.ip.writeDo_A(channel.SAM_COIL_ON, 1)
                time.sleep(0.1)
                self.ip.writeDo_A(channel.SAM_COIL_ON, 0)
            else:
                self.ip.writeDo_A(channel.SAM_COIL_ON, 0)
                self.ip.writeDo_A(channel.SAM_COIL_OFF, 1)
                time.sleep(0.1)
                self.ip.writeDo_A(channel.SAM_COIL_OFF, 0)
            
            time.sleep(0.2)
            # Verify Hardware actually flipped
            actual_status = self.ip.readDi_A(channel.SAM_COIL_STATUS)
            if actual_status == intended_state:
                hardware_success = True
        except Exception: pass
        """
        hardware_success = True # Bypass for UI Testing
        
        if hardware_success:
            if intended_state == 1:
                self.samCoilButtonStatus = -1
                btn.config(text="SAM COIL ON", bg=COLOR_ON, fg="white")
            else:
                self.samCoilButtonStatus = 0
                btn.config(text="SAM COIL OFF", bg=COLOR_WHITE, fg=COLOR_TEXT)

    def toggle_dual(self, key, state):
        """ Generic color toggle checking hardware success """
        hardware_success = False
        
        # --- HARDWARE DISABLED FOR TESTING ---
        """
        try:
            # Mapping Keys to C++ Functions
            if key == "TX_SEL":
                if state == "ON": # TX1
                    self.ip.writeOptoDo_A(channel.RPFTX2, 1)
                    self.ip.writeOptoDo_A(channel.RPFTX1, 0)
                else: # TX2
                    self.ip.writeOptoDo_A(channel.RPFTX1, 1)
                    self.ip.writeOptoDo_A(channel.RPFTX2, 0)
            elif key == "K8_LNA":
                if state == "ON": self.obpLink = self.serial.k8On()
                else: self.obpLink = self.serial.k8Off()
            elif key == "AWG":
                if state == "ON":
                    self.gpib.initAwgCont()
                    self.gpib.initOsc()
                    self.gpib.awgConton()
                else:
                    self.gpib.awgContoff()
                    self.gpib.initAwgTrig()
            elif key == "G_SW":
                self.ip.writeDo_A(channel.G_SWITCH_CLOSE, 1 if state == "ON" else 0)
            elif key == "SAM_K8":
                self.ip.writeDo_A(channel.K8OFF, 0 if state == "ON" else 1)
                self.ip.writeDo_A(channel.K8ON, 1 if state == "ON" else 0)
                time.sleep(0.1)
                self.ip.writeDo_A(channel.K8ON if state == "ON" else channel.K8OFF, 0)
                if state == "ON":
                    st1, st2, st3 = self.serial.relayOn(3), self.serial.relayOn(4), self.serial.relayOn(5)
                else:
                    st1, st2, st3 = self.serial.relayOff(3), self.serial.relayOff(4), self.serial.relayOff(5)
                self.obpLink = 0 if (st1==1 and st2==1 and st3==1) else -1
            elif key == "SAM_K9":
                st = self.serial.relayOn(6) if state == "ON" else self.serial.relayOff(6)
                self.obpLink = 0 if st == 1 else -1

            hardware_success = True
        except Exception: pass
        """
        hardware_success = True # Bypass for UI Testing

        if not hardware_success: return
        
        btn_on = self.buttons[f"{key}_ON"]
        btn_off = self.buttons[f"{key}_OFF"]
        
        btn_on.config(bg=COLOR_WHITE, fg=COLOR_TEXT)
        btn_off.config(bg=COLOR_WHITE, fg=COLOR_TEXT)
        
        if state == "ON":
            btn_on.config(bg=COLOR_ON, fg="white")
            if key == "K8_LNA": self.obpLink = 1
        else:
            btn_off.config(bg=COLOR_OFF, fg="white")
            self.root.after(300, lambda: btn_off.config(bg=COLOR_WHITE, fg=COLOR_TEXT))
            if key == "K8_LNA": self.obpLink = 0

    def on_tx1PushButton_clicked(self): self.toggle_dual("TX_SEL", "ON")
    def on_tx2PushButton_clicked(self): self.toggle_dual("TX_SEL", "OFF")
    def on_k8onPushButton_clicked(self): self.toggle_dual("K8_LNA", "ON")
    def on_k8offPushButton_clicked(self): self.toggle_dual("K8_LNA", "OFF")
    def on_contPushButton_clicked(self): self.toggle_dual("AWG", "ON")
    def on_contoffPushButton_clicked(self): self.toggle_dual("AWG", "OFF")
    def on_gSwitchOnPushButton_clicked(self): self.toggle_dual("G_SW", "ON")
    def on_gSwitchOffPushButton_clicked(self): self.toggle_dual("G_SW", "OFF")
    def on_samk8onPushButton_clicked(self): self.toggle_dual("SAM_K8", "ON")
    def on_samk8offPushButton_clicked(self): self.toggle_dual("SAM_K8", "OFF")
    def on_samk9onPushButton_clicked(self): self.toggle_dual("SAM_K9", "ON")
    def on_samk9offPushButton_clicked(self): self.toggle_dual("SAM_K9", "OFF")

    def on_trgPushButton_clicked(self):
        self.update_entry("PULSE AMP1", "Wait")
        self.update_entry("PULSE WIDTH", "Wait")
        
        fpAmp, fpWidth, temp = 0.0, 0.0, 0
        
        # --- HARDWARE DISABLED FOR TESTING ---
        """
        try:
            temp = self.gpib.firingPulseOscAmplitude(fpAmp, fpWidth)
        except Exception: pass
        """
        temp = 1 # Bypass (1 represents success in C++)
        fpAmp, fpWidth = 4.5, 0.012 

        if temp == 0:
            self.update_entry("PULSE AMP1", "NF")
            self.update_entry("PULSE WIDTH", "NF")
        elif temp == 1:
            self.update_entry("PULSE AMP1", f"{fpAmp:.2f} V")
            self.update_entry("PULSE WIDTH", f"{fpWidth*1000:.2f} mS")
            self.toggle_dual("K8_LNA", "OFF") # C++ logic auto-turns K8 off on success

    def on_measPowerSpectrumPushButton_clicked(self):
        tx1Power = 0.0
        
        # --- HARDWARE DISABLED FOR TESTING ---
        """
        try:
            tx1Power, freq = self.gpib.saPower()
        except Exception: pass
        """
        tx1Power = -10.5 # Bypass
        
        self.update_entry("TX S_POWER", f"{tx1Power:.2f} dBm")

    def hardware_polling_loop(self):
        """ Replicates updateAnalog threading """
        if not self.hardware_active: return

        intVolt, intCurrent, extVolt, extCurrent, tbMonVolt = 0.0, 0.0, 0.0, 0.0, 0.0
        gSwitch = 0

        # --- HARDWARE DISABLED FOR TESTING ---
        """
        try:
            # Replicates fetching from Thread1
            extVolt = self.thread1.extVolt
            extCurrent = self.thread1.extCurrent
            intVolt = self.thread1.intVolt
            intCurrent = self.thread1.intCurrent
            tbMonVolt = self.thread1.tbMonVolt
            gSwitch = self.ip.readDi_A(channel.G_SWITCH_STATUS)
        except Exception: pass
        """

        self.update_entry("SIM TB VOLTAGE", f"{intVolt:.2f} V")
        self.update_entry("SIM TB CURRENT", f"{intCurrent:.2f} A")
        self.update_entry("EXT VOLTAGE", f"{extVolt:.2f} V")
        self.update_entry("EXT CURRENT", f"{extCurrent:.2f} A")
        self.update_entry("TB MON VOLTAGE", f"{tbMonVolt:.2f} V")
        
        self.update_entry("OBP LINK", "UP" if self.obpLink == 1 else "DOWN")
        self.update_entry("G SWITCH STATUS", "CLOSE" if gSwitch == 1 else "OPEN")

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
            self.hardware_active = False 
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RPFChecksGUI(root)
    root.mainloop()
