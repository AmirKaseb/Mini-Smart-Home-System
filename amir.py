import serial
import time

# Set up the serial connection
ser = serial.Serial('COM4', 9600, timeout=1)  # Replace 'COM3' with your serial port

# Allow the connection to initialize
time.sleep(2)

# Send the "Open" message
ser.write(b'change')  # 'b' is for sending bytes
time.sleep(3)
ser.write(b'123')  # 'b' is for sending bytes
# Close the serial connection
ser.close()
