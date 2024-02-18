
from scipy.cluster.hierarchy import dendrogram, linkage, cut_tree
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from scipy.cluster.vq import vq
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cm as cm
from sklearn.decomposition import PCA, FastICA
sns.set()
plt.style.use('ggplot')
plt.rcParams.update({'figure.figsize': (10, 7), 'figure.dpi': 120})

import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_samples, silhouette_score
import seaborn as sns
import numpy as np
from matplotlib import cm
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


class Clustering:

    def __init__(self,df:pd.DataFrame):
        self.df = df
        

    def preproccess(self,):
        # Preprocessing the values to perform hierarchical clustering
        numeric_features = self.df.select_dtypes(include=['int64','float64']).columns.values.tolist()
        scaler = StandardScaler()
        X_transformed = scaler.fit_transform(X=self.df)
        return X_transformed
    
    #HIERARCHICAL CLUSTERING
    def plot_dendrogram(self, truncate_mode:str, X_transformed=None ,p=30, figsize=(10,7), color_threshold=15):

        assert truncate_mode in ['lastp','level','none'] , "truncate_mode must be one of 'lastp','level','none'"
        # En caso de intruducir datos escalados o no
        if X_transformed is not None:
            linked = linkage(X_transformed, 'ward')
        else:
            linked = linkage(self.df, 'ward')
        #Se crea la figura
        plt.figure(figsize=figsize)
        if truncate_mode != 'none':
            show_leaf_counts=True
            if truncate_mode == 'lastp':
                p= 10
            elif truncate_mode == 'level':
                p= 4
        else:
            show_leaf_counts=False

        #Se crea el dendrograma
        dendrogram(linked,
                    orientation='top',
                    labels=self.df.index, # labels of the rows
                    truncate_mode= truncate_mode, # No truncation of the tree
                    above_threshold_color='k', # Differentiate color above threshold
                    color_threshold=color_threshold, #Threshold value for deciding leaves color
                    distance_sort='descending',
                    show_leaf_counts=show_leaf_counts,
                    p=p)
        #title formatting
        if truncate_mode is not 'none':
            plt.gca().set_title(f'Hierarchical Clustering Dendrogram {truncate_mode} (truncated)')
        else:
            plt.gca().set_title('Dendrogram using no truncation')
        plt.show()


    
    def cut_dendrogram(self,cuts:int,X_transformed,by="height",method="ward"):
        """
        Esta función devuelve un print de la cantidad de clusters que se obtienen al cortar el dendrograma, el dendrograma se puede
        cortar por altura o por número de clusters.

        Parameters
        ----------
        cuts : int
            Número de cortes que se quieren hacer en el dendrograma.

        by : str, optional
            Indica si se quiere cortar por altura o por número de clusters. The default is "height".

        method : str, optional
            Método de clustering jerárquico. The default is "ward".

        Returns
        -------
        None.
        """

        assert by in ["n_clusters","height"] , "by must be one of 'n_clusters','height'"
        assert method in ["ward","single","complete","average","weighted","centroid","median"] , "method must be one of 'ward','single','complete','average','weighted','centroid','median' for more info visit https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html"

        # Cut dendrogram tree by number of clusters
        linked = linkage(X_transformed, method=method)
        if by == "height":
            cluster_nclust = cut_tree(linked, height=[cuts])
            print('Clusters specifying number of height:')
        elif by == "n_clusters":
            cluster_nclust = cut_tree(linked, n_clusters=[cuts])
            print('Clusters specifying number of clusters:')
        unique, counts = np.unique(cluster_nclust, return_counts=True)
        print(pd.DataFrame(np.asarray(counts), index=unique, columns=['# Samples']))


    def dendrogram_evaluate(self, n_clusters, X_transformed=None, figsize=(10,7), method="ward"):
        """
        Este método devuelve un plot que mide la evaluación del dendrograma, por defecto se calcula sobre el df inicial, pero se puede
        introducir el X_transformed para que se calcule sobre los datos escalados.

        Parameters
        ----------
        n_clusters : int
            Número de clusters que se quieren obtener.

        X_transformed : np.ndarray
            Array con los datos escalados.

        figsize : tuple, optional
            Tamaño de la figura. The default is (10,7).

        method : str, optional
            Método de clustering jerárquico. The default is "ward".
            Otros métodos: 'single','complete','average','weighted','centroid','median'
            https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html"
        
        
        """

        assert method in ["ward","single","complete","average","weighted","centroid","median"] , "method must be one of 'ward','single','complete','average','weighted','centroid','median' for more info visit https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html"

        if X_transformed is not None:
            linked = linkage(X_transformed, method=method)
            X=X_transformed
        else:
            linked = linkage(self.df, method)
            X=self.df

        # Create a figure
        cluster_labels = cut_tree(linked, n_clusters=n_clusters)
        # Percenta
        print('Clusters specifying number of clusters:')
        unique, counts = np.unique(cluster_labels, return_counts=True)
        print(pd.DataFrame(np.asarray(counts), index=unique, columns=['# Samples']))

        # The silhouette_score gives the average value for all the samples.
        # This gives a perspective into the density and separation of the formed clusters
        silhouette_avg = silhouette_score(X, cluster_labels)
        print("The average silhouette_score is :", silhouette_avg)

        #Plot 
        plt.figure(figsize=figsize)
        self._plot_clusters_silhoutte(self.df, cluster_labels)


    #-------------------------------------KMEANS-------------------------------------------------------------
    def kmeans_clusters(self, X_transformed = None, cluster_range=[2,10], plot=False, random_state=10):
        """
        Este método calcula la clusterización por KMeans y devuelve un plot con la suma de los cuadrados de las distancias y otro con los valores de silueta, según el numero de clusters.
        Por otro lado y manera opcional, tambien puede mostrar la evaluación y visualización de los clusters por PCA, mostrando tambien el silhouette score.

        Parameters
        ----------
        X_transformed : np.ndarray, optional
            Array con los datos escalados. The default is None.
        cluster_range : list, optional
            Rango de clusters que se quieren calcular. The default is [2,10].

        plot : bool, optional
            Indica si se quiere mostrar la evaluación y visualización de los clusters por PCA. The default is False.

        random_state : int, optional
            Semilla para la reproducibilidad del KMeans en la inicilización de los centroides. The default is 10.

        Returns
        -------
        None.
        """
        ## K_means and silhouette method simultaneously with different number of clusters
        range_n_clusters = list(range(cluster_range[0],cluster_range[1]))
        SSQ = []
        sil_avg = []

        if X_transformed is None:
            X=self.df
        else:
            X=X_transformed
        for n_clusters in range_n_clusters:

            # Initialize the clusterer with n_clusters value and a random generator
            # seed of 10 for reproducibility.
            clusterer = KMeans(n_clusters=n_clusters, random_state=random_state)
            cluster_labels = clusterer.fit_predict(X)

            #Obtain Reconstruction error
            _ , err = vq(X, clusterer.cluster_centers_)
            SSQ.append(np.sum(err**2))
            #Obtain silhouette
            sil_avg.append(silhouette_score(X, cluster_labels))
            if plot:
                self._plot_clusters_silhoutte(self.df, cluster_labels, centers=clusterer.cluster_centers_, figsize=(6,4))

        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.plot(range_n_clusters,SSQ, marker='o')
        ax1.set_title("Sum of Squares")
        ax1.set_xlabel("Number of clusters")
        ax2.plot(range_n_clusters,sil_avg, marker='o')
        ax2.set_title("Silhouette values")
        ax2.set_xlabel("Number of clusters")
        fig.suptitle("Kmeans")
        plt.show()

    def kmeans_fit_final_model_and_validate(self, n_clusters:list, X_transformed=None, figsize=(10,6)):
        """
        Este método calcula la clusterización por KMeans y devuelve un plot con la suma de los cuadrados de las distancias y otro con los valores de silueta, según el numero de clusters.

        Parameters
        ----------
        n_clusters : list
            Lista con el número de clusters que se quieren calcular.

        X_transformed : np.ndarray, optional
            Array con los datos escalados. The default is None.

        figsize : tuple, optional
            Tamaño de la figura. The default is (10,6).

        Returns
        -------
        None.
        """
        if X_transformed is None:
            X=self.df
        else:
            X=X_transformed

        # Fit final model and validate
        clusterer = KMeans(n_clusters=n_clusters, random_state=10)
        #Predict on training dataset
        cluster_knn = clusterer.fit_predict(X)
        #  by number of clusters
        print('Clusters specifying number of clusters:')
        unique, counts = np.unique(cluster_knn, return_counts=True)
        print(pd.DataFrame(np.asarray(counts), index=unique, columns=['# Samples']))

        # Silhouette
        silhouette_avg = silhouette_score(X, cluster_knn)
        print("The average silhouette_score is :", silhouette_avg)
        scaler=StandardScaler()
        scaler.fit_transform(X=self.df.copy())
        # Plot clustering classification
        self._plot_clusters_silhoutte(self.df, cluster_knn, centers= scaler.inverse_transform(clusterer.cluster_centers_), figsize=figsize )


    def _plot_clusters_silhoutte(self, df, labels, feature1:str=None, feature2:str=None, centers=None, show_curves:bool=False, figsize=(12, 9), alpha_curves:float=0.5, scale=False):

        """
        Plot silhouette and cluster of samples 
        
        Create two plots, one with silhouette score and other with a 2D view of the cluster of df.
        If there are more than 2 features in df, 2D view is made on the first 2 PCAs space.
        labels must have the same samples as df. If there are more than 2 features in df, show_curves 
        argument make a plot assuming you are trying to cluster curve samples, indexed by rows. 
        Arguments
        ---------

        df (pd.core.frame.DataFrame):
            data.frame containing samples to be clustered
        labels (np.ndarray): 
            cluster labels
        feature1 (str, optional): 
            Name of the x-axis variable to create plot. Defaults to None.
        feature2 (str, optional): 
            Name of the y-axis variable to create plot. Defaults to None.
        centers (np.ndarray, optional): 
            cluster centers. Defaults to None.
        show_curves (bool, optional): 
            show curve plot. Defaults to False.
        figsize (tuple, optional): 
            Size of created figure. Defaults to (12, 9).
        alpha_curves (float, optional): 
            alpha property of curve plot. Defaults to 0.5.
        scale (bool, optional): 
            Scale axis in scatter plot in range [0, 1]. Defaults to False.
        -------
        Raises:
            ValueError: feature1 and feature2 must be df column names

        Returns:
        -------
        None.
        """

        if type(df) is not pd.core.frame.DataFrame:
            raise TypeError(f"df argument must be a pandas DataFrame, object passed is  {type(df)}")
        if df.shape[1] == 1:
            # Plot silhouette 
            # Create a subplot with 1 row and 1 columns
            _, (ax1) = plt.subplots(1, 1, figsize=figsize)
        elif df.shape[1] == 2 or not show_curves:
            # Plot silhouette and real clusters
            # Create a subplot with 1 row and 2 columns
            _, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        else:
            fig = plt.figure(figsize=figsize)
            ax1 = fig.add_subplot(2, 2, 3)
            ax3 = fig.add_subplot(2, 1, 1)
            ax2 = fig.add_subplot(2, 2, 4)
        
        if len(labels.shape) > 1:
            labels = np.squeeze(labels)
        # Obtain number of clusters
        n_clusters = len(np.unique(labels))
        
        # The (n_clusters+1)*10 is for inserting blank space between silhouette
        # plots of individual clusters, to demarcate them clearly.
        ax1.set_ylim([0, df.shape[0] + (n_clusters + 1) * 10])
        y_lower = 10
        
        # Compute the silhouette scores for each sample
        scaler = StandardScaler()
        X_transformed = scaler.fit_transform(X=df.values)
        pca = PCA(n_components=2,)
        X_pca = pd.DataFrame(pca.fit_transform(X_transformed), columns=['PC1','PC2'])
        sample_silhouette_values = silhouette_samples(X_transformed, labels)
        if scale:
            scalex = 1.0/(X_pca.iloc[:,0].max() - X_pca.iloc[:,0].min())
            scaley = 1.0/(X_pca.iloc[:,1].max() - X_pca.iloc[:,1].min())
            X_pca.iloc[:,0] = X_pca.iloc[:,0] * scalex
            X_pca.iloc[:,1] = X_pca.iloc[:,1] * scaley
            
            
        for i in range(n_clusters):
            # Aggregate the silhouette scores for samples belonging to
            # cluster i, and sort them
            samples_cluster = labels == i
            ith_cluster_silhouette_values = \
                sample_silhouette_values[samples_cluster]

            ith_cluster_silhouette_values.sort()

            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i

            color = cm.nipy_spectral(float(i) / n_clusters)
            ax1.fill_betweenx(np.arange(y_lower, y_upper),
                                0, ith_cluster_silhouette_values,
                                facecolor=color, edgecolor=color, alpha=0.7)

            # Label the silhouette plots with their cluster numbers at the middle
            ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

            # Compute the new y_lower for next plot
            y_lower = y_upper + 10  # 10 for the 0 samples
            if df.shape[1] == 2:
                if feature1 is None:
                    feature1 = df.columns[0]
                if feature2 is None:
                    feature2 = df.columns[1]
                
                if feature1 not in df.columns:
                    raise ValueError(f'feature {feature1} is not in provided data')
                if feature2 not in df.columns:
                    raise ValueError(f'feature {feature2} is not in provided data') 
                # 2nd Plot showing the actual clusters formed
                df_plot = df.iloc[samples_cluster,:]
                sns.scatterplot(x='X1', y='X2', data=df_plot, color=color, edgecolor='black', legend='full', ax=ax2)

                ax2.set_title("Visualization of the clustered data.")
                ax2.set_xlabel(f"Feature space for {feature1}")
                ax2.set_ylabel(f"Feature space for {feature2}")
                
                if centers is not None:
                    # Draw white circles at cluster centers
                    ax2.scatter(centers[:, 0], centers[:, 1], marker='o',
                                c="white", alpha=1, s=200, edgecolor='k')

                    for i, c in enumerate(centers):
                        ax2.scatter(c[0], c[1], marker='$%d$' % i, alpha=1,
                                    s=50, edgecolor='k')
            if df.shape[1] > 2:
                
                df_plot = X_pca.iloc[samples_cluster,:]
                sns.scatterplot(x='PC1', y='PC2', data=df_plot, color=color, edgecolor='black', legend='full', ax=ax2)

                ax2.set_title("Visualization of the clustered data.")
                ax2.set_xlabel(f"Feature space for PC1")
                ax2.set_ylabel(f"Feature space for PC2")
                
                if centers is not None:
                    center_pca = pca.transform(scaler.transform(centers))
                    if scale:
                        center_pca[:,0] = center_pca[:,0] * scalex
                        center_pca[:,1] = center_pca[:,1] * scaley
                        
                    # Draw white circles at cluster centers
                    ax2.scatter(center_pca[:, 0], center_pca[:, 1], marker='o',
                                c="white", alpha=1, s=200, edgecolor='k')

                    for i, c in enumerate(center_pca):
                        ax2.scatter(c[0], c[1], marker='$%d$' % i, alpha=1,
                                    s=50, edgecolor='k')

        ax1.set_title(f"Silhouette plot. Mean silhouette: {round(sample_silhouette_values.mean(),3)}")
        ax1.set_xlabel("Silhouette coefficient values")
        ax1.set_ylabel("Cluster label")

        # The vertical line for average silhouette score of all the values
        ax1.axvline(x=sample_silhouette_values.mean(), color="red", linestyle="--")

        ax1.set_yticks([])  # Clear the yaxis labels / ticks
        ax1.set_xticks([-1, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1])
        if df.shape[1] > 2 and show_curves:
            ## Multivariate plots
            for i in range(n_clusters):
                # Aggregate the silhouette scores for samples belonging to
                # cluster i, and sort them
                samples_cluster = labels == i
                ith_cluster_silhouette_values = \
                    sample_silhouette_values[samples_cluster]

                ith_cluster_silhouette_values.sort()

                size_cluster_i = ith_cluster_silhouette_values.shape[0]
                y_upper = y_lower + size_cluster_i

                color = cm.nipy_spectral(float(i) / n_clusters)
                df.iloc[samples_cluster,:].T.plot(legend=None, color=color, ax=ax3, alpha=alpha_curves)
            
        plt.suptitle(("Silhouette analysis for hierarchical clustering on sample data "
                        "with n_clusters = %d" % n_clusters),
                        fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()   

    #----------------------------------------------------------------------------GAUSSIAN MIXTURE MODEL-----------------------------------------------------------------------
    def gaussian_mixture_clusters(self, X_transformed=None, cluster_range:list=[2,10], plot=False, figsize=(6,4), random_state=10, cv_type='full'):

        """
        Este método calcula la clusterización por Gaussian Mixture y devuelve un plot con la suma de los cuadrados de las distancias y otro con los valores de silueta, según el numero de clusters.

        Parameters
        ----------
        X_transformed : np.ndarray, optional
            Array con los datos escalados. The default is None.

        cluster_range : list, optional
            Rango de clusters que se quieren calcular. The default is [2,10].

        plot : bool, optional
            Indica si se quiere mostrar la evaluación y visualización de los clusters por PCA. The default is False.

        figsize : tuple, optional
            Tamaño de la figura. The default is (6,4).

        random_state : int, optional
            Semilla para la reproducibilidad del KMeans en la inicilización de los centroides. The default is 10.

        cv_type : str, optional
            Tipo de matriz de covarianza. The default is 'full'.
            Otros métodos: 'spherical','diag','tied'
            https://scikit-learn.org/stable/modules/generated/sklearn.mixture.GaussianMixture.html

        Returns
        -------
        None.
        
        """
        if X_transformed is None:
            X=self.df

        else:
            X=X_transformed

            ## K_means and silhouette method simultaneously with different number of clusters
        range_n_clusters = list(range(cluster_range[0],cluster_range[1]))
        SSQ = []
        sil_avg = []
        for n_clusters in range_n_clusters:
            # fit model
            clusterer = GaussianMixture(n_components=n_clusters,
                                    covariance_type=cv_type,
                                    random_state=random_state)
            cluster_labels = clusterer.fit_predict(X)

            #Obtain Reconstruction error
            _ , err = vq(X, clusterer.means_)
            SSQ.append(np.sum(err**2))
            #Obtain silhouette
            sil_avg.append(silhouette_score(X, cluster_labels))
            if plot:
                self._plot_clusters_silhoutte(self.df, cluster_labels, centers=clusterer.means_, figsize=figsize)

        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.plot(range_n_clusters,SSQ, marker='o')
        ax1.set_title("Sum of Squares")
        ax1.set_xlabel("Number of clusters")
        ax2.plot(range_n_clusters,sil_avg, marker='o')
        ax2.set_title("Silhouette values")
        ax2.set_xlabel("Number of clusters")
        fig.suptitle("Gaussian Mixture")
        plt.show()


    def gaussian_mixture_fit_final_model_and_validate(self, n_components:int, X_transformed=None, figsize=(10,6)):

        """
        Este método calcula la clusterización por Gaussian Mixture y devuelve un plot con la suma de los cuadrados de las distancias y otro con los valores de silueta, según el numero de clusters.

        Parameters
        ----------
        n_components : int
            Número de clusters que se quieren calcular.

        X_transformed : np.ndarray, optional
            Array con los datos escalados. The default is None.

        figsize : tuple, optional
            Tamaño de la figura. The default is (10,6).

        Returns
        -------
        None.
        
        """
        if X_transformed is None:
            X=self.df
        else:
            X=X_transformed

        # Fit final model and validate
        clusterer_GMM = GaussianMixture(n_components=n_components,
                                    covariance_type='full',
                                    random_state=10)
        #Predict on training dataset
        cluster_GMM = clusterer_GMM.fit_predict(X)
        # Cut dendrogram tree by number of clusters
        print('Clusters specifying number of clusters:')
        unique, counts = np.unique(cluster_GMM, return_counts=True)
        print(pd.DataFrame(np.asarray(counts), index=unique, columns=['# Samples']))
        # Silhouette
        silhouette_avg = silhouette_score(X, cluster_GMM)
        print("The average silhouette_score is :", silhouette_avg)
        scaler=StandardScaler()
        scaler.fit_transform(X=self.df.copy())
        # Plot clustering classification
        self._plot_clusters_silhoutte(self.df, cluster_GMM, centers= scaler.inverse_transform(clusterer_GMM.means_), figsize=figsize)

        #DBSCAN
        #OTHER CLUSTERINGS    
    

    def dbscan_clusters(df, X_transformed, eps_range=np.arange(0.1, 2.0, 0.1), min_samples=5, plot=False):
        # Lista para almacenar los promedios de los coeficientes de silueta
        sil_scores = []
        
        for eps in eps_range:
            # Aplicar DBSCAN con el valor actual de eps y min_samples fijos
            db = DBSCAN(eps=eps, min_samples=min_samples)
            cluster_labels = db.fit_predict(X_transformed)
            
            # No todos los valores de eps darán lugar a clusters significativos.
            # DBSCAN puede resultar en un cluster para todos los puntos (label = 0) o ruido (-1 para todos).
            # Verificar si se formaron clusters válidos antes de calcular el silhouette score.
            if len(set(cluster_labels)) > 1:
                sil_score = silhouette_score(X_transformed, cluster_labels)
                sil_scores.append(sil_score)
            else:
                # Si no se formaron clusters válidos, agregar un valor NaN o un marcador
                sil_scores.append(np.nan)
            
            if plot and len(set(cluster_labels)) > 1:
                # Puedes añadir tu propia función de trazado aquí para visualizar los clusters
                # Por ejemplo: plot_clusters(df, cluster_labels)
                pass

        # Graficar los resultados
        plt.figure(figsize=(10, 6))
        plt.plot(eps_range, sil_scores, marker='o')
        plt.title("DBSCAN Silhouette Scores for Varying eps")
        plt.xlabel("eps")
        plt.ylabel("Silhouette Score")
        plt.show()

        return sil_scores

    # Nota: Necesitas definir 'df' y 'X_transformed' antes de llamar a esta función.
    # También puede ser necesario ajustar el rango de 'eps_range' y 'min_samples' según tu conjunto de datos.


    def dbscan_clusters(self, X_transformed=None, eps_values=[0.5], min_samples_values=[5], plot=False):
        """
        Este método calcula la clusterización por DBSCAN para diferentes valores de eps y min_samples,
        y opcionalmente muestra la evaluación y visualización de los clusters por PCA, incluyendo el silhouette score.

        Parameters
        ----------
        X_transformed : np.ndarray, optional
            Array con los datos escalados. Si es None, se utilizará self.df.
        eps_values : list, optional
            Lista de valores de eps para probar.
        min_samples_values : list, optional
            Lista de valores de min_samples para probar.
        plot : bool, optional
            Indica si se quiere mostrar la evaluación y visualización de los clusters por PCA.

        Returns
        -------
        None.
        """
        if X_transformed is None:
            X = self.df
        else:
            X = X_transformed

        results = []

        for eps in eps_values:
            for min_samples in min_samples_values:
                db = DBSCAN(eps=eps, min_samples=min_samples)
                labels = db.fit_predict(X)

                # Ignorar el ruido identificado por DBSCAN, si existe
                n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
                if n_clusters_ > 0:
                    silhouette_avg = silhouette_score(X, labels)
                else:
                    silhouette_avg = -1

                results.append((eps, min_samples, n_clusters_, silhouette_avg))
                print(f"DBSCAN with eps={eps}, min_samples={min_samples} --> clusters: {n_clusters_}, silhouette: {silhouette_avg}")

                if plot and n_clusters_ > 0:
                    self._plot_clusters_dbscan(X, labels)

        results_df = pd.DataFrame(results, columns=['eps', 'min_samples', 'n_clusters', 'silhouette'])
        return results_df

    def _plot_clusters_dbscan(self, X, labels):
        """
        Visualiza los clusters utilizando PCA para reducir la dimensionalidad a 2D si es necesario.

        Parameters
        ----------
        X : np.ndarray
            Datos de entrada.
        labels : np.ndarray
            Etiquetas de cluster generadas por DBSCAN.

        Returns
        -------
        None.
        """
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X)

        unique_labels = set(labels)
        colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

        for k, col in zip(unique_labels, colors):
            if k == -1:
                # Color de ruido.
                col = [0, 0, 0, 1]

            class_member_mask = (labels == k)

            xy = X_pca[class_member_mask]
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=14 if k == -1 else 6)

        plt.title('Clusters by DBSCAN')
        plt.show()

