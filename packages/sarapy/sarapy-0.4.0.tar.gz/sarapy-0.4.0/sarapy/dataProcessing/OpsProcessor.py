###Documentación en https://github.com/lucasbaldezzari/sarapy/blob/main/docs/Docs.md

import numpy as np
from sarapy.mlProcessors import PlantinFMCreator
from sarapy.mlProcessors import PlantinClassifier
import warnings

class OpsProcessor():
    """Clase para procesar las operaciones de los operarios. La información se toma de la base de datos
    hostórica y se procesa para obtener un array con las operaciones clasificadas para cada operario.
    
    La clase recibe una muestra desde la base de datos histórica y la procesa para obtener las
    operaciones clasificadas para cada operario. Se clasifican las operaciones desde el punto de vista
    del plantín y del fertilizante. La clasificación del tipo de operación respecto de plantín se hace
    con el pipeline para plantín, idem para el fertilizante.
    """
    
    def __init__(self, distanciaMedia = 1.8, umbral_precision = 0.3, dist_mismo_lugar = 0.0,
                 max_dist = 100, umbral_ratio_dCdP = 0.5, deltaO_medio = 4,
                 keepDimsPFMC = False, columnToImputePFMC = 0):
        """Constructor de la clase OpsProcessor.
        
        Args:
            - distanciaMedia: Distancia media entre operaciones.
        """

        self._plantinFMCreator = PlantinFMCreator(distanciaMedia = distanciaMedia, umbral_precision = umbral_precision,
                                                  dist_mismo_lugar = dist_mismo_lugar, max_dist = max_dist,
                                                  umbral_ratio_dCdP = umbral_ratio_dCdP, deltaO_medio = deltaO_medio)
        
        self._plantin_classifier = PlantinClassifier()
        # self._fertilizerFMCreator = FertilizerFMCreator() ## PARA IMPLEMENTAR
        
        self._operationsDict = {} ##diccionario de operarios con sus operaciones
        self._classifiedOperations = np.array([]) ##array con las operaciones clasificadas
        self._last_row_db = 0 ##indicador de la última fila de los datos extraidos de la base de datos histórica
        
    def processOperations(self, newSample):
        """Método para procesar las operaciones de los operarios.

        Se toma una nueva muestra y se procesa la información para clasificar las operaciones considerando el
        plantín y por otro lado el fertilizante.
        Se retorna un array con las clasificaciones concatenadas, manteniendo el orden de las operaciones por operario.
        
        Args:
            - newSample: lista con los datos (numpy.array de strings) de una muestra de operaciones.
            La forma de cada dato dentro de la lista newSample es (n,6). Las columnas de newSample son,
            
                - 0: op_number
                - 1: id_oprr
                - 2: tlm_spbb
                - 3: date_oprc
                - 4: lat
                - 5: lon
                - 6: precision
        """
        
        ##chqueo que newSample no esté vacío
        if len(newSample) != 0:
            #Si tenemos nuevas operaciones, actualizamos el diccionario de operaciones
            self.updateOperationsDict(newSample) #actualizamos diccionario interno de la clase
            plantinClassifications = self.classifyForPlantin() #clasificamos las operaciones para plantín
            # ops_numbers = newSample[:,0]
            ops_numbers = self.getActualOperationsNumbers() #obtenemos los números de operaciones desde el diccionario de operaciones
            return plantinClassifications.round(2), ops_numbers
        
        else:
            self.resetAllNewSamplesValues()
            return None
        
    def updateOperationsDict(self, newSample):
        """Actualiza el diccionario de operaciones.
        
        Args:
            - newSample: lista con los datos (numpy.array de strings) de las operaciones.
            La forma de cada dato dentro de la lista newSample es (n,6). Las columnas de newSample son,
            
                - 0: op_number
                - 1: id_oprr
                - 2: tlm_spbb
                - 3: date_oprc
                - 4: lat
                - 5: lon
                - 6: precision
                
        Returns:
            - None
            NOTA: PENSAR SI SE DEVUELVE ALGO COMO UN TRUE O FALSE PARA SABER SI SE ACTUALIZÓ O NO EL DICCIONARIO
            DE MANERA CORRECTA O HUBO ALGÚN PROBLEMA Y ASÍ VER QUÉ HACER EN EL MAIN
        """
        
        id_oprrs_w_newOperations = np.unique(newSample[:,1]) ##identificadores de operarios con nuevas operaciones en la muestra
        
        ##chqueo si estos id_oprrs ya están en el diccionario, sino los agrego
        for id_oprr in id_oprrs_w_newOperations:
            if id_oprr not in self._operationsDict:
                #El diccionario contiene la siguiente información:
                #sample_ops: np.array con las columnas de tlm_spbb, date_oprc, lat, lon, precision
                #last_oprc: np.array de la última operación con las columnas de tlm_spbb, date_oprc, lat, lon, precision
                #first_day_op_classified: booleano para saber si es la primera operación del día fue clasificada
                self._operationsDict[id_oprr] = {"sample_ops": None,
                                                 "last_oprc": None, 
                                                 "first_day_op_classified": False,
                                                 "new_sample": False,
                                                 "ops_numbers": None} #inicio del diccionario anidado para el nuevo operario
                
        ##actualizo el diccionario con las operaciones nuevas para aquellos operarios que correspondan
        for id_oprr in id_oprrs_w_newOperations:
            sample_ops = newSample[newSample[:,1] == id_oprr][:,2:] #me quedo con las columnas de tlm_spbb, date_oprc, lat, lon, precision
            ops_numbers = newSample[newSample[:,1] == id_oprr][:,0]
            ##actualizo el diccionario
            self._operationsDict[id_oprr]["sample_ops"] = sample_ops
            self._operationsDict[id_oprr]["ops_numbers"] = ops_numbers
            ##chequeo si tenemos última operación, si es así, asignamos dicha operación en la primera fila de sample_ops
            last_op = self._operationsDict[id_oprr]["last_oprc"]
            ###si last_op es not None y last_op no está vacía, entonces concatenamos last_op con sample_ops
            if last_op is not None and last_op.size != 0:
                self._operationsDict[id_oprr]["sample_ops"] = np.vstack((last_op, sample_ops))
                
        self.updateNewSamplesValues(id_oprrs_w_newOperations) #actualizo el estado de 'new_sample' en el diccionario de operaciones
        self.updateLastOperations(id_oprrs_w_newOperations) #actualizo la última operación de una muestra de operaciones en el diccionario de operaciones

    def classifyForPlantin(self):
        """Método para clasificar las operaciones para plantín.
        Se recorre el diccionario de operaciones y se clasifican las operaciones para plantín.

        Returns:
            - plantinClassifications: np.array con las clasificaciones de las operaciones para plantín.
        """

        ##creamos/reiniciamos el array con las clasificaciones de las operaciones para plantín
        plantinClassifications = None
        
        ##me quedo con los id_oprrs que tengan _operationsDict[id_oprr]["new_sample"] iguales a True
        ops_with_new_sample = [id_oprr for id_oprr in self.operationsDict.keys() if self.operationsDict[id_oprr]["new_sample"]]

        for id_oprr in ops_with_new_sample:#self.operationsDict.keys():
            ##clasificamos las operaciones para plantín
            operations = self.operationsDict[id_oprr]["sample_ops"]
            classified_ops = self._plantin_classifier.classify(operations)
            
            ##chequeo si first_day_op_classified es True, si es así, no se considera la primera fila de las classified_ops
            if self.operationsDict[id_oprr]["first_day_op_classified"]:
                classified_ops = classified_ops[1:]
                
            plantinClassifications = np.vstack((plantinClassifications, classified_ops)) if plantinClassifications is not None else classified_ops
                
            self.operationsDict[id_oprr]["first_day_op_classified"] = True

        return plantinClassifications
            
    def updateLastOperations(self, id_oprrs_w_newOperations):
        """Método para actualizar la última operación de una muestra de operaciones en el diccionario de operaciones

        Args:
            - newSample: lista con los datos (numpy.array de strings) de las operaciones.
            La forma de cada dato dentro de la lista newSample es (n,6). Las columnas de newSample son,
            
                - 0: op_number
                - 1: id_oprr
                - 2: tlm_spbb
                - 3: date_oprc
                - 4: lat
                - 5: lon
                - 6: precision
        """
        
        for id_oprr in id_oprrs_w_newOperations:
            self._operationsDict[id_oprr]["last_oprc"] = self._operationsDict[id_oprr]["sample_ops"][-1]

    def updateOperationsNumbers(self, new_ops_numbers):
        """Método para actualizar los números de operaciones en el diccionario de operaciones.

        Args:
            - new_ops_numbers: array de la forma (n,2) con los números de operaciones en la primer columna y los id_oprrs en la segunda.
        """
        id_oprrs_w_newOperations = np.unique(new_ops_numbers[:,1]) ##identificadores de operarios con nuevas operaciones en la muestra
        opsNumbersList = np.array([]) ##array con los números de operaciones

        for id_oprr in id_oprrs_w_newOperations:
            opsNumbersList = np.append(opsNumbersList, self.operationsDict[id_oprr]["ops_numbers"].flatten())

        return opsNumbersList
    
    def updateNewSamplesValues(self, id_oprrs_w_newOperations):
        """Método para actualizar el estado de 'new_sample' del diccionario de operaciones.

        Args:
            - id_oprrs_w_newOperations: lista con los id_oprrs que tienen nuevas operaciones.
        """

        ##recorro el diccionario de operaciones y actualizo el estado de 'new_sample' a
        ##True para los id_oprrs que tienen nuevas operaciones y a False para los que no tienen nuevas operaciones
        for id_oprr in self.operationsDict.keys():
            if id_oprr in id_oprrs_w_newOperations:
                self._operationsDict[id_oprr]["new_sample"] = True
            else:
                self._operationsDict[id_oprr]["new_sample"] = False
    
    def resetAllNewSamplesValues(self):
        """Método para resetar todos los valores de new_sample en el diccionario de operaciones.
        """
        
        for id_oprr in self.operationsDict.keys():
            self._operationsDict[id_oprr]["new_sample"] = False

    def getActualOperationsNumbers(self):
        """Método para obtener los números de operaciones desde el diccionario de operaciones para aquellos operarios que
        tienen nuevas operaciones en la muestra."""

        opsNumbersList = np.array([])
        for id_oprr in self.operationsDict.keys():
            if self.operationsDict[id_oprr]["new_sample"]:
                opsNumbersList = np.append(opsNumbersList, self.operationsDict[id_oprr]["ops_numbers"].flatten())

        return opsNumbersList

    def cleanSamplesOperations(self):
        """Método para limpiar las operaciones de un operario en el diccionario de operaciones.

        Args:
            - newSample: lista con los datos (numpy.array de strings) de las operaciones.
            La forma de cada dato dentro de la lista newSample es (n,6). Las columnas de newSample son,
            
                - 0: op_number
                - 1: id_oprr
                - 2: tlm_spbb
                - 3: date_oprc
                - 4: lat
                - 5: lon
                - 6: precision
        """

        for id_oprr in self.operationsDict.keys():
            self._operationsDict[id_oprr]["sample_ops"] = None

    def updateFirstDayOp(self):
        """Método para actualizar el indicador de si es la primera operación del día para cada operario en el diccionario de operaciones.
        """

        for id_oprr in self.operationsDict.keys():
            self._operationsDict[id_oprr]["first_day_op_classified"] = False
    
    @property
    def operationsDict(self):
        return self._operationsDict
    
    
if __name__ == "__main__":
    #cargo archivo examples\volcado_17112023_NODE_processed.csv
    import pandas as pd
    import numpy as np
    import os
    path = os.path.join(os.getcwd(), "examples\\volcado_17112023_NODE_processed.csv")
    data_df = pd.read_csv(path, sep=";", )
    raw_data = data_df.to_numpy().astype(str)

    ##seed de numpy en 42
    np.random.seed(42)

    size = data_df[data_df["id_oprr"] == 1].shape[0]
    data_df.loc[data_df["id_oprr"] == 1, "id_dataBase"] = range(1,size+1)
    size = data_df[data_df["id_oprr"] == 2].shape[0]
    data_df.loc[data_df["id_oprr"] == 2, "id_dataBase"] = range(1,size+1)
    ##tomo raw_data y obtengo muestras de entre 7 a 15 filas una detrás de la otra. El valor de entre 7 y 15 es aleatorio.
    samples = []
    index = 0
    while True:
        random_value = np.random.randint(8, 15)
        if index + random_value < len(raw_data):
            samples.append(raw_data[index:index+random_value])
        else:
            break
        index += random_value
    
    from sarapy.dataProcessing import OpsProcessor
    op = OpsProcessor()

    op.operationsDict

    ##procesamos una muestra
    print(op.processOperations(samples[0]))
    print(op.processOperations(np.array([])))
    print(op.processOperations(samples[1]))
    # ##recorro los samsamples[0]ples y los proceso
    # for sample in print(op.operationsDict[":
    #     op.processOperations(sample)
    data_df.loc[data_df["id_oprr"] == 1].head(15)
