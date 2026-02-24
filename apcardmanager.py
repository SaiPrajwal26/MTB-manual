import ctypes
import time
import channel
from limits import Limits

class APCardManager:
    def __init__(self):
        self.card = ctypes.CDLL("libacromag.so")
        self.limits = Limits()

    def ap_open(self):
        return self.card.ap_open()

    def ap_close(self):
        return self.card.ap_close()

    def ap_read_di(self, ch):
        return self.card.ap_read_di(ch)

    def ap_write_do(self, ch, value):
        return self.card.ap_write_do(ch, value)

    def ap_read_ai(self, ch):
        return self.card.ap_read_ai(ch)
        
    def ap_write_opto_do(self, ch, value):
        return self.card.ap_write_opto_do(ch, value)

    # ==========================================
    # POWER SUBSYSTEM (manualpowerwindow)
    # ==========================================
    def sam_coil_on(self):
        self.ap_write_do(channel.SAM_COIL_OFF, 0)
        self.ap_write_do(channel.SAM_COIL_ON, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.SAM_COIL_ON, 0)
        time.sleep(0.2)
        return self.ap_read_di(channel.SAM_COIL_STATUS)

    def sam_coil_off(self):
        self.ap_write_do(channel.SAM_COIL_ON, 0)
        self.ap_write_do(channel.SAM_COIL_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.SAM_COIL_OFF, 0)
        time.sleep(0.2)
        return self.ap_read_di(channel.SAM_COIL_STATUS)

    def obp_on(self):
        self.ap_write_do(channel.OBP_OFF, 0)
        self.ap_write_do(channel.OBP_ON, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.OBP_ON, 0)
        time.sleep(0.2)
        return self.ap_read_di(channel.OBP_STATUS)

    def obp_off(self):
        self.ap_write_do(channel.OBP_ON, 0)
        self.ap_write_do(channel.OBP_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.OBP_OFF, 0)
        time.sleep(0.2)
        return self.ap_read_di(channel.OBP_STATUS)

    def tm_on(self):
        self.ap_write_do(channel.TM_OFF, 0)
        self.ap_write_do(channel.TM_ON, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.TM_ON, 0)
        time.sleep(0.2)
        return self.ap_read_di(channel.TM_STATUS)

    def tm_off(self):
        self.ap_write_do(channel.TM_ON, 0)
        self.ap_write_do(channel.TM_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.TM_OFF, 0)
        time.sleep(0.2)
        return self.ap_read_di(channel.TM_STATUS)

    def scu_on(self):
        self.ap_write_do(channel.SCU_OFF, 0)
        self.ap_write_do(channel.SCU_ON, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.SCU_ON, 0)
        time.sleep(0.2)
        return self.ap_read_di(channel.SCU_STATUS)

    def scu_off(self):
        self.ap_write_do(channel.SCU_ON, 0)
        self.ap_write_do(channel.SCU_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.SCU_OFF, 0)
        time.sleep(0.2)
        return self.ap_read_di(channel.SCU_STATUS)

    def cgu_on(self):
        self.ap_write_do(channel.CGU_OFF, 0)
        self.ap_write_do(channel.CGU_ON, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.CGU_ON, 0)
        time.sleep(0.2)
        return self.ap_read_di(channel.CGU_STATUS)

    def cgu_off(self):
        self.ap_write_do(channel.CGU_ON, 0)
        self.ap_write_do(channel.CGU_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.CGU_OFF, 0)
        time.sleep(0.2)
        return self.ap_read_di(channel.CGU_STATUS)

    def rpf_on(self):
        self.ap_write_do(channel.RPF_OFF, 0)
        self.ap_write_do(channel.RPF_ON, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.RPF_ON, 0)
        time.sleep(0.2)
        return self.ap_read_di(channel.RPF_STATUS)

    def rpf_off(self):
        self.ap_write_do(channel.RPF_ON, 0)
        self.ap_write_do(channel.RPF_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.RPF_OFF, 0)
        time.sleep(0.2)
        return self.ap_read_di(channel.RPF_STATUS)

    def ips_on(self):
        self.ap_write_do(channel.IPS_OFF, 0)
        self.ap_write_do(channel.IPS_ON, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.IPS_ON, 0)
        time.sleep(0.2)
        return self.ap_read_di(channel.IPS_STATUS)

    def ips_off(self):
        self.ap_write_do(channel.IPS_ON, 0)
        self.ap_write_do(channel.IPS_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.IPS_OFF, 0)
        time.sleep(0.2)
        return self.ap_read_di(channel.IPS_STATUS)

    # ==========================================
    # PYRO SUBSYSTEM (manualpyrowindow)
    # ==========================================
    def pyro_ps_on(self):
        self.ap_write_do(channel.PYRO_PS_OFF, 0)
        self.ap_write_do(channel.PYRO_PS_ON, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.PYRO_PS_ON, 0)
        time.sleep(0.5)
        return self.ap_read_di(channel.PYRO_PS_STATUS)

    def pyro_ps_off(self):
        self.ap_write_do(channel.PYRO_PS_ON, 0)
        self.ap_write_do(channel.PYRO_PS_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.PYRO_PS_OFF, 0)
        time.sleep(0.5)
        return self.ap_read_di(channel.PYRO_PS_STATUS)

    def gnd_pyro_arm(self):
        self.ap_write_do(channel.BOOSTER_GND_RELAY, 1)
        self.ap_write_do(channel.THAB_GND_RELAY, 1)

    def gnd_pyro_safe(self):
        self.ap_write_do(channel.BOOSTER_GND_RELAY, 0)
        self.ap_write_do(channel.THAB_GND_RELAY, 0)

    def ne_pyro_arm(self):
        self.ap_write_do(channel.NOZZLE_PYRO_RELAY_SAFE, 0)
        self.ap_write_do(channel.NOZZLE_PYRO_RELAY_ARM, 1)
        time.sleep(0.1)
        return self.ap_write_do(channel.NOZZLE_PYRO_RELAY_ARM, 0)

    def ne_pyro_safe(self):
        self.ap_write_do(channel.NOZZLE_PYRO_RELAY_ARM, 0)
        self.ap_write_do(channel.NOZZLE_PYRO_RELAY_SAFE, 1)
        time.sleep(0.1)
        return self.ap_write_do(channel.NOZZLE_PYRO_RELAY_SAFE, 0)

    def booster_fire(self):
        self.ap_write_do(channel.BOOSTER_FIRE, 1)
        time.sleep(5.0)
        self.ap_write_do(channel.BOOSTER_FIRE, 0)

    def thbatt_fire(self):
        self.ap_write_do(channel.THBATTERY_FIRE, 1)
        time.sleep(5.0)
        self.ap_write_do(channel.THBATTERY_FIRE, 0)

    def airbottle_fire(self):
        self.ap_write_do(channel.AIRBOTTLE_FIRE, 1)
        time.sleep(5.0)
        self.ap_write_do(channel.AIRBOTTLE_FIRE, 0)

    def pr_switch_close(self):
        self.ap_write_do(channel.PR_SWITCH_OFF, 0)
        self.ap_write_do(channel.PR_SWITCH_ON, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.PR_SWITCH_ON, 0)
        return self.ap_read_di(channel.PR_SWITCH_STATUS)

    def pr_switch_open(self):
        self.ap_write_do(channel.PR_SWITCH_ON, 0)
        self.ap_write_do(channel.PR_SWITCH_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.PR_SWITCH_OFF, 0)
        return self.ap_read_di(channel.PR_SWITCH_STATUS)

    def all_safe(self):
        self.ap_write_do(channel.BOOSTER_GND_RELAY, 0)
        self.ap_write_do(channel.THAB_GND_RELAY, 0)
        self.ap_write_do(channel.NOZZLE_PYRO_RELAY_ARM, 0)
        self.ap_write_do(channel.NOZZLE_PYRO_RELAY_SAFE, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.NOZZLE_PYRO_RELAY_SAFE, 0)
        self.ap_write_do(channel.PYRO_PS_ON, 0)
        self.ap_write_do(channel.PYRO_PS_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.PYRO_PS_OFF, 0)
        self.ap_write_do(channel.IPS_ON, 0)
        self.ap_write_do(channel.IPS_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.IPS_OFF, 0)
        self.ap_write_do(channel.PR_SWITCH_ON, 0)
        self.ap_write_do(channel.PR_SWITCH_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.PR_SWITCH_OFF, 0)

    # ==========================================
    # CGU / OPTO SUBSYSTEM (manualcguwindow)
    # ==========================================
    def cgu_fin1_on(self):
        self.ap_write_opto_do(channel.CGUTX3, 1)
        self.ap_write_opto_do(channel.CGUTX1, 0)
        self.ap_write_opto_do(channel.CGURX3, 1)
        self.ap_write_opto_do(channel.CGURX1, 0)

    def cgu_fin3_on(self):
        self.ap_write_opto_do(channel.CGUTX1, 1)
        self.ap_write_opto_do(channel.CGUTX3, 0)
        self.ap_write_opto_do(channel.CGURX1, 1)
        self.ap_write_opto_do(channel.CGURX3, 0)

    # ==========================================
    # RPF SUBSYSTEM (manualrpfwindow)
    # ==========================================
    def set_delay_opto(self, delay_ch):
        for p in range(8):
            self.ap_write_opto_do(p, 1)
        time.sleep(0.1)
        self.ap_write_opto_do(delay_ch, 0)

    def rpf_tx1_on(self):
        self.ap_write_opto_do(channel.RPFTX2, 1)
        self.ap_write_opto_do(channel.RPFTX1, 0)

    def rpf_tx2_on(self):
        self.ap_write_opto_do(channel.RPFTX1, 1)
        self.ap_write_opto_do(channel.RPFTX2, 0)

    def g_switch_on(self):
        self.ap_write_do(channel.G_SWITCH_CLOSE, 1)

    def g_switch_off(self):
        self.ap_write_do(channel.G_SWITCH_CLOSE, 0)

    def k8_relay_on(self):
        self.ap_write_do(channel.K8OFF, 0)
        self.ap_write_do(channel.K8ON, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.K8ON, 0)

    def k8_relay_off(self):
        self.ap_write_do(channel.K8ON, 0)
        self.ap_write_do(channel.K8OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.K8OFF, 0)

    # RPF Attenuators
    def atten_1db_on(self):
        self.ap_write_do(channel.A1DB_OFF, 0)
        self.ap_write_do(channel.A1DB_ON, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.A1DB_ON, 0)

    def atten_1db_off(self):
        self.ap_write_do(channel.A1DB_ON, 0)
        self.ap_write_do(channel.A1DB_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.A1DB_OFF, 0)

    def atten_2db_on(self):
        self.ap_write_do(channel.A2DB_OFF, 0)
        self.ap_write_do(channel.A2DB_ON, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.A2DB_ON, 0)

    def atten_2db_off(self):
        self.ap_write_do(channel.A2DB_ON, 0)
        self.ap_write_do(channel.A2DB_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.A2DB_OFF, 0)

    def atten_4db_on(self):
        self.ap_write_do(channel.A4DB_OFF, 0)
        self.ap_write_do(channel.A4DB_ON, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.A4DB_ON, 0)

    def atten_4db_off(self):
        self.ap_write_do(channel.A4DB_ON, 0)
        self.ap_write_do(channel.A4DB_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.A4DB_OFF, 0)

    def atten_4db1_on(self):
        self.ap_write_do(channel.A4DB1_OFF, 0)
        self.ap_write_do(channel.A4DB1_ON, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.A4DB1_ON, 0)

    def atten_4db1_off(self):
        self.ap_write_do(channel.A4DB1_ON, 0)
        self.ap_write_do(channel.A4DB1_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.A4DB1_OFF, 0)

    def atten_10db_on(self):
        self.ap_write_do(channel.A10DB_OFF, 0)
        self.ap_write_do(channel.A10DB_ON, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.A10DB_ON, 0)

    def atten_10db_off(self):
        self.ap_write_do(channel.A10DB_ON, 0)
        self.ap_write_do(channel.A10DB_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.A10DB_OFF, 0)

    def atten_20db_on(self):
        self.ap_write_do(channel.A20DB_OFF, 0)
        self.ap_write_do(channel.A20DB_ON, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.A20DB_ON, 0)

    def atten_20db_off(self):
        self.ap_write_do(channel.A20DB_ON, 0)
        self.ap_write_do(channel.A20DB_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.A20DB_OFF, 0)

    def atten_30db_on(self):
        self.ap_write_do(channel.A30DB_OFF, 0)
        self.ap_write_do(channel.A30DB_ON, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.A30DB_ON, 0)

    def atten_30db_off(self):
        self.ap_write_do(channel.A30DB_ON, 0)
        self.ap_write_do(channel.A30DB_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.A30DB_OFF, 0)

    def atten_30db1_on(self):
        self.ap_write_do(channel.A30DB1_OFF, 0)
        self.ap_write_do(channel.A30DB1_ON, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.A30DB1_ON, 0)

    def atten_30db1_off(self):
        self.ap_write_do(channel.A30DB1_ON, 0)
        self.ap_write_do(channel.A30DB1_OFF, 1)
        time.sleep(0.1)
        self.ap_write_do(channel.A30DB1_OFF, 0)
