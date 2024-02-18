# -*- coding: utf-8 -*-

from itertools import chain

#%%

class UtilitiesGOs():
    
    def __init__(self, fbd):
        self.fbd = fbd
        self.GO = self.fbd.Ontology_Terms.GO()
        
    def get_GO(self):
        return self.GO

    
    def get_GAF(self, EVIDENCE_BLACKLIST = ['IEA']):
        gaf = self.fbd.GOAnn.GAF()
        if gaf is not None:
            gaf.dropna(subset=['DB Object Symbol'], inplace=True) 
            gaf = gaf[~gaf['Evidence'].isin(EVIDENCE_BLACKLIST)]
            gaf.drop_duplicates(subset=['DB Object Symbol', 'GO ID'], inplace=True)
            gaf.reset_index(drop=True, inplace=True)
            
            gaf = gaf.loc[:, ['DB Object ID', 'DB Object Symbol', 'GO ID', "DB Object Type"]]
            
            return gaf
        
    def vald_goList(self, ListgoTerms):
        if isinstance(ListgoTerms, list):
            ListgoTerms = list(set(ListgoTerms) & set(self.GO.nodes))
            if len(ListgoTerms) == 0:
                print("GO terms not found")
                return None
            else:
                return ListgoTerms
        else:
            print("The format of your gene list is incorrect. Try again with a list of strings.")
            return None
        
    
    def get_ascendent(self, ListgoTerms, i_max, EXCLUDE=['GO:0005575', 'GO:0003674', 'GO:0008150']):
        if not isinstance(i_max, int) or isinstance(i_max, bool):
            print("The requested number of nodes is invalid. Please enter an integer instead")
            return None
        
        i = 0
        
        def obtener_sucesore(goTerm, i = i):
            sucesor_directo = list(self.GO.successors(goTerm))
            sucesores_totales.extend(sucesor_directo)
            for sucesor in sucesor_directo:
                tipo_relacion = list(self.GO[goTerm][sucesor])[0]
                if tipo_relacion != 'is_not' and i < i_max:
                    obtener_sucesore(sucesor, i = i + 1)
                    
        ListgoTerms = self.vald_goList(ListgoTerms)
        if ListgoTerms is not None:
            dict_goTerms = {}
            for goTerm in ListgoTerms:            
                sucesores_totales = []
                obtener_sucesore(goTerm)
                sucesores_totales = sorted(set(sucesores_totales))
                for termino in EXCLUDE:
                    while termino in sucesores_totales:
                        sucesores_totales.remove(termino)
                dict_goTerms[goTerm] = sucesores_totales
    
            return dict_goTerms
        return None
        
    
    
    def get_descendent(self, ListgoTerms, i_max,  EXCLUDE=['GO:0005575', 'GO:0003674', 'GO:0008150']):
            if not isinstance(i_max, int) or isinstance(i_max, bool):
                print("The requested number of nodes is invalid. Please enter an integer instead")
                return None
            i = 0
            
            def obtener_predecesores(goTerm, i=i):
                predecesores_directo = list(self.GO.predecessors(goTerm))
                predecesores_totales.extend(predecesores_directo)
                for predecesor in predecesores_directo:
                    tipo_relacion = list(self.GO[predecesor][goTerm])[0]
                    if tipo_relacion != 'is_not' and i < i_max:
                        obtener_predecesores(predecesor, i=i + 1)
                
            ListgoTerms = self.vald_goList(ListgoTerms)
            if ListgoTerms is not None:
                dict_goTerms = {}
                for goTerm in ListgoTerms:
                    predecesores_totales = []
                    obtener_predecesores(goTerm)
                    
                    predecesores_totales = sorted(set(predecesores_totales))
                    for termino in EXCLUDE:
                        while termino in predecesores_totales:
                            predecesores_totales.remove(termino)
                    
                    if len(predecesores_totales) > 0:
                        dict_goTerms[goTerm] = predecesores_totales
                
                return dict_goTerms
            return None
            
    def get_extend(self, GOpos, i_max_asc, i_max_desc):
        hijos_dict = self.get_descendent(GOpos, i_max_desc)
        padres_dict = self.get_ascendent(GOpos, i_max=i_max_asc)
        
        ancestros = []
        descendencia = []
        
        if len(hijos_dict) > 0:
            descendencia = list(chain.from_iterable(hijos_dict.values()))
  
        if len(padres_dict) > 0:
            ancestros = list(chain.from_iterable(padres_dict.values()))
        
        return list(set(ancestros + descendencia))
        
    def contar_elementos_por_nodo(self, diccionario_elementos):
        contador_elementos = {}
    
        def contar_elementos_iterativo(nodo):
            nodos_por_visitar = [nodo]
            elementos_contados = set()
            while nodos_por_visitar:
                actual = nodos_por_visitar.pop()
                elementos_contados.update(diccionario_elementos.get(actual, []))
                nodos_por_visitar.extend(hijo for hijo in self.GO.predecessors(actual))
            return len(elementos_contados)
    
        for nodo in self.GO.nodes():
            contador_elementos[nodo] = contar_elementos_iterativo(nodo)
    
        return contador_elementos
    


