# BrainGenix-NES
# AGPLv3

import json

from . import Configuration

from BrainGenix.NES.Client import RequestHandler

import BrainGenix.LibUtils.ConfigCheck


class Cylinder:

    def __init__(self, _Configuration:Configuration, _RequestHandler:RequestHandler, _SimulationID:int):

        # Early exit if we're creating this with a bulk route
        if (_Configuration == None):
            return
        
        # Create Attributes
        self.Name = _Configuration.Name
        self.RequestHandler = _RequestHandler

        # Run Configuration Check
        BrainGenix.LibUtils.ConfigCheck.ConfigCheck(_Configuration)

        # Create Box On Server
        Point1Position = json.dumps(_Configuration.Point1Position_um)
        Point2Position = json.dumps(_Configuration.Point2Position_um)
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Geometry/Shape/Cylinder/Create?SimulationID={_SimulationID}&Name={_Configuration.Name}&Point1Radius_um={_Configuration.Point1Radius_um}&Point1Position_um={Point1Position}&Point2Radius_um={_Configuration.Point2Radius_um}&Point2Position_um={Point2Position}")
        assert(Response != None)
        self.ID = Response["ShapeID"]