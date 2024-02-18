#!/usr/bin/python
import os
import sys
from rich import print
from rich.panel import Panel
import platform
# Action performed by the tool

ACTIONS = {
    "connect": "wgconnect",
    "disconnect": "wgdisconnect",
    "configure": "configure",
    "login": "login",
    "logout": "logout",
    "add_device": "add_device",
    "showinfo": "showinfo",
    "isinstalled":"isinstalled",
    "mypublickey":"mypublickey",
    "listdevices":"listdevices",
    "wizmode":"wizmode",
    "remove_device":"remove_device"
}
HELPMESSAGE = """
[bold red]Note:[/bold red] If you're using this VPN for the first time, run the below command to set up WireGuard: [bold green1]ninjalinker configure[/bold green1]

[bold green1]Usage:[/bold green1] $ ninjalinker configure [bold][/bold]

[bold green1]Other Options:[/bold green1]
  :small_blue_diamond: [bold]-h | --help[/bold]: Show available options
  :small_blue_diamond: [bold]configure[/bold]: Set up WireGuard
  :small_blue_diamond: [bold]login[/bold]: Log in to your GitLab account
  :small_blue_diamond: [bold]add_device[/bold]: Add a new device
  :small_blue_diamond: [bold]connect[/bold]: Establish a connection
  :small_blue_diamond: [bold]disconnect[/bold]: Terminate the connection
  :small_blue_diamond: [bold]logout[/bold]: Log out from GitLab
  :small_blue_diamond: [bold]remove_device[/bold]: Remove a device from GitLab

For detailed documentation, check [bold]https://docs.selfmade.ninja/[/bold]

"""
# Below code is to find the platform 
if platform.system().lower() == "linux":
    from ninjalinker.wglib.wg import Wireguard
elif platform.system().lower() == "windows":
    from ninjalinker.wglib.windowswg import windowswireguard as Wireguard
elif platform.system().lower() == "mac":
    print("[bold red]:small_blue_diamond: Under Development Comming soon[/bold red]")
else:
    print("[bold red]Unsupported Platform[/bold red]")

def main():
    if len(sys.argv) < 2 or sys.argv[1] == "--help" or sys.argv[1] =="-h":
        print(HELPMESSAGE)
        return

    action = sys.argv[1]

    if action in ACTIONS:
        action_function_name = ACTIONS[action]
        wireguardobj = Wireguard()

        if hasattr(wireguardobj, action_function_name):
            action_function = getattr(wireguardobj, action_function_name)
            print(f"[bold green1]:small_blue_diamond: Performing action: [bold]{action}[/bold][/bold green1]")
            action_function()
        else:
            print(f"[red]Error:[/red] Action '{action}' not supported.")
    else:
        print(f"[red]Error:[/red] Action '{action}' not recognized. see ninja -h or --help")
if __name__ == "__main__":
    main()