#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: hg3n
"""

from sklearn import svm, metrics
import numpy as np


class Recognizer:
    def __init__(self, datasets=None):
        """
        c'tor
        :param datasets:
        """
        # create classifier
        self.classifier = svm.SVC(gamma=0.001, probability=True)

        # initialize if dataset is available
        if datasets != None:
            self.initialize(datasets)

    def initialize(self, datasets):
        """
        initialize shape detector, shaping the data, learning according to input datasets
        :param datasets:
        :return:
        """
        self.datasets = datasets
        images = join_datasets([d.images for d in datasets])
        targets = join_datasets([d.targets for d in datasets])

        # determine number of samples
        n_samples = len(images)

        # reshape data
        data = images.reshape((n_samples, -1))
        # learn from dataset
        self.classifier.fit(data, targets)

    def old_predict(self, targets):
        """
        predict input targets using svc's predict function
        :param targets:
        :return:
        """
        print(type(targets[0]))

        return self.classifier.predict(targets)

    def predict(self, targets_to_predict):
        """
        predict input targets using svc's predict function
        :param targets:
        :return:
        """
        # predict target probabilities
        probabilities = self.classifier.predict_proba(targets_to_predict)
        classes = self.classifier.classes_

        # build return dict containing
        result = {}
        for cl, pr in zip(classes, probabilities[0]):
            result[cl] = pr

        return result

    def report(self, targets, results):
        """
        returns the classifier and a generated classification report
        :param targets: input list of targets to predict (need to be learned first)
        :param results: input list of predicted elements
        :return:
        """
        report = metrics.classification_report(targets, results)
        return self.classifier, report


def join_datasets(datasets):
    """
    join datasets into one
    :param datasets:
    :return:
    """
    first = datasets[0]
    for i in range(1, len(datasets)):
        first += datasets[i]
    return np.asarray(first)
