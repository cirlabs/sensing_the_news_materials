import time
from datetime import datetime, timedelta
import RPi.GPIO as GPIO
import Adafruit_DHT

from Adafruit_LED_Backpack import SevenSegment

button_pin = 19
hum = 0
temp = 0

MODE = 'temp'
READING_DELAY = 2  # Seconds between reading attempts

last_read_time = None
current_temp = None
current_hum = None

def toggle_button(pin):
    global MODE
    if MODE == 'temp':
        MODE = 'humidity'
    else:
        MODE = 'temp'
    print 'Button pressed. New mode: ' + MODE

    update_reading()

def c_to_f(temp):
    return temp * float(9) / float(5) + 32

def update_reading():
    if current_temp and current_hum:
        if MODE == 'temp':
            write_to_display(c_to_f(current_temp))
        else:
            write_to_display(current_hum)

def write_to_display(input_value):
    segment.clear()

    # Round float temp
    int_value = int(round(input_value))

    if int_value < 0:
        segment.set_digit(1, '-')
    else:
        segment.set_digit(1, '')
    segment.set_digit(2, int_value / 10)  # Tens
    segment.set_digit(3, int_value % 10)  # Ones

    segment.write_display()


def get_reading():
    global current_temp
    global current_hum
    print "Checking temp/humidity..."
    sensor = Adafruit_DHT.DHT22
    pin = 4

    hum, temp = Adafruit_DHT.read_retry(sensor, pin)
    current_temp = temp
    current_hum = hum
    return hum, temp

# set up button
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Listen for button push
GPIO.add_event_detect(button_pin, GPIO.RISING, callback=toggle_button, bouncetime=200)

# Instantiate screen
segment = SevenSegment.SevenSegment(address=0x70)

# Initialize the display. Must be called once before using the display.
segment.begin()

try:
    while True:

        update_reading()

        # if it's time for a reading, check
        current_time = datetime.now()
        if not last_read_time or last_read_time + timedelta(seconds=READING_DELAY) <= current_time:
            last_read_time = current_time

            # Check for a new reading, which may or may not be available
            reading = get_reading()
            print reading

except KeyboardInterrupt:
    segment.clear()
    segment.write_display()
    raise

