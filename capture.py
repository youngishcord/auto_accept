import datetime
import time
import cv2
import pyautogui
from PIL import ImageGrab
import numpy as np

from PySide6.QtCore import QThread, Signal, Slot


class CaptureThread(QThread):
    update_frame = Signal(np.ndarray)
    start_click = Signal(bool, int, int)
    
    def __init__(self, crop_size: int = 20, delay: float = 0.05, color_threshold: int = 1,
                 max_click = 10, parent = None):
        super().__init__(parent)
        
        self.crop_size = crop_size
        self.delay = delay
        self.max_click = max_click
        
        self.prev_image = None
        self.threshold = color_threshold
        self.started = False
        self.counter = 0
        self.timer = 0
        
    @Slot()
    def set_clicker(self):
        self.started = not self.started
        self.timer = time.time()
        self.counter = 0
        self.prev_image = None
        self.start_click.emit(self.started, int(time.time() - self.timer), self.counter)
        
    def run(self):
        while True:
            x, y = pyautogui.position()
            
            screen_shot = ImageGrab.grab(bbox=(x-self.crop_size,
                                              y-self.crop_size,
                                              x+self.crop_size,
                                              y+self.crop_size))
            screen_shot_np = np.array(screen_shot)
            frame = cv2.cvtColor(screen_shot_np, cv2.COLOR_RGB2BGR)
            
            if self.prev_image is not None and self.started and (time.time() - self.timer) > 5:
                if np.mean(np.abs(screen_shot_np - self.prev_image)) > self.threshold:
                    pyautogui.click()
                    self.counter += 1
                    self.start_click.emit(self.started, int(time.time() - self.timer), self.counter)
                    if self.counter >= self.max_click:
                        self.started = False
                        self.start_click.emit(self.started, int(time.time() - self.timer), self.counter)
            elif self.started:
                self.start_click.emit(self.started, int(time.time() - self.timer), self.counter)
            
            self.prev_image = screen_shot
            
            self.update_frame.emit(frame)
            time.sleep(self.delay)