import smbus
import time

def get_pichondria_address():
    bus = smbus.SMBus(1)
    pichondria_address = bus.read_byte_data(0x50, 0x99)
    bus.close()
    return(pichondria_address)

def set_pichondria_address(address):
    try:
        bus = smbus.SMBus(1)
        old_address = get_pichondria_address()
        bus.write_byte_data(0x50, 0x99, address)
        time.sleep(0.1)
        bus.write_byte_data(old_address, 0x07, 0x01)
        time.sleep(3)
        bus.close()
        return True
    except:
        return False

def input_availability_ad(pichondria_address):
    bus = smbus.SMBus(1)
    response = bus.read_byte_data(pichondria_address,0x02)
    bus.close()
    if (response == 1):
        return True
    else:
        return False
    
def input_availability():
    bus = smbus.SMBus(1)
    pichondria_address = bus.read_byte_data(0x50, 0x99)
    response = bus.read_byte_data(pichondria_address,0x02)
    bus.close()
    if (response == 1):
        return True
    else:
        return False
    
def is_charging_ad(pichondria_address):
    bus = smbus.SMBus(1)
    response = bus.read_byte_data(pichondria_address,0x03)
    bus.close()
    if (response == 1):
        return True
    else:
        return False
    
def is_charging():
    bus = smbus.SMBus(1)
    pichondria_address = bus.read_byte_data(0x50, 0x99)
    response = bus.read_byte_data(pichondria_address,0x03)
    bus.close()
    if (response == 1):
        return True
    else:
        return False

def get_input_voltage():
    bus = smbus.SMBus(1)
    pichondria_address = bus.read_byte_data(0x50, 0x99)
    msb, lsb = bus.read_i2c_block_data(pichondria_address,0x04,0x02)
    bus.close()
    result = adc_voltage_converstion(msb, lsb)
    return result

def get_input_voltage_ad(pichondria_address):
    bus = smbus.SMBus(1)
    msb, lsb = bus.read_i2c_block_data(pichondria_address,0x04,0x02)
    bus.close()
    result = adc_voltage_converstion(msb, lsb)
    return result

def get_output_voltage():
    bus = smbus.SMBus(1)
    pichondria_address = bus.read_byte_data(0x50, 0x99)
    msb, lsb = bus.read_i2c_block_data(pichondria_address,0x05,0x02)
    bus.close()
    result = adc_voltage_converstion(msb, lsb)
    return result

def get_output_voltage_ad(pichondria_address):
    bus = smbus.SMBus(1)
    msb, lsb = bus.read_i2c_block_data(pichondria_address,0x05,0x02)
    bus.close()
    result = adc_voltage_converstion(msb, lsb)
    return result

def get_battery_voltage():
    bus = smbus.SMBus(1)
    pichondria_address = bus.read_byte_data(0x50, 0x99)
    msb, lsb = bus.read_i2c_block_data(pichondria_address,0x06,0x02)
    bus.close()
    result = adc_voltage_converstion(msb, lsb)
    return result

def get_battery_voltage_ad(pichondria_address):
    bus = smbus.SMBus(1)
    msb, lsb = bus.read_i2c_block_data(pichondria_address,0x06,0x02)
    bus.close()
    result = adc_voltage_converstion(msb, lsb)
    return result

def apply_settings():
    try:
        bus = smbus.SMBus(1)
        pichondria_address = bus.read_byte_data(0x50, 0x99)
        bus.write_byte_data(pichondria_address, 0x07, 0x01)
        time.sleep(3)
        bus.close()
        return True
    except:
        return False

def adc_voltage_converstion(msb, lsb):
    adc_value = (msb << 8) | lsb
    reference_voltage = 3.3
    adc_resolution = 10
    max_adc_value = 2 ** adc_resolution - 1
    voltage_step = reference_voltage / max_adc_value
    voltage_value = adc_value * voltage_step * 6.5 / 1.5
    return voltage_value
    
def get_startup_voltage():
    bus = smbus.SMBus(1)
    msb, lsb = bus.read_i2c_block_data(0x50,0x13,0x02)
    bus.close()
    startup_voltage = adc_voltage_converstion(msb, lsb)
    return startup_voltage    

def get_shutdown_voltage():
    bus = smbus.SMBus(1)
    msb, lsb = bus.read_i2c_block_data(0x50,0x16,0x02)
    bus.close()
    shutdown_voltage = adc_voltage_converstion(msb, lsb)
    return shutdown_voltage

def get_wake_up_timer():
    bus = smbus.SMBus(1)
    time4, time3, time2, time1 = bus.read_i2c_block_data(0x50,0x70,0x04)
    bus.close()
    wake_up_timer = time4 * 256 * 256 * 256 + time3 * 256 * 256 + time2 * 256 + time1
    return wake_up_timer

def get_shutdown_timer():
    bus = smbus.SMBus(1)
    shutdown_timer = bus.read_byte_data(0x50, 0x80)
    bus.close()
    return shutdown_timer

def get_bootup_timer():
    bus = smbus.SMBus(1)
    bootup_timer = bus.read_byte_data(0x50, 0x86)
    bus.close()
    return bootup_timer

def enable_autopilot():
    try:
        bus = smbus.SMBus(1)
        bus.write_byte_data(0x50, 0x11, 0x01)
        time.sleep(0.1)
        pichondria_address = bus.read_byte_data(0x50, 0x99)
        bus.write_byte_data(pichondria_address, 0x07, 0x01)
        time.sleep(3)
        bus.close()
        return True
    except:
        return False

def disable_autopilot():
    try:
        bus = smbus.SMBus(1)
        bus.write_byte_data(0x50, 0x11, 0x00)
        time.sleep(0.1)
        pichondria_address = bus.read_byte_data(0x50, 0x99)
        bus.write_byte_data(pichondria_address, 0x07, 0x01)
        time.sleep(3)
        bus.close()
        return True
    except:
        return False

def check_autopilot_mode():
    bus = smbus.SMBus(1)
    autopilot = bus.read_byte_data(0x50, 0x11)
    bus.close()
    if autopilot:
        return True
    else:
        return False
    
def enable_acknowledgement_mode():
    try:
        bus = smbus.SMBus(1)
        pichondria_address = bus.read_byte_data(0x50, 0x99)
        bus.write_byte_data(0x50, 0x98, 0x01)
        time.sleep(0.1)
        bus.write_byte_data(pichondria_address, 0x07, 0x01)
        time.sleep(3)
        bus.close()
        return True
    except:
        return False

def check_acknowledgement_mode():
    bus = smbus.SMBus(1)
    ack_mode = bus.read_byte_data(0x50, 0x98)
    bus.close()
    if ack_mode:
        return True
    else:
        return False

def disable_acknowledgement_mode():
    try:
        bus = smbus.SMBus(1)
        pichondria_address = bus.read_byte_data(0x50, 0x99)
        bus.write_byte_data(0x50, 0x98, 0x00)
        time.sleep(0.1)
        bus.write_byte_data(pichondria_address, 0x07, 0x01)
        time.sleep(3)
        bus.close()
        return True
    except:
        return False

def voltage_to_adc(voltage):
    adc_resolution = 10
    reference_voltage = 3.3
    max_adc_value = 2 ** adc_resolution - 1
    voltage_step = reference_voltage / max_adc_value
    voltage = voltage * 1.5 / 6.5
    adc_value = int(round(voltage / voltage_step))
    adc_value = max(min(adc_value, max_adc_value), 0)
    return adc_value

def set_startup_voltage(voltage):
    try:
        adc_value = voltage_to_adc(voltage)
        msb_value = (adc_value >> 8) & 0xFF
        lsb_value = adc_value & 0xFF
        bus = smbus.SMBus(1)
        bus.write_byte_data(0x50, 0x13, msb_value)
        time.sleep(0.1)
        bus.write_byte_data(0x50, 0x14, lsb_value)
        time.sleep(0.1)
        bus.close()
        return True
    except:
        return False

def set_shutdown_voltage(voltage):
    try:
        adc_value = voltage_to_adc(voltage)
        msb_value = (adc_value >> 8) & 0xFF
        lsb_value = adc_value & 0xFF
        bus = smbus.SMBus(1)
        bus.write_byte_data(0x50, 0x16, msb_value)
        time.sleep(0.1)
        bus.write_byte_data(0x50, 0x17, lsb_value)
        time.sleep(0.1)
        bus.close()
        return True
    except:
        return False

