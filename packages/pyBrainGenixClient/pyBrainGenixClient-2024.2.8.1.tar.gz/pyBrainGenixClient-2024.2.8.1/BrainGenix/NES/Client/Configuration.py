# BrainGenix-NES
# AGPLv3


# Configuration 'struct' for the client
class Configuration:

    def __init__(self):

        self.Mode = "Remote"

        self.Host:str = ""
        self.Port:int = 0
        self.UseHTTPS:bool = None

        self.AuthenticationMethod:str = "Token"
        self.Username:str = ""
        self.Password:str = ""
        self.Token:str = ""
        
