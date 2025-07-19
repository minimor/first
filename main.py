from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.colorpicker import ColorPicker
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from jnius import autoclass
import os

# Bluetooth UUID for SPP
SPP_UUID = "00001101-0000-1000-8000-00805F9B34FB"

class AndroidBluetoothManager:
    def __init__(self):
        self.BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
        self.BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
        self.BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
        self.UUID = autoclass('java.util.UUID')
        
        self.adapter = self.BluetoothAdapter.getDefaultAdapter()
        self.socket = None
        self.connected = False
    
    def enable_bluetooth(self):
        if not self.adapter.isEnabled():
            return self.adapter.enable()
        return True
    
    def scan_devices(self):
        if not self.adapter.isEnabled():
            self.enable_bluetooth()
        
        paired_devices = self.adapter.getBondedDevices().toArray()
        return [(dev.getAddress(), dev.getName()) for dev in paired_devices]
    
    def connect(self, address):
        try:
            device = self.adapter.getRemoteDevice(address)
            uuid = self.UUID.fromString(SPP_UUID)
            self.socket = device.createRfcommSocketToServiceRecord(uuid)
            self.socket.connect()
            self.connected = True
            return True
        except Exception as e:
            print(f"Bluetooth connection error: {str(e)}")
            return False
    
    def disconnect(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.connected = False
    
    def send_command(self, command):
        if not self.connected or not self.socket:
            return False
        
        try:
            output_stream = self.socket.getOutputStream()
            output_stream.write(command.encode('utf-8'))
            output_stream.flush()
            return True
        except Exception as e:
            print(f"Command send error: {str(e)}")
            self.disconnect()
            return False

class DeviceListPopup(Popup):
    def __init__(self, devices, callback, **kwargs):
        super().__init__(**kwargs)
        self.title = "Select Bluetooth Device"
        self.size_hint = (0.8, 0.8)
        self.callback = callback
        
        layout = BoxLayout(orientation='vertical')
        scroll = ScrollView()
        list_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for addr, name in devices:
            btn = Button(
                text=f"{name} ({addr})",
                size_hint_y=None,
                height=60,
                on_press=lambda x, a=addr: self.select_device(a)
            )
            list_layout.add_widget(btn)
        
        scroll.add_widget(list_layout)
        layout.add_widget(scroll)
        layout.add_widget(Button(text="Cancel", on_press=lambda x: self.dismiss()))
        
        self.content = layout
    
    def select_device(self, address):
        self.callback(address)
        self.dismiss()

class ColorPickerPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.title = "Select Color"
        self.size_hint = (0.9, 0.8)
        self.callback = callback
        
        layout = BoxLayout(orientation='vertical')
        self.color_picker = ColorPicker()
        layout.add_widget(self.color_picker)
        layout.add_widget(Button(
            text="Select", 
            size_hint_y=None,
            height=50,
            on_press=self.select_color
        ))
        
        self.content = layout
    
    def select_color(self, instance):
        color = self.color_picker.color
        self.callback(color)
        self.dismiss()

class ControlPanel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 20
        
        self.bt_manager = AndroidBluetoothManager()
        self.selected_color = (1, 1, 1, 1)  # Белый по умолчанию
        self.brightness = 128
        self.effect_index = 0
        self.led_enabled = True
        self.effects = [
            "Без эффекта", 
            "🌈 Радуга", 
            "Плавный переход", 
            "🎵 Музыкальный режим"
        ]
        
        # UI Elements
        self.connection_button = Button(
            text="Connect to Bluetooth",
            size_hint_y=None,
            height=60,
            on_press=self.show_device_list
        )
        self.add_widget(self.connection_button)
        
        self.status_label = Label(text="Status: Not connected")
        self.add_widget(self.status_label)
        
        # Toggle button
        self.toggle_button = Button(
            text="Выключить ленту" if self.led_enabled else "Включить ленту",
            size_hint_y=None,
            height=50,
            on_press=self.toggle_leds
        )
        self.add_widget(self.toggle_button)
        
        # Color button
        self.color_button = Button(
            text="Выбрать цвет",
            size_hint_y=None,
            height=50,
            on_press=self.show_color_picker
        )
        self.add_widget(self.color_button)
        
        # Brightness slider
        self.brightness_label = Label(text=f"Яркость: {self.brightness}")
        self.add_widget(self.brightness_label)
        
        self.brightness_slider = Slider(
            min=0,
            max=255,
            value=self.brightness,
            step=1
        )
        self.brightness_slider.bind(value=self.on_brightness_change)
        self.add_widget(self.brightness_slider)
        
        # Effects selector
        self.effects_label = Label(text="Эффекты:")
        self.add_widget(self.effects_label)
        
        self.effects_spinner = Spinner(
            text=self.effects[self.effect_index],
            values=self.effects,
            size_hint_y=None,
            height=50
        )
        self.effects_spinner.bind(text=self.on_effect_select)
        self.add_widget(self.effects_spinner)
        
        # Sensitivity and calibration
        self.sensitivity_label = Label(text=f"Чувствительность: 5.0")
        self.add_widget(self.sensitivity_label)
        
        self.sensitivity_slider = Slider(
            min=1,
            max=20,
            value=5,
            step=0.1
        )
        self.sensitivity_slider.bind(value=self.on_sensitivity_change)
        self.add_widget(self.sensitivity_slider)
        
        self.calibration_label = Label(text=f"Калибровка: 1.0x")
        self.add_widget(self.calibration_label)
        
        self.calibration_slider = Slider(
            min=0.1,
            max=5.0,
            value=1.0,
            step=0.1
        )
        self.calibration_slider.bind(value=self.on_calibration_change)
        self.add_widget(self.calibration_slider)
    
    def show_device_list(self, instance):
        devices = self.bt_manager.scan_devices()
        if not devices:
            self.status_label.text = "Status: No devices found"
            return
        
        popup = DeviceListPopup(
            devices=devices,
            callback=self.connect_to_device
        )
        popup.open()
    
    def connect_to_device(self, address):
        if self.bt_manager.connect(address):
            self.status_label.text = f"Status: Connected to {address}"
            # Send initial state
            self.send_color(self.selected_color)
            self.bt_manager.send_command(f"B{self.brightness}")
            self.bt_manager.send_command(f"E{self.effect_index}")
            self.bt_manager.send_command(f"T{1 if self.led_enabled else 0}")
        else:
            self.status_label.text = "Status: Connection failed"
    
    def toggle_leds(self, instance):
        self.led_enabled = not self.led_enabled
        self.toggle_button.text = "Выключить ленту" if self.led_enabled else "Включить ленту"
        self.bt_manager.send_command(f"T{1 if self.led_enabled else 0}")
    
    def show_color_picker(self, instance):
        popup = ColorPickerPopup(callback=self.set_color)
        popup.open()
    
    def set_color(self, color):
        self.selected_color = color
        self.send_color(color)
    
    def send_color(self, color):
        r, g, b = [int(c * 255) for c in color[:3]]
        self.bt_manager.send_command(f"C{r},{g},{b},{self.brightness}")
    
    def on_brightness_change(self, instance, value):
        self.brightness = int(value)
        self.brightness_label.text = f"Яркость: {self.brightness}"
        self.bt_manager.send_command(f"B{self.brightness}")
    
    def on_effect_select(self, instance, text):
        self.effect_index = self.effects.index(text)
        self.bt_manager.send_command(f"E{self.effect_index}")
    
    def on_sensitivity_change(self, instance, value):
        self.sensitivity_label.text = f"Чувствительность: {value:.1f}"
    
    def on_calibration_change(self, instance, value):
        self.calibration_label.text = f"Калибровка: {value:.1f}x"

class LEDControlApp(App):
    def build(self):
        return ControlPanel()

if __name__ == '__main__':
    LEDControlApp().run()