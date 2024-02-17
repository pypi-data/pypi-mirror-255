import subprocess
import os
import time
from rich.progress import Progress
from rich import print
from rich.prompt import Prompt

content = """
[Interface]
PrivateKey = {private_key}
Address = 172.30.0.19/32

[Peer]
PublicKey = 7RsI7PiuvapEqClIqUvcREjGfUgnPtBUbVYZwFWX/VA=
AllowedIPs = 172.30.0.0/16
Endpoint = vpn.selfmade.ninja:44556
PersistentKeepalive = 30
"""

class Freshinstall:


    def fresh_installation_ubuntu(self):
        print("[bold green1]:small_Blue_Diamond: Starting the process WireGuard [/bold green1]:Thumbs_Up:")
        wireguard_installed = subprocess.run(["sudo", "apt", "install", "-y", "wireguard-tools"],capture_output=True,)
        with Progress() as progress:
            task = progress.add_task("[bold green1]:small_Blue_Diamond: Installing WireGuard", total=10)
            start_time = time.time()
            downloaded_bytes = 0
            while not progress.finished:
                # Estimate download speed based on time
                elapsed_time = time.time() - start_time
                download_speed = downloaded_bytes / elapsed_time if elapsed_time > 0 else 0

                progress.update(task, advance=1, description=f"[bold green1]:small_Blue_Diamond: Download speed: {download_speed:.2f} bytes/s [bold green1]")
                time.sleep(1)  # Update every second

                # Example: estimate 1 byte downloaded per second
                downloaded_bytes += 1
        print("[bold green1]:small_Blue_Diamond: WireGuard Successfully Installed [/bold green1]:Thumbs_Up:")

        if wireguard_installed.returncode == 0:
            subprocess.run("wg genkey | sudo tee /etc/wireguard/private.key",shell=True,capture_output=True,)
            time.sleep(3)
            output = subprocess.run("sudo cat /etc/wireguard/private.key | wg pubkey | sudo tee /etc/wireguard/public.key",shell=True,stdout=subprocess.PIPE,)
            if output.returncode == 0:
                print("[bold green1]:small_Blue_Diamond: Keys Generated [/bold green1]:Thumbs_Up:")
                output2 = subprocess.run("sudo cat /etc/wireguard/private.key",shell=True,stdout=subprocess.PIPE,)
                private_key = output2.stdout.decode()
                config_content = content.replace("{private_key}", "{}".format(private_key))
                command = f'echo "{config_content}" | sudo tee /etc/wireguard/wg0.conf'
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                print("[bold green1]:small_Blue_Diamond: WireGuard configuration has been created [/bold green1]:Thumbs_Up:")