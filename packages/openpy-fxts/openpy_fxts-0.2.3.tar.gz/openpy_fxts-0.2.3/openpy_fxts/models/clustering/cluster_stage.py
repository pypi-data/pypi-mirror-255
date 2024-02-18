import numpy as np  # librería para manejos de arreglos
import pandas as pd  # librería para el tratamiento de datos
from sklearn.cluster import KMeans

from sklearn.preprocessing import MinMaxScaler
# from sklearn.metrics import silhouette_samples
from tslearn.barycenters import euclidean_barycenter, dtw_barycenter_averaging, softdtw_barycenter
from scipy import cluster, spatial


class Conglomerados:
    """
    Clase que contiene métodos para realizar los cluster permite metodos de DTW y K-means estan definidos en esta clase
    """

    List_clusterTree = []  # Lista vacía para almacenar dataframe obtenidos de los cluster
    Curva_mediaTree = []  # Lista vacía para almacenar
    List_Electric_Feature = []  # lista vacia para almacenar dataframe de datos electricos
    Cluster_NumberTree = int  # entero para almacenar la cantidad máxima de clustlista_num = []
    lista_Nu_cluster = []  # lista para almacenar número de cluster, la posicion coicide con el número de cluster
    indexprimercluster = []
    list_residuos = []  # lista para alamacenar los residuos entre la curva DBA y los perfiles de carga
    list_residuos_media = []  # Lista para alamcenar valores medios de los residuos de cada cluster
    corr_cluster = []  # Lista para almacenar valores de la correlación de cada cluster
    corr_cluster_media = []  # Lista para almacenar la medai de los valores de correlación total de cada cluster


    print("Análisis de Curvas de Carga")

    def __init__(self, escenario, stdist=None, season=None, typeDay=None):
        self.escenario = escenario
        self.stdist = stdist
        self.season = season
        self.typeDay = typeDay

    def normalice_axis(self, df):
        """"Método que normaliza datasets frame por axisas."""
        # df = df.dropna(how ='any')
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_df = scaler.fit_transform(df.transpose())
        scaled_df = pd.DataFrame(scaled_df.T)
        scaled_df = scaled_df.set_index(df.index)
        return scaled_df

    def normalice(self, df):
        """Método para normalizar"""
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_df = scaler.fit_transform(df)
        scaled_df = pd.DataFrame(scaled_df)
        return scaled_df

    def DTWDistance(self, s1, s2):
        """Método para calcular distancía dinámica temporal"""

        DTW = {}

        for i in range(len(s1)):
            DTW[(i, -1)] = float('inf')
        for i in range(len(s2)):
            DTW[(-1, i)] = float('inf')
        DTW[(-1, -1)] = 0

        for i in range(len(s1)):
            for j in range(len(s2)):
                dist = (s1[i] - s2[j]) ** 2
                DTW[(i, j)] = dist + min(DTW[(i - 1, j)], DTW[(i, j - 1)], DTW[(i - 1, j - 1)])

        return np.sqrt(DTW[len(s1) - 1, len(s2) - 1])

    def ClusterIndicesNumpy(self, clustNum, labels_array):  # función para agrupar las observaciones por cluster
        """Métodos para agrupara observaciones"""
        return np.where(labels_array == clustNum)[0]

    def ClusterIndicesComp(self, clustNum, labels_array):  # list comprehension
        return np.array([i for i, x in enumerate(labels_array) if x == clustNum])

    def clusterizar(self):
        """#  Métodos para clusterizar"""
        escenario_ = self.escenario.dropna(how='any')
        E_H = np.array(escenario_)
        E_W = np.array(self.normalice_axis(escenario_))  # array normalizado algoritmo Normalizado dataframe de energías para DTW
        df_List_W = self.normalice_axis(escenario_)  # datafreme normalizado para poder normalizar DTW y graficar.

        f = lambda u, v: np.sqrt(((u - v) ** 2).sum())  # distancia euclidiana.
        k = lambda S1, S2: self.DTWDistance(S1, S2)  # distancia DTW.

        Array_DTW = cluster.hierarchy.fclusterdata(E_W, t=1.7, criterion='distance', metric=k, depth=2, method='ward', R=None)  # lista que muestra en cada posición el numero de cluster al que pertenece
        # arrayTree_ = self.ClusterIndicesNumpy(1,Array_DTW)    # devuelve un arreglo con las posiciones de las observaciones pertenecientes al cluster 3
        self.Cluster_NumberTree = Array_DTW.max()  # contiene el número máximo de cluster obtenidos
        self.lista_Nu_cluster = self.listaCluster(self.Cluster_NumberTree)

        for i in range(1, self.Cluster_NumberTree + 1):
            arrayTree = self.ClusterIndicesNumpy(i, Array_DTW)  # devuelve un arreglo con las posiciones de las observaciones pertenecientes al cluster i

            # arrayTree = ClusterIndicesComp(Cluster_NumberTree, Array_DTW)
            # Y[ClusterIndicesNumpy(2,kmeans.labels_)]                          #devuelve el vector de las dimensiones de las observaciones que hay en cada cluster
            # print(arrayTree)
            # df_Temp = df_List.ix[arrayTree]                                   # filtra el datasets frame segun la lista array
            df_Temp = df_List_W.iloc[arrayTree]  # filtra el datasets frame segun la lista array nrmalizada se obteiene un datasets frame con los perfiles de un cluster
            df_Temp_E = self.stdist.iloc[arrayTree]  # dataframe que contiene valores estadisticos de cada perfil individual
            # C_Media = df_Temp.mean()                                          # se calcula el promedio de las curvas dentro de un mismo cluster
            Z = np.array(df_Temp)  # se crea un NumpyArray del dataframe que contiene el clsuter de la iteración i.
            dba_Media = dtw_barycenter_averaging(Z, max_iter=100, verbose=False)  # se realiza la media de DTW.
            # dba_Media = softdtw_barycenter(Z, gamma=1., max_iter=100)
            dba_Media = pd.DataFrame(dba_Media)
            dba_Media_scalaed = self.normalice(dba_Media)
            self.List_clusterTree.append(df_Temp)
            self.List_Electric_Feature.append(df_Temp_E)
            self.Curva_mediaTree.append(dba_Media_scalaed)  # contiene un arreglo de vectores que representan la curva de

        for Q in range(0, len(self.List_clusterTree)):
            media_ = self.Curva_mediaTree[Q].T
            residuos = pd.DataFrame(
                self.List_clusterTree[Q].values - media_.values,
                columns=self.List_clusterTree[Q].columns
            )  # calculos de los residuos
            ECM = sum(residuos.pow(2).mean()) / len(self.List_clusterTree[Q])  # calcula los errores cuadraticos mnedios respecta a la media DBA
            ECM = round(ECM, 3)
            self.list_residuos.append(ECM)

            list_corr_value = []
            temp_matrix = self.List_clusterTree[Q]
            temp_matrix = temp_matrix[~np.all(temp_matrix == 0, axis=1)]  # elimina filas con todos los elemetos cero
            for b in range(0, len(temp_matrix)):
                # curva_carga = self.List_clusterTree[Q].iloc[b].values
                curva_carga = temp_matrix.iloc[b].values
                curva_tipica = self.Curva_mediaTree[Q].T.values
                correlacion = self.norm_cross_corr(curva_carga, curva_tipica)
                correlacion = round(correlacion, 4)
            list_corr_value.append(correlacion)

            self.corr_cluster.append(list_corr_value)
            self.corr_cluster_media.append(sum(list_corr_value) / len(list_corr_value))

    def norm_cross_corr(self, serie1, serie2):
        """ La función para encontrar la correlación cruzada normalizada en python es: statsmodels.tsa.stattools.ccf
            :param: serie1: serie de tiempo\n
            :param: serie2: serie de tiempo promedio\n
            :return: valor de correlacion entre las series"""
        return np.sum(serie1 * serie2) / (np.linalg.norm(serie1) * np.linalg.norm(serie2))

    """
    def listResiduos(self,Curva_mediaTree,List_clusterTree):
        Metodo que permite calcular el error cuadratico medio a entre entre el vector de curva promedios y las restantes curvas dentro de grupo.\n\n
        :param : Curva_mediaTree: lista que continen en cada posicion la curva promedio. \n
        :param : List_clusterTree: lista que contiene en cada posición los gruppos de curva 
                resultado de clustering 

        for Q in range(0, len(List_clusterTree)):
            media_ = Curva_mediaTree[Q].T
            residuos = pd.DataFrame(List_clusterTree[Q].values - media_.values, columns=List_clusterTree[Q].columns)
            # EC = residuos.pow(2)
            ECM = sum(residuos.pow(2).mean()) / len(List_clusterTree[Q])
            ECM = round(ECM, 3)
            self.list_residuos.append(ECM)
    """

    def Kmeans_Cluster(self, df, Cluster_Number, Normalice=0):
        """Parametros datafreme a clsuterizar, nuemro de lcuster, 1 si normaliza por filas y cero si normaliza por columnas.\n
        parameter:Cluster_Number \n
        parameter:Normalice"""

        List_cluster = []  # Lista vacía para almacenar
        # Curva_media = []
        if Normalice == 1:
            df_nor = self.normalice_axis(df)
        else:
            df_nor = self.normalice(df)
        # df_nor = normalice_axis(df)# normmaliza datasets frame de enrgias
        array_df = np.array(df_nor)
        kmeans = KMeans(n_clusters=Cluster_Number, init='k-means++', max_iter=300).fit(
            array_df)  # pasamos como parámetros la lsita de puntos X.

        # centroids = kmeans.cluster_centers_  # nos devuelve los centroirde de los clúster
        # Predicting the clusters
        # labels = kmeans.predict(array_df)  # devuelve una lista alineada que nos dice a que clúster pertenece cada punto
        # num_cluster_points = kmeans.labels_.tolist()  # muestra el numero de cluster separados por ,

        for i in range(0, Cluster_Number):
            array = self.ClusterIndicesNumpy(i, kmeans.labels_)  # devuelve un arreglo con las posiciones de las observaciones pertenecientes al cluster 3
            df_Temp = df_nor.iloc[array]  # fitra el datasets frame segun la lista array
            List_cluster.append(df_Temp)  # almacena en un arreglo los dataframe dque representa cada cluster.
        return List_cluster

    def listaCluster(self, num):
        """
        Metodo para almacenar en una lista los numero de cluster\n
        :argument : num\n
        :return: lista de los cluster
        """
        lista_num = list(range(num))
        for i in lista_num:
            lista_num[i] = str(lista_num[i] + 1)

        return lista_num