#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 13:08:19 2024

@author: javicolors
"""

import pandas as pd
import os


class UtilitiesProteinComplex():
    
    def __init__(self):

        current_script_path = os.path.realpath(__file__)
        subfolder_path = os.path.join(os.path.dirname(current_script_path), 'ExtraData')
        archivo_tsv = os.path.join(subfolder_path, '7227.tsv')
        
        self.prot_cmp = pd.read_csv(archivo_tsv, sep = '\t')
       
    def get_protein_complex(self):
        return self.prot_cmp
    
    def get_GOs_byCmp(self):
        
        GOs_byCmp = self.prot_cmp['Go Annotations'].apply(lambda x: [s[:10] for s in x.split('|')])
        
        return dict(zip(self.prot_cmp['#Complex ac'], GOs_byCmp))
        