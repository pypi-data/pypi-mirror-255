import os
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
from rich.columns import Columns
from rich.markdown import Markdown
from rich.prompt import Prompt
import subprocess
from readchar import readkey,key
banner = """
# Ninja Connecter Wizard
"""
# This is ninja connector wizard this is wizard for the 
# this tool 
custom_theme = Theme({
    "good": "bold green1",
    "bad": "bold red"
})
console = Console(theme=custom_theme, record=True)
class Cliwiz:
    global selected_option
    def __init__(self, choices):
        self.choices = choices
        self.current_selection = 0

    def display_menu(self):
        os.system("clear")
        panel = Panel.fit(Markdown(banner), title="</>", width=80)
        console.print(Columns([panel]), style="yellow2")
        for i, choice in enumerate(self.choices):
            if i == self.current_selection:
                console.print(f":small_blue_diamond: {choice}", style="good")
            else:
                console.print(f"{choice}", style="good")

    def input_process(self):
        global selected_option
        while True:
            self.display_menu()
            keystroke = readkey()

            if keystroke == key.UP:
                if self.current_selection > 0:
                    self.current_selection -= 1
            elif keystroke == key.DOWN:
                if self.current_selection < len(self.choices) - 1:
                    self.current_selection += 1
            elif keystroke == key.ENTER:
                selected_option = self.choices[self.current_selection]
                print(f"[bold orchid]Selected: {selected_option}[/bold orchid]")
                break

def wizarding():
    wiz = Cliwiz(choices=['configure', 'login', 'add_device', 'connect', 'disconnect', 'logout'])
    try:
        wiz.input_process()
        if selected_option == "configure":
            subprocess.run("ninja configure",shell=True)
        elif selected_option == "login":
            subprocess.run("ninja login",shell=True)
        elif selected_option == "add_device":
            subprocess.run("ninja add_device",shell=True)
        elif selected_option == "connect":
            subprocess.run("ninja connect",shell=True)
        elif selected_option == "disconnect":
            subprocess.run("ninja disconnect",shell=True)
        elif selected_option == "logout":
            subprocess.run("ninja logout",shell=True)
        else:
            print("[bold green1]Option Not Valid[/bold green1]")
    except KeyboardInterrupt as k:
        print(f"[bold orchid]Keyboard Intrupted{k}[/bold orchid]")