import numpy as np
import pandas as pd
import time
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import GridSearchCV
from SupervisedDiscretization.CounterfactualAnalysis.counterfactualExplanations import CounterfactualExplanation

class Discretizer:
    def fit(self, x, y):
        raise NotImplementedError

    def transform(self, x, y, tao=None):
        if tao is None:
            tao = self.tao
        x_discretized = tao.apply(lambda t: (x[t['Feature']]<=t['Threshold']).astype(int),axis=1).T
        x_discretized.columns = tao.apply(lambda t: f"{t['Feature']}<={t['Threshold']}", axis=1)
        return x_discretized, y

    def fit_transform(self, x, y):
        self.fit(x, y)
        return self.transform(x, y)

    def compression_rate(self, x, y, tao=None):
        if tao is None:
            tao = self.tao
        x_discr, y_discr = self.transform(x, y, tao)
        u = np.unique(x_discr,axis=0,return_index=True)[1]
        compression_rate = 1 - len(u)/len(x)
        return compression_rate

    def inconsistency_rate(self, x, y, tao=None):
        if tao is None:
            tao = self.tao
        x_discr, y_discr = self.transform(x, y, tao)
        x_discr['y'] = y_discr.values
        inconsistency_rate = x_discr.groupby(x_discr.columns[:-1].to_list()).agg(min_count=(x_discr.columns[-1], lambda x: min(np.count_nonzero(x == 0), np.count_nonzero(x == 1))))['min_count'].sum() / len(x_discr)

        return inconsistency_rate

    @staticmethod
    def GetTollerance(x):
        eps = pd.Series(index=x.columns,dtype=float)
        for i in x.columns:
            try:
                eps[i] = max(1.e-4, np.min(np.diff(np.unique(x[i]))) / 2)
            except:
                eps[i] = 1.e-4
        return eps


class NoDiscretization(Discretizer):
    def fit(self, x, y):
        self.tao = pd.DataFrame(columns=['Feature','Threshold'])

    def transform(self, x, y, tao=None):
        return x, y

class TotalDiscretizer(Discretizer):
    def fit(self, x, y):
        self.tao = pd.DataFrame(columns=['Feature','Threshold'])
        for i in x.columns:
            self.tao = pd.concat((self.tao,self.getAllThresholds(x, i)))

    def getAllThresholds(self, x, c):
        tao_c = pd.DataFrame(columns=['Feature','Threshold'])
        x_c = np.sort(np.unique((x[c])))
        tao_c['Threshold'] = x_c[:-1] + (x_c[1:] - x_c[:-1]) / 2
        tao_c['Feature'] = c
        return tao_c


class BucketDiscretizer(Discretizer):
    def fit(self, x, y):
        self.tao = pd.DataFrame(columns=['Feature','Threshold'])
        for i in x.columns:
            self.tao = pd.concat((self.tao,self.getAllThresholds(x, y, i)))

    def getAllThresholds(self, x, y, c):
        tao_c = pd.DataFrame(columns=['Feature','Threshold'])
        x_c, i_c = np.unique(x[c], return_index=True)
        i_c = i_c[np.argsort(x_c)]
        x_c = x[c].iloc[i_c].to_numpy()
        y_c = y.iloc[i_c].to_numpy().flatten()
        t = x_c[:-1] + (x_c[1:] - x_c[:-1]) / 2
        mask = (y_c[1:] - y_c[:-1]) != 0
        tao_c['Threshold'] = t[mask]
        tao_c['Feature'] = c
        return tao_c

class QuantileDiscretizer(Discretizer):
    def __init__(self, n=100, *args, **kwargs):
        self.n = n
        super().__init__(*args, **kwargs)

    def fit(self, x, y):
        self.tao = pd.DataFrame(columns=['Feature','Threshold'])
        for i in x.columns:
            self.tao = pd.concat((self.tao,self.getAllThresholds(x, i)))

    def getAllThresholds(self, x, c):
        thresholds = []
        for i in np.arange(0,1,1/self.n):
            thresholds.append(np.quantile(x[c], i))
        thresholds = np.unique(thresholds)
        tao_c = pd.DataFrame(columns=['Feature','Threshold'])
        tao_c['Threshold'] = thresholds
        tao_c['Feature'] = c
        return tao_c

