import __local__
from luma.preprocessing.scaler import StandardScaler
from luma.preprocessing.outlier import LocalOutlierFactor
from luma.model_selection.split import TrainTestSplit
from luma.reduction.select import SBS
from luma.regressor.linear import RidgeRegressor, KernelRidgeRegressor
from luma.pipe.pipeline import Pipeline
from luma.metric.regression import RootMeanSquaredError
from luma.visual.evaluation import ResidualPlot

from sklearn.datasets import load_diabetes


X, y = load_diabetes(return_X_y=True)

X_train, X_test, y_train, y_test = TrainTestSplit(X, y, 
                                                  test_size=0.2,
                                                  random_state=42).get

param_dict = {'sbs__estimator': RidgeRegressor(),
              'sbs__n_features': 2,
              'sbs__metric': RootMeanSquaredError,
              'sbs__random_state': 42,
              'lof__threshold': 1.5,
              'k_ridge__gamma': 1.0,
              'k_ridge__kernel': 'rbf'}

pipe = Pipeline(models=[('sc', StandardScaler()),
                        ('lof', LocalOutlierFactor()),
                        ('sbs', SBS()),
                        ('k_ridge', KernelRidgeRegressor())],
                param_dict=param_dict)

pipe.fit(X_train, y_train)

res = ResidualPlot(pipe.estimator, *pipe.transform(X_test, y_test))
res.plot(show=True)
