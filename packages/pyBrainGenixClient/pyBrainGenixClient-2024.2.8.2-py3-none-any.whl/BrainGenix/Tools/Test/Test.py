# BrainGenix-NES
# AGPLv3

import BrainGenix.NES as NES
import BrainGenix



def Test(_Host:str="localhost", _Port:int=8000, _UseHTTPS:bool=False, _Username:str="Admonishing", _Password:str="Instruction"):

    # Create Client Configuration For Local Simulation
    print(" -- Creating Client Configuration For Local Simulation")
    ClientCfg = NES.Client.Configuration()
    ClientCfg.Mode = NES.Client.Modes.Remote
    ClientCfg.Host = _Host
    ClientCfg.Port = _Port
    ClientCfg.UseHTTPS = _UseHTTPS
    ClientCfg.AuthenticationMethod = NES.Client.Authentication.Password
    ClientCfg.Username = _Username
    ClientCfg.Password = _Password

    # Create Client Instance
    print(" -- Creating Client Instance")
    ClientInstance = NES.Client.Client(ClientCfg)

    assert(ClientInstance.IsReady())

    
    # Create A New Simulation
    print(" -- Creating Simulation")
    SimulationCfg = NES.Simulation.Configuration()
    SimulationCfg.Name = "My First Simulation"
    MySim = ClientInstance.CreateSimulation(SimulationCfg)
    

    # Create Sphere
    print(" -- Creating Sphere")
    SphereCfg = NES.Shapes.Sphere.Configuration()
    SphereCfg.Name = "My Sphere"
    SphereCfg.Radius_um = 8.
    SphereCfg.Center_um = [10, 10, 10]
    MySphere = MySim.AddSphere(SphereCfg)

    # Create Compartments
    print(" -- Creating BS Compartment With Sphere")
    Cfg = NES.Models.Compartments.BS.Configuration()
    Cfg.Name = "My Compartment 1"
    Cfg.SpikeThreshold_mV = 0.0
    Cfg.DecayTime_ms = 0.0
    Cfg.MembranePotential_mV = 0.0
    Cfg.RestingPotential_mV = 0.0
    Cfg.AfterHyperpolarizationAmplitude_mV = 0.0
    Cfg.Shape = MySphere
    MySphereCompartment = MySim.AddBSCompartment(Cfg)


    # Setup VSDA Renderer
    print(" -- Setting Up VSDA EM Renderer")
    EMConfig = NES.VSDA.EM.Configuration()
    EMConfig.PixelResolution_nm = 0.2
    EMConfig.ImageWidth_px = 512
    EMConfig.ImageHeight_px = 512
    EMConfig.SliceThickness_nm = 100
    EMConfig.ScanRegionOverlap_percent = 0
    EMConfig.MicroscopeFOV_deg = 50
    EMConfig.NumPixelsPerVoxel_px = 3
    VSDAEMInstance = MySim.AddVSDAEM(EMConfig)

    print(" -- Setting Up VSDA EM Scan Region")
    VSDAEMInstance.DefineScanRegion([0,0,0], [20,20,20])
    
    print(" -- Queueing Render Operation")
    VSDAEMInstance.QueueRenderOperation()

    VSDAEMInstance.WaitForRender()
    VSDAEMInstance.SaveImageStack("BG-EMImages")
    
    print(" -- Reconstructing Image Stack")
    BrainGenix.Tools.StackStitcher.StackStitcher("BG-EMImages", "ReconstructedImages")