class FCCA(Discretizer):
    def __init__(self, estimator, p0=0.5, p1=1, lambda0=0.1, lambda1=1, lambda2=0.0, compress=True, timelimit=1*60, verbose=True):
        super().__init__()
        self.estimator = estimator
        self.p0 = p0
        self.p1 = p1
        self.lambda0 = lambda0
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.compress = compress
        self.timelimit = timelimit
        self.verbose = verbose

    def fit(self, x, y):
        t0 = time.time()

        x = x.copy()
        scaler = MinMaxScaler()
        x[x.columns] = scaler.fit_transform(x)
        self.estimator.fit(x, y)

        if isinstance(self.estimator, GridSearchCV):
            self.estimator = self.estimator.best_estimator_

        eps = self.GetTollerance(x)
        x0, y0 = self.getRelevant(x, y)
        if self.verbose:
            print(f"Number of CEs to compute: {len(x0)}")
        xCE, yCE = self.getCounterfactualExplanations(x0, y0, eps)

        x0[x0.columns] = scaler.inverse_transform(x0)
        xCE[xCE.columns] = scaler.inverse_transform(xCE)
        self.tao = self.getCounterfactualThresholds(x0, xCE, eps)
        if self.compress:
            self.tao = self.compressThresholds(self.tao)

        if self.verbose:
            print(f'Time needed for fitting the discretizers discretizer: {time.time()-t0} seconds')

    def selectThresholds(self, Q):
        threshold_importance = np.quantile(self.tao['Count'], Q)
        return self.tao[self.tao['Count']>=threshold_importance]

    def getCounterfactualThresholds(self, x0, xCE, eps):
        xCE = xCE.loc[x0.index]
        difference = (x0 - xCE).abs()

        tao = pd.DataFrame(columns=['Feature', 'Threshold', 'Count'])
        for i in x0.columns:
            tao_i = pd.DataFrame((xCE[i][difference[i]>eps[i]]).tolist(), columns=['Threshold'])
            tao_i['Feature'] = i
            tao_i['Count'] = 1
            tao = pd.concat((tao,tao_i))
        tao.index = np.arange(len(tao))

        return tao

    def compressThresholds(self, thresholds, tollerance=0.01):

        thresholds['flag'] = np.nan
        thresholds = thresholds.sort_values(['Feature', 'Threshold'])
        for f in thresholds['Feature'].unique():
            thresholds_f = thresholds[thresholds['Feature'] == f]
            mask = (thresholds_f['Threshold'].diff().isna()) | (thresholds_f['Threshold'].diff() > tollerance)
            thresholds_f.loc[mask,'flag'] = np.arange(mask.sum())
            thresholds.loc[thresholds['Feature']==f,'flag'] = thresholds_f['flag'].fillna(method='ffill')

        thresholds = thresholds.groupby(['Feature','flag']).agg({'Threshold':'mean','Count':'count'}).reset_index().drop(columns=['flag'])

        return thresholds

    def getCounterfactualExplanations(self, x0, y0, eps):
        solver = CounterfactualExplanation(self.estimator, lambda0=self.lambda0, lambda1=self.lambda1, lambda2=self.lambda2, eps=eps, timelimit=self.timelimit, verbose=self.verbose)
        xCE, yCE = solver.compute(x0, y0)
        return xCE, yCE

    def getRelevant(self, x, y):
        try:
            index = np.where((self.estimator.predict(x) == y) &
                            (np.max(self.estimator.predict_proba(x), axis=1) >= self.p0) &
                            (np.max(self.estimator.predict_proba(x), axis=1) <= self.p1))[0]
        except:
            index = np.where((self.estimator.predict(x) == y) &
                            (np.max(self.estimator._predict_proba_lr(x), axis=1) >= self.p0) &
                            (np.max(self.estimator._predict_proba_lr(x), axis=1) <= self.p1))[0]
        x_relevant = x.iloc[index]
        y_relevant = y.iloc[index]
        return x_relevant, y_relevant
