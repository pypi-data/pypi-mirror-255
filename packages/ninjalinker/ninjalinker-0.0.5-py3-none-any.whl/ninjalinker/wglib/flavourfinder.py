import subprocess
import os
import time
from rich.progress import Progress
from rich import print
from rich.prompt import Prompt
from ninjalinker.wglib.freshinstaller import Freshinstall
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

class FlavorFinder:
    INSTALLWG = "sudo apt-get install -y wireguard"
    INSTALLWGGET = "sudo apt-get install -y wireguard"
    INSTALLWGGETARCH = "sudo pacman -S --noconfirm wireguard-tools"

    def wgcheck(self):
        try:
            path = "/usr/bin/wg-quick"
            if os.path.exists(path):
                print(":Warning:[bold Red]  WireGuard Already Installed but not configured for this vpn[/bold Red]")
                print(":small_blue_diamond:[bold green1] Give yes to configure and use the wireguard in auto mode [/bold green1]")
                return True
            else:
                if self.getdistro() == "ubuntu":
                    installtion = Freshinstall()
                    installtion.fresh_installation_ubuntu()
            return False  # Return False if neither condition is met
        except subprocess.CalledProcessError as e:
            print("[bold red]:cross_mark: Error occurred with apt. Trying apt-get instead... [bold red]")
            try:
                subprocess.run(
                    self.INSTALLWGGET,
                    shell=True,
                    text=True,
                    check=True,
                    capture_output=False,
                )
            except subprocess.CalledProcessError as e:
                print(f"[bold red]:cross_mark: Error occurred. Check .env: {e.stderr.strip()} [bold red]")
            return False  # Return False if an error occurs

    def wgarchcheck(self):
        try:
            path = "/usr/bin/wg-quick"
            if os.path.exists(path):
                print(":Warning:[bold Red]  WireGuard Already Installed but not configured for this vpn[/bold Red]")
                print(":small_blue_diamond:[bold green1] Give yes to configure and use the wireguard in auto mode [/bold green1]")
                return True
            else:
                wgcmd1 = subprocess.run(
                    self.INSTALLWGGETARCH,
                    shell=True,
                    text=True,
                    check=True,
                    capture_output=False,
                )
                if "is already the newest version" in wgcmd1.stdout:
                    print("[bold green1]:small_Blue_Diamond: WireGuard is already installed [bold green1]")
                    return True
            return False  # Return False if neither condition is met
        except subprocess.CalledProcessError as e:
            print("[bold red]:cross_mark: Error occurred with pacman. [bold red]")
            try:
                subprocess.run(
                    self.INSTALLWGGETARCH,
                    shell=True,
                    text=True,
                    check=True,
                    capture_output=False,
                )
            except subprocess.CalledProcessError as e:
                print(f"[bold red]:cross_mark: Error occurred. Check .env: {e.stderr.strip()} [bold red]")
            return False  # Return False if an error occurs

    def getdistro(self):
        with open("/etc/os-release", 'r') as file:
            for line in file:
                if line.startswith("ID="):
                    key, value = line.strip().split("=")
                    return value.lower()

    def isinstalled(self):
        if os.path.exists("/usr/bin/wg"):
            return True
        else:
            return False
    def ubuntu_flav(self):
        try:
            subprocess.run(["sudo","apt-get", "remove", "--purge", "-y", "wireguard", "wireguard-tools"], check=True, capture_output=True)
            subprocess.run(["sudo","rm", "-rf", "/etc/wireguard/*"], check=True, capture_output=True)
            if self.isinstalled():
                print("[bold green1]:small_Blue_Diamond:Old Configurations removed[bold green1]")
            else:
                pass
            time.sleep(3)
            print("[bold green1]:small_Blue_Diamond: Initiating the process[bold green1]")
            wireguard_installed = subprocess.run(
                ["sudo", "apt", "install", "-y", "wireguard-tools"],
                capture_output=True,
            )
            with Progress() as progress:
                task = progress.add_task(
                    "[bold green1]:small_Blue_Diamond: Installing WireGuard", total=10.348
                )

                while not progress.finished:
                    progress.update(task, advance=1)
                    time.sleep(1)
            print("[bold green1]:small_Blue_Diamond: WireGuard Successfully Installed [/bold green1]:Thumbs_Up:")
            if wireguard_installed.returncode == 0:
                subprocess.run(
                    "wg genkey | sudo tee /etc/wireguard/private.key",
                    shell=True,
                    capture_output=True,
                )
                time.sleep(3)
                output = subprocess.run(
                    "sudo cat /etc/wireguard/private.key | wg pubkey | sudo tee /etc/wireguard/public.key",
                    shell=True,
                    stdout=subprocess.PIPE,
                )
                if output.returncode == 0:
                    print("[bold green1]:small_Blue_Diamond: Keys Generated [/bold green1]:Thumbs_Up:")
                output2 = subprocess.run(
                    "sudo cat /etc/wireguard/private.key",
                    shell=True,
                    stdout=subprocess.PIPE,
                )
                private_key = output2.stdout.decode()
                config_content = content.replace(
                    "{private_key}", "{}".format(private_key)
                )
                command = f'echo "{config_content}" | sudo tee /etc/wireguard/wg0.conf'
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                print("[bold green1]:small_Blue_Diamond: WireGuard configuration has been created [/bold green1]:Thumbs_Up:")
        except subprocess.CalledProcessError:
            print("[bold green1]:small_Blue_Diamond: Failed to install WireGuard. Please install it manually :No_Entry:")
            return
    def arch_flav(self):
        try:
            subprocess.run(["sudo","pacman", "-Rns", "--noconfirm","wireguard-tools"], check=True, capture_output=True)
            subprocess.run(["sudo","rm", "-rf", "/etc/wireguard/*"], check=True, capture_output=True)
            if self.isinstalled():
                print("[bold green1]:small_Blue_Diamond:Old Configurations removed[bold green1]")
            else:
                pass
            time.sleep(3)
            print("[bold green1]:small_Blue_Diamond: Initiating the process[bold green1]")
            wireguard_installed = subprocess.run(
                ["sudo", "pacman", "-S", "--noconfirm", "wireguard-tools"],
                capture_output=True,
            )
            with Progress() as progress:
                task = progress.add_task(
                    "[bold green1]:small_Blue_Diamond: Installing WireGuard", total=10.348
                )

                while not progress.finished:
                    progress.update(task, advance=1)
                    time.sleep(1)
            print("[bold green1]:small_Blue_Diamond: WireGuard Successfully Installed [/bold green1]:Thumbs_Up:")
            if wireguard_installed.returncode == 0:
                subprocess.run(
                    "wg genkey | sudo tee /etc/wireguard/private.key",
                    shell=True,
                    capture_output=True,
                )
                time.sleep(3)
                output = subprocess.run(
                    "sudo cat /etc/wireguard/private.key | wg pubkey | sudo tee /etc/wireguard/public.key",
                    shell=True,
                    stdout=subprocess.PIPE,
                )
                if output.returncode == 0:
                    print("[bold green1]:small_Blue_Diamond: Keys Generated [/bold green1]:Thumbs_Up:")
                output2 = subprocess.run(
                    "sudo cat /etc/wireguard/private.key",
                    shell=True,
                    stdout=subprocess.PIPE,
                )
                private_key = output2.stdout.decode()
                config_content = content.replace(
                    "{private_key}", "{}".format(private_key)
                )
                command = f'echo "{config_content}" | sudo tee /etc/wireguard/wg0.conf'
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                print("[bold green1]:small_Blue_Diamond: WireGuard configuration has been created [/bold green1]:Thumbs_Up:")
        except subprocess.CalledProcessError:
            print("[bold green1]:small_Blue_Diamond: Failed to install WireGuard. Please install it manually :No_Entry:")
            return
    def flavor_installer(self):
        if self.getdistro() == "ubuntu":
            if self.wgcheck():
                reconfigurestate = Prompt.ask("[bold green1]:small_Blue_Diamond: Are you going use wireguard in auto mode (yes/no) [bold green1]")
                if reconfigurestate.lower() == "y" or reconfigurestate.lower() == "yes":
                    self.ubuntu_flav()
                elif reconfigurestate.lower() == "n" or reconfigurestate.lower() == "no":
                    print("[bold green1]:small_Blue_Diamond: Ok go with manual setup [bold green1]")
        elif self.getdistro() == "arch":
            if self.wgarchcheck():
                reconfigurestate = Prompt.ask("[bold green1]:small_Blue_Diamond: Are you going use wireguard in auto mode (Y/N) [bold green1]")
                if reconfigurestate.lower() == "y" or reconfigurestate.lower() == "yes":
                    self.arch_flav()
                elif reconfigurestate.lower() == "n" or reconfigurestate.lower() == "no":
                    print("[bold green1]:small_Blue_Diamond: Ok go with manual setup [bold green1]")
        elif self.getdistro() == "debian":
            if self.wgcheck():
                reconfigurestate = Prompt.ask("[bold green1]:small_Blue_Diamond: Are you going use wireguard in auto mode (yes/no) [bold green1]")
                if reconfigurestate.lower() == "y" or reconfigurestate.lower() == "yes":
                    self.ubuntu_flav()
                elif reconfigurestate.lower() == "n" or reconfigurestate.lower() == "no":
                    print("[bold green1]:small_Blue_Diamond: Ok go with manual setup [bold green1]")
        return False  # Indicate failure
