
from dataclasses import dataclass
from pathlib import Path
import json
import os
import re
import subprocess
import time


@dataclass(frozen=True)
class AndroidSmsOtpProvider:
    ssh_user: str
    sender: str
    code_length: int = 4
    ssh_port: int = 18022
    ssh_key: Path | None = None

    @classmethod
    def from_environment(cls):
        user = os.getenv("TERMUX_SSH_USER", "").strip()
        sender = os.getenv("PROCREDIT_SMS_SENDER", "").strip()
        length = int(os.getenv("PROCREDIT_OTP_LENGTH", "4"))
        key = Path(os.getenv("TERMUX_SSH_KEY", str(Path.home() / ".ssh" / "termux_pixel7"))).expanduser()
        if not re.fullmatch(r"[\w-]+", user, flags=re.ASCII):
            raise ValueError("Set TERMUX_SSH_USER to the value from Termux 'whoami'")
        if not sender:
            raise ValueError("Set PROCREDIT_SMS_SENDER to the sender shown in your SMS app")
        if length not in (4, 5, 6, 7, 8):
            raise ValueError("PROCREDIT_OTP_LENGTH must be 4–8")
        if not key.is_file():
            raise FileNotFoundError("The configured TERMUX_SSH_KEY was not found")
        return cls(user, sender, length, ssh_key=key)

    def _read_messages(self):
        command = [
            "ssh",
            "-i", str(self.ssh_key),
            "-p", str(self.ssh_port),
            "-o", "BatchMode=yes",
            "-o", "IdentitiesOnly=yes",
            "-o", "ForwardAgent=no",
            "-o", "Compression=no",
            "-o", "StrictHostKeyChecking=yes",
            "-o", "ConnectTimeout=8",
            f"{self.ssh_user}@127.0.0.1",
            "termux-sms-list -t inbox -l 30",
        ]
        try:
            response = subprocess.run(command, capture_output=True, text=True,
                                      encoding="utf-8", errors="replace",
                                      timeout=25, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise RuntimeError("Cannot reach Termux SMS API via local SSH") from exc
        if response.returncode:
            # Never include stderr or stdout in raised errors: either may expose SMS text.
            raise RuntimeError("SMS read failed: check ADB forward, SSH agent and Termux permissions")
        try:
            items = json.loads(response.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError("SMS API returned invalid JSON") from exc
        if not isinstance(items, list):
            raise RuntimeError("SMS API returned an unexpected response")
        return [m for m in items if isinstance(m, dict)]

    @staticmethod
    def _identity(message):
        # Stable key avoids using an older code on a later login attempt.
        identifier = message.get("_id") or message.get("id")
        if identifier is not None:
            return str(identifier)
        return json.dumps([message.get("number"), message.get("received"),
                           message.get("date"), message.get("body")], ensure_ascii=False)

    def snapshot_ids(self):
        """Call immediately before the click that requests a fresh code."""
        return {self._identity(m) for m in self._read_messages()}

    def wait_for_new_code(self, previous_ids, timeout=90, interval=2, purpose="login"):
        """Extract a new code from an explicitly labelled SMS from our bank.

        login:    the line starting `code: 1234`
        transfer: the line starting `TAN CODE: 1234`

        Transfer SMS messages also contain the recipient account's 4-digit suffix.
        Never guess which number is an OTP from arbitrary digit sequences.
        The default remains "login" for existing callers; final transfer steps
        must explicitly request purpose="transfer".
        """
        patterns = {
            "login": rf"^\s*code\s*:\s*(\d{{{self.code_length}}})(?!\d)",
            "transfer": rf"^\s*TAN\s+CODE\s*:\s*(\d{{{self.code_length}}})(?!\d)",
        }
        if purpose not in patterns:
            raise ValueError("SMS code purpose must be 'login' or 'transfer'")
        pattern = re.compile(patterns[purpose], re.IGNORECASE | re.MULTILINE)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            for msg in self._read_messages():
                if self._identity(msg) in previous_ids:
                    continue
                sender = str(msg.get("number") or msg.get("address") or "").strip()
                if sender.casefold() != self.sender.casefold():
                    continue
                matches = pattern.findall(str(msg.get("body") or ""))
                if len(matches) == 1:
                    return matches[0]
            time.sleep(min(interval, max(0, deadline - time.monotonic())))
        raise TimeoutError("No fresh labelled SMS code arrived from the configured sender")
