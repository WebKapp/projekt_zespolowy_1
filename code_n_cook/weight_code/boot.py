from machine import Pin, I2C, ADC
import ssd1306
from micropython import const

import bluetooth
import random
import struct
import time
import micropython

from _thread import start_new_thread

product_str = ""
products_data = ""
mass = 0
state = 3
data_changed = False

# Bluetooth stuff
################################################################

# Stuff related to getting data from weight via Bluetooth.

from ble_advertising import decode_services, decode_name

from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_READ_REQUEST = const(4)
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_SERVICE_DONE = const(10)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
_IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE = const(14)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_READ_DONE = const(16)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_GATTC_NOTIFY = const(18)
_IRQ_GATTC_INDICATE = const(19)

_ADV_IND = const(0x00)
_ADV_DIRECT_IND = const(0x01)
_ADV_SCAN_IND = const(0x02)
_ADV_NONCONN_IND = const(0x03)

_UART_SERVICE_UUID = bluetooth.UUID(0xffb0)


class BLESimpleCentral:
    def __init__(self, ble):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)

        self._reset()

    def _reset(self):
        # Cached name and address from a successful scan.
        self._name = None
        self._addr_type = None
        self._addr = None

        # Callbacks for completion of various operations.
        # These reset back to None after being invoked.
        self._scan_callback = None
        self._conn_callback = None
        self._read_callback = None

        # Persistent callback for when new data is notified from the device.
        self._notify_callback = None

        # Connected device.
        self._conn_handle = None
        self._start_handle = None
        self._end_handle = None

    def _irq(self, event, data):
        global state
        print("State: " + str(state))
        print(event)
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            if adv_type in (_ADV_IND, _ADV_DIRECT_IND) and _UART_SERVICE_UUID in decode_services(
                adv_data
            ):
                # Found a potential device, remember it and stop scanning.
                self._addr_type = addr_type
                self._addr = bytes(
                    addr
                )  # Note: addr buffer is owned by caller so need to copy it.
                self._name = decode_name(adv_data) or "?"
                self._ble.gap_scan(None)

        elif event == _IRQ_SCAN_DONE:
            if self._scan_callback:
                if self._addr:
                    # Found a device during the scan (and the scan was explicitly stopped).
                    self._scan_callback(self._addr_type, self._addr, self._name)
                    self._scan_callback = None
                else:
                    # Scan timed out.
                    self._ble.gap_scan(2000, 30000, 30000)
                    self._scan_callback(None, None, None)

        elif event == _IRQ_PERIPHERAL_CONNECT:
            # Connect successful.
            global products_data
            state = 1 if products_data else 0
            conn_handle, addr_type, addr = data
            if addr_type == self._addr_type and addr == self._addr:
                self._conn_handle = conn_handle
                self._ble.gattc_discover_services(self._conn_handle)

        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            # Disconnect (either initiated by us or the remote end).
            global state
            state = 3
            conn_handle, _, _ = data
            if conn_handle == self._conn_handle:
                # If it was initiated by us, it'll already be reset.
                self._reset()
            start_new_thread(weight,())
            self.disconnect()


        elif event == _IRQ_GATTC_SERVICE_RESULT:
            # Connected device returned a service.
            conn_handle, start_handle, end_handle, uuid = data
            print("service", data)
            if conn_handle == self._conn_handle:
                self._start_handle, self._end_handle = start_handle, end_handle

        elif event == _IRQ_GATTC_SERVICE_DONE:
            # Service query complete.
            if self._start_handle and self._end_handle:
                self._ble.gattc_discover_characteristics(
                    self._conn_handle, self._start_handle, self._end_handle
                )
            else:
                print("Failed to find uart service.")

        elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
            # Connected device returned a characteristic.
            conn_handle, def_handle, value_handle, properties, uuid = data
            print(data)

        elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
            # Characteristic query complete.
            update_oled()
            global state
            state = 0
            print(self._conn_callback)

        elif event == _IRQ_GATTC_WRITE_DONE:
            conn_handle, value_handle, status = data
            print("TX complete")

        elif event == _IRQ_GATTC_NOTIFY:
            conn_handle, value_handle, notify_data = data
            if conn_handle == self._conn_handle:
                if self._notify_callback:
                    self._notify_callback(notify_data)

    # Returns true if we've successfully connected and discovered characteristics.
    def is_connected(self):
        return (
            self._conn_handle is not None
        )

    # Find a device advertising the environmental sensor service.
    def scan(self, callback=None):
        self._addr_type = None
        self._addr = None
        self._scan_callback = callback
        self._ble.gap_scan(2000, 30000, 30000)
        # self._ble.gap_scan(10000)

    # Connect to the specified device (otherwise use cached address from a scan).
    def connect(self, addr_type=None, addr=None, callback=None):
        self._addr_type = addr_type or self._addr_type
        self._addr = addr or self._addr
        self._conn_callback = callback
        if self._addr_type is None or self._addr is None:
            return False
        self._ble.gap_connect(self._addr_type, self._addr)
        return True

    # Disconnect from current device.
    def disconnect(self):
        if not self._conn_handle:
            return
        self._ble.gap_disconnect(self._conn_handle)
        self._reset()

    # Send data over the UART
    def write(self, v, response=False):
        if not self.is_connected():
            return
        self._ble.gattc_write(self._conn_handle, v, 1 if response else 0)

    # Set handler for when data is received over the UART.
    def on_notify(self, callback):
        self._notify_callback = callback


