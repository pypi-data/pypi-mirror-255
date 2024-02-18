# BrainGenix-NES
# AGPLv3

import json

from . import Configuration

from BrainGenix.NES.Client import RequestHandler
import BrainGenix.LibUtils.GetID

import BrainGenix.LibUtils.ConfigCheck


class Visualizer:

    def __init__(self, _RequestHandler:RequestHandler, _SimulationID:int):
        # Create Attributes
        self.RequestHandler = _RequestHandler
        self.SimulationID = _SimulationID


    ## Access Methods
    def GenerateVisualization(self, _Configuration:object):

        # Run Configuration Check
        BrainGenix.LibUtils.ConfigCheck.ConfigCheck(_Configuration)


        QueryList:list = []
        QueryList.append({
            "VisualizerGenerateImage": {
                "CameraPositionX_um": _Configuration.CameraPosition_um[0],
                "CameraPositionY_um": _Configuration.CameraPosition_um[1],
                "CameraPositionZ_um": _Configuration.CameraPosition_um[2],
                "CameraLookAtPositionX_um": _Configuration.CameraLookAtPosition_um[0],
                "CameraLookAtPositionY_um": _Configuration.CameraLookAtPosition_um[1],
                "CameraLookAtPositionZ_um": _Configuration.CameraLookAtPosition_um[2],
                "CameraFOV_deg": _Configuration.CameraFOV_deg,
                "SimulationID": self.SimulationID
            }
        })
        Response = self.RequestHandler.BuildPostQuery(QueryList, "/NES")[0]
        assert(Response != None)
        Status = Response["StatusCode"]

        
        


    def BuildMesh(self, _ImageWidth_px:int, _ImageHeight_px:int):

        QueryList:list = []
        QueryList.append({
            "VisualizerBuildMesh": {
                "ImageWidth_px": _ImageWidth_px,
                "ImageHeight_px": _ImageHeight_px,
                "SimulationID": self.SimulationID
            }
        })
        Response = self.RequestHandler.BuildPostQuery(QueryList, "/NES")[0]
        assert(Response != None)
        return Response["StatusCode"]

