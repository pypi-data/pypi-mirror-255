from rich import print

class GitlabauthExpection(Exception):
    def __init__(self, statuscode, message):
        self.statuscode = statuscode
        self.message = message
        formatted_message = f"[bold red1]:small_blue_diamond: GitlabAuthexpection: Error Code {statuscode}, Message: {message}[/bold red1]"
        super().__init__(formatted_message)
        
class AlreadyregisterExpection(TypeError):
    def __init__(self, statuscode, message):
        self.statuscode = statuscode
        self.message = message
        formatted_message = f"[bold red1]:small_blue_diamond: AlreadyregisterExpection: Error Code {statuscode}, Message: {message}[/bold red1]"
        super().__init__(formatted_message)

class UnabletoDeleteExpection(Exception):
    def __init__(self,statuscode,message):
        self.statuscode = statuscode
        self.message = message
        formatted_message = f"[bold red1]:small_blue_diamond: UnabletoDeleteDevice: Error Code {statuscode}, Message: {message}[/bold red1]"
        super().__init__(formatted_message)