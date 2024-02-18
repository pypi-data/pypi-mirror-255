from rich import print

class Listdevice(Exception):
    def __init__(self, statuscode, message):
        self.statuscode = statuscode
        self.message = message
        formatted_message = f"[bold red1]DeviceListExpection: Status Code {statuscode}, Message: {message}[/bold red1]"
        super().__init__(formatted_message)