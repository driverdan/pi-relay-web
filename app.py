#!/usr/bin/env python3
"""
Raspberry Pi Relay Controller Web App
Backend Flask application to control two relays via GPIO pins
"""

from flask import Flask, render_template, request, jsonify
import RPi.GPIO as GPIO
import time
import threading
import logging

app = Flask(__name__)

# GPIO pin configuration
RELAY1_PIN = 18  # GPIO 18 (Physical pin 12)
RELAY2_PIN = 19  # GPIO 19 (Physical pin 35)
RELAY3_PIN = 20  # GPIO 20 (Physical pin 38)
RELAY4_PIN = 21  # GPIO 21 (Physical pin 40)

# Relay states
relay_states = {
    'relay1': False,
    'relay2': False,
    'relay3': False,
    'relay4': False
}

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_gpio():
    """Initialize GPIO pins for relay control"""
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RELAY1_PIN, GPIO.OUT)
        GPIO.setup(RELAY2_PIN, GPIO.OUT)
        GPIO.setup(RELAY3_PIN, GPIO.OUT)
        GPIO.setup(RELAY4_PIN, GPIO.OUT)
        
        # Initialize relays to OFF state (assuming active LOW relays)
        GPIO.output(RELAY1_PIN, GPIO.HIGH)
        GPIO.output(RELAY2_PIN, GPIO.HIGH)
        GPIO.output(RELAY3_PIN, GPIO.HIGH)
        GPIO.output(RELAY4_PIN, GPIO.HIGH)
        
        logger.info("GPIO pins initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize GPIO: {e}")
        return False

def cleanup_gpio():
    """Clean up GPIO pins on exit"""
    try:
        GPIO.cleanup()
        logger.info("GPIO cleanup completed")
    except Exception as e:
        logger.error(f"GPIO cleanup failed: {e}")

def control_relay(relay_pin, state):
    """Control individual relay state"""
    try:
        # Assuming active LOW relays (common configuration)
        # LOW = ON, HIGH = OFF
        if state:
            GPIO.output(relay_pin, GPIO.LOW)
        else:
            GPIO.output(relay_pin, GPIO.HIGH)
        return True
    except Exception as e:
        logger.error(f"Failed to control relay on pin {relay_pin}: {e}")
        return False

@app.route('/')
def index():
    """Main page route"""
    return render_template('index.html', relay_states=relay_states)

@app.route('/api/relay/<int:relay_num>/toggle', methods=['POST'])
def toggle_relay(relay_num):
    """Toggle relay state"""
    if relay_num not in [1, 2, 3, 4]:
        return jsonify({'error': 'Invalid relay number'}), 400
    
    relay_key = f'relay{relay_num}'
    relay_pins = {1: RELAY1_PIN, 2: RELAY2_PIN, 3: RELAY3_PIN, 4: RELAY4_PIN}
    relay_pin = relay_pins[relay_num]
    
    # Toggle state
    new_state = not relay_states[relay_key]
    
    if control_relay(relay_pin, new_state):
        relay_states[relay_key] = new_state
        logger.info(f"Relay {relay_num} toggled to {'ON' if new_state else 'OFF'}")
        return jsonify({
            'success': True,
            'relay': relay_num,
            'state': new_state,
            'message': f'Relay {relay_num} turned {"ON" if new_state else "OFF"}'
        })
    else:
        return jsonify({'error': 'Failed to control relay'}), 500

@app.route('/api/relay/<int:relay_num>/set', methods=['POST'])
def set_relay(relay_num):
    """Set relay to specific state"""
    if relay_num not in [1, 2, 3, 4]:
        return jsonify({'error': 'Invalid relay number'}), 400
    
    data = request.get_json()
    if data is None or 'state' not in data:
        return jsonify({'error': 'Missing state parameter'}), 400
    
    state = bool(data['state'])
    relay_key = f'relay{relay_num}'
    relay_pins = {1: RELAY1_PIN, 2: RELAY2_PIN, 3: RELAY3_PIN, 4: RELAY4_PIN}
    relay_pin = relay_pins[relay_num]
    
    if control_relay(relay_pin, state):
        relay_states[relay_key] = state
        logger.info(f"Relay {relay_num} set to {'ON' if state else 'OFF'}")
        return jsonify({
            'success': True,
            'relay': relay_num,
            'state': state,
            'message': f'Relay {relay_num} set to {"ON" if state else "OFF"}'
        })
    else:
        return jsonify({'error': 'Failed to control relay'}), 500

@app.route('/api/status')
def get_status():
    """Get current relay states"""
    return jsonify({
        'relay1': relay_states['relay1'],
        'relay2': relay_states['relay2'],
        'relay3': relay_states['relay3'],
        'relay4': relay_states['relay4'],
        'timestamp': time.time()
    })

@app.route('/api/all/off', methods=['POST'])
def turn_all_off():
    """Turn off all relays"""
    success_count = 0
    relay_pins = {1: RELAY1_PIN, 2: RELAY2_PIN, 3: RELAY3_PIN, 4: RELAY4_PIN}
    
    for relay_num in [1, 2, 3, 4]:
        relay_key = f'relay{relay_num}'
        relay_pin = relay_pins[relay_num]
        
        if control_relay(relay_pin, False):
            relay_states[relay_key] = False
            success_count += 1
    
    if success_count == 4:
        logger.info("All relays turned OFF")
        return jsonify({
            'success': True,
            'message': 'All relays turned OFF',
            'states': relay_states
        })
    else:
        return jsonify({'error': 'Failed to turn off all relays'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize GPIO
    if setup_gpio():
        try:
            # Run Flask app
            app.run(host='0.0.0.0', port=5000, debug=False)
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        finally:
            cleanup_gpio()
    else:
        logger.error("Failed to initialize GPIO. Exiting.")
