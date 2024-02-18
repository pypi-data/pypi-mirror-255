# SARAPY

Library for processing SARAPICO project metadata of _AMG_.

#### Version 0.4.0 (working)

- Se implementa _OpsProcessor_.
- Se implementa _PlanntinClassifier_.
- Se corrige salida de _transform()_ y _fit_transform()_ de GeoProcessor.
- Se mueve PlantinFMCreator a mlProcessors
- Se cambia nombre de TLMSensorDataCreator a TLMSensorDataProcessor

#### Version 0.3.10

- Se corrige línea en DistancesImputer.

#### Version 0.3.9

- Se corrige nombre de argumento en el constructor de PlantinFMCreator

#### Version 0.3.8

- Se agregan condiciones para mejorar la imputación de distancias en _DistancesImputer_.

#### Version 0.3.7

- Se implementa la imputación de distancias con _DistancesImputer_ dentro de PlantinFMCreator.
- Se agregan argumentos al constructor de _PlantinFMCreator_ necesarios para poder imputar con _DistancesImputer_.
- Se agrega argumento dist*mismo_lugar en *DistancesImputer\* para usar dicho valor en las imputaciones que correspondan a operaciones en el mismo lugar.

#### Version 0.3.6

- Se agregan argumentos al constructor de _DistancesImputer_ para que Transform y fit_transform puedan entregar un array de shape (n,1) o bien de (n,6) eligiendo la columna a imputar.

#### Version 0.3.5

- Se implementa clase _DistancesImputer_.

#### Version 0.3.4

- Se actializa _dataPositions_ de PlantinFMCreator.

#### Version 0.3.3

- Se cambia el nombre de la clase FMCreator a PlantinFMCreator. Se modifica la matriz transformada quitando el dato de distorsión de Fertilizante.

#### Version 0.3.2

- Se agrega property en FMCreator para acceder a _dataPosition_. Se cambia la forma de los diccionarios de _dataPosition_ de FMCreator, TimeSeriesProcesor y TLMSensorDataExtractor. Además, ahora este atributo se crea en init().
- Se corrige bug por división por cero en el cálculo de _ratio_dCdP_ de TimeSeriesProcessor.

#### Version 0.3.1

- Se corrige forma de acceder a los datos de X en FMCreator.fit().

#### Version 0.3.0

- Se implementa clase FMCreator.
- Se quita método TLMSensorDataExtractor.getMetadataRevisionNumber().
- Se agrega cálculo de ratio_dCdP en TimeSeriesProcessor
- Se cambia nombre de clase _GeoAnalyzer_ por _GeoProcessor_
- Se agrega atritubo dataPositions en _TLMSensorDataExtractor_ para poder saber qué representa cada columna dentro del array devuelto por tranform.
- Se agrega dataPositions a TimeSeriesProcessor
