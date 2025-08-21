import queue
import tempfile
import threading
import tkinter as tk
from tkinter import ttk

import pyperclip
import numpy as np
import sounddevice as sd
import torch
import whisper

from SettingsWindow import SettingsWindow
from sound_file_writer import sound_file_writer

class MainWindow(tk.Tk):

    filename = None
    stream = None

    def __init__(self):
        super().__init__()

        self.model = None
        self.title('Simple Whisper')

        padding = 10

        f = ttk.Frame()

        self.record_button = ttk.Button(f)
        self.record_button.pack(side='left', padx=padding, pady=padding)

        self.settings_button = ttk.Button(
            f, text='settings', command=self.on_settings)
        self.settings_button.pack(side='left', padx=padding, pady=padding)

        f.pack(expand=True, padx=padding, pady=padding)

        self.translated_text = tk.Label(text="(Nothing said yet)")
        self.translated_text.pack(fill='x')

        self.cuda_label = tk.Label(text=f"Used device: {self.get_device()}")
        self.cuda_label.pack(side='left', padx=padding, pady=padding)

        self.model_label = tk.Label(text="No model")
        self.model_label.pack(side='right', padx=padding, pady=padding)

        self.model_combobox = ttk.Combobox()
        self.model_combobox['values'] = whisper.available_models()
        self.model_combobox.pack(side='left', padx=padding, pady=padding)

        self.model_select = ttk.Button(text="Select model", command=self.on_select_model)
        self.model_select.pack(side='right', padx=padding, pady=padding)

        self.create_stream()

        self.recording = self.previously_recording = False
        self.audio_q = queue.Queue()

        self.protocol('WM_DELETE_WINDOW', self.close_window)
        self.init_buttons()

    def on_select_model(self):
        model_name = self.model_combobox.get()
        self.model = whisper.load_model(model_name)
        self.model_label['text'] = f"Selected model {model_name}"
        self.init_buttons()

    @staticmethod
    def get_device():
        return 'cuda' if torch.cuda.is_available() else 'cpu'

    def create_stream(self, device=None):
        if self.stream is not None:
            self.stream.close()
        self.stream = sd.InputStream(
            device=device, channels=1, callback=self.audio_callback)
        self.stream.start()

    def audio_callback(self, indata, frames, time, status):
        if self.recording:
            self.audio_q.put(indata.copy())
            self.previously_recording = True
        else:
            if self.previously_recording:
                self.audio_q.put(None)
                self.previously_recording = False

    def on_rec(self):
        self.settings_button['state'] = 'disabled'
        self.recording = True

        self.filename = tempfile.mktemp(
            prefix='delme_rec_gui_', suffix='.wav', dir='')

        if self.audio_q.qsize() != 0:
            print('WARNING: Queue not empty!')
        self.thread = threading.Thread(
            target=sound_file_writer,
            kwargs=dict(
                file=self.filename,
                mode='x',
                samplerate=int(self.stream.samplerate),
                channels=self.stream.channels,
                q=self.audio_q,
            ),
        )
        self.thread.start()

        self.record_button['text'] = 'stop'
        self.record_button['command'] = self.on_stop
        self.record_button['state'] = 'normal'

    def on_stop(self, *args):
        self.record_button['state'] = 'disabled'
        self.recording = False
        self.wait_for_thread()

    def wait_for_thread(self):
        self.after(10, self._wait_for_thread)

    def _wait_for_thread(self):
        if self.thread.is_alive():
            self.wait_for_thread()
            return
        self.thread.join()
        self.translate_recording()
        self.init_buttons()

    def translate_recording(self):
        if self.model is not None and self.filename is not None:
            result = self.model.transcribe(self.filename)
            translated_text = result["text"]
            pyperclip.copy(translated_text)
            self.translated_text.configure(text=translated_text)

    def on_settings(self, *args):
        w = SettingsWindow(self, 'Settings')
        if w.result is not None:
            self.create_stream(device=w.result)

    def init_buttons(self):
        self.record_button['text'] = 'record'
        self.record_button['command'] = self.on_rec
        if self.stream and self.model:
            self.record_button['state'] = 'normal'
        else:
            self.record_button['state'] = 'disabled'
        self.settings_button['state'] = 'normal'

    def close_window(self):
        if self.recording:
            self.on_stop()
        self.destroy()
