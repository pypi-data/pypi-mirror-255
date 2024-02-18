import pandas as pd
from scipy import stats
import math


class MultiplesArchivos(object):

    dfList = []  # Declara una lista vacía
    dfList_User = []
    Ener = pd.DataFrame()
    df_Season = pd.DataFrame()
    df_Season_Stadistic = pd.DataFrame()
    noFile = int
    progress = int

    def __init__(self, indir, temp, t_day):
        self.temp = temp
        self.indir = indir
        self.t_day = t_day

    def user(self, df):
        """
        Método para leer atributos de los usuraios y el ID
        """
        global Terminal
        Terminal = df['Unnamed: 1'][1]  # obtien valores de la columna 'Unnamed: 1' inice 1
        # Domicilio = df['Unnamed: 1'][2]
        # Servicio = df['Unnamed: 1'][3]
        # Periodo = df['Unnamed: 8'][2]
        # datos = pd.DataFrame({'Terminal': [Terminal],'Domicilio':[Domicilio],'Servicio':[Servicio]})
        return Terminal

    def cleanExcel(self, df):
        """
        Metodo que permite realizar la limpieza de la hoja de datos (panilla excel)
        """
        # axis es 0 para fila, 1 para columna
        df = df.drop(
            labels=[
                'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 5', 'Unnamed: 6',
                'Unnamed: 7', 'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10', 'Unnamed: 12'
            ],
            axis=1
            )  # elimana la columna 'Unnamed: 1' ......
        df = df.drop([0, 1, 2, 3, 4, 5, 6, 7])  # Eliminar las filas.
        df = df.reset_index(drop=True)  # Reiniciar al indexado.
        # Cambiar los nombres de las columnas
        df = df.rename(index=str, columns={
            "Reporte de Registros Periódicos": "Fecha hora",
            # "Unnamed: 2": "Tensión(V)",
            # "Unnamed: 3": "Corriente",
            "Unnamed: 4": "E_Activa(Wh)",
            # "Unnamed: 5": "E_Aparente(VARh)",
            # "Unnamed: 7": "E_Reactiva(VAh)",
            # "Unnamed: 9": "Frec(Hz)",
            # "Unnamed: 10": "FP",
            "Unnamed: 11": "D.Max(W)"}
        )
        df = df.dropna(how='any')
        return df

    def proces_DF(self, df):
        """
        Códigos para obtener por separdos en diferentes columnas del dataframe /n horas menses y días de la semana /n
        """
        global Min
        global Horas
        global Dias_S
        global Dia_M
        global Mes
        global year

        df['Fecha hora'] = pd.to_datetime(df['Fecha hora'], errors='coerce')
        Horas = df['Fecha hora'].dt.hour        # con la propiedad .dt podemos acceder a los difrentes intervalos de fecha y hora.
        Dias_S = df['Fecha hora'].dt.weekday    # Obtener los días de la semana, cero para lunes, y 6 para domingo.
        Dia_M = df['Fecha hora'].dt.day
        Mes = df['Fecha hora'].dt.month         # obtener los meses de la columna fecha.
        Min = df['Fecha hora'].dt.minute        # obtener los minutos.
        year = df['Fecha hora'].dt.year
        pot_media = df['E_Activa(Wh)'] / 0.25   # Se calcula la pontencia activa instantánea\n",

        # Añadimos la columna al dataframe de las potencias unas vez calculadas.
        user_data_temp = df.copy()
        user_data_temp['Pot_media(W)'] = pot_media  # Añadimos la columna Potencia activa
        user_data_temp['Tipo de Día'] = Dias_S      # Añadimos la columna días de la semana.
        user_data_temp['Dia del Mes'] = Dia_M
        user_data_temp['Hora del Día'] = Horas
        user_data_temp['Mes'] = Mes
        user_data_temp['Año'] = year
        df = user_data_temp
        return df

    def fil_type_day(self, df):
        """
        Metodo que filtra por tipo de día de la semana seleccionado
        """
        if self.t_day == 'habil':
            df_type_day = df[(df['Tipo de Día'] <= 4)]  # Seleccionamos los días hábileses un dataframe donde solo se incluyen los días Hábiles.
        elif self.t_day == 'no habil':
            df_type_day = df[(df['Tipo de Día'] >= 5)]  # selección de los días no hábiles.
        return df_type_day

    def fil_season(self, df):
        """
        Metodo que filtra el dataframe que recibe por la estación del año selecionada
        """
        # global df_season
        verano = [12, 1, 2]
        invierno = [6, 7, 8]
        intermedio = [3, 4, 5, 9, 10, 11]
        if self.temp == 'verano':
            df_type_season = df[df['Mes'].isin(verano)]
        elif self.temp == 'invierno':
            df_type_season = df[df['Mes'].isin(invierno)]
        elif self.temp == 'otoño y primavera':
            df_type_season = df[df['Mes'].isin(intermedio)]
        return df_type_season

    def maxDeman(self, df, user):
        """
        Método que recibe el dataframe y la lista del usuario para devolver un dataframe compuesta por energías y
        potencias indexadas por el codigo del usuario
        """
        '''        
        Df_Temp = pd.DataFrame()
        Df_Temp['D.Max(W)'] = df['D.Max(W)'].max()
        Df_Temp['Usuario'] = user

        user_data_temp = Df_Temp.copy()
        user_data_temp['Usuario'] = user  # se añade la columna de los codigos a la el dataframe de los datos
        result = user_data_temp.set_index('Usuario')  # se coloca codigos de los usuarios como indices de la tabla promedio
        '''
        result = pd.DataFrame([[df['D.Max(W)'].max(), user]], columns=['D.Max(W)', 'Usuario'])
        return result

    def ener_hora_acum(self, df):
        """
        Este método devuelve un DataFrame que contiene columnas con los valores de las energías horarias acumuladas
        durante las 24 horas las filas son las mediciones totales agrupadas cada 15 minutos esto representa la cantidad
        de dias, siendo este acumulado perteneciente al número de día en que se obtuvo medicion.
        """
        Listdf_clean = pd.DataFrame()  # datasets frame vacío.
        for h in range(0, 24):  # h va a ieterar 24 veces representando las 24 horas del día.
            df_clean = pd.DataFrame()
            k = [h]
            Hora_Dia = df[df['Hora del Día'].isin(k)]  # filtramos por hora del dia
            Hora_Dia_Acumu = Hora_Dia.groupby(
                [year, Mes, Dia_M, Horas])['E_Activa(Wh)'].sum()  # Sumar las mediciones de los periodos de 15 min entre horas
            Hora_Dia_Acum_ = pd.DataFrame(pd.DataFrame(Hora_Dia_Acumu))  # convertir a datasets frame a dataframe
            Hora_Dia_Acum_ = Hora_Dia_Acum_.reset_index(drop=True)  # se elimina niveles de indices

            vector = Hora_Dia_Acum_['E_Activa(Wh)']
            name_colum = '$%d$' % h  # nombre de la columna
            df_clean = df_clean.copy()

            df_clean[name_colum] = vector  # coloca el vector hora h en la columna h de df_celan
            Listdf_clean = pd.concat([Listdf_clean, df_clean], axis=1)  # adjuntos el nuevo vector de las horas a al dataframe
            Listdf_clean = Listdf_clean.dropna(how='any')  # Elimino datos null de df
            Listdf_clean.columns = range(Listdf_clean.shape[1])  # cambiamos el tipo de datos de los nombres de las columnas para dierecccionar luego

        return Listdf_clean

    def prom_clean(self, df, User):
        """"
        Este método elimina los datos atípicos y entrega un vector de la energía promedio horario indexado por ID de usuario
        """
        z_critical = stats.norm.ppf(q=0.999)  # Get the z-critical value* determina el
        data_graf = []
        vector_Prom = []
        num = len(df.columns)
        dfData_graf = pd.DataFrame()
        if df.empty:
            print('here')

        for i in range(num):
            data = df[i]
            sample_size = len(data)     # determinar la longitud de los datos
            if sample_size != 0:
                sample_mean = data.mean()   # determina la media.
                pop_stdev = data.std()      # Get the population standard deviation
                margin_of_error = z_critical * (pop_stdev / math.sqrt(sample_size))  # margen de error
                confidence_interval = (sample_mean - margin_of_error, sample_mean + margin_of_error)
                interv_min = sample_mean - margin_of_error
                interv_max = sample_mean + margin_of_error
                data = data[(data >= interv_min)]  # filtrar obteniendo los valores de mayores al min
                data = data[(data <= interv_max)]  # filtrar obteniendo los valores de menores al min
            data_graf.append(data)
            # P = pd.DataFrame(datasets)
            # dfData_graf =  dfData_graf.join(P)
            Promedio = data_graf[i].mean()
            vector_Prom.append(Promedio)

        # Normalizar datos
        vector_Prom = pd.DataFrame(vector_Prom)
        # scaler = MinMaxScaler(feature_range=(0,1))
        # vector_Prom = scaler.fit_transform(vector_Prom)
        # vector_Prom = normalice(vector_Prom)
        vector_Prom_T = pd.DataFrame(vector_Prom).T

        vector = vector_Prom_T.copy()
        vector['Usuario'] = User  # se añade la columna de los codigos a la el dataframe de los datos
        # print(user_data_temp)
        vector = vector.set_index('Usuario')  # se coloca codigos de los usuarios como indices de la tabla promedio
        # vector.fillna(method='ffill', axis=1, inplace = True) # Se rellenan los campos nulos que pudieran existir
        return vector

    def stadistic(self, df1, df2):
        df_temp = pd.DataFrame()
        # media = df1.median(axis=1)
        desv_estandar = df1.std(axis=1)
        # kurtosis  = df1.kurtosis(axis=1)  # compara cantidad de datos cerca de la media con lo que esat lejos
        # asimetria  = df1.skew(axis=1)     # calculo de asimetría de los datos sobre la media
        Ener_Pro_Dia = df1.sum(axis=1)
        Deman_Max = df2['D.Max(W)'].max()

        # df_temp['Media'] = media
        df_temp['dev_Estandar'] = desv_estandar
        # df_temp['kurtosis'] = kurtosis
        df_temp['Ener_Pro_Dia'] = Ener_Pro_Dia
        # df_temp['Asimetría'] = asimetria
        df_temp['Dema_Pico'] = Deman_Max
        return df_temp
