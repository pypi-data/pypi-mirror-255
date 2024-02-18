#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 14:10:28 2024

@author: javicolors
"""


from D3mel.utilities.utilities import Utilities

#%%

class D3mel(Utilities):
    def __init__(self, email, internet = True, msg = False):
        self.email = email
        if msg:
            print("Welcome to D3mel library")
        super().__init__(self.email, internet)
    
    def get_GAF(self, EVIDENCE_BLACKLIST = ['IEA']):
        return super().get_GAF(EVIDENCE_BLACKLIST = EVIDENCE_BLACKLIST)
    
    def get_GO(self):
        return super().get_GO()
    
    def get_order(self, valid_chr = ['2L', '2R', '3L', '3R', 'X']):
        return super().get_order(valid_chr = valid_chr)
    
    def get_ascendent(self, ListgoTerms, i_max = 7227, EXCLUDE=['GO:0005575', 'GO:0003674', 'GO:0008150']):
       return super().get_ascendent(ListgoTerms = ListgoTerms, i_max = i_max, EXCLUDE=EXCLUDE)   
   
    def get_descendent(self, ListgoTerms, i_max = 7227, EXCLUDE=['GO:0005575', 'GO:0003674', 'GO:0008150']):
          return super().get_descendent(ListgoTerms = ListgoTerms, i_max = i_max, EXCLUDE=EXCLUDE)  
   
    def get_extend(self, GOpos, i_max_desc = 7227, i_max_asc = 7227):
        return super().get_extend(GOpos, i_max_desc = i_max_desc, i_max_asc = i_max_asc)
    
    def get_go_count(self, diccionario_elementos):
        return super().contar_elementos_por_nodo(diccionario_elementos)
    
    def get_protein_complex(self):
        return super().get_protein_complex()
    
    def get_GOs_byCmp(self):
        return super().get_GOs_byCmp()
    
    def coding_genes (self):
        return super().coding_genes()
    
    def RNA_by_proyect(self,g,  proyects = None):
        return super().RNA_by_proyect(g, proyects)
    def get_proyects(self):
        return super().get_proyects()
    
    def close_app(self):
        super().close_app()