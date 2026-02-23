import tkinter as tk
from tkinter import messagebox
import subprocess
import random  # Used only to mock hardware measurements

# =====================================================
# CONFIGURATION & THEME ("Facebook / Elegant" Style)
# =====================================================
PAGE_TITLE = "CGU CHECKS"

COLOR_BG_MAIN = "#F0F2F5"       
COLOR_PANEL_BG = "#FFFFFF"      
COLOR_HEADER = "#1877F2"        
COLOR_TEXT = "#1C1E21"          
COLOR_LABEL_TEXT = "#65676B"    
COLOR_ENTRY_BG = "#F0F2F5"      
COLOR_ACCENT = "#1877F2"        
COLOR_ACCENT_HOVER = "#166FE5"  

# --- Exact Colors from your C++ Code ---
COLOR_SUCCESS = "#09B509"       # rgb(9, 181, 9)
COLOR_FAIL = "#FF0000"          # rgb(255, 0, 0)
COLOR_ACTIVE_PINK = "#FFA6AF"   # rgb(255, 166, 175)
COLOR_WHITE = "#FFFFFF"         # rgb(255, 255, 255)

FONT_HEADER = ("Helvetica", 22, "bold")
FONT_PANEL_TITLE = ("Helvetica", 13, "bold")
FONT_LABEL = ("Helvetica", 11, "bold")
FONT_VALUE = ("Helvetica", 12, "bold")

