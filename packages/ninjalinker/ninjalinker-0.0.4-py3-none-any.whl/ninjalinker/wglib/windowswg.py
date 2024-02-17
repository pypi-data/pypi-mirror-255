import subprocess
import os
import ctypes
import requests
import rich
from rich import print
from rich.prompt import Prompt
from rich.console import Console
from rich.panel import Panel
from ninjalinker.wglib.storesess import Store
from ninjalinker.wgexpection.wireguardexpections import *
import json
import urllib.parse
import tempfile
from ninjalinker.wglib.auth import GitlabOuth
from ninjalinker.wglib.headlessdevice import HeadlessDeviceAuth
import shutil
import platform
console = Console()
ob = Store()
SERVICENAME = "SNALABS"
USERNAME = "SNALABS"
msi_url = "https://download.wireguard.com/windows-client/wireguard-installer.exe"
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:
        return False
def gui_retun_code():
    if platform.system() == "Linux":
        if "DISPLAY" in os.environ:
            return 1
        else:
            return 0
    elif platform.system() == "Windows":
        if "WINDIR" in os.environ:
            return 1
        else:
            return 0
gui_retun_code()
version = "0.0.4"
class windowswireguard:
    def wireguardcheck(self):
        if os.path.exists("C:\Program Files\WireGuard\Data"):
            return True
        else:
            return False
    def configure(self):
        try:
            if not self.wireguardcheck():
                wireguardmsi = requests.get(msi_url)
                open(r"C:\Users\wireguard-installer.exe", "wb").write(wireguardmsi.content)
                subprocess.run([r"C:\Users\wireguard-installer.exe", "/S"], shell=True)
                print(":small_blue_diamond:[bold green1] WireGuard Installed Successfully [/bold green1]")
                self.generatekeys()
                print(":small_blue_diamond:[bold green1] Keys Generated Successfully [/bold green1]")
                print(":small_blue_diamond:[bold green1] Now login with ninjalinker login command [/bold green1]")
            else:
                print(":Warning:[bold Red]  Note: The tool only work in cli mode [/bold Red]")
                print(":Warning:[bold Red]  WireGuard Already Installed but not configured for this vpn[/bold Red]")
                print(":small_blue_diamond:[bold green1] Give yes to configure and use the wireguard in cli mode [/bold green1]")
                try:
                    reconfig = Prompt.ask("[bold green1]:small_blue_diamond: Are you going use wireguard in cli mode (yes/no) [/bold green1]")
                except KeyboardInterrupt:
                    print(":small_blue_diamond:[bold red] Keyboard Interrupted[/bold red]")
                else:
                    if reconfig.lower() in ["y", "yes"]:
                        self.newconfigure()
                    elif reconfig.lower() in ["n", "no"]:
                        print("[bold green1]:small_blue_diamond: OK go with GUI [bold green1]")
                    else:
                        print("[bold green1]:small_blue_diamond: Option not valid[bold green1]")
        except Exception as e:
            print(f"[bold red]:Prohibited: Run the cmd or terminal as Administrator [bold red]")
    def generatekeys(self):
        privatekey = subprocess.run('"C:\Program Files\WireGuard\wg.exe" genkey', shell=True, capture_output=True, text=True)
        if privatekey.returncode == 0:
            private_key_str = privatekey.stdout
            public_key_gen = f'"C:\Program Files\WireGuard\wg.exe" pubkey'
            publickey = subprocess.run(public_key_gen, shell=True,input=private_key_str, capture_output=True, text=True)
            public_key_str = publickey.stdout
            private_file_path = "C:\Program Files\WireGuard\private.key"
            public_file_path = "C:\Program Files\WireGuard\public.key"

            with open(private_file_path, "w") as private_file:
                private_file.write(private_key_str)

            with open(public_file_path, "w") as public_file:
                public_file.write(public_key_str)
    def getwinpublickey(self):
        with open("C:\Program Files\WireGuard\public.key","r") as public:
            return public.read()
    def getwinprivatekey(self):
        with open("C:\Program Files\WireGuard\private.key","r") as private:
            return private.read()
    def winlistdevices(self):
        try:
            session = ob.getsess()
            if session is not None:
                alllsitdeviceurl = "https://labs.selfmade.ninja/api/device/v2/all"
                headers = {"Cookie": f"PHPSESSID={session}"}
                deviceresponse = requests.get(alllsitdeviceurl, headers=headers)
                devicedata = deviceresponse.json()
                return devicedata
            else:
                # print(":small_blue_diamond: [bold red1]Your are not login[bold red1]")        
                return []
        except:
            print("[bold red]:small_blue_diamond: No Such Password found[/bold red]")
    def addip(self):
        # Load JSON data from 'labs.json'
        with open('labs.json', "r") as l:
            content = json.load(l)
            preer = content.get("peer_info", {})
            allowed_ips = preer.get('allowed ips')

        try:
            # Use subprocess to create a temporary PowerShell script
            temp_dir = tempfile.mkdtemp()
            temp_script = f"{temp_dir}\\modify_wg.ps1"

            # Construct the PowerShell script
            powershell_script = [
                f'$content = Get-Content "C:\\Program Files\\WireGuard\\Win.conf"',
                f'$content -replace \'(?<=Address\s*=\s*)\S+\', "{allowed_ips}" | Set-Content "C:\\Program Files\\WireGuard\\Win.conf"'
            ]

            # Write the PowerShell script to a temporary file
            with open(temp_script, 'w') as script_file:
                script_file.write('\n'.join(powershell_script))

            # Run the PowerShell script with -ExecutionPolicy Bypass using subprocess
            subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', temp_script], check=True)

            # ipmodify = [
            #     "[bold green1]:small_blue_diamond: Device IP Added :link:[/bold green1]",
            # ]
            # ippanel = Panel("\n".join(ipmodify), title='SELF-MADE-NINJA-ACADEMY-CLI-VPN', style='bold orchid')
            # console = Console()
            # console.print(ippanel)
        except subprocess.CalledProcessError:
            print("Error: Failed to modify 'Win.conf'")
    def add_device(self):
        try:
            if ob.getsess() is not None and is_admin():
                device_name = Prompt.ask("[bold green1]:small_blue_diamond: Enter the device name :Desktop_Computer:  [/bold green1]")
                device_url = "https://labs.selfmade.ninja/api/device/add"
                payload = {
                    "device_name": str(device_name),
                    "device_type": "Laptop",
                    "device_key": self.getwinpublickey(),
                }
                session = ob.getsess()
                headers = {"Cookie": f"PHPSESSID={session}"}
                response = requests.post(device_url, headers=headers, data=payload)
                data = response.json()
                json_string = json.dumps(data,indent=4)
                with open("labs.json", "w") as j:
                    j.write(json_string)
                    # connected_device =  len(self.winlistdevices())
                    # print(f"[bold red1]:small_blue_diamond: No of Added devices in labs {connected_device}[/bold red1]")
                if response.status_code == 200:
                    self.configfilecreate()
                    self.addip()
                    print("[bold green1]:small_blue_diamond: Device added successfully![/bold green1]")
                    print("[bold green1]:small_blue_diamond: Now use ninjalinker connect to connect[/bold green1]")
                elif response.status_code == 409:
                    print("[bold red1]:small_blue_diamond: This Device Already Registered :No_Entry:[/bold red1]")
                elif "You reached a rate limit" in response.text:
                    print("[bold red1]:small_blue_diamond: You have reached the limit of devices. You cannot add more. You can delete an existing device and add one.:No_Entry:[/bold red1]")
            else:
                print("[bold red]:Prohibited: Login and run the command promt as admin [/bold red]")
        except PermissionError:
            print("[bold red]:Prohibited: Login and run the command promt as admin ")
        except KeyboardInterrupt:
            print("[bold red]:Prohibited: Keyboard Interrupted ")

    def configfilecreate(self):
        deviceiplabconf = "https://labs.selfmade.ninja/api/device/wgconfig?id="
        publickey = self.getwinpublickey()
        encodepublickey = urllib.parse.quote(publickey)
        session = ob.getsess()
        headers = {"Cookie": f"PHPSESSID={session}"}
        configresponse = requests.get(deviceiplabconf+encodepublickey,headers=headers)
        tunnelconf = configresponse.text.replace("{private_key}",self.getwinprivatekey())
        with open("C:\Program Files\WireGuard\Win.conf","w") as w:
            w.write(tunnelconf)

    def wgconnect(self):
        if ob.getkey() is not None and is_admin():
            try:
                subprocess.run('wireguard /installtunnelservice "C:\Program Files\WireGuard\Win.conf',shell=True,capture_output=True)
                messages = [
                            "[bold green1]:small_blue_diamond: Device Connected Successfully to Labs [/bold green1]"]
                panel = Panel("\n".join(messages),title="SELF-MADE-NINJA-ACADEMY-CLI-VPN",style="bold orchid")
                console.print(panel)
            except subprocess.CalledProcessError as e:
                print(f"Error {e}")
        else:
            unabletolog = [
                "[bold red]:Prohibited: Login and run the command promt as admin ",
            ]
            uabletoconnect = Panel("\n".join(unabletolog),title='SELF-MADE-NINJA-ACADEMY-CLI-VPN',style='bold orchid')
            console.print(uabletoconnect)
    def wgdisconnect(self):
        if ob.getkey() is not None and is_admin():
            try:
                subprocess.run('wireguard /uninstalltunnelservice Win')
                disconnect_message = [
                    "[bold green1]:small_blue_diamond: Device [red1]disconnect[/red1] from labs[/bold green1]",
                ]
                disconnet_pannel = Panel("\n".join(disconnect_message),title='SELF-MADE-NINJA-ACADEMY-CLI-VPN',style='bold orchid')
                console.print(disconnet_pannel)
            except subprocess.CalledProcessError as e:
                print(f"Error{e}")
            except Exception as s:
                print("An error occurred",str(e))
        else:
            unabletolog = [
                "[bold red]:Prohibited: Login and run the command promt as admin ",
            ]
            uabletoconnect = Panel("\n".join(unabletolog),title='SELF-MADE-NINJA-ACADEMY-CLI-VPN',style='bold orchid')
            console.print(uabletoconnect)            
                
    def login(self):
        if gui_retun_code() == 1:
            auth = GitlabOuth()
            auth.gitlablogin()
        elif gui_retun_code() == 0:
            try:
                token_value = Prompt.ask("[bold green]:small_blue_diamond: Enter the GitLab token [/bold green]")
                headleessauth = HeadlessDeviceAuth(access_token=token_value)
                headleessauth.get_access_token_store()
            except KeyboardInterrupt as key:
                print(key)
    def logout(self):
        session = ob.getsess()
        if session is not None:
            ob.deletekey()
            gitloboutmessages = [
                "[bold green1]:small_blue_diamond: [red1]Logged[/red1] out from Gitlabs :door:[/bold green1]",
            ]
            gitlout = Panel("\n".join(gitloboutmessages),title="SELF-MADE-NINJA-ACADEMY-CLI-VPN",style="bold orchid")
            console.print(gitlout)
        else:
            notinlabs = [
                "[bold green1]:small_blue_diamond: You are not [red1]Logged[/red1] in gitlabs :Prohibited:[/bold green1]",
            ]
            notlogedin = Panel("\n".join(notinlabs),title="SELF-MADE-NINJA-ACADEMY-CLI-VPN",style="bold orchid")
            console.print(notlogedin)
    def newconfigure(self):
        try:
            subprocess.run('wmic product where name="WireGuard" call uninstall',capture_output=True,shell=True)
            folder_path = r'C:\Program Files\WireGuard'
            try:
                shutil.rmtree(folder_path)
            except Exception as e:
                pass
            wireguardmsi = requests.get(msi_url)
            open(r"C:\Users\wireguard-installer.exe","wb").write(wireguardmsi.content)
            subprocess.run([r"C:\Users\wireguard-installer.exe","/S"],shell=True)
            print(":small_blue_diamond:[bold green1] WireGuard Successfully Configured for this tool [/bold green1]")
            print(":small_blue_diamond:[bold green1] login with ninjalinker login command [/bold green1]")
            self.generatekeys()
        except subprocess.CalledProcessError as e:
            print(f"Error{e}")
    def showinfo(self):
        devices = len(self.winlistdevices())
        print(":small_blue_diamond:[green1 bold] NAME : Ninjalinker[/green1 bold]")
        print(f":small_blue_diamond:[green1 bold] Version : {version}[/green1 bold]")
        console.print(f":small_blue_diamond:[red1 bold] Number of connected devices in  labs {devices}[/red1 bold]")
        print(":small_blue_diamond: [green1 bold]Developed Prasaanth Sakthivel[/green1 bold] :wrench:")
        print(":small_blue_diamond: [green1 bold]Purpose : Educational VPN[/green1 bold] :mortar_board:")
        print(":small_blue_diamond: [green1 bold]Upto 5 device can connect to labs[/green1 bold] :link:")
        print(":small_blue_diamond: [green1 bold]Supported Platforms : Linux , Windows , IOT [/green1 bold] :penguin:")
        print(":small_blue_diamond: [green1 bold]PIP url : ")
    def remove_device(self):
        deleteapiurl  = "https://labs.selfmade.ninja/api/device/delete"
        payload = {
            'id': self.getwinpublickey(),
        }
        if gui_retun_code() == 1:
            session = ob.getsess()
        elif gui_retun_code() == 0:
            session = ob.getheadless()
        else:
            print("[bold red]Unsuppport Device[bold red]")
        headers = {"Cookie": f"PHPSESSID={session}"}
        try:
            response = requests.request("POST",url=deleteapiurl,headers=headers,data=payload)
            if "true" in response.text:
                print("[bold green1]:small_blue_diamond: Device Removed Succesfully[/bold green1]")
            else:
                raise UnabletoDeleteExpection(103,"Unable to Remove Device")
        except UnabletoDeleteExpection as d:
            print(d.args[0])