from sklearn.preprocessing import StandardScaler
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA, FastICA
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler




class PCA:

    def __init__(self,df):
        self.df=df
    

        
    def preproccess(self,):
        """
        Este método se encarga de preprocesar los datos a través a de un escalado estandar

        Arguments
        ----------  

        X: pd.DataFrame
            Dataframe con las variables a preprocesar
        
        """
        # Preprocessing the values to perform hierarchical clustering
        numeric_features = self.df.select_dtypes(include=['int64','float64']).columns.values.tolist()
        scaler = StandardScaler()
        X_transformed = scaler.fit_transform(X=self.df)
        self.X_transformed_ = X_transformed
        return X_transformed
    

    def pca_fit_transform(self,X_transformed):
        """
        Este método se encarga de fitear y tranformar los datos a través del PCA

        Arguments
        ----------
        X_transformed: pd.DataFrame
            Dataframe con las variables preprocesadas o no transformadas

        Returns
        ----------
        pca: PCA
            Objeto PCA fiteado y transformado
        """
        pca = PCA(n_components=X_transformed.shape[1],) #Tantas compoentes como variables tienen los datos y ya posteriormente elegimos las optimas
        X_pca = pca.fit_transform(X_transformed)

        self.pca_ = pca
        self.X_pca_ = X_pca
        return pca
    


    def exp_variance(self,n_componentes_print:int=3):
        """
        Este método se encarga de calcular la varianza explicada por cada componente principal

        Arguments
        ----------
        n_componentes_print: int
            Número de componentes principales a imprimir, con información del % de varianza de los datos explicada respecto 
            de la original.

        Returns
        ----------
        exp_variance: pd.DataFrame
            Dataframe con la varianza explicada por cada componente principal y la varianza explicada acumulada

        """

        if hasattr(self, 'pca_'):
            pass
        else:
            raise Exception('You must run pca_fit_transform first')
        exp_variance = pd.DataFrame(data=self.pca_.explained_variance_ratio_, index = ['PC' + str(n_pca + 1) for n_pca in range(self.pca_.n_components)], columns=['Exp_variance'])
        exp_variance['cum_Exp_variance'] = exp_variance['Exp_variance'].cumsum()

        print(f"Con las {n_componentes_print} primeras componentes principales explicamos el {exp_variance.iloc[n_componentes_print-1,1]*100} % de la varianza de los datos")
        return exp_variance
    

    def plot_exp_variance(self,figsize=(8,5),rot=0):
        """
        Este método dibuja la varianza explicada por cada componente principal y la varianza explicada acumulada

        Arguments
        ----------
        figsize: tuple
            Tamaño de la figura
        rot: int
            Rotación de las etiquetas del eje x

        Returns
        ----------
        None
        
        """
        sns.set()
        plt.style.use('ggplot')
        plt.rcParams.update({'figure.figsize': (10, 7), 'figure.dpi': 120})
        exp_variance_df =self.exp_variance()
        plt.figure(figsize=figsize)
        sns.barplot(data=exp_variance_df, x=exp_variance_df.index, y='Exp_variance', color='gray')
        sns.lineplot(data=exp_variance_df, x=exp_variance_df.index, y='cum_Exp_variance', color='blue', label='Cumulative Proportion')
        plt.gca().set_ylabel('Proportion of Variance Explained')
        plt.gca().set_xlabel('Principal Component')

        if rot!=0:
            plt.xticks(rotation=rot)
            plt.tight_layout()
        else:
            pass
        plt.legend()
        plt.show()


    def plot_pca_coefs(self,figsize=(12,6),rot=0):
        """
        Este método dibuja los coeficientes de cada variable en cada componente principal

        Arguments
        ----------

        figsize: tuple
            Tamaño de la figura
        rot: int
            Rotación de las etiquetas del eje x

        Returns
        ----------
        None
        """
        sns.set()
        plt.style.use('ggplot')
        plt.rcParams.update({'figure.figsize': (10, 7), 'figure.dpi': 120})
        self.loadings = pd.DataFrame(self.pca_.components_.T * np.sqrt(self.pca_.explained_variance_), columns=['PC' + str(pca + 1) for pca in range(self.pca_.n_components)], index=self.df.select_dtypes(include=['int64','float64']).columns.values.tolist())
        # Plot the 3 first PCs
        # fig, axes = plt.subplots(loadings.shape[1], 1, figsize=(16,9))
        fig, axes = plt.subplots(3, 1, figsize=figsize)
        PC = 0
        for ax in axes.ravel():
            sns.barplot(data=self.loadings, x=self.loadings.index, y=self.loadings.columns.values.tolist()[PC], color='gray', ax=ax)
            PC += 1
            
            if rot!=0:
                ax.set_xticklabels(ax.get_xticklabels(), rotation=rot)
                plt.tight_layout()
            else:
                pass
        plt.show()


    def _sign(x):
        """
        Este es un método privado que se encarga de devolver el signo de un número, y se utiliza en la función describe_component para obtener la descripción de cada componente principal
        
        """
        if x>0:
            return "positivamente"
        else:
            return "negativamente"

    def describe_component(self, n_components_to_describe:list, return_df:bool=False):
        """
        Esta función se encarga de describir cada componente principal, indicando las variables más ligadas a cada componente principal

        Arguments
        ----------
        n_components_to_describe: list
            Lista con los componentes principales a describir
        
        """
        self.loadings = pd.DataFrame(self.pca_.components_.T * np.sqrt(self.pca_.explained_variance_), columns=['PC' + str(pca + 1) for pca in range(self.pca_.n_components)], index=self.df.select_dtypes(include=['int64','float64']).columns.values.tolist())
        assert len(np.intersect1d(self.loadings.index[:3],self.loadings.index[-2:]))==0 , "Las variables del dataframe son pocas como para hacer una descripción de las 3 primeras y las 2 últimas, pues se solapan.\
            El numero de variables debe de ser >4"
        top_comp_list=[]

        for component in self.loadings.columns[np.array(n_components_to_describe)-1]:
            top_comp=pd.DataFrame()
            top_comp[component]=abs(self.loadings[component]).sort_values(ascending=False)
            top_comp["sign"]=np.sign(self.loadings[component])

            print(f"Para {component} se observa que en comparación con el resto de variables, está ligado a la '{top_comp.index[0]}' {self._sign(top_comp.sign[0])}, a la '{top_comp.index[1]}' {self._sign(top_comp.sign[1])} y a la '{top_comp.index[2]}' {self._sign(top_comp.sign[2])} más fuertemente,\
                   mientras que en una menor medida los coeficientes están menos ligados con '{top_comp.index[-1]}' {self._sign(top_comp.sign[-1])} y a la '{top_comp.index[-2]}' {self._sign(top_comp.sign[-2])}.")
            top_comp_list.append(top_comp)
        if return_df:
            return top_comp_list
        else:
            pass



    def biplot(score, coeff, y=None, labels:list=None, 
            figsize=(12,9), xlim=None, ylim=None, scale=False):
        """

        A biplot is plot which aims to represent both the observations and variables of a matrix of multivariate 
        data on the same plot. 
        Arguments
        ---------
        score (np.ndarray):
            Score of PCAs.
        coeff (np.ndarray):
            Component of PCAs.
            np.transpose(pca.components_[0:2, :])
        y (pd.core.series.Series, optional):
            sample labels. Defaults to None.
            y
        labels (list, optional):
            sample properties. Defaults to None.
            X.columns.values.tolist()
        figsize (tuple, optional): 
            Size of created figure. Defaults to (12,9).
        xlim (tuple, optional): 
            X limits of created plot. Defaults to None.
        ylim (tuple, optional): 
            Y limits of creataed plot. Defaults to None.
        scale(bool, optional):
            Whether to scale PCAs. Defaults to False.

        Returns
        -------
        None.

        """
        sns.set()
        plt.style.use('ggplot')
        plt.rcParams.update({'figure.figsize': (10, 7), 'figure.dpi': 120})

        xs = score[:,0]
        ys = score[:,1]
        n = coeff.shape[0]
        if scale:
            scalex = 1.0/(xs.max() - xs.min())
            scaley = 1.0/(ys.max() - ys.min())
            scale_xs = xs * scalex
            scale_ys = ys * scaley
        else:
            scale_xs = xs 
            scale_ys = ys 
            
        # df = pd.DataFrame({'x':xs * scalex, 'y':ys * scaley})
        # df['c'] = y.values
        _, ax = plt.subplots(figsize=figsize)
        # if labels is None:
        sns.scatterplot(x=scale_xs * 1.15, y=scale_ys * 1.15, alpha=0)
        # else:
        #     sns.scatterplot(x='x', y='y', hue='c', data=df)
        if y is not None:
            try:
                for i, txt in enumerate(y.values):
                    ax.annotate(txt[0], (scale_xs[i], scale_ys[i]))
            except:
                for i, txt in enumerate(y):
                    ax.annotate(txt[0], (scale_xs[i], scale_ys[i]))
                
        for i in range(n):
            plt.arrow(0, 0, np.abs(scale_xs).max() * coeff[i,0], np.abs(scale_ys).max() * coeff[i,1],color = 'r')
            if labels is None:
                plt.text(np.abs(scale_xs).max() * coeff[i,0] * 1.15, np.abs(scale_ys).max() * coeff[i,1] * 1.15, "Var"+str(i+1), color = 'g', ha = 'center', va = 'center')
            else:
                plt.text(np.abs(scale_xs).max() * coeff[i,0] * 1.15, np.abs(scale_ys).max() * coeff[i,1] * 1.15, labels[i], color = 'g', ha = 'center', va = 'center')
        if xlim is not None:
            plt.xlim(*xlim)
        if ylim is not None:
            plt.ylim(*ylim)
        plt.xlabel("PC{}".format(1))
        plt.ylabel("PC{}".format(2))
        plt.grid()