# =====================================================
# MAIN GUI CLASS
# =====================================================
class CGUChecksGUI:

    def __init__(self, root):
        self.root = root
        self.root.title(PAGE_TITLE)
        
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg=COLOR_BG_MAIN)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        self.entries = {} 
        self.buttons = {}
        
        # --- Backend Variables Mapped Exactly from C++ Constructor ---
        self.coarseStep = 5.0
        self.fineStep = 0.2
        self.sigPower = -60.0
        self.cgutxPower = 0.0
        self.obpLink = 0

        self.build_ui()
        
        # Set initial UI states
        self.update_entry("SIG GEN POWER", f"{self.sigPower:.2f} dBm")
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
        self.create_header_btn(header, "Exit System ✖", self.safe_exit, COLOR_FAIL).grid(row=0, column=2, padx=20, sticky="e")

        # --- MAIN AREA ---
        main_frame = tk.Frame(self.root, bg=COLOR_BG_MAIN)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=30)
        main_frame.grid_columnconfigure(0, weight=1); main_frame.grid_columnconfigure(1, weight=1); main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        self.build_ip_rf_panel(main_frame, 0, 0)
        self.build_pulse_power_panel(main_frame, 0, 1)
        self.build_status_panel(main_frame, 0, 2)

    def create_panel_frame(self, parent, row_idx, col_idx, title):
        container = tk.Frame(parent, bg=COLOR_BG_MAIN)
        container.grid(row=row_idx, column=col_idx, sticky="nsew", padx=15)
        container.grid_columnconfigure(0, weight=1); container.grid_rowconfigure(1, weight=1)
        tk.Label(container, text=title, bg=COLOR_BG_MAIN, fg=COLOR_TEXT, font=FONT_PANEL_TITLE, anchor="center").grid(row=0, column=0, pady=(0, 8))
        card = tk.Frame(container, bg=COLOR_PANEL_BG, highlightbackground="#DADDDF", highlightthickness=1)
        card.grid(row=1, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1); card.grid_columnconfigure(1, weight=1)
        return card

    # =====================================================
    # PANEL 1: IP & RF (Col 0)
    # =====================================================
    def build_ip_rf_panel(self, parent, row_idx, col_idx):
        card = self.create_panel_frame(parent, row_idx, col_idx, "IP & RF CONTROLS")
        
        # FIX APPLIED HERE: Passed "42" and "98" directly as the 4th positional argument
        self.add_entry_row(card, 0, "IP CODE", "42", editable=True)
        self.add_entry_row(card, 1, "IP FREQ", "98", editable=True)
        
        self.buttons["IPSET"] = self.add_full_btn(card, 2, "IP SET", COLOR_ACCENT, self.on_ipsetPushButton_clicked)
        self.buttons["IP VAL"] = self.add_complex_entry_row(card, 3, "IP VAL", "IP VAL", self.on_ipvalPushButton_clicked)
        
        self.buttons["FIN1"] = self.add_full_btn(card, 4, "FIN 1", COLOR_WHITE, self.on_fin1PushButton_clicked, fg_color=COLOR_TEXT)
        self.buttons["FIN3"] = self.add_full_btn(card, 5, "FIN 3", COLOR_WHITE, self.on_fin3PushButton_clicked, fg_color=COLOR_TEXT)
        self.buttons["RFON"] = self.add_full_btn(card, 6, "SIG RF ON", COLOR_WHITE, self.on_rfonPushButton_clicked, fg_color=COLOR_TEXT)
        self.buttons["RFOFF"] = self.add_full_btn(card, 7, "SIG RF OFF", COLOR_ENTRY_BG, self.on_rfoffPushButton_clicked, fg_color=COLOR_TEXT)
        
        self.add_full_btn(card, 8, "SPECTRUM P", COLOR_ACCENT, lambda: self.readSaVal())

        for i in range(9): card.grid_rowconfigure(i, weight=1)

    # =====================================================
    # PANEL 2: PULSE & POWER (Col 1)
    # =====================================================
    def build_pulse_power_panel(self, parent, row_idx, col_idx):
        card = self.create_panel_frame(parent, row_idx, col_idx, "PULSE & POWER TUNING")
        
        self.add_entry_row(card, 0, "pAmplitude", "0.00 V")
        self.add_entry_row(card, 1, "pWidth", "0.00 nS")
        self.add_entry_row(card, 2, "pRiseTime", "0.00 nS")
        self.add_entry_row(card, 3, "pFallTime", "0.00 nS")
        
        self.buttons["PULSE"] = self.add_full_btn(card, 4, "PULSE CHAR", COLOR_ACCENT, self.on_pushButton_CGUpulse_clicked)

        # STC values are editable manually
        self.buttons["USTC"] = self.add_complex_entry_row(card, 5, "U-STC", "SET U-STC", self.on_setusctPushButton_clicked, editable=True, placeholder="0.0")
        self.buttons["DSTC"] = self.add_complex_entry_row(card, 6, "D-STC", "SET D-STC", self.on_setdsctPushButton_clicked, editable=True, placeholder="0.0")

        # Step sizes are editable manually
        self.add_tuning_row(card, 7, "FINE POWER", str(self.fineStep), self.on_finedownPushButton_clicked, self.on_fineupPushButton_clicked)
        self.add_tuning_row(card, 8, "COARSE POWER", str(self.coarseStep), self.on_coarsedownPushButton_clicked, self.on_coarseupPushButton_clicked)

        for i in range(9): card.grid_rowconfigure(i, weight=1)

    # =====================================================
    # PANEL 3: STATUS & RELAYS (Col 2)
    # =====================================================
    def build_status_panel(self, parent, row_idx, col_idx):
        card = self.create_panel_frame(parent, row_idx, col_idx, "SYSTEM STATUS & RELAYS")
        
        status_labels = [
            "SIG GEN POWER", "CGU TX FREQ", "CGU TX POWER", "OBP LINK", 
            "K1", "K2", "K3", "K4", "K5", "K6", "K7"
        ]

        for i, text in enumerate(status_labels):
            self.add_entry_row(card, i, text, "")
            card.grid_rowconfigure(i, weight=1)

    # =====================================================
    # UI HELPERS
    # =====================================================
    def add_entry_row(self, parent, row_idx, label_text, placeholder, editable=False):
        lbl = tk.Label(parent, text=label_text, bg=COLOR_PANEL_BG, fg=COLOR_LABEL_TEXT, font=FONT_LABEL, anchor="e")
        lbl.grid(row=row_idx, column=0, sticky="e", padx=(10, 10), pady=4)
        
        bg_color = "#FFFFFF" if editable else COLOR_ENTRY_BG
        relief_style = "solid" if editable else "flat"
        
        entry = tk.Entry(parent, font=FONT_VALUE, bg=bg_color, fg=COLOR_TEXT, justify="center", relief=relief_style, bd=1 if editable else 5, highlightthickness=0, width=12)
        entry.grid(row=row_idx, column=1, sticky="w", padx=(0, 20), pady=4, ipady=4)
        
        if placeholder:
            entry.insert(0, placeholder)
            
        if not editable: 
            entry.config(state="readonly")
            
        self.entries[label_text] = entry

    def add_full_btn(self, parent, row_idx, text, color, cmd, fg_color="white"):
        btn = tk.Button(parent, text=text, bg=color, fg=fg_color, font=FONT_LABEL, relief="ridge", bd=1, cursor="hand2", command=cmd)
        btn.grid(row=row_idx, column=0, columnspan=2, sticky="ew", padx=40, pady=6, ipady=4)
        return btn

    def add_complex_entry_row(self, parent, row_idx, label_text, btn_text, cmd, editable=False, placeholder=""):
        tk.Label(parent, text=label_text, bg=COLOR_PANEL_BG, fg=COLOR_LABEL_TEXT, font=FONT_LABEL, anchor="e").grid(row=row_idx, column=0, sticky="e", padx=(10, 10))
        container = tk.Frame(parent, bg=COLOR_PANEL_BG)
        container.grid(row=row_idx, column=1, sticky="w", padx=(0, 20))
        
        bg_color = "#FFFFFF" if editable else COLOR_ENTRY_BG
        relief_style = "solid" if editable else "flat"
        
        entry = tk.Entry(container, font=FONT_VALUE, bg=bg_color, fg=COLOR_TEXT, justify="center", relief=relief_style, bd=1 if editable else 5, highlightthickness=0, width=7)
        entry.pack(side="left", ipady=4, padx=(0, 5))
        
        if placeholder:
            entry.insert(0, placeholder)
            
        if not editable: 
            entry.config(state="readonly")
            
        self.entries[label_text] = entry
        btn = tk.Button(container, text=btn_text, bg=COLOR_ACCENT, fg="white", font=("Helvetica", 9, "bold"), relief="flat", cursor="hand2", bd=0, command=cmd)
        btn.pack(side="left", ipady=2, ipadx=4)
        return btn

    def add_tuning_row(self, parent, row_idx, label_text, default_val, cmd_down, cmd_up):
        tk.Label(parent, text=label_text, bg=COLOR_PANEL_BG, fg=COLOR_LABEL_TEXT, font=FONT_LABEL, anchor="e").grid(row=row_idx, column=0, sticky="e", padx=(10, 10))
        container = tk.Frame(parent, bg=COLOR_PANEL_BG)
        container.grid(row=row_idx, column=1, sticky="w", padx=(0, 20))
        
        entry = tk.Entry(container, font=FONT_VALUE, bg="#FFFFFF", fg=COLOR_TEXT, justify="center", relief="solid", bd=1, highlightthickness=0, width=6)
        entry.pack(side="left", ipady=4, padx=(0, 5))
        entry.insert(0, default_val)
        self.entries[label_text] = entry
        
        tk.Button(container, text="◀", bg="#65676B", fg="white", font=FONT_LABEL, relief="flat", cursor="hand2", bd=0, command=cmd_down).pack(side="left", padx=2, ipady=1, ipadx=4)
        tk.Button(container, text="▶", bg="#65676B", fg="white", font=FONT_LABEL, relief="flat", cursor="hand2", bd=0, command=cmd_up).pack(side="left", padx=2, ipady=1, ipadx=4)

    def create_header_btn(self, parent, text, command, color):
        return tk.Button(parent, text=text, bg=color, fg="white", font=("Helvetica", 11, "bold"), relief="flat", cursor="hand2", command=command, padx=20, bd=0)

    # ==============================================================================
    # ⚙️ BACKEND LOGIC PORTED FROM C++
    # ==============================================================================
    def init_hardware(self):
        print("[SYSTEM] Initializing SA CGU...")
        # Gpib.initSa()
        self.readSaVal()

    def on_ipsetPushButton_clicked(self):
        """ 
        Reads Code as Decimal (Base 10)
        Reads Freq as Hex (Base 16)
        Defaults to Code 42, Freq 0x98 if empty.
        """
        code_str = self.entries["IP CODE"].get().strip()
        freq_str = self.entries["IP FREQ"].get().strip()

        if code_str and freq_str:
            try:
                ipcode = int(code_str, 10) # Base 10
                ipfreq = int(freq_str, 16) # Base 16
            except ValueError:
                messagebox.showerror("Input Error", "IP CODE must be decimal. IP FREQ must be hexadecimal (e.g. 98 or 0x98).")
                self.buttons["IPSET"].config(bg=COLOR_FAIL)
                return
        else:
            # Fallbacks from C++
            ipcode = 42
            ipfreq = 0x98

        print(f"[HW TX] Serial.setIpcode(Freq: {hex(ipfreq)}, Code: {ipcode})")
        
        # Mock serial status
        status = random.choice([1, 0]) 
        
        if status == 1:
            self.buttons["IPSET"].config(bg=COLOR_SUCCESS)
            self.update_entry("OBP LINK", "UP")
            self.obpLink = 1
        else:
            self.buttons["IPSET"].config(bg=COLOR_FAIL)
            self.update_entry("OBP LINK", "DOWN")
            self.obpLink = 0

    def on_ipvalPushButton_clicked(self):
        ipByte = "42" # Mock read from hardware
        self.update_entry("IP VAL", ipByte)
        
        if ipByte:
            self.buttons["IP VAL"].config(bg=COLOR_SUCCESS)
            self.update_entry("OBP LINK", "UP")
            self.obpLink = 1
        else:
            self.buttons["IP VAL"].config(bg=COLOR_FAIL)
            self.update_entry("OBP LINK", "DOWN")
            self.obpLink = 0

    def on_fin1PushButton_clicked(self):
        self.buttons["FIN1"].config(bg=COLOR_ACTIVE_PINK, fg="black")
        self.buttons["FIN3"].config(bg=COLOR_WHITE, fg=COLOR_TEXT)
        print("[OPTO] FIN1 Activated")

    def on_fin3PushButton_clicked(self):
        self.buttons["FIN3"].config(bg=COLOR_ACTIVE_PINK, fg="black")
        self.buttons["FIN1"].config(bg=COLOR_WHITE, fg=COLOR_TEXT)
        print("[OPTO] FIN3 Activated")

    def on_rfonPushButton_clicked(self):
        self.buttons["RFON"].config(bg=COLOR_ACTIVE_PINK, fg="black")
        print("[GPIB] Signal RF ON")
        self.readSaVal()

    def on_rfoffPushButton_clicked(self):
        self.buttons["RFON"].config(bg=COLOR_WHITE, fg=COLOR_TEXT)
        print("[GPIB] Signal RF OFF")

    def on_setusctPushButton_clicked(self):
        """ Clamps to max 9.9 just like C++ """
        val_str = self.entries["U-STC"].get()
        if not val_str:
            val_str = "0.0"
            
        try:
            ustc1 = float(val_str)
            if ustc1 >= 10.0:
                ustc1 = 9.9
                self.update_entry_editable("U-STC", "9.9")
                
            print(f"[DAC] Write U-STC: {ustc1}")
            self.buttons["USTC"].config(bg=COLOR_SUCCESS)
            self.root.after(3000, self.readSaVal)
        except ValueError:
            self.buttons["USTC"].config(bg=COLOR_FAIL)

    def on_setdsctPushButton_clicked(self):
        """ Clamps to max 5.0 just like C++ """
        val_str = self.entries["D-STC"].get()
        if not val_str:
            val_str = "0.0"
            
        try:
            dstc1 = float(val_str)
            if dstc1 > 5.0:
                dstc1 = 5.0
                self.update_entry_editable("D-STC", "5.0")
                
            print(f"[DAC] Write D-STC: {dstc1}")
            self.buttons["DSTC"].config(bg=COLOR_SUCCESS)
            self.root.after(3000, self.readSaVal)
        except ValueError:
            self.buttons["DSTC"].config(bg=COLOR_FAIL)

    def update_power_steps(self):
        """ Dynamically read user changes to the step sizes """
        try: self.fineStep = float(self.entries["FINE POWER"].get())
        except: pass
        try: self.coarseStep = float(self.entries["COARSE POWER"].get())
        except: pass

    def apply_power_change(self, step_val):
        """ The math engine behind the arrows """
        self.sigPower += step_val
        self.update_entry("SIG GEN POWER", f"{self.sigPower:.2f} dBm")
        print(f"[GPIB] Sig RF Vary: {self.sigPower} dBm")
        self.root.after(3000, self.readSaVal)

    def on_finedownPushButton_clicked(self):
        self.update_power_steps()
        self.apply_power_change(-self.fineStep)

    def on_fineupPushButton_clicked(self):
        self.update_power_steps()
        self.apply_power_change(self.fineStep)

    def on_coarsedownPushButton_clicked(self):
        self.update_power_steps()
        self.apply_power_change(-self.coarseStep)

    def on_coarseupPushButton_clicked(self):
        self.update_power_steps()
        self.apply_power_change(self.coarseStep)

    def readSaVal(self):
        # Mocking Gpib.saPower(&power,&freq)
        power = random.uniform(-10, 10)
        freq = 9800000000.0 # 9.8 GHz in Hz
        
        self.update_entry("CGU TX POWER", f"{power:.2f} dBm")
        self.update_entry("CGU TX FREQ", f"{freq/1e9:.3f} GhZ")

    def on_pushButton_CGUpulse_clicked(self):
        self.buttons["PULSE"].config(bg=COLOR_ACTIVE_PINK, fg="black")
        self.update_entry("pAmplitude", "Wait")
        self.update_entry("pWidth", "Wait")
        self.update_entry("pFallTime", "Wait")
        self.update_entry("pRiseTime", "Wait -")
        
        print("[GPIB] Config OSC CGU Pulse...")
        self.root.after(1500, self._finish_pulse_measure)

    def _finish_pulse_measure(self):
        pulseAmp = 5.12
        pulseWidth = 0.000000120   # 120 nS in Seconds
        pulseFallTime = 0.000000015  # 15 nS
        pulseRiseTime = 0.000000014  # 14 nS

        self.update_entry("pAmplitude", f"{pulseAmp:.2f} V")
        self.update_entry("pWidth", f"{pulseWidth * 1e9:.2f} nS")
        self.update_entry("pFallTime", f"{pulseFallTime * 1e9:.2f} nS")
        self.update_entry("pRiseTime", f"{pulseRiseTime * 1e9:.2f} nS")
        
        self.buttons["PULSE"].config(bg=COLOR_ACCENT, fg="white")

    def update_entry(self, key, text):
        entry = self.entries.get(key)
        if entry:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, text)
            entry.config(state="readonly")

    def update_entry_editable(self, key, text):
        entry = self.entries.get(key)
        if entry:
            entry.delete(0, tk.END)
            entry.insert(0, text)

    def open_dashboard(self):
        self.safe_exit(prompt=False)
        subprocess.Popen(["python3", "ManualDashboard.py"])

    def safe_exit(self, prompt=True):
        if not prompt or messagebox.askyesno("Confirm Exit", "Shut down the system?"):
            print("[GPIB] Sig RF OFF")
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CGUChecksGUI(root)
    root.mainloop()
