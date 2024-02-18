# BrainGenix-NES
# AGPLv3

import requests

from . import Configuration
from . import Modes
from . import RequestHandler

from .. import Simulation


def GetTokenFromCredentials(_Username:str, _Password:str, _BaseURI:str = "https://api.braingenix.org"):

    RequestURI = f"{_BaseURI}/Auth/GetToken?Username={_Username}&Password={_Password}"
    ServerRequst = requests.get(RequestURI)
    ResponseJSON = ServerRequst.json()

    if (ResponseJSON["StatusCode"] != 0):
        raise ValueError("Invalid Credentials Passed. Please Check Your Username/Password!")
    else:
        return ResponseJSON["AuthKey"]



class Client:

    def __init__(self, _Configuration:Configuration):

        # Get And Validate Configuration
        self.Configuration = _Configuration
        self.ValidateConfig()
        self.Setup()


    # Helper Functions
    def ValidateConfig(self):

        # Check Mode
        ValidModes =  [Modes.Remote, Modes.Local]
        if self.Configuration.Mode not in ValidModes:
            raise Exception("NES Client Configuration Mode Not Set")


        
        # Local not yet implemented
        if self.Configuration.Mode == Modes.Local:
            raise NotImplementedError("Randal - please copy this over from your vbp repo.")

        # Remote Mode
        elif self.Configuration.Mode == Modes.Remote:

            # Check That User Has Actually Set Host/Port
            if (self.Configuration.Host == ""):
                raise ValueError("Please Set The API Host (ClientConfig.Host string)")
            if (self.Configuration.Port == 0):
                raise ValueError("Please Set The API Port (ClientConfig.Port int)")
            if (self.Configuration.UseHTTPS == None):
                raise ValueError("Please Indicate If You Would Like To Use HTTPS Or HTTP (ClientConfig.UseHTTPS true/false)")
            if (self.Configuration.AuthenticationMethod not in ['Token', 'Password']):
                raise ValueError("Please Set The Method Of Authentication You Are Using (ClientConfig.AuthenticationMethod 'Token'/'Password')")
            if (self.Configuration.Token == "" and self.Configuration.AuthenticationMethod == "Token"):
                raise ValueError("Please Set The API Token (ClientConfig.Token string)")
            if (self.Configuration.Username == "" and self.Configuration.AuthenticationMethod == "Password"):
                raise ValueError("Please Set Your API Username (ClientConfig.Username string)")
            if (self.Configuration.Password == "" and self.Configuration.AuthenticationMethod == "Password"):
                raise ValueError("Please Set Your API Password (ClientConfig.Password string)")


            # Build Request URI Base
            ProtocolBase = "http"
            if (self.Configuration.UseHTTPS):
                ProtocolBase = "https"
            self.URIBase = f"{ProtocolBase}://{self.Configuration.Host}:{self.Configuration.Port}"



    def Setup(self): # this should do some logic to make sure the connection is actually good.

        # If We're Operating With Password Mode, Get The Token
        if (self.Configuration.AuthenticationMethod == "Password"):
            self.Configuration.Token = GetTokenFromCredentials(self.Configuration.Username, self.Configuration.Password, self.URIBase)

        self.RequestHandler = RequestHandler.RequestHandler(self.URIBase, self.Configuration.Token)
        self.HasConnection = True


    # Getter Functions
    def IsReady(self):
        return self.HasConnection
    
    def GetAPIVersion(self):
        Status = self.RequestHandler.MakeQuery("/Diagnostic/Version")
        return Status['Version']


    # Creation Functions
    # create=False is used when a Simulation object is needed during loading (see BG_API.py)
    def CreateSimulation(self, _SimulationConfig, create=True):
        return Simulation.Simulation(_SimulationConfig, self.RequestHandler, create=create)


    # NESRequest (generic with JSON data)
    # Note that what is returned is a JSON String, i.e. a
    # String (str) with JSON content. It is not a Python dict object.
    def NESRequest(self, RequestJSON):
        StatusJSON = self.RequestHandler.MakePostQuery(RequestJSON)
        return StatusJSON # for now... while testing...
