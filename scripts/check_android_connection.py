import subprocess
from pathlib import Path

ssh_key = Path.home() / ".ssh" / "termux_pixel7"

result = subprocess.run(
    [
        "ssh",
        "-i", str(ssh_key),
        "-o", "BatchMode=yes",
        "-o", "IdentitiesOnly=yes",
        "-o", "ConnectTimeout=10",
        "-p", "8022",
        "u0_a321@127.0.0.1",
        "termux-battery-status"
    ],
    capture_output=True,
    text=True,
    timeout=20,
    check=True
)

print("Android connected successfully")
print(result.stdout)
