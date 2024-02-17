# BrainGenix-NES
# AGPLv3

import json

from . import Configuration

from BrainGenix.NES.Client import RequestHandler

import BrainGenix.LibUtils.GetID
import BrainGenix.LibUtils.ConfigCheck


class PatchClampDAC:

    def __init__(self, _Configuration:Configuration, _RequestHandler:RequestHandler, _SimulationID:int):
        # Create Attributes
        self.Name =  _Configuration.Name
        self.RequestHandler = _RequestHandler
        self.SimulationID = _SimulationID

        # Run Configuration Check
        BrainGenix.LibUtils.ConfigCheck.ConfigCheck(_Configuration)

        # Create On Server
        ClampLocation = json.dumps(_Configuration.ClampLocation_um)
        DestinationCompartmentID = BrainGenix.LibUtils.GetID.GetID(_Configuration.DestinationCompartment)
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Tool/PatchClampDAC/Create?SimulationID={_SimulationID}&Name={_Configuration.Name}&DestinationCompartmentID={DestinationCompartmentID}&ClampLocation_um={ClampLocation}")
        assert(Response != None)
        self.ID = Response["PatchClampDACID"]


    ## Access Methods
    def SetOutputList(self, _Timestep_ms:float, _VoltageList:list):
        OutputList = json.dumps(_VoltageList)
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Tool/PatchClampDAC/SetOutputList?SimulationID={self.SimulationID}&TargetDAC={self.ID}&Timestep_ms={_Timestep_ms}&DACVoltages_mV={OutputList}")
        assert(Response != None)
        return Response["StatusCode"]