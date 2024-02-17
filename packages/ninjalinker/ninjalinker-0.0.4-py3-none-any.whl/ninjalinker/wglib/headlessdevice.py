import os
import requests
from rich import print
from rich.prompt import Prompt
from rich.panel import Panel
from rich.console import Console
console = Console()
api_url = "https://labs.selfmade.ninja/api/app/impersonate"

class HeadlessDeviceAuth:
    def __init__(self, access_token):
        self.access_token = access_token

    def get_access_token_store(self):
        username_cmd = "whoami"
        data = {
            "access_token": self.access_token
        }
        response = requests.post(api_url, data=data)

        if response.status_code == 200:
            user_data = response.json()
            session = user_data['PHPSESSID']
            output = os.popen(username_cmd).read()
            lnx_name = output.strip()

            with open(f"/usr/bin/labssession", 'w') as f:
                f.write(session)
            gitlabdata = [
                    "[bold green1]:small_blue_diamond: Gitlab Authentication Successfull[/bold green1]",
                    f"[bold green1]:small_blue_diamond: Name : {user_data['name']}[/bold green1]",
                    f"[bold green1]:small_blue_diamond: Email : {user_data['email']}[/bold green1]"
            ]
            gitlabp = Panel("\n".join(gitlabdata),title="SELF-MADE-NINJA-ACADEMY-CLI-VPN",style='bold orchid')
            console.print(gitlabp)
            premium_user = [
                "[bold green1]:small_blue_diamond: Enjoy Premium Access with Exclusive Features :star2::moneybag:[/bold green1]",
                f"[bold green1]:small_blue_diamond: Welcome, {user_data['name']}! Access the Full Range of Our Premium Services :trophy:[/bold green1]",
            ]
            premium_access_panel = Panel("\n".join(premium_user), title="Premium Access Experience", style='bold orchid')
            free_user = [
                "[bold green1]:small_blue_diamond: You're on our Free Plan. Discover Our Basic Features :bulb::unlock:[/bold green1]",
                f"[bold green1]:small_blue_diamond: Hello, {user_data['name']}! Start Your Journey with Our Free Access :smile:[/bold green1]",
            ]
            free_access_panel = Panel("\n".join(free_user), title="Welcome to Our Free Plan", style='bold orchid')
            if user_data['plan'] == "default":
                console.print(premium_access_panel)
            elif user_data['plan'] == "free":
                console.print(free_access_panel)
            else:
                print("[bold red]:small_blue_diamond: Your are not in the plan[/bold red]")
        elif response.status_code == 403:
            print("[bold red]:small_blue_diamond: Not Valid Token[/bold red]")
        else:
            print("Failed to make the request. Status code:", response.status_code)
            print("Response content:", response.text)

# token_value = Prompt.ask("[bold green]:small_blue_diamond: Enter the GitLab token [/bold green]")
# gitlab_auth = HeadlessDeviceAuth(access_token=token_value)
# gitlab_auth.get_access_token_store()