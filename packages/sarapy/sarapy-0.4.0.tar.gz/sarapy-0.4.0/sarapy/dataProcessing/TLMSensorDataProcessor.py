###Documentación en https://github.com/lucasbaldezzari/sarapy/blob/main/docs/Docs.md

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class TLMSensorDataProcessor(BaseEstimator, TransformerMixin):
    """- Autor: BALDEZZARI Lucas
    
    Metadata utilizada: Versión 9
    """
    
    def __init__(self, *args, **kwargs):
        """Constructor de la clase MetadataManager"""

        ### Creamos constantes que sirven para buscar los datos en el string de telemetría
        ### Cada constante es una tupla con la posición del bit menos significativo y la posición del bit más significativo
        self.__RFflag_pos = (0,0) #RF(1bit)
        self.__GNSSflag_pos = (1,1) #GNSS(1bit)
        self.__RFIDflag_pos = (2,2) #RFID(1bit)
        self.__FLASHflag_pos = (3,3) #FLASH(1bit)
        self.__RTCSflag_pos = (4,4) #RTCS(1bit)
        self.__MODEflag_pos = (5,5) #MODE(1bit)
        self.__NBAT_pos = (6,7) #NBAT(2bits)
        self.__TIMEAC_pos = (8,14) #TIMEAC(8bits)
        self.__ESTACflag_pos = (15,15) #ESTAC(1bit)
        self.__DSTRPT_pos = (16,19) #DSTR PT(4bits)
        self.__INESTPTflag_pos = (20,20) #INEST PT(1bit) Inestabilidad de plantín
        self.__OFFSPT_pos = (21,22) #OFFS PT(2bits)
        self.__DSTRFT_pos = (24,27) #DSTR FT(4bits)
        self.__INESTFTflag_pos = (28,28) #INEST FT(1bit)
        self.__OFFSFT_pos = (29,30) #OFFS FT(2bits)
        self.__PMSTFlag = (31,31) #PMST(1bit)
        self.__GYROX_pos = (32,34) #GYRO_X(3bits)
        self.__GYROY_pos = (35,37) #GYRO_Y(3bits)
        self.__GYROZf_pos = (38,39) #GYRO_Z(2bits)
        self.__ACELX_pos = (40,41) #ACEL_X(2bits)
        self.__ACELY_pos = (42,43) #ACEL_Y(2bits)
        self.__ACELZ_pos = (44,45) #ACEL_Z(2bits)
        self.__ESTMOflag_pos = (46,46) #EST MO(1bit)
        self.__ESTORflag_pos = (47,47) #EST OR(1bit)
        self.__SBAT_pos = (48,49) #SBAT(2bits) salud de la batería
        self.__VBAT_pos = (50,52) #VBAT(3bits) voltaje de la batería
        self.__CBAT_pos = (53,54) #CBAT(2bits) consumo de la batería
        self.__ESTBMSflag_pos = (55,55) #EST BMS(1bit)
        self.__FIX_pos = (56,58) #FIX(3bits)
        self.__SIV_pos = (59,63) #SIV(5bits)
        
        ##creamos un diccionario para saber la posición de cada dato dentro del array devuelto por transform()
        self._dataPositions = {
            "RFFlag": 0, "GNSSFlag": 1, "RFIDFlag": 2, "FLASHFlag": 3, "RTCSFlag": 4,
            "MODEFlag": 5, "NBAT": 6, "TIMEAC": 7, "ESTAC": 8, "DSTRPT": 9,
            "INESTPT": 10, "OFFSPT": 11, "DSTRFT": 12, "INESTFT": 13, "OFFSFT": 14,
            "PMSTFlag": 15, "GYROX": 16, "GYROY": 17, "GYROZ": 18, "ACELX": 19, "ACELY": 20,
            "ACELZ": 21, "ESTMOFlag": 22, "ESTORFlag": 23, "SBAT": 24, "VBAT": 25, "CBAT": 26,
            "ESTBMSFlag": 27, "FIX": 28, "SIV": 29}
        
        # self.kilometers = kwargs.pop('kilometers', 0)
        self.is_fitted = False

    def fit(self, X, y=None):
        """Método para generar datos a partir de la metadata.
        
        Args:
         - X: Es un array con los datos provenientes (strings) de la base de datos histórica. La forma de X es (n,1) donde n es la cantidad de datos.
        """

        ##chequeamos si todos los strings de X tienen la misma longitud, sino arrojamos un assert
        assert all(len(x) == len(X[0]) for x in X), "Todos los strings de X deben tener la misma longitud"

        self._RFFlag = np.vectorize(self.getRFFlag)(X)
        self._GNSSFlag = np.vectorize(self.getGNSSFlag)(X)
        self._RFIDFlag = np.vectorize(self.getRFIDFlag)(X)
        self._FLASHFlag = np.vectorize(self.getFLASHFlag)(X)
        self._RTCSFlag = np.vectorize(self.getRTCSFlag)(X)
        self._MODEFlag = np.vectorize(self.getMODEFlag)(X)
        self._NBAT = np.vectorize(self.getNBAT)(X)
        self._TIMEAC = np.vectorize(self.getTIMEAC)(X)
        self._ESTAC = np.vectorize(self.getESTAC)(X)
        self._DSTRPT = np.vectorize(self.getDSTRPT)(X)
        self._INESTPT = np.vectorize(self.getINESTPTFlag)(X)
        self._OFFSPT = np.vectorize(self.getOFFSPT)(X)
        self._DSTRFT = np.vectorize(self.getDSTRFT)(X)
        self._INESTFT = np.vectorize(self.getINESTFTFlag)(X)
        self._OFFSFT = np.vectorize(self.getOFFSFT)(X)
        self._PMSTFlag = np.vectorize(self.getPMSTFlag)(X)
        self._GYROX = np.vectorize(self.getGYROX)(X)
        self._GYROY = np.vectorize(self.getGYROY)(X)
        self._GYROZ = np.vectorize(self.getGYROZ)(X)
        self._ACELX = np.vectorize(self.getACELX)(X)
        self._ACELY = np.vectorize(self.getACELY)(X)
        self._ACELZ = np.vectorize(self.getACELZ)(X)
        self._ESTMOFlag = np.vectorize(self.getESTMOFlag)(X)
        self._ESTORFlag = np.vectorize(self.getESTORFlag)(X)
        self._SBAT = np.vectorize(self.getSBAT)(X)
        self._VBAT = np.vectorize(self.getVBAT)(X)
        self._CBAT = np.vectorize(self.getCBAT)(X)
        self._ESTBMSFlag = np.vectorize(self.getESTBMSFlag)(X)
        self._FIX = np.vectorize(self.getFIX)(X)
        self._SIV = np.vectorize(self.getSIV)(X)

        self.is_fitted = True


    def transform(self, X, y=None):
        """Transforma los datos de entrada en un array de numpy.

        Args:
         - X: Es un array con los datos provenientes (strings) de la base de datos histórica. La forma de X es (n,1) donde n es la cantidad de datos.
        """
        
        ##chequeamos si se ha llamado a fit(). Sino, se arroja un error
        if not self.is_fitted:
            raise ValueError("MetadataManager no ha sido fitteado. Llame a fit() previamente.")
        
        return np.array([   self._RFFlag,
                            self._GNSSFlag,
                            self._RFIDFlag,
                            self._FLASHFlag,
                            self._RTCSFlag,
                            self._MODEFlag,
                            self._NBAT,
                            self._TIMEAC,
                            self._ESTAC,
                            self._DSTRPT,
                            self._INESTPT,
                            self._OFFSPT,
                            self._DSTRFT,
                            self._INESTFT,
                            self._OFFSFT,
                            self._PMSTFlag,
                            self._GYROX,
                            self._GYROY,
                            self._GYROZ,
                            self._ACELX,
                            self._ACELY,
                            self._ACELZ,
                            self._ESTMOFlag,
                            self._ESTORFlag,
                            self._SBAT,
                            self._VBAT,
                            self._CBAT,
                            self._ESTBMSFlag,
                            self._FIX,
                            self._SIV]).T

    def fit_transform(self, X, y=None):
        """Combinamos fit() y transform() en un solo método.
        
        Args:
         - X: Es un array con los datos provenientes (strings) de la base de datos histórica. La forma de X es (n,1) donde n es la cantidad de datos.
        """
        self.fit(X)
        return self.transform(X)

    def getRFFlag(self, metadata):
        """
        Devuelve el valor del flag RF.

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
            int
                Valor del flag RF.
        """

        return np.uint8(int(metadata[self.__RFflag_pos[0]:self.__RFflag_pos[1]+1],2))
    
    def getGNSSFlag(self, metadata):
        """
        Devuelve el valor del flag RF.

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
            int
                Valor del flag GNSS.
        """

        return np.uint8(int(metadata[self.__GNSSflag_pos[0]:self.__GNSSflag_pos[1]+1],2))
    
    def getRFIDFlag(self, metadata):
        """
        Devuelve el valor del flag RFID.

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
            int
                Valor del flag RFID.
        """

        return np.uint8(int(metadata[self.__RFIDflag_pos[0]:self.__RFIDflag_pos[1]+1],2))
    
    def getFLASHFlag(self, metadata):
        """
        Devuelve el valor del flag FLASH.

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
            int
                Valor del flag FLASH.
        """

        return np.uint8(int(metadata[self.__FLASHflag_pos[0]:self.__FLASHflag_pos[1]+1],2))
    
    def getRTCSFlag(self, metadata):
        """
        Devuelve el valor del flag RTCS.

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
            int
                Valor del flag RTCS.
        """

        return np.uint8(int(metadata[self.__RTCSflag_pos[0]:self.__RTCSflag_pos[1]+1],2))
    
    def getMODEFlag(self, metadata):
        """
        Devuelve el valor del flag MODE.

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------

            int
                Valor del flag MODE.
        """

        return np.uint8(int(metadata[self.__MODEflag_pos[0]:self.__MODEflag_pos[1]+1],2))
    
    def getNBAT(self, metadata):
        """
        Devuelve el valor del flag NBAT.

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
            int
                Valor del flag NBAT.
        """

        return np.uint8(int(metadata[self.__NBAT_pos[0]:self.__NBAT_pos[1]+1],2))

    def getTIMEAC(self, metadata):
        """
        Devuelve el tiempo de accionamiento en segundos

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
            float
                Tiempo de accionamiento en segundos.
        """

        return np.float16(int(metadata[self.__TIMEAC_pos[0]:self.__TIMEAC_pos[1]+1],2)*0.1)
    
    def getESTAC(self, metadata):
        """
        Devuelve el valor del flag de ANOMALÍA OPERATIVA

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
            int
                Valor del flag de ANOMALÍA OPERATIVA.
        """

        return np.uint8(int(metadata[self.__ESTACflag_pos[0]:self.__ESTACflag_pos[1]+1],2))
    
    def getDSTRPT(self, metadata):
        """
        Devuelve el nivel de distorsión para plantín

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
            int:
                Valor de distorsión para plantín.
        """

        return np.uint8(int(metadata[self.__DSTRPT_pos[0]:self.__DSTRPT_pos[1]+1],2))

    def getINESTPTFlag(self,metadata):
            """
            Devuelve el valor del flag de INESTABILIDAD PARA PLANTÍN

            Parametros
            ----------
                metadata: str
                    String con los metadatos obtenidos de la base de datos.
            Return
            ------
                    int:
                        Valor del flag de INESTABILIDAD PARA PLANTÍN.
            """

            return np.uint8(int(metadata[self.__INESTPTflag_pos[0]:self.__INESTPTflag_pos[1]+1],2))

    def getOFFSPT(self,metadata):
        """
        Devuelve el valor del flag de OFFSET PARA PLANTÍN

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
                int:
                    Valor del flag de OFFSET PARA PLANTÍN.
        """

        return np.uint8(int(metadata[self.__OFFSPT_pos[0]:self.__OFFSPT_pos[1]+1],2))

    def getDSTRFT(self,metadata):
        """
        Devuelve el nivel de distorsión para fertilizante

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
            int:
                Valor de distorsión para fertilizante.
        """

        return np.uint8(int(metadata[self.__DSTRFT_pos[0]:self.__DSTRFT_pos[1]+1],2))  
    
    def getINESTFTFlag(self,metadata):
        """
        Devuelve el valor del flag de INESTABILIDAD PARA FERTILIZANTE

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
                int:
                    Valor del flag de INESTABILIDAD PARA FERTILIZANTE.
        """

        return np.uint8(int(metadata[self.__INESTFTflag_pos[0]:self.__INESTFTflag_pos[1]+1],2))
    
    def getOFFSFT(self,metadata):
        """
        Devuelve el valor del flag de OFFSET PARA FERTILIZANTE

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
                int:
                    Valor del flag de OFFSET PARA FERTILIZANTE.
        """

        return np.uint8(int(metadata[self.__OFFSFT_pos[0]:self.__OFFSFT_pos[1]+1],2))

    def getPMSTFlag(self,metadata):
        """
        Devuelve el valor del flag perdida de muestreo.

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
            int:
                Valor de flag perdida de muestreo.
        """

        return np.uint8(int(metadata[self.__PMSTFlag[0]:self.__PMSTFlag[1]+1],2))
    
    def getGYROX(self,metadata):
        """
        Devuelve el valor del giroscopio en X.

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
                int:
                    Valor del giroscopio en X.
        """

        return np.uint8(int(metadata[self.__GYROX_pos[0]:self.__GYROX_pos[1]+1],2))
    
    def getGYROY(self,metadata):
        """
        Devuelve el valor del giroscopio en Y.

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
                int:
                    Valor del giroscopio en Y.
        """

        return np.uint8(int(metadata[self.__GYROY_pos[0]:self.__GYROY_pos[1]+1],2))
    
    def getGYROZ(self,metadata):
        """
        Devuelve el valor del giroscopio en Z.

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
                int:
                    Valor del giroscopio en Z.
        """

        return np.uint8(int(metadata[self.__GYROZf_pos[0]:self.__GYROZf_pos[1]+1],2))
    
    def getACELX(self,metadata):
        """
        Devuelve el valor del acelerómetro en X.

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
                int:
                    Valor del acelerómetro en X.
        """

        return np.uint8(int(metadata[self.__ACELX_pos[0]:self.__ACELX_pos[1]+1],2))
    
    def getACELY(self,metadata):
        """
        Devuelve el valor del acelerómetro en Y.

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
                int:
                    Valor del acelerómetro en Y.
        """

        return np.uint8(int(metadata[self.__ACELY_pos[0]:self.__ACELY_pos[1]+1],2))
    
    def getACELZ(self,metadata):
        """
        Devuelve el valor del acelerómetro en Z.

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
                int:
                    Valor del acelerómetro en Z.
        """

        return np.uint8(int(metadata[self.__ACELZ_pos[0]:self.__ACELZ_pos[1]+1],2))
    
    def getESTMOFlag(self, metadata):
        """
        Devuelve el valor del flag de ESTMO

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
                int:
                    Valor del flag de ESTMO
        """

        return np.uint8(int(metadata[self.__ESTMOflag_pos[0]:self.__ESTMOflag_pos[1]+1],2))
    
    def getESTORFlag(self, metadata):
        """
        Devuelve el valor del flag de ESTOR

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
                int:
                    Valor del flag de ESTOR
        """

        return np.uint8(int(metadata[self.__ESTORflag_pos[0]:self.__ESTORflag_pos[1]+1],2))
    
    def getSBAT(self, metadata):
        """
        Devuelve el valor del estado de salud de la batería

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------
                int:
                    Valor del flag de SBAT
        """

        return np.uint8(int(metadata[self.__SBAT_pos[0]:self.__SBAT_pos[1]+1],2))
    
    def getVBAT(self, metadata):
        """
        Devuelve el valor del voltaje de la batería

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------

                int:
                    Valor del flag de VBAT
        """

        return np.uint8(int(metadata[self.__VBAT_pos[0]:self.__VBAT_pos[1]+1],2))
    
    def getCBAT(self, metadata):
        """
        Devuelve el valor del consumo de la batería

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------

                int:
                    Valor del flag de CBAT
        """

        return np.uint8(int(metadata[self.__CBAT_pos[0]:self.__CBAT_pos[1]+1],2))
    
    def getESTBMSFlag(self, metadata):
        """
        Devuelve el valor del flag de ESTBMS

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------

                int:
                    Valor del flag de ESTBMS
        """

        return np.uint8(int(metadata[self.__ESTBMSflag_pos[0]:self.__ESTBMSflag_pos[1]+1],2))
    
    def getFIX(self, metadata):
        """
        Devuelve el valor del flag de FIX

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------

                int:
                    Valor del flag de FIX
        """

        return np.uint8(int(metadata[self.__FIX_pos[0]:self.__FIX_pos[1]+1],2))
    
    def getSIV(self, metadata):
        """
        Devuelve el valor del flag de SIV

        Parametros
        ----------
            metadata: str
                String con los metadatos obtenidos de la base de datos.
        Return
        ------

                int:
                    Valor del flag de SIV
        """

        return np.uint8(int(metadata[self.__SIV_pos[0]:self.__SIV_pos[1]+1],2))
    
            
    @property
    def RFFlag(self):
        return self._RFFlag
    
    @property
    def GNSSFlag(self):
        return self._GNSSFlag
    
    @property
    def RFIDFlag(self):
        return self._RFIDFlag
    
    @property
    def FLASHFlag(self):
        return self._FLASHFlag
    
    @property
    def RTCSFlag(self):
        return self._RTCSFlag
    
    @property
    def MODEFlag(self):
        return self._MODEFlag
    
    @property
    def NBAT(self):
        return self._NBAT
    
    @property
    def TIMEAC(self):
        return self._TIMEAC
    
    @property
    def ESTAC(self):
        return self._ESTAC
    
    @property
    def DSTRPT(self):
        return self._DSTRPT
    
    @property
    def INESTPT(self):
        return self._INESTPT
    
    @property
    def OFFSPT(self):
        return self._OFFSPT
    
    @property
    def DSTRFT(self):
        return self._DSTRFT
    
    @property
    def INESTFT(self):
        return self._INESTFT
    
    @property
    def OFFSFT(self):
        return self._OFFSFT
    
    @property
    def PMSTFlag(self):
        return self._PMSTFlag
    
    @property
    def GYROX(self):
        return self._GYROX
    
    @property
    def GYROY(self):
        return self._GYROY
    
    @property
    def GYROZ(self):
        return self._GYROZ
    
    @property
    def ACELX(self):
        return self._ACELX
    
    @property
    def ACELY(self):
        return self._ACELY
    
    @property
    def ACELZ(self):
        return self._ACELZ
    
    @property
    def ESTMOFlag(self):
        return self._ESTMOFlag
    
    @property
    def ESTORFlag(self):
        return self._ESTORFlag
    
    @property
    def SBAT(self):
        return self._SBAT
    
    @property
    def VBAT(self):
        return self._VBAT
    
    @property
    def CBAT(self):
        return self._CBAT
    
    @property
    def ESTBMSFlag(self):
        return self._ESTBMSFlag
    
    @property
    def FIX(self):
        return self._FIX
    
    @property
    def SIV(self):
        return self._SIV
    
    @property
    def dataPositions(self):
        return self._dataPositions
    
if __name__ == "__main__":
    tlmsde = TLMSensorDataProcessor()

    sample = np.array(["1010001000010000110000001011000000000000000000001111011010001001",
              "1010001000010000110000001011000000000000000000001111011010001001"])

    tlmsde.getTIMEAC(sample[0])

    # tlmsde.fit(sample)
    data_transformed = tlmsde.fit_transform(sample)
    print(tlmsde.dataPositions)
    print(tlmsde.dataPositions["TIMEAC"])
    print(data_transformed)
    print(data_transformed.shape)
    
    print(tlmsde.SIV)