def weight():

    def update_oled(product="", mass="", all_products=""):
        oled.fill(0)
        oled.text(product, 0, 0)
        oled.text(mass, 0, 10)
        oled.text(all_products, 0, 20)
        oled.text(all_products, 0, 20)
        oled.show()

    update_oled()
    ble = bluetooth.BLE()
    central = BLESimpleCentral(ble)

    not_found = False

    def on_scan(addr_type, addr, name):
        if addr_type is not None:
            print("Found peripheral:", addr_type, addr, name)
            central.connect()
        else:
            nonlocal not_found
            not_found = True
            print("No peripheral found.")
            global state
            state = 3
            update_oled(product_str, "Weight not found")


    central.scan(callback=on_scan)

    # Wait for connection...
    while not central.is_connected():
        time.sleep_ms(100)
        if not_found:
            return

    print("Connected")

    def on_rx(data):
        #This is where the weight data is recieved.
        bites = ""
        global mass
        mass = 0
        for index, byte in enumerate(data):
            if index == 3:
                mass += int(bin(byte), 2) * 256
            elif index == 4:
                mass += int(bin(byte), 2)
        print(mass)

    central.on_notify(on_rx)


########################################################
# Stuff relating to connecting device to the app via Wi-Fi.


def app():
    def update_oled(product, mass, all_products=""):
        oled.fill(0)
        oled.text(product, 0, 0)
        oled.text(mass, 0, 10)
        oled.text(all_products, 0, 20)
        oled.show()

    try:
      import usocket as socket
    except:
      import socket

    import network

    import esp
    esp.osdebug(None)

    import gc
    gc.collect()


    ssid = ''
    password = ''

    station = network.WLAN(network.STA_IF)

    station.active(True)
    station.connect(ssid, password)

    while station.isconnected() == False:
      pass

    print('Connection successful')
    print(station.ifconfig())

    global products_data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)

    while True:
        conn, addr = s.accept()
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        request = request.decode()
        products_data = request
        global state
        if state != 3 and request:
            state = 1
        # Request is the data recieved from the client.
        print('Content = %s' % request)

        if request:
            global data_changed
            data_changed = True
        conn.close()



#######################################################
# Stuff related to showing data for the user and also
# for getting inputs from him.

