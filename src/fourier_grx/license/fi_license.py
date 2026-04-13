# src/fourier_grx/license/fi_license.py
import os
import time
import json
import hashlib
import hmac
import uuid

from datetime import datetime, timedelta

from fourier_core.logger import *


class License:
    """Enhanced time lock to prevent simple tampering"""

    def __init__(self, days_allowed=365, license_file=".license"):
        self.days_allowed = days_allowed
        license_file = os.path.expanduser(license_file)
        license_file = os.path.expandvars(license_file)
        self.license_file = license_file
        self.machine_id = self._get_machine_id()

    def _get_machine_id(self):
        """Generate unique ID based on machine hardware"""
        return hashlib.md5(f"{uuid.getnode()}".encode()).hexdigest()

    def _sign_payload(self, payload_bytes):
        return hmac.new(self.machine_id.encode(), payload_bytes, hashlib.sha256).hexdigest()

    def _encode(self, data):
        """Base64 + XOR with integrity protection"""
        import base64
        key = self.machine_id[:8].encode()
        payload = {
            'first_run': data['first_run'],
            'machine_id': data['machine_id']
        }
        payload_json = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode()
        payload['sig'] = self._sign_payload(payload_json)
        json_bytes = json.dumps(payload, separators=(',', ':')).encode()
        xor_bytes = bytes(b ^ key[i % len(key)] for i, b in enumerate(json_bytes))
        return base64.b64encode(xor_bytes).decode()

    def _decode(self, encoded_data):
        """Base64 decode with signature verification"""
        import base64
        key = self.machine_id[:8].encode()
        xor_bytes = base64.b64decode(encoded_data.encode())
        json_bytes = bytes(b ^ key[i % len(key)] for i, b in enumerate(xor_bytes))
        data = json.loads(json_bytes.decode())

        sig = data.pop('sig', None)
        if sig is None:
            raise ValueError("Missing signature")
        payload_json = json.dumps(data, separators=(',', ':'), sort_keys=True).encode()
        expected_sig = self._sign_payload(payload_json)
        if not hmac.compare_digest(sig, expected_sig):
            raise ValueError("Signature mismatch")
        if data.get('machine_id') != self.machine_id:
            raise ValueError("Machine mismatch")

        return datetime.fromisoformat(data['first_run'])

    def _get_first_run_time(self):
        """Get first run time (create or read)"""
        if os.path.exists(self.license_file):
            try:
                with open(self.license_file, 'r', encoding='utf-8') as f:
                    return self._decode(f.read())
            except Exception:
                return None

        first_run = datetime.now()
        data = {
            'first_run': first_run.isoformat(),
            'machine_id': self.machine_id
        }

        os.makedirs(os.path.dirname(os.path.abspath(self.license_file)) or '.', exist_ok=True)
        with open(self.license_file, 'w', encoding='utf-8') as f:
            f.write(self._encode(data))

        return first_run

    def is_valid(self):
        """Check if license is valid"""
        first_run = self._get_first_run_time()
        if first_run is None:
            Logger().print_warning("License file is invalid or has been tampered with!")
            return False

        now = datetime.now()
        elapsed = now - first_run
        remaining = timedelta(days=self.days_allowed) - elapsed

        if remaining.total_seconds() <= 0:
            Logger().print_warning("Program has expired! Need re-authorization.")
            return False

        Logger().print_info(
            f"First run time: {first_run.strftime('%Y-%m-%d %H:%M')}"
        )
        return True


def license_init():
    """
    Initialize and validate license

    Jason 2026-01-26:
    默认授权 5 年，医疗器械类软件通常授权期限为 5 年，5 年后需要重新申请授权，这样有利于设备复购。
    """
    lic = License(days_allowed=365 * 5, license_file="~/.fourier-grx/.license")
    if not lic.is_valid():
        exit(1)


def main():
    lic = License(days_allowed=30, license_file="~/.fourier-grx/.license")
    if not lic.is_valid():
        Logger().print_warning("Program cannot start, please contact administrator: admin@fftai.com")
        exit(1)

    Logger().print_info("=" * 50)
    Logger().print_info("Program started successfully!")
    Logger().print_info("=" * 50)

    try:
        for i in range(10):
            Logger().print_info(f"Running... {i + 1}/10", end="", flush=True)
            time.sleep(1)
        Logger().print_info("FSMItem completed!")
    except KeyboardInterrupt:
        Logger().print_info("Program stopped")


if __name__ == "__main__":
    main()
