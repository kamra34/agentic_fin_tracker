"""
Script to kill processes using a specific port on Windows
"""

import subprocess
import sys


def kill_process_on_port(port):
    """Kill all processes using the specified port"""
    print(f"Looking for processes using port {port}...")

    try:
        # Find processes using the port
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode != 0 or not result.stdout.strip():
            print(f"No processes found using port {port}")
            return

        # Extract PIDs from netstat output
        pids = set()
        for line in result.stdout.strip().split('\n'):
            parts = line.split()
            if len(parts) >= 5:
                pid = parts[-1]
                if pid.isdigit():
                    pids.add(pid)

        if not pids:
            print(f"No processes found using port {port}")
            return

        print(f"Found {len(pids)} process(es) using port {port}")

        # Kill each process
        for pid in pids:
            print(f"Killing process {pid}...")
            try:
                subprocess.run(f'taskkill /F /PID {pid}', shell=True, check=True)
                print(f"✓ Successfully killed process {pid}")
            except subprocess.CalledProcessError:
                print(f"✗ Failed to kill process {pid} (may require admin privileges)")

        print(f"\n✓ Port {port} is now free")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else "8001"
    kill_process_on_port(port)
