#!/usr/bin/env python3
#
# main.py: main script for testing Persistent Weisfeiler--Lehman graph
# kernels.


import igraph as ig
import numpy as np

import argparse
import collections
import logging

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

from tqdm import tqdm

from features import FeatureSelector
from features import PersistentWeisfeilerLehman

def read_labels(filename):
    labels = []
    with open(filename) as f:
        labels = f.readlines()
        labels = [label.strip() for label in labels]

    return labels


def main(args, logger):

    graphs = [ig.read(filename) for filename in args.FILES]
    labels = read_labels(args.labels)

    logger.debug('Read {} graphs and {} labels'.format(len(graphs), len(labels)))

    assert len(graphs) == len(labels)

    y = np.array(labels)
    X, num_columns_per_iteration = PersistentWeisfeilerLehman().transform(graphs,
                                                                          args.num_iterations)

    np.random.seed(42)
    cv = StratifiedKFold(n_splits=10, shuffle=True)
    mean_accuracies = []

    for i in range(10):

        # Contains accuracy scores for each cross validation step; the
        # means of this list will be used later on.
        accuracy_scores = []

        for train_index, test_index in cv.split(X, y):
            rf_clf = RandomForestClassifier(n_estimators=50)

            if args.grid_search:
                pipeline = Pipeline(
                    [
                        ('fs', FeatureSelector(num_columns_per_iteration)),
                        ('clf', rf_clf)
                    ]
                )

                grid_params = {
                    'fs__num_iterations': np.arange(0, args.num_iterations + 1),
                    'clf__n_estimators': [10, 20, 50, 100, 150, 200]
                }
                # FIXME: replace...

                clf = GridSearchCV(pipeline, grid_params, cv=StratifiedKFold(n_splits=10, shuffle=True), iid=False, scoring='accuracy', n_jobs=16)

            else:
                clf = rf_clf

            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]

            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)

            accuracy_scores.append(accuracy_score(y_test, y_pred))

            logger.info(clf)
        logger.info('  - Mean 10-fold accuracy: {:2.2f}'.format(np.mean(accuracy_scores)))
        mean_accuracies.append(np.mean(accuracy_scores))

    logger.info('Accuracy: {:2.2f} +- {:2.2f}'.format(np.mean(mean_accuracies) * 100, np.std(mean_accuracies) * 100))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('FILES', nargs='+', help='Input graphs (in some supported format)')
    parser.add_argument('-d', '--dataset', help='Name of data set')
    parser.add_argument('-l', '--labels', type=str, help='Labels file', required=True)
    parser.add_argument('-n', '--num-iterations', default=3, type=int, help='Number of Weisfeiler-Lehman iterations')
    parser.add_argument('-f', '--filtration', type=str, default='sublevel', help='Filtration type')
    parser.add_argument('-g', '--grid-search', type=bool, default=False, help='Whether to do hyperparameter grid search')

    args = parser.parse_args()
    
    logging.basicConfig(level=logging.DEBUG, filename='{}_{}.log'.format(args.dataset, args.num_iterations))
    logger = logging.getLogger('P-WL')

    main(args, logger)
