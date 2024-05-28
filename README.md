# EV3 tc-n3t3m

This project is a Python script designed to run on a LEGO EV3 brick using EV3DEV. It allows you to post network metrics such as delay and loss rate to `tc netem` using EV3 motors and sensors. The metrics are displayed on the EV3 screen and posted to a tc-gui endpoint when the touch sensor is pressed.

## Prerequisites

- LEGO EV3 brick with EV3DEV
- Python 3
- `dotenv` library for managing environment variables
- `requests` library for HTTP requests

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/PimSanders/tc-n3t3m.git
    cd tc-n3t3m
    ```

2. **Install the required Python libraries:**

    ```bash
    pip install python-dotenv requests
    ```

3. **Create a `.env` file in the root directory of the project and configure your environment variables:**

    ```env
    INTERFACES=eth0,wlan0
    POST_URL=http://example.com:5000/new_rule/
    ```

## Hardware Setup

1. Connect a touch sensor to any sensor port.
2. Connect two large motors to ports A and B.

## Usage

Run the script on your EV3 brick:

```bash
./tc-n3t3m.py
```

## Script Overview

- **Load Environment Variables:**
  
  The script loads environment variables from a `.env` file to configure network interfaces and the server URL.

- **Initialize Devices:**
  
  Initialize the touch sensor, motors, button, sound, and display.

- **Display Metrics:**
  
  The `display_metrics` function updates the EV3 screen with current delay and loss metrics.

- **Post Metrics:**
  
  The `post_metrics` function sends the collected metrics to the configured server endpoint.

- **Main Loop:**
  
  The `main_loop` function handles the touch sensor inputs and updates the metrics continuously. When the touch sensor is pressed, it posts the metrics to the server and resets the motor positions.

## Detailed Explanation

1. **Display Metrics:**

    ```python
    def display_metrics(delay_time, loss_rate):
        display.clear()
        display.text_pixels("Delay="+delay_time+"ms\nLoss="+loss_rate+"%", x=0, y=0, font=FONT)
        display.update()
    ```

    This function clears the EV3 screen and displays the current delay and loss rate.

2. **Post Metrics:**

    ```python
    def post_metrics(interface, delay_time, loss_rate):
        data = {
            'Rate': '', 'rate_unit': 'mbit', 'Delay': delay_time,
            'DelayVariance': '', 'Loss': loss_rate, 'LossCorrelation': '',
            'Duplicate': '', 'Reorder': '', 'ReorderCorrelation': '',
            'Corrupt': '', 'Limit': '10240'
        }
        response = requests.post(POST_URL+interface, data=data)
        return response.status_code, response.reason
    ```

    This function sends a POST request with the metrics data to the server.

3. **Main Loop:**

    ```python
    def main_loop():
        while True:
            while not touch_sensor.is_pressed:
                delay_time = str(-int(round(delay_motor.position / 10)))
                loss_rate = str(int(round(loss_motor.position / 10)))
                display_metrics(delay_time, loss_rate)
                if btn.any():
                    delay_motor.position = 0
                    loss_motor.position = 0
                time.sleep(0.1)

            display.text_pixels("Ship it", x=0, y=0, font=FONT)
            display.update()

            sound.beep()

            for interface in INTERFACES:
                status_code, reason = post_metrics(interface, delay_time, loss_rate)
                display.clear()
                display.text_pixels(interface+"\n"+str(status_code)+", "+reason, x=0, y=0, font=FONT)
                display.update()
                time.sleep(0.5)

            time.sleep(2)
    ```

    This loop continuously checks the touch sensor. When pressed, it posts the metrics and resets the motors. It also allows resetting the motors by pressing any button.

## Conclusion

This script provides a simple way to report network metrics to `tc netem` using a LEGO EV3 brick. It can be easily adapted and extended for other use cases involving EV3 sensors and motors.
