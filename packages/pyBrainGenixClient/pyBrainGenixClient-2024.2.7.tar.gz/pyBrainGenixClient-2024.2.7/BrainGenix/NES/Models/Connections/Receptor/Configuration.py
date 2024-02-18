# BrainGenix-NES
# AGPLv3


class Configuration():

    def __init__(self):
        
        # Create Attributes
        self.Name:str = None
        self.SourceCompartment = None
        self.DestinationCompartment = None
        self.Conductance_nS:float = None
        self.TimeConstantRise_ms:float = None
        self.TimeConstantDecay_ms:float = None
        self.ReceptorLocation_um:list = None
    
