# BrainGenix-NES
# AGPLv3

import json

from . import Configuration

from BrainGenix.NES.Client import RequestHandler
import BrainGenix.LibUtils.GetID

import BrainGenix.LibUtils.ConfigCheck


class PatchClampADC:

    def __init__(self, _Configuration:Configuration, _RequestHandler:RequestHandler, _SimulationID:int):
        # Create Attributes
        self.Name =  _Configuration.Name
        self.RequestHandler = _RequestHandler
        self.SimulationID = _SimulationID

        # Run Configuration Check
        BrainGenix.LibUtils.ConfigCheck.ConfigCheck(_Configuration)

        # Create On Server
        ClampLocation = json.dumps(_Configuration.ClampLocation_um)
        SourceCompartmentID = BrainGenix.LibUtils.GetID.GetID(_Configuration.SourceCompartment)
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Tool/PatchClampADC/Create?SimulationID={_SimulationID}&Name={_Configuration.Name}&SourceCompartmentID={SourceCompartmentID}&ClampLocation_um={ClampLocation}")
        assert(Response != None)
        self.ID = Response["PatchClampADCID"]


    ## Access Methods
    def SetSampleRate(self, _Timestep_ms:float):
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Tool/PatchClampADC/SetSampleRate?SimulationID={self.SimulationID}&TargetADC={self.ID}&Timestep_ms={_Timestep_ms}")
        assert(Response != None)
        return Response["StatusCode"]

    def GetRecordedData(self):
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Tool/PatchClampADC/GetRecordedData?SimulationID={self.SimulationID}&TargetADC={self.ID}")
        assert(Response != None)
        return Response