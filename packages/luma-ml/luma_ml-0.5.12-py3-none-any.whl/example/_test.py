import __local__
from luma.reduction.linear import KDA
from luma.classifier.discriminant import QDAClassifier, KDAClassifier
from luma.ensemble.vote import VotingClassifier
from luma.visual.evaluation import DecisionRegion

from sklearn.datasets import load_iris


X, y = load_iris(return_X_y=True)

kda = KDA(n_components=2,
          gamma=0.1,
          kernel='rbf')

X = kda.fit_transform(X, y)

vote = VotingClassifier(estimators=[QDAClassifier(),
                                    KDAClassifier(gamma=10, kernel='rbf')],
                        voting='label',
                        weights=[0.2, 0.8],
                        verbose=True)

vote.fit(X, y)

dec = DecisionRegion(vote, X, y,
                     title="Voting Classifier (QDA: 0.2, KDA: 0.8) " +\
                         f"[Acc: {vote.score(X, y):4f}]")

dec.plot(show=True)
