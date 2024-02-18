#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .utilities_position_map import UtilitiesPositionMap
from .utilities_gos import UtilitiesGOs
from .utilities_protein_complex import UtilitiesProteinComplex
from .utilities_rnaseq import UtilitiesRNAseq
from FlyBaseDownloads.FBD import FBD

#%%

class Utilities(UtilitiesGOs, UtilitiesPositionMap, 
                UtilitiesProteinComplex, UtilitiesRNAseq):
    
    
    def __init__(self, email, internet = True):
        
        self.fbd = FBD(email, internet)
        
        UtilitiesProteinComplex.__init__(self)
        UtilitiesGOs.__init__(self, self.fbd)
        UtilitiesPositionMap.__init__(self, self.fbd)
        UtilitiesRNAseq.__init__(self, self.fbd)
        
        self.gaf = UtilitiesGOs.get_GAF(self)
    
    def close_app(self):
        if self.fbd is not None:
            self.fbd.close_app()

 
       