class Joystick():
    def __init__(self):
        self._led_green1 = Pin(13, Pin.OUT)
        self._led_green1.off()
        self._led_yellow = Pin(14, Pin.OUT)
        self._led_yellow.off()
        self._led_red = Pin(12, Pin.OUT)
        self._led_red.off()
        self._led_green2 = Pin(15, Pin.OUT)
        self._led_green2.off()
        self.x_axis = ADC(Pin(32, Pin.IN))
        self.y_axis = ADC(Pin(33, Pin.IN))
        self.button = ADC(Pin(35, Pin.IN))
        self.x_axis.atten(ADC.ATTN_11DB)
        self.y_axis.atten(ADC.ATTN_11DB)
        self.button.atten(ADC.ATTN_11DB)
        self._data = None
        self._products_list = None
        self._current_index = 0
        self._products_done = None
        self._products_number = None
        self._button_count = 0
        self._char_count = 0
        self._shift_right = True


        self.get_input()


    def get_data(self):
        global products_data
        global data_changed
        print(self._data)
        if (products_data != self._data or data_changed) and products_data:
                print("ok")
                self._current_index = 0
                self._data = products_data
                self.update_data(products_data)
                self._products_number = len(self._products_list)
                self._products_done = 0
                data_changed = False


    def update_data(self, new_data):
        if new_data:
            splited_raw_data = new_data.split('/')
            print(splited_raw_data)
            if splited_raw_data:
                self._products_list = []
                print(splited_raw_data)
                for raw_data in splited_raw_data:
                    raw_data = raw_data.split(",")
                    product_data = [raw_data[0], int(raw_data[1]), False]
                    self._products_list.append(product_data)


    def get_input(self):
        while True:
            self.get_data()
            global state
            if state == 1:
                axis_x = self.x_axis.read()
                axis_y = self.y_axis.read()
                global mass
                product_mass = self._products_list[self._current_index][1]
                mass_fraction = product_mass * 0.05
                new_mass_str = f"{mass}/{product_mass}"
                global product_str
                product_str = self.get_part_of_str(self._products_list[self._current_index][0])
                if self.button.read() == 0:
                    self._button_count += 1
                    if self._button_count == 1000:
                        # do stuff
                        print("Button pressed")
                        self._button_count = 0
                else:
                    self._button_count = 0
            # if self._products_list:
                if axis_x == 0:
                    if self._current_index == 0:
                        self._current_index = len(self._products_list)-1
                    else:
                        self._current_index -= 1
                elif axis_x > 4000:
                    if self._current_index == len(self._products_list)-1:
                        self._current_index = 0
                    else:
                        self._current_index += 1
                elif axis_y == 0 and not self._products_list[self._current_index][2]:
                    self._products_list[self._current_index][2] = True
                    self._led_green2.on()
                    self._products_done += 1
                if self._products_done == self._products_number:
                    # wszystko gotowe
                    products_done_str = 'All done'
                    global state
                    state = 2
                else:
                    pro_str = "Products" if self._products_number != 1 else "Product"
                    products_done_str = f'{self._products_done}/{self._products_number} {pro_str}'
                if self._products_list[self._current_index][2]:
                    self._led_green2.on()
                else:
                    self._led_green2.off()
                if abs(mass - product_mass) <= mass_fraction:
                    # green
                    self._led_green1.on()
                    self._led_yellow.off()
                    self._led_red.off()
                elif mass < product_mass:
                    # yellow
                    self._led_green1.off()
                    self._led_yellow.on()
                    self._led_red.off()
                else:
                    # red
                    self._led_green1.off()
                    self._led_yellow.off()
                    self._led_red.on()
                update_oled(product_str, new_mass_str, products_done_str)
                time.sleep(0.5)
            else:
                if state != 2:
                    self._led_green2.off()
                self._led_green1.off()
                self._led_yellow.off()
                self._led_red.off()

    def get_part_of_str(self, name):
        if len(name) <= 16:
            return name
        else:
            max_idx = len(name) - 16
            part_name = name[self._char_count:self._char_count + 16]

            if self._shift_right:
                if self._char_count == max_idx:
                    self._shift_right = False
                else:
                    self._char_count += 1

            else:
                if self._char_count == 0:
                    self._shift_right = True
                else:
                    self._char_count -= 1
        time.sleep(0.3)

        return part_name

def show_output():
    joystick = Joystick()

########################################################
# Stuff related to components of ESP32.

i2c = I2C(-1, scl=Pin(22), sda=Pin(21))
oled_width = 128
oled_height = 32
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
########################################################


def update_oled(product="", mass="", all_products=""):
    oled.fill(0)
    global state
    if state == 3:
        oled.text("Weight not found", 0, 10)
    elif state == 2:
        oled.text("All done!", 28, 10)
    elif state == 0:
        oled.text("Waiting for data", 0, 10)
    else:
        oled.text(mass, 0, 10)
        oled.text(product, 0, 0)
        oled.text(all_products, 0, 20)
    oled.show()


########################################################

if __name__ == "__main__":
    update_oled("", "")
    start_new_thread(weight,())
    start_new_thread(app, ())
    start_new_thread(show_output, ())
########################################################

