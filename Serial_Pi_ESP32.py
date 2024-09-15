
import time
import serial
print("Serial_Pi_ESP32: Module Read")
ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)

def esp32_done():
    while True:
        ser.flush()
        response = ser.readline().decode('utf-8').strip()
        print(response)
        if response == "Done":
            ser.reset_input_buffer()
            break


def esp32_comms(ser, commandESP):
    # Encode string with a separation at the end
    commandESP = f"{commandESP}\n".encode('utf-8')

    # Send the string to ESP32
    ser.write(commandESP)

    # Ensure command transmission is successful
    ser.flush()

    # Print confirmation for sending
    print(f"Sent: {commandESP.decode('utf-8').strip()}")

    # Allocate time for ESP32 to respond
    time.sleep(0.3)

    # Read reply from ESP32
    receive = ser.readline().decode('utf-8').rstrip()

    timer_start = time.time()
    resend_counter = 0
    # Checking if ESP32 received the command
    while not receive == 'OK':

        # Setup a timeout scenario to attempt a command resend
        timer_end = time.time()
        time_diff = timer_end - timer_start

        # Resend command after 5 seconds for 1 time
        if time_diff == 5 and resend_counter < 1:
            esp32_comms(ser, commandESP)
            resend_counter += 1
       # else:
            #Shutdown system as ESP32 is not responding
            #system_shutdown()
            

    # Clear lingering serial inputs
    ser.reset_input_buffer()

    # Wait for ESP32 to complete task or continue immediately after sending command.
    match commandESP:
        case ["EMAGNET_ON" | "EMAGNET_OFF"]:
            time.sleep(1)
            return
        case ["LIGHTS_ON" | "LIGHTS_OFF" | "GREENLED_ON" | "GREENLED_OFF" | "REDLED_ON" | "REDLED_OFF"]:
            return
        case ["LID_OPEN" | "LID_CLOSE" | "GATE_CLOSE" | "G_OPEN" | "G_CLOSE" | "S" | "M"]:
            receive = ser.readline().decode('utf-8').rstrip()
            while not receive == 'Done':
                time.sleep(0.005)
                receive = ser.readline().decode('utf-8').rstrip()

            # Clear lingering serial inputs
            ser.reset_input_buffer()
            return



print("Serial_Pi_ESP32: Module Done")
