# Reverse-engineering Moen / U by Moen Faucet for Home Assistant Integration

## Executive summary
Your faucet uses **AWS IoT (MQTT over TLS, port 8883)** with **mutual TLS** (device presents a client certificate), and the official **mobile app** talks to **AWS API Gateway** endpoints (observed host: `*.execute-api.us-east-2.amazonaws.com`) to send commands.  
Local impersonation is not practical. The recommended path is to reproduce the **app→cloud API calls** (login → token → command).

---

## Evidence
- **Device IP**: 10.0.30.161
- **Cloud services**:
  - AWS IoT endpoint: `a1r2q5ic87novc-ats.iot.us-east-2.amazonaws.com:8883`
  - API Gateway host: e.g. `exo9f857n8.execute-api.us-east-2.amazonaws.com`
- **TLS client certificate CN**: `MOEN_...` (unique per device)
- **App JSON payloads** (examples, sanitized):
  ```json
  { "commandSrc": "app", "dispenseActiveTimeout": 120 }
  ```
  ```json
  { "client_id": "<client_id>", "username": "<email>", "password": "<password>" }
  ```

---

## Integration design (cloud API path)
1. **Login** to API Gateway with client_id, username, password → get `access_token`.
2. **List devices**: GET /devices → returns device ids.
3. **Send command**: POST /devices/{device_id}/commands with JSON (dispense, start, stop, preset).
4. **Poll status**: GET /devices/{device_id}/status or similar (observed in capture).

---

## Example HTTP flows

### Login
```bash
POST /prod/auth/login
Host: exo9f857n8.execute-api.us-east-2.amazonaws.com
Content-Type: application/json

{
  "client_id": "<client_id>",
  "username": "user@example.com",
  "password": "<REDACTED>"
}
```

### Command (dispense)
```bash
POST /prod/devices/<DEVICE_ID>/commands
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{
  "commandSrc": "app",
  "action": "dispense",
  "volume_ml": 250,
  "dispenseActiveTimeout": 120
}
```

---

## Home Assistant custom_component outline

### manifest.json
```json
{
  "domain": "moen_faucet",
  "name": "Moen Smart Faucet (Unofficial)",
  "version": "0.1.0",
  "requirements": ["requests>=2.28"],
  "dependencies": [],
  "codeowners": ["@you"],
  "iot_class": "cloud_polling"
}
```

### client.py (skeleton)
```python
import time, requests

API_BASE = "https://exo9f857n8.execute-api.us-east-2.amazonaws.com/prod"

class MoenClient:
    def __init__(self, client_id, username, password):
        self.client_id = client_id
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = None
        self.expiry = 0

    def login(self):
        payload = {"client_id": self.client_id, "username": self.username, "password": self.password}
        r = self.session.post(f"{API_BASE}/auth/login", json=payload)
        r.raise_for_status()
        data = r.json()
        self.token = data["access_token"]
        self.expiry = time.time() + data.get("expires_in", 3600) - 60
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        return data

    def ensure_auth(self):
        if not self.token or time.time() > self.expiry:
            self.login()

    def list_devices(self):
        self.ensure_auth()
        r = self.session.get(f"{API_BASE}/devices")
        r.raise_for_status()
        return r.json()

    def send_command(self, device_id, payload):
        self.ensure_auth()
        r = self.session.post(f"{API_BASE}/devices/{device_id}/commands", json=payload)
        r.raise_for_status()
        return r.json()
```

### Entities
- `button.start_dispense`
- `button.stop_dispense`
- `button.dispense_preset_X`
- `number.target_volume_ml`
- `sensor.faucet_state`
- `sensor.last_dispense_volume`
- `sensor.cloud_connected`

---

## Security & Legal notes
- Credentials are required (stored in HA secure config).
- All traffic goes via Moen’s cloud.
- May violate Terms of Service — proceed at own risk.
- Hardware key extraction (local MQTT impersonation) is possible but invasive.

---

## Next steps for implementer
1. Fill in exact endpoints from mitm capture.
2. Implement config_flow for username/client_id/password.
3. Implement MoenClient in `client.py`.
4. Expose entities and services.
5. Test login, list devices, send command.
6. Document usage and cautions.

---

