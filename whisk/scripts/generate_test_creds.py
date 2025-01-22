#!/usr/bin/env python3
import subprocess
import os
from pathlib import Path

def run_command(cmd: list) -> None:
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        raise

def generate_local_creds():
    """Generate test credentials for local development only"""
    if not os.getenv("WHISK_LOCAL_DEV"):
        raise EnvironmentError("This script is for local development only!")

    creds_dir = Path("config/nats/creds")
    creds_dir.mkdir(parents=True, exist_ok=True)

    # Setup test environment
    commands = [
        ["nsc", "add", "operator", "--name", "KitchenAITest"],
        ["nsc", "add", "account", "--name", "SYSTEM"],
        ["nsc", "add", "account", "--name", "KITCHENAI_MASTER",
         "--js-mem-storage", "1G", "--js-disk-storage", "10G"],
        ["nsc", "add", "account", "--name", "TEST_USER1",
         "--js-mem-storage", "500M", "--js-disk-storage", "5G"],
        ["nsc", "add", "user", "--name", "master-test", "--account", "KITCHENAI_MASTER"],
        ["nsc", "add", "user", "--name", "user1-test", "--account", "TEST_USER1"],
    ]

    for cmd in commands:
        run_command(cmd)

    # Generate credential files
    run_command(["nsc", "generate", "creds",
                "--name", "master-test",
                "--account", "KITCHENAI_MASTER",
                "--output", str(creds_dir / "master.creds")])
    
    run_command(["nsc", "generate", "creds",
                "--name", "user1-test",
                "--account", "TEST_USER1",
                "--output", str(creds_dir / "user1.creds")])

if __name__ == "__main__":
    generate_local_creds() 