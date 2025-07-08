# Raspberry Pi Relay Controller Setup

## Hardware Requirements

- Raspberry Pi (3B+ or 4 recommended)
- 4-channel relay module (5V)
- Jumper wires
- Power supply for Raspberry Pi

## Wiring Connections

Connect the relay module to your Raspberry Pi:

```
Relay Module    Raspberry Pi
VCC         →   5V (Pin 2)
GND         →   Ground (Pin 6)
IN1         →   GPIO 18 (Pin 12)
IN2         →   GPIO 19 (Pin 35)
IN3         →   GPIO 20 (Pin 38)
IN4         →   GPIO 21 (Pin 40)
```

## Software Setup

### 1. Install Python Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python pip if not installed
sudo apt install python3-pip -y

# Install required Python packages
pip3 install flask RPi.GPIO
```

### 2. Create Project Structure

```bash
mkdir relay_controller
cd relay_controller
mkdir templates
```

### 3. Save the Files

Save the Python backend code as `app.py` in the `relay_controller` directory.

Save the HTML frontend code as `index.html` in the `templates` directory.

### 4. Enable GPIO Access

Add your user to the gpio group:

```bash
sudo usermod -a -G gpio $USER
```

Log out and log back in for the changes to take effect.

### 5. Run the Application

```bash
cd relay_controller
python3 app.py
```

The web interface will be available at:
- Local: `http://localhost:5000`
- Network: `http://[raspberry-pi-ip]:5000`

## Features

### Web Interface
- Modern, responsive design that adapts to 4 relays
- Real-time status indicators for all 4 relays
- Individual relay control (ON/OFF/Toggle) for each relay
- Master "Turn All OFF" button
- Auto-refresh every 30 seconds
- Error handling and user feedback
- Optimized layout for 4 relays with smaller cards

### API Endpoints
- `GET /` - Main web interface
- `POST /api/relay/<num>/toggle` - Toggle relay state
- `POST /api/relay/<num>/set` - Set relay to specific state
- `GET /api/status` - Get current relay states
- `POST /api/all/off` - Turn all relays off

### Example API Usage

```bash
# Get current status
curl http://localhost:5000/api/status

# Turn relay 1 ON
curl -X POST http://localhost:5000/api/relay/1/set \
  -H "Content-Type: application/json" \
  -d '{"state": true}'

# Turn relay 3 ON
curl -X POST http://localhost:5000/api/relay/3/set \
  -H "Content-Type: application/json" \
  -d '{"state": true}'

# Toggle relay 4
curl -X POST http://localhost:5000/api/relay/4/toggle

# Turn all relays OFF
curl -X POST http://localhost:5000/api/all/off
```

## Safety Notes

1. **Always disconnect power** when making wiring connections
2. **Double-check wiring** before powering on
3. **Use appropriate fuses** for high-power loads
4. **Never exceed relay ratings** (check your relay module specifications)
5. **Ensure proper isolation** between low-voltage control and high-voltage loads

## Troubleshooting

### GPIO Permission Issues
```bash
# Check if user is in gpio group
groups $USER

# If not in gpio group, add user
sudo usermod -a -G gpio $USER
```

### Port Already in Use
```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill process if needed
sudo kill -9 <PID>
```

### GPIO Already in Use
```bash
# Check GPIO usage
gpio readall

# If GPIO is stuck, try resetting
sudo gpio unexportall
```

## Customization

### Changing GPIO Pins
Edit the pin assignments in `app.py`:
```python
RELAY1_PIN = 18  # Change to your preferred pin
RELAY2_PIN = 19  # Change to your preferred pin
RELAY3_PIN = 20  # Change to your preferred pin
RELAY4_PIN = 21  # Change to your preferred pin
```

### Adding More Relays
1. Add new pin definitions
2. Update the `relay_states` dictionary
3. Add new API endpoints (update the validation ranges)
4. Update the HTML template with new relay cards

### Running as Service
Create a systemd service file:
```bash
sudo nano /etc/systemd/system/relay-controller.service
```

Add service configuration:
```ini
[Unit]
Description=Raspberry Pi Relay Controller
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/relay_controller
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable relay-controller.service
sudo systemctl start relay-controller.service
```

## Security Considerations

- The app runs on all interfaces (0.0.0.0) for network access
- Consider adding authentication for production use
- Use HTTPS in production environments
- Implement rate limiting for API endpoints
- Consider firewall rules to restrict access