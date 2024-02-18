from .cluster_stage import Conglomerados
from .load_files import MultiplesArchivos
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np  # libreria para arreglos
from matplotlib import cm
import pandas as pd  # Librería para para tratamiento de datos, (dataframe)
import glob
import os


class Mult_escenarios:

    dfList = []  # Declara una lista vacía
    dfList_User = []
    Ener = pd.DataFrame()
    df_Season = pd.DataFrame()
    df_Season_Stadistic = pd.DataFrame()
    noFile = int
    progress = int

    def loadFiles(self, path, season, typeDay):

        self.path = path
        self.season = season
        self.typeDay = typeDay

        self.Estudio = MultiplesArchivos(
            self.path,
            self.season,
            self.typeDay
        )  # Se crea el objeto

        os.chdir(self.path)  # cambia el directorio de trabajo a la direcion Indir.
        filelist = glob.glob("*.xlsx")  # Muestra una lista de todos los archivos excel dentro del directorio
        i = 0
        for filename in filelist:
            print(filename)
            i = i + 1
            data_user = pd.read_excel(filename)
            id_users = self.Estudio.user(data_user)  # obtener el terminal de usuario(el ID)
            data_user = self.Estudio.cleanExcel(data_user)  # Limpiar el excel
            data_user = self.Estudio.proces_DF(data_user)  # Desagregar las fechas en columnas por separado.
            data_user = self.Estudio.fil_type_day(data_user)  # Filtramos dataframe por tipo de día de las semanas
            Ener_mean = self.Estudio.maxDeman(data_user, id_users)  # Máxima demanda consumida en el escenario
            self.Ener = pd.concat([self.Estudio.Ener, Ener_mean], axis=1)  # se añade la fila de energías obtenidas
            df_season = self.Estudio.fil_season(data_user)  # Se obtiene el datasets frame filtrado por los meses de estación
            df_Ener_season = self.Estudio.ener_hora_acum(df_season)  # datasets frame de energía por horas
            df_Ener_vector = self.Estudio.prom_clean(df_Ener_season, id_users)  # se obtiene promedio indexado por ID de usuario
            self.Estudio.df_Season = pd.concat([self.Estudio.df_Season, df_Ener_vector], axis=0)  # se concatenan los datos ciclicamente.
            df_Estadistic_Season = self.Estudio.stadistic(df_Ener_vector, df_season)
            self.Estudio.df_Season_Stadistic = pd.concat([self.Estudio.df_Season_Stadistic, df_Estadistic_Season], axis=0)
            print('here')

    def madeCluster(self):
        self.Escenario = Conglomerados(
            self.Estudio.df_Season,
            self.Estudio.df_Season_Stadistic,
            self.season,
            self.typeDay
        )  # Se crea el objeto
        self.Escenario.clusterizar()


