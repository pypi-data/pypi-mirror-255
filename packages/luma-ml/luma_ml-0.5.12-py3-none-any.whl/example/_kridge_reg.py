import __local__
from luma.regressor.linear import KernelRidgeRegressor
from luma.model_selection.split import TrainTestSplit
from luma.model_selection.search import RandomizedSearchCV
from luma.metric.regression import RSquaredScore
from luma.visual.evaluation import ResidualPlot

import numpy as np
import matplotlib.pyplot as plt

n_samples = 200
np.random.seed(42)

X = np.linspace(-3, 3, n_samples)
y = np.sin(X) + np.random.normal(0, 0.1, n_samples)
y_true = np.sin(X)

X = X.reshape(-1, 1)
indices = np.random.choice(n_samples, n_samples // 3)
y[indices] += np.random.normal(0, 0.5, n_samples // 3)

X_train, X_test, y_train, y_test = TrainTestSplit(X, y).get


param_dist = {'alpha': np.logspace(-3, 1),
              'deg': range(2, 10),
              'gamma': np.logspace(-2, 1),
              'coef': np.logspace(-1, 1),
              'kernel': ['lin', 'poly', 'rbf', 'tanh', 'lap']}

rand = RandomizedSearchCV(estimator=KernelRidgeRegressor(),
                          param_dist=param_dist,
                          max_iter=100,
                          cv=5,
                          metric=RSquaredScore,
                          refit=True,
                          random_state=42)

rand.fit(X_train, y_train)

model = rand.best_model
params = rand.best_params
score = rand.best_score

y_pred = model.predict(X)
label = r'$\alpha=$' + f"{params['alpha']:.4f}\n"
label += r'$\gamma=$' + f"{params['gamma']:.4f}\n"
label += r'$c_0=$' + f"{params['coef']:.4f}\n"
label += r'$d=$' + f"{params['deg']}\n"
label += r'$\kappa=$' + f"'{params['kernel']}'"

fig = plt.figure(figsize=(11, 5))
ax1 = fig.add_subplot(1, 2, 1)
ax2 = fig.add_subplot(1, 2, 2)

ax1.scatter(X_train, y_train, c='dimgray', marker='x', s=20, alpha=0.5)
ax1.scatter(X_test, y_test, c='black', s=20, alpha=0.5)
ax1.plot(X, y_pred, c='dodgerblue', lw=2, label=label)
ax1.plot(X, y_true, c='dodgerblue', ls='--', lw=2, alpha=0.4)
ax1.fill_between(X.flatten(), y_pred, y_true, color='dodgerblue', alpha=0.1)

ax1.set_title('Kernel Ridge Regression [' + r'$R^2=$' + f'{score:.4f}]')
ax1.legend(loc='lower right')

res = ResidualPlot(estimator=model, X=X, y=y)
res.plot(ax2)

plt.tight_layout()
plt.show()
