from pynput import mouse
import logging

logging.basicConfig(level=logging.INFO)

def on_click(x, y, button, pressed):
    logging.info(f"Mouse event: button={button}, pressed={pressed}, x={x}, y={y}")

listener = mouse.Listener(on_click=on_click)
listener.start()
listener.join()
