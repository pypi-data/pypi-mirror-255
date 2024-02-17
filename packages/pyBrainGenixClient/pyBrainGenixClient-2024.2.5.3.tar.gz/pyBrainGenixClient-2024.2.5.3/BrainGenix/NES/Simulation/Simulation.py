# BrainGenix-NES
# AGPLv3

from .. import Models
from . import Configuration

from BrainGenix.NES.Client import RequestHandler

from BrainGenix.NES.Shapes import Sphere
from BrainGenix.NES.Shapes import Box
from BrainGenix.NES.Shapes import Cylinder

from BrainGenix.NES.VSDA import EM
from BrainGenix.NES.Models.Connections import Staple, Receptor
from BrainGenix.NES import Tools

import BrainGenix.LibUtils.ConfigCheck
import BrainGenix.LibUtils.GetID
import json

class Simulation():

    def __init__(self, _Configuration:Configuration, _RequestHandler:RequestHandler):
        # Create Attributes
        self.Name = _Configuration.Name
        self.RequestHandler = _RequestHandler

        # Run Configuration Check
        BrainGenix.LibUtils.ConfigCheck.ConfigCheck(_Configuration)

        # Create Sim On Server
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Simulation/Create?SimulationName={_Configuration.Name}")
        assert(Response != None)
        self.ID = Response["SimulationID"]


    
    ## Methods For Adding Objects

     # Tool Init Commands
    def AddPatchClampDAC(self, _PatchClampDACConfig:Tools.PatchClampDAC.Configuration):
        return Tools.PatchClampDAC.PatchClampDAC(_PatchClampDACConfig, self.RequestHandler, self.ID)

    def AddPatchClampADC(self, _PatchClampADCConfig:Tools.PatchClampADC.Configuration):
        return Tools.PatchClampADC.PatchClampADC(_PatchClampADCConfig, self.RequestHandler, self.ID)


     # Connection Init Commands
    def AddReceptor(self, _ReceptorConfig:Receptor.Configuration):
        return Receptor.Receptor(_ReceptorConfig, self.RequestHandler, self.ID)

    def AddStaple(self, _StapleConfig:Staple.Configuration):
        return Staple.Staple(_StapleConfig, self.RequestHandler, self.ID)


     # VSDA Init Commands
    def AddVSDAEM(self, _VSDAEMConfig:EM.Configuration):
        return EM.EM(_VSDAEMConfig, self.RequestHandler, self.ID)


     # Compartments Add Methods
    def AddBSCompartment(self, _BSCompartmentConfig:Models.Compartments.BS.Configuration):
        return Models.Compartments.BS.BS(_BSCompartmentConfig, self.RequestHandler, self.ID)


    def AddBSCompartments(self, _BSCompartmentConfigs:list):

        # Build data
        Names:list = []
        ShapeIDList:list = []
        MembranePotentialList_mV:list = []
        SpikeThresholdList_mV:list = []
        DecayTimeList_ms:list = []
        RestingPotentialList_mV:list = []
        AfterHyperpolarizationAmplitudeList_mV:list = []

        for Config in _BSCompartmentConfigs:
            BrainGenix.LibUtils.ConfigCheck.ConfigCheck(Config)
            Names.append(Config.Name)
            ShapeIDList.append(BrainGenix.LibUtils.GetID.GetID(Config.Shape))
            MembranePotentialList_mV.append(Config.MembranePotential_mV)
            SpikeThresholdList_mV.append(Config.SpikeThreshold_mV)
            DecayTimeList_ms.append(Config.DecayTime_ms)
            RestingPotentialList_mV.append(Config.RestingPotential_mV)
            AfterHyperpolarizationAmplitudeList_mV.append(Config.AfterHyperpolarizationAmplitude_mV)
        NameList = json.dumps(Names)
        ShapeIDList = json.dumps(ShapeIDList)
        MembranePotentialList_mV = json.dumps(MembranePotentialList_mV)
        SpikeThresholdList_mV = json.dumps(SpikeThresholdList_mV)
        DecayTimeList_ms = json.dumps(DecayTimeList_ms)
        RestingPotentialList_mV = json.dumps(RestingPotentialList_mV)
        AfterHyperpolarizationAmplitudeList_mV = json.dumps(AfterHyperpolarizationAmplitudeList_mV)
        IDs = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Compartment/BS/BulkCreate?SimulationID={self.ID}&NameList={NameList}&ShapeIDList={ShapeIDList}&MembranePotentialList_mV={MembranePotentialList_mV}&SpikeThresholdList_mV={SpikeThresholdList_mV}&DecayTimeList_ms={DecayTimeList_ms}&RestingPotentialList_mV={RestingPotentialList_mV}&AfterHyperpolarizationAmplitudeList_mV={AfterHyperpolarizationAmplitudeList_mV}")["CompartmentIDs"]

        Objects:list = []
        for i in range(len(IDs)):
            Object = Models.Compartments.BS.BS(None, None, None)
            Object.ID = IDs[i]
            Object.Name = Names[i]
            Objects.append(Object)

        return Objects

    # Neurons Add Methods
    def AddBSNeuron(self, _BSNeuronConfig:Models.Neurons.BS.Configuration):
        return Models.Neurons.BS.BSNeuron(_BSNeuronConfig, self.RequestHandler, self.ID)

    
     # Geometry Add Methods
    def AddSphere(self, _SphereConfig:Sphere.Configuration):
        return Sphere.Sphere(_SphereConfig, self.RequestHandler, self.ID)

    def AddSpheres(self, _SphereConfigs:list):

        # Build data
        Names:list = []
        RadiusList:list = []
        CenterXList:list = []
        CenterYList:list = []
        CenterZList:list = []
        for SphereConfig in _SphereConfigs:
            BrainGenix.LibUtils.ConfigCheck.ConfigCheck(SphereConfig)
            Names.append(SphereConfig.Name)
            RadiusList.append(SphereConfig.Radius_um)
            CenterXList.append(SphereConfig.Center_um[0])
            CenterYList.append(SphereConfig.Center_um[1])
            CenterZList.append(SphereConfig.Center_um[2])
        NameList = json.dumps(Names)
        RadiusList = json.dumps(RadiusList)
        CenterXList_um = json.dumps(CenterXList)
        CenterYList_um = json.dumps(CenterYList)
        CenterZList_um = json.dumps(CenterZList)
        IDs = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Geometry/Shape/Sphere/BulkCreate?SimulationID={self.ID}&NameList={NameList}&RadiusList_um={RadiusList}&CenterXList_um={CenterXList_um}&CenterYList_um={CenterYList_um}&CenterZList_um={CenterZList_um}")["ShapeIDs"]


        Objects:list = []
        for i in range(len(IDs)):
            Object = Sphere.Sphere(None, None, None)
            Object.ID = IDs[i]
            Object.Name = Names[i]
            Objects.append(Object)

        return Objects


    def AddBox(self, _BoxConfig:Box.Configuration):
        return Box.Box(_BoxConfig, self.RequestHandler, self.ID)

    def AddBoxes(self, _BoxConfigs:list):

        # Build data
        Names:list = []
        CenterXList:list = []
        CenterYList:list = []
        CenterZList:list = []
        DimensionsXList:list = []
        DimensionsYList:list = []
        DimensionsZList:list = []
        RotationXList:list = []
        RotationYList:list = []
        RotationZList:list = []
        for Config in _BoxConfigs:
            BrainGenix.LibUtils.ConfigCheck.ConfigCheck(Config)
            Names.append(Config.Name)
            CenterXList.append(Config.CenterPosition_um[0])
            CenterYList.append(Config.CenterPosition_um[1])
            CenterZList.append(Config.CenterPosition_um[2])
            DimensionsXList.append(Config.Dimensions_um[0])
            DimensionsYList.append(Config.Dimensions_um[1])
            DimensionsZList.append(Config.Dimensions_um[2])
            RotationXList.append(Config.Rotation_rad[0])
            RotationYList.append(Config.Rotation_rad[1])
            RotationZList.append(Config.Rotation_rad[2])
        NameList = json.dumps(Names)
        CenterXList_um = json.dumps(CenterXList)
        CenterYList_um = json.dumps(CenterYList)
        CenterZList_um = json.dumps(CenterZList)
        DimensionsZList_um = json.dumps(DimensionsZList)
        DimensionsXList_um = json.dumps(DimensionsXList)
        DimensionsYList_um = json.dumps(DimensionsYList)
        RotationXList_um = json.dumps(RotationXList)
        RotationYList_um = json.dumps(RotationYList)
        RotationZList_um = json.dumps(RotationZList)
        IDs = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Geometry/Shape/Box/BulkCreate?SimulationID={self.ID}&NameList={NameList}&CenterXList_um={CenterXList_um}&CenterYList_um={CenterYList_um}&CenterZList_um={CenterZList_um}&DimensionsXList_um={DimensionsXList_um}&DimensionsYList_um={DimensionsYList_um}&DimensionsZList_um={DimensionsZList_um}&RotationXList_rad={RotationXList_um}&RotationYList_rad={RotationYList_um}&RotationZList_rad={RotationZList_um}")["ShapeIDs"]

        Objects:list = []
        for i in range(len(IDs)):
            Object = Box.Box(None, None, None)
            Object.ID = IDs[i]
            Object.Name = Names[i]
            Objects.append(Object)

        return Objects

    def AddCylinder(self, _CylinderConfig:Cylinder.Configuration):
        return Cylinder.Cylinder(_CylinderConfig, self.RequestHandler, self.ID)

    def AddCylinders(self, _CylinderConfigs:list):

        # Build data
        Names:list = []
        Point1RadiusList:list = []
        Point2RadiusList:list = []
        Point1XList:list = []
        Point1YList:list = []
        Point1ZList:list = []
        Point2XList:list = []
        Point2YList:list = []
        Point2ZList:list = []

        for Config in _CylinderConfigs:
            BrainGenix.LibUtils.ConfigCheck.ConfigCheck(Config)
            Names.append(Config.Name)
            Point1RadiusList.append(Config.Point1Radius_um)
            Point2RadiusList.append(Config.Point2Radius_um)
            Point1XList.append(Config.Point1Position_um[0])
            Point1YList.append(Config.Point1Position_um[1])
            Point1ZList.append(Config.Point1Position_um[2])
            Point2XList.append(Config.Point2Position_um[0])
            Point2YList.append(Config.Point2Position_um[1])
            Point2ZList.append(Config.Point2Position_um[2])
        NameList = json.dumps(Names)
        Point1RadiusList_um = json.dumps(Point1RadiusList)
        Point2RadiusList_um = json.dumps(Point2RadiusList)
        Point1ZList_um = json.dumps(Point1ZList)
        Point1XList_um = json.dumps(Point1XList)
        Point1YList_um = json.dumps(Point1YList)
        Point2XList_um = json.dumps(Point2XList)
        Point2YList_um = json.dumps(Point2YList)
        Point2ZList_um = json.dumps(Point2ZList)
        IDs = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Geometry/Shape/Cylinder/BulkCreate?SimulationID={self.ID}&NameList={NameList}&Point1RadiusList_um={Point1RadiusList_um}&Point2RadiusList_um={Point2RadiusList_um}&Point2XList_um={Point2XList_um}&Point2YList_um={Point2YList_um}&Point2ZList_um={Point2ZList_um}&Point1XList_um={Point1XList_um}&Point1YList_um={Point1YList_um}&Point1ZList_um={Point1ZList_um}")["ShapeIDs"]

        Objects:list = []
        for i in range(len(IDs)):
            Object = Cylinder.Cylinder(None, None, None)
            Object.ID = IDs[i]
            Object.Name = Names[i]
            Objects.append(Object)

        return Objects
    

    ## Simulation Update Routes
    def Reset(self):
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Simulation/Reset?SimulationID={self.ID}")
        assert(Response != None)
        return Response

    def RunFor(self, _SimulationDuration_ms:float):
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Simulation/RunFor?SimulationID={self.ID}&Runtime_ms={_SimulationDuration_ms}")
        assert(Response != None)
        return Response

    def RecordAll(self, _MaxRecordTime_ms:float):
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Simulation/RecordAll?SimulationID={self.ID}&MaxRecordTime_ms={_MaxRecordTime_ms}")
        assert(Response != None)
        return Response

    def GetRecording(self):
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Simulation/GetRecording?SimulationID={self.ID}")
        assert(Response != None)
        print("GetRecording Is Not Yet Fully Implemented (FYI)!")
        print(Response)
        return Response

    def GetStatus(self):
        Response = self.RequestHandler.MakeAuthenticatedQuery(f"/NES/Simulation/GetStatus?SimulationID={self.ID}")
        assert(Response != None)
        return Response
