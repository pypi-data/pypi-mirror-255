import cv2
import pyautogui
import time
import numpy as np

def capture_screen(gray=False):
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    if not gray:
        return screenshot
    else:
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        return screenshot_gray

def click_dotted_line_x(coords, myRange, tts=1):
    (x,y) = coords
    for increment in myRange:
        click_x = x + increment
        click_y = y 
        pyautogui.click(click_x, click_y)
        time.sleep(tts) 
        
def click_dotted_line_y(coords, myRange, tts=1):
    (x,y) = coords
    for increment in myRange:
        click_x = x
        click_y = y + increment
        pyautogui.click(click_x, click_y)
        time.sleep(tts) 
        
def click(coords, tts=1):
    (click_x,click_y) = coords
    pyautogui.click(click_x, click_y)
    time.sleep(tts) 