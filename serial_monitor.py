import flet as ft
import serial
import threading
import time

# Initialize serial communication (9600 baud rate)
ser = serial.Serial(port='COM4', baudrate=9600, timeout=1)  # Adjust 'COM4' for your specific port

def read_serial_data(output_area):
    """Function to read serial data continuously, update text area, and clear after 10 lines."""
    line_count = 0  # To track the number of lines displayed
    while True:
        if ser.in_waiting > 0:
            serial_data = ser.readline().decode('utf-8').strip()
            output_area.value += f"{serial_data}\n"
            output_area.update()
            line_count += 1

            # After 10 lines, wait for 3 seconds and then clear the text area
            if line_count == 10:
                time.sleep(.3)  # Wait for 3 seconds
                output_area.value = ""  # Clear the output area
                output_area.update()
                line_count = 0  # Reset the line counter

def main(page: ft.Page):
    page.title = "Serial Monitor"
    
    # Create an output text area for displaying serial data
    output_area = ft.TextField(
        label="Serial Monitor",
        multiline=True,
        min_lines=20,
        max_lines=25,
        width=500,
        read_only=True,
    )
    
    # Start the thread for reading serial data
    threading.Thread(target=read_serial_data, args=(output_area,), daemon=True).start()

    # Add the output area to the page
    page.add(output_area)

# Start the Flet app
ft.app(target=main)
