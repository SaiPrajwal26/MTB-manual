import time
import sys
import pyvisa

TDK_LAMBDA = 1
powerSupplyType = TDK_LAMBDA
EXPORT_VER = False

OSC_IP = "192.168.1.12" 
FC_IP = "192.168.1.10"
AWG_IP = "192.168.1.11"
POWM_IP = "192.168.1.8"
SIG_IP = "192.168.1.9"
EXT_PS_IP = "192.168.1.3"
STS_PS_IP = "192.168.1.4"
TX_PS_IP = "192.168.1.5" 

PRECISION = 0.00001
FMAX = 5.7e9
FMIN = 5.6e9

class instr:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.defaultRM = self.rm
        self.osc = None
        self.sig = None
        self.awg = None
        self.fc = None
        self.powm = None
        self.extps = None
        self.stsps = None
        self.txps = None

    def __del__(self):
        self.close()

    def delay(self, d_ms):
        time.sleep(d_ms / 1000.0)

    def WaitForOperationComplete(self, instrSession):
        try:
            instrSession.write("*OPC")
            while True:
                response = int(instrSession.query("*ESR?").strip())
                if (response & 1) == 1:
                    break
                time.sleep(0.005)
        except pyvisa.VisaIOError:
            pass

    def close(self):
        for inst in [self.sig, self.osc, self.awg, self.powm, self.fc]:
            try:
                if inst:
                    inst.close()
            except Exception:
                pass

        if powerSupplyType == TDK_LAMBDA:
            self.ExtPsClose()
            self.StsPsClose()
            try:
                if self.txps:
                    self.txps.close()
            except Exception:
                pass

        try:
            self.rm.close()
        except Exception:
            pass

    def initGpib(self):
        for fn in [self.initAwgCont, self.initPowm, self.initSig, self.initOsc, self.initFreqCounter]:
            ret = fn()
            if ret != 0:
                return ret

        if powerSupplyType == TDK_LAMBDA:
            for fn in [self.initExtPs, self.initStsPs, self.initTxPS]:
                ret = fn()
                if ret != 0:
                    return ret

        print("instr: All Instr Opened")
        return 0

    def initOsc(self):
        try:
            visa_address = f"TCPIP0::{OSC_IP}::inst0::INSTR"
            self.osc = self.rm.open_resource(visa_address, open_timeout=100)
            self.osc.write("*RST")
            print("instr: OSC Instr Opened")
            return 0
        except Exception as e:
            print("instr: OSC Instr NOT Opened:", e)
            return 1

    def initSig(self):
        try:
            visa_address = f"TCPIP0::{SIG_IP}::inst0::INSTR"
            self.sig = self.rm.open_resource(visa_address, open_timeout=100)
            self.sig.write("*RST")
            self.sig.write("POWER -20DBM")
            
            if EXPORT_VER:
                self.sig.write("FREQ 9.34GHZ")
            else:
                self.sig.write("FREQ 9.32GHZ")
                
            self.sig.write(":POW:ALC OFF")
            self.sig.write("PULM:SOUR EXT")
            self.sig.write("PULM:EXT:POL NORM")
            self.sig.write("PULM:STAT ON")
            self.sig.write("DISP OFF")
            print("instr: SIG GEN Instr Opened")
            return 0
        except Exception as e:
            print("instr: SIG GEN Instr NOT Opened:", e)
            return 2

    def initAwgCont(self):
        try:
            visa_address = f"TCPIP0::{AWG_IP}::inst0::INSTR"
            self.awg = self.rm.open_resource(visa_address, open_timeout=100)
            self.awg.write("*RST")
            self.awg.write("DISP OFF")
            self.awg.write("FUNC SQU")
            self.awg.write("FREQ 16MHZ")
            self.awg.write("VOLT 5.0VPP")
            self.awg.write("VOLT:OFFSET 0")
            self.awg.write("OUTP:STAT ON")
            print("instr: AWG Instr Opened")
            return 0
        except Exception as e:
            print("instr: AWG NOT opened:", e)
            return 3
            
    def initAwgTrig(self):
        try:
            visa_address = f"TCPIP0::{AWG_IP}::inst0::INSTR"
            self.awg = self.rm.open_resource(visa_address, open_timeout=100)
            self.awg.write("*RST")
            self.WaitForOperationComplete(self.awg)
            self.awg.write("DISP ON")
            self.awg.write("FUNC SQU")
            self.awg.write("FREQ 16MHZ")
            self.awg.write("VOLT 5.0VPP")
            self.awg.write("VOLT:OFFSET 0")
            self.awg.write("BURS:MODE TRIG")
            self.awg.write("BURS:NCYC 80000")
            self.awg.write("TRIG:SOUR BUS")
            self.awg.write("TRIG:SLOP POS")
            self.WaitForOperationComplete(self.awg)
            self.awg.write("BURS:STAT ON")
            self.awg.write("OUTP:STAT ON")
            return 0
        except Exception as e:
            print("instr: AWG TRIG NOT opened:", e)
            return 4

    def initPowm(self):
        try:
            visa_address = f"TCPIP0::{POWM_IP}::inst0::INSTR"
            self.powm = self.rm.open_resource(visa_address, open_timeout=100)
            self.powm.write("*RST")
            print("instr: POWM opened")
            return 0
        except Exception as e:
            print("instr: POWM NOT opened:", e)
            return 6

    def initFreqCounter(self):
        try:
            visa_address = f"TCPIP0::{FC_IP}::inst0::INSTR"
            self.fc = self.rm.open_resource(visa_address, open_timeout=100)
            self.fc.write("*RST")
            self.fc.write("DISP OFF")
            self.fc.write(":CONF:FREQ:BURS (@3)")
            self.fc.write(":INP:BURS:LEV -6")
            self.fc.write(":SENS:FREQ:BURS:GATE:NARR ON")
            self.fc.write(":SENS:FREQ:BURS:GATE:AUTO ON")
            self.fc.write("SENS:ROSC:SOUR:AUTO OFF")
            self.fc.write("SENS:ROSC:SOUR INT")
            print("instr: FC opened")
            return 0
        except Exception as e:
            print("instr: FC NOT opened:", e)
            return 7

    def initExtPs(self): 
        try:
            visa_address = f"TCPIP0::{EXT_PS_IP}::inst0::INSTR"
            self.extps = self.rm.open_resource(visa_address, open_timeout=100)
            self.extps.write("*RST")
            self.delay(200)
            
            if EXPORT_VER:
                self.extps.write(f"VOLT {28.00:.2f}")
                self.delay(200)
                self.extps.write(f"CURR {8.00:.2f}")
            else:
                self.extps.write(f"VOLT {31.00:.2f}")
                self.delay(200)
                self.extps.write(f"CURR {12.00:.2f}")
                
            self.delay(100)
            return 0
        except Exception as e:
            print("instr: ExtPs NOT opened:", e)
            return 8

    def ExtPsOff(self):
        if self.extps: self.extps.write("OUTP OFF")
    
    def ExtPsOn(self):
        if self.extps: self.extps.write("OUTPUT:STATE 1")

    def ExtPsVolMes(self):
        return float(self.extps.query("MEASURE:VOLTAGE?"))

    def ExtPsCurMes(self):
        return float(self.extps.query("MEAS:CURR?"))

    def ExtPsStatusCheck(self):
        try:
            self.extps.query("*STB?")
            return 0
        except Exception:
            return 7

    def ExtPsClose(self):
        if self.extps:
            self.extps.write("OUTPUT:STATE 0")
            self.extps.close()

    def initStsPs(self):
        try:
            visa_address = f"TCPIP0::{STS_PS_IP}::inst0::INSTR"
            self.stsps = self.rm.open_resource(visa_address, open_timeout=100)
            self.stsps.write("*RST")
            self.delay(200)
            self.stsps.write(f"VOLT {5.00:.2f}")
            self.delay(200)
            self.stsps.write(f"CURR {3.00:.2f}")
            self.delay(100)
            return 0
        except Exception as e:
            print("instr: StsPs NOT opened:", e)
            return 9

    def StsPsOff(self):
        if self.stsps: self.stsps.write("OUTP OFF")
    
    def StsPsOn(self):
        if self.stsps: self.stsps.write("OUTP ON")

    def StsPsVolMes(self):
        return float(self.stsps.query("MEAS:VOLT?"))

    def StsPsCurMes(self):
        return float(self.stsps.query("MEAS:CURR?"))

    def StsPsClose(self):
        if self.stsps:
            self.stsps.write("OUTPUT:STATE 0")
            self.stsps.close()

    def initTxPS(self):
        try:
            visa_address = f"TCPIP0::{TX_PS_IP}::inst0::INSTR"
            self.txps = self.rm.open_resource(visa_address, open_timeout=100)
            self.txps.write("*RST")
            self.delay(200)
            self.txps.write(f"VOLT {60.00:.2f}")
            self.delay(200)
            self.txps.write(f"CURR {12.00:.2f}")
            return 0
        except Exception as e:
            print("instr: TxPS NOT opened:", e)
            return 10

    def txPsOff(self):
        if self.txps: self.txps.write("OUTP OFF")

    def txPsOn(self):
        if self.txps: self.txps.write("OUTP ON")
        
    def txPsVolMes(self):
        return float(self.txps.query("MEAS:VOLT?"))
    
    def txPsCurMes(self):
        return float(self.txps.query("MEAS:CURR?"))

    def txPsStatusCheck(self):
        try:
            self.txps.query("*STB?")
            return 0
        except Exception:
            return 7

    def configOscCgu(self):
        self.osc.write("*RST")
        self.WaitForOperationComplete(self.osc)
        self.osc.write(":BLANK")
        self.osc.write(":CHAN1:DISP ON")
        self.osc.write(":CHAN1:IMP FIFT")
        self.osc.write(":CHAN1:PROB 1")
        self.osc.write(":CHAN1:COUP DC")
        self.osc.write(":CHAN1:SCAL 300mV")
        self.osc.write(":CHAN1:OFFS -900mV")
        self.osc.write(":TIM:REF CENT")
        self.osc.write(":TIM:SCAL 2E-7")
        self.osc.write(":TIM:MODE MAIN")

    def configOscCguPulse(self):
        self.osc.write(":TRIG:TV:SOURCE CHAN1")
        self.osc.write(":TRIG:SWE NORM")
        self.osc.write(":TRIG:MODE EDGE")
        self.osc.write(":TRIG:EDGE:SLOP NEG")
        self.osc.write(":TRIG:LEV -100mV")

    def configOscCguPulseCapture(self):
        self.osc.write(":CHAN1:IMP FIFT")
        self.osc.write(":TRIG:MODE EDGE")
        self.osc.write(":TRIGger:EDGE:SOURce CHANnel1")
        self.osc.write(":TRIG:LEV -500mV")
        self.osc.write(":TRIG:EDGE:SLOP NEG")
        self.osc.write(":TRIG:SWE NORM")

    def configOscContLeft(self):
        self.osc.write("*RST")
        self.WaitForOperationComplete(self.osc)
        self.osc.write(":BLANK")
        self.osc.write(":CHAN2:DISP ON")
        self.osc.write(":TIM:SCAL 50E-3")
        self.osc.write(":CHAN2:SCAL 5V")
    
    def configOscContRight(self):
        self.osc.write("*RST")
        self.WaitForOperationComplete(self.osc)
        self.osc.write(":BLANK")
        self.osc.write(":CHAN3:DISP ON")
        self.osc.write(":TIM:SCAL 50E-3")
        self.osc.write(":CHAN3:SCAL 5V")
    
    def configOscPulseLeft(self):
        self.osc.write("*RST")
        self.WaitForOperationComplete(self.osc)
        self.osc.write(":BLANK")
        self.osc.write(":CHAN2:DISP ON")
        self.osc.write(":TIM:SCAL 5E-2")
        self.osc.write(":TRIG:SWE NORM")
        self.osc.write(":TRIG:MODE EDGE")
        self.osc.write(":TRIG:SOUR CHAN2")
        self.osc.write("TRIG:EDGE:SLOPE POS")
        self.osc.write("TRIG:LEV 8.63V")
        self.WaitForOperationComplete(self.osc)
    
    def configOscPulseRight(self):
        self.osc.write("*RST")
        self.WaitForOperationComplete(self.osc)
        self.osc.write(":BLANK")
        self.osc.write(":CHAN3:DISP ON")
        self.osc.write(":TIM:SCAL 5E-2")
        self.osc.write(":TRIG:SWE NORM")
        self.osc.write(":TRIG:MODE EDGE")
        self.osc.write(":TRIG:SOUR CHAN3")
        self.osc.write("TRIG:EDGE:SLOPE POS")
        self.osc.write("TRIG:LEV 8.63V")
        self.WaitForOperationComplete(self.osc)

    def oscMeasure(self):
        pAmp = 0.0
        pwidth = -1.0
        ft = -1.0
        rt = -1.0
        count = 0
        pwidth_tot = 0.0

        self.configOscCgu()
        self.configOscCguPulseCapture()
        self.WaitForOperationComplete(self.osc)

        for _ in range(3):
            status = 0
            retryCount = 0
            
            self.osc.write(":SING")
            self.delay(1000)
            
            start = time.monotonic()

            while status == 0:
                reg = int(self.osc.query(":OPERegister:CONDition?").strip())
                runFlag = reg & 0x0008

                if runFlag == 0:
                    self.osc.write(":MEAS:VAMP CHAN1")
                    self.WaitForOperationComplete(self.osc)
                    
                    pAmp = float(self.osc.query(":MEAS:VAMP? CHAN1"))

                    self.osc.write(":MEAS:NWIDTH CHAN1")
                    self.osc.write(":MEAS:FALL CHAN1")
                    self.osc.write(":MEAS:RIS CHAN1")
                    self.WaitForOperationComplete(self.osc)

                    pwidth = float(self.osc.query(":MEAS:NWIDTH? CHAN1"))
                    ft = float(self.osc.query(":MEAS:FALL? CHAN1"))
                    rt = float(self.osc.query(":MEAS:RIS? CHAN1"))

                    if 2e-7 < pwidth < 4e-7:
                        status = 1
                        break
                    else:
                        break

                elapsed_ms = (time.monotonic() - start) * 1000
                if elapsed_ms > 2000:
                    if retryCount == 0:
                        self.osc.write(":CHAN1:SCAL 100mV")
                        self.osc.write(":CHAN1:OFFS -300mV")
                        self.osc.write(":TRIG:LEV -200mV")
                    else:
                        self.osc.write(":CHAN1:SCAL 50mV")
                        self.osc.write(":CHAN1:OFFS -150mV")
                        self.osc.write(":TRIG:LEV -100mV")

                    retryCount += 1
                    if retryCount == 3:
                        break
                    self.delay(200)

                self.delay(100)

            if status == 1:
                count += 1
                pwidth_tot += pwidth
                pwidth = pwidth_tot / count

        self.delay(2000)
        return pAmp, pwidth, ft, rt

    def oscMeasureE2NV(self):
        try:
            self.osc.write(":DVM:MODE ACRMs")
            self.osc.write(":DVM:ENABle ON")
            self.osc.write(":DVM:SOUR CHAN4")
            return float(self.osc.query(":MEAS:VRMS? CHAN4"))
        except Exception:
            return -1.0

    def firingPulseOscAmplitudeLeft(self):
        fpAmp = 0.0
        fpWidth = 0.0
        TIMEOUT = 5000 
        
        self.configOscPulseLeft()   
        self.osc.write(":SING")
        self.delay(2000)  
        
        self.awg.write("TRIG")
        self.WaitForOperationComplete(self.awg)
        
        start_time = time.monotonic()
        elapsed = 0
        
        while elapsed <= TIMEOUT:
            varQueryResult = int(self.osc.query(":OPERegister:CONDition?").strip())
            runFlag = varQueryResult & 0x0008
            
            if runFlag == 0:
                break
            else:
                self.delay(100)
                elapsed = (time.monotonic() - start_time) * 1000
                
        if elapsed < TIMEOUT:
            self.osc.write(":MEAS:VAMP CHAN2")
            self.osc.write(":MEAS:PWIDTH CHAN2")
            self.WaitForOperationComplete(self.osc)
            fpAmp = float(self.osc.query(":MEAS:VAMP? CHAN2"))
            fpWidth = float(self.osc.query(":MEAS:PWIDTH? CHAN2"))
            return 1, fpAmp, fpWidth
        else:
            self.configOscPulseLeft()
            return 0, -1.0, -1.0

    def firingPulseOscAmplitudeRight(self):
        fpAmp = 0.0
        fpWidth = 0.0
        TIMEOUT = 5000 
        
        self.configOscPulseRight()  
        self.osc.write(":SING")
        self.delay(2000)
        
        self.awg.write("*TRG")
        self.WaitForOperationComplete(self.awg)
        
        start_time = time.monotonic()
        elapsed = 0
        
        while elapsed <= TIMEOUT:
            varQueryResult = int(self.osc.query(":OPERegister:CONDition?").strip())
            runFlag = varQueryResult & 0x0008
            
            if runFlag == 0:   
                break
            else:
                self.delay(100)
                elapsed = (time.monotonic() - start_time) * 1000

        if elapsed < TIMEOUT:
            self.osc.write(":MEAS:VAMP CHAN3")
            self.osc.write(":MEAS:PWIDTH CHAN3")
            self.WaitForOperationComplete(self.osc)
            fpAmp = float(self.osc.query(":MEAS:VAMP? CHAN3"))
            fpWidth = float(self.osc.query(":MEAS:PWIDTH? CHAN3"))
            return 1, fpAmp, fpWidth
        else:
            self.configOscPulseRight()
            return 0, -1.0, -1.0

    def measureFrequency(self):
        retryCount = 0
        frequency = 0.0
        while retryCount < 2:
            self.fc.write("READ")
            self.WaitForOperationComplete(self.fc)
            frequency = float(self.fc.query("READ?"))

            if FMIN - PRECISION <= frequency <= FMAX + PRECISION:
                break

            retryCount += 1
            self.delay(100)

        return frequency

    def powmPower(self):
        self.powm.write("MEAS1")
        return float(self.powm.query("MEAS1?"))
    
    def skrpowmPower(self):
        self.powm.write("MEAS2")
        return float(self.powm.query("MEAS2?"))

    def sigRfVary(self, power):
        if power >= 0:
            power = 0
        self.sig.write(f"POWER {power:.2f}DBM")

    def sigRfOn(self):
        self.sig.write("OUTP:STAT ON")

    def sigRfOff(self):
        self.sig.write("OUTP:STAT OFF")

    def awgContoff(self):
        self.awg.write("OUTP:STAT OFF")
    
    def awgConton(self):
        self.awg.write("OUTP:STAT ON")
    
    def genAwgTrigger(self):
        self.awg.write("TRIG")

    def displayGpibError(self, error: int):
        error_map = {
            1: "UNABLE TO CONNECT WITH OSCILLOSCOPE",
            2: "UNABLE TO CONNECT WITH SIGNAL GENERATOR",
            3: "UNABLE TO CONNECT WITH AWG (CONT)",
            4: "UNABLE TO CONNECT WITH AWG (TRIG)",
            5: "UNABLE TO CONNECT WITH SPECTRUM ANALYZER",
            6: "UNABLE TO CONNECT WITH POWERMETER",
            7: "UNABLE TO CONNECT WITH FREQUENCY COUNTER",
            8: "UNABLE TO CONNECT WITH 28V EXT PS",
            9: "UNABLE TO CONNECT WITH 5V STATUS PS",
            10: "UNABLE TO CONNECT WITH TX POWER SUPPLY"
        }
        message = error_map.get(error, "UNKNOWN ERROR OCCURRED IN GPIB")
        print(f"\nCRITICAL ERROR: {message}")
        print("PROGRAM CAN'T PROCEED FURTHER. QUITTING PROGRAM.")
        sys.exit(0)