def set_wake_up_timer(timer):
    try:
        msb1 = (timer >> 24) & 0xFF
        msb2 = (timer >> 16) & 0xFF
        msb3 = (timer >> 8) & 0xFF
        lsb = timer & 0xFF
        bus = smbus.SMBus(1)
        bus.write_byte_data(0x50, 0x70, msb1)
        time.sleep(0.1)
        bus.write_byte_data(0x50, 0x71, msb2)
        time.sleep(0.1)
        bus.write_byte_data(0x50, 0x72, msb3)
        time.sleep(0.1)
        bus.write_byte_data(0x50, 0x73, lsb)
        time.sleep(0.1)
        bus.close()
        return True
    except:
        return False

def set_shutdown_timer(timer):
    try:
        bus = smbus.SMBus(1)
        bus.write_byte_data(0x50, 0x80, timer)
        time.sleep(0.1)
        bus.close()
        return True
    except:
        return False

def set_bootup_timer(timer):
    try:
        bus = smbus.SMBus(1)
        bus.write_byte_data(0x50, 0x86,timer)
        time.sleep(0.1)
        bus.close()
        return True
    except:
        return False
    
def send_acknowledgement():
    try:
        bus = smbus.SMBus(1)
        pichondria_address = bus.read_byte_data(0x50, 0x99)
        bus.write_byte_data(pichondria_address, 0x08, 0x01)
        bus.close()
        return True
    except:
        return False

def check_shutdown():
    bus = smbus.SMBus(1)
    pichondria_address = bus.read_byte_data(0x50, 0x99)
    status = bus.read_byte_data(pichondria_address, 0x09)
    bus.close()
    if (status != 0):
        return True
    else:
        return False
    
def check_shutdown_ad(pichondria_address):
    bus = smbus.SMBus(1)
    status = bus.read_byte_data(pichondria_address, 0x09)
    bus.close()
    if (status != 0):
        return True
    else:
        return False
    
def req_shutdown():
    try:
        bus = smbus.SMBus(1)
        pichondria_address = bus.read_byte_data(0x50, 0x99)
        bus.write_byte_data(pichondria_address, 0x11, 0x01)
        bus.close()
        return True
    except:
        return False

def req_reboot():
    try:
        bus = smbus.SMBus(1)
        pichondria_address = bus.read_byte_data(0x50, 0x99)
        bus.write_byte_data(pichondria_address, 0x12, 0x01)
        bus.close()
        return True
    except:
        return False

def req_scheduled_reboot():
    try:
        bus = smbus.SMBus(1)
        pichondria_address = bus.read_byte_data(0x50, 0x99)
        bus.write_byte_data(pichondria_address, 0x14, 0x01)
        bus.close()
        return True
    except:
        return False

def req_power_restore_shutdown():
    try:
        bus = smbus.SMBus(1)
        pichondria_address = bus.read_byte_data(0x50, 0x99)
        bus.write_byte_data(pichondria_address, 0x13, 0x01)
        bus.close()
        return True
    except:
        return False

def req_shutdown_ad(pichondria_address):
    try:
        bus = smbus.SMBus(1)
        bus.write_byte_data(pichondria_address, 0x11, 0x01)
        bus.close()
        return True
    except:
        return False

def req_reboot_ad(pichondria_address):
    try:
        bus = smbus.SMBus(1)
        bus.write_byte_data(pichondria_address, 0x12, 0x01)
        bus.close()
        return True
    except:
        return False

def req_scheduled_reboot_ad(pichondria_address):
    try:
        bus = smbus.SMBus(1)
        bus.write_byte_data(pichondria_address, 0x14, 0x01)
        bus.close()
        return True
    except:
        return False

def req_power_restore_shutdown_ad(pichondria_address):
    try:
        bus = smbus.SMBus(1)
        bus.write_byte_data(pichondria_address, 0x13, 0x01)
        bus.close()
        return True
    except:
        return False
