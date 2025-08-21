import contextlib
from tkinter import ttk
from tkinter.simpledialog import Dialog

import sounddevice as sd


class SettingsWindow(Dialog):
    def body(self, master):
        ttk.Label(master, text='Select sound device:').pack(anchor='w')
        self.hostapi_list = ttk.Combobox(master, state='readonly', width=50)
        self.hostapi_list.pack()
        self.hostapi_list['values'] = [
            hostapi['name'] for hostapi in sd.query_hostapis()]
        self.device_ids = []
        self.device_list = ttk.Combobox(master, state='readonly', width=50)
        self.device_list.pack()

        self.hostapi_list.bind('<<ComboboxSelected>>', self.update_device_list)
        with contextlib.suppress(sd.PortAudioError):
            self.hostapi_list.current(sd.default.hostapi)
            self.hostapi_list.event_generate('<<ComboboxSelected>>')

    def update_device_list(self, *args):
        hostapi = sd.query_hostapis(self.hostapi_list.current())
        self.device_ids = [
            idx
            for idx in hostapi['devices']
            if sd.query_devices(idx)['max_input_channels'] > 0]
        self.device_list['values'] = [
            sd.query_devices(idx)['name'] for idx in self.device_ids]
        default = hostapi['default_input_device']
        if default >= 0:
            self.device_list.current(self.device_ids.index(default))

    def validate(self):
        self.result = self.device_ids[self.device_list.current()]
        return True