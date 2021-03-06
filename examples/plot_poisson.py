# -*- coding: utf-8 -*-
"""
============================
GLM for Poisson distribution
============================
This is an example demonstrating how Pyglmnet works.

"""

# Author: Pavan Ramkumar
# License: MIT

import numpy as np
from sklearn.preprocessing import StandardScaler
import scipy.sparse as sps
from scipy.special import expit
import matplotlib.pyplot as plt

########################################################
# Here are inputs that you can provide when you instantiate the `GLM` class.
# If not provided, it will be set to the respective defaults
#
# - `distr`: str, `'poisson'` or `'normal'` or `'binomial'` or `'multinomial'`
#     default: `'poisson'`
# - `alpha`: float, the weighting between L1 and L2 norm, default: 0.5
# - `reg_lambda`: array, array of regularized parameters,
#     default: `np.logspace(np.log(0.5), np.log(0.01), 10, base=np.exp(1))`
# - `learning_rate`: float, learning rate for gradient descent,
#     default: 1e-4
# - `max_iter`: int, maximum iteration for the model, default: 100

########################################################

# import GLM model
from pyglmnet import GLM

# create regularize parameters for model
reg_lambda = np.logspace(np.log(0.5), np.log(0.01), 10, base=np.exp(1))
model = GLM(distr='poisson', verbose=False, alpha=0.05,
            max_iter=1000, learning_rate=1e-4,
            reg_lambda=reg_lambda)

##########################################################
# Simulate a dataset
# ------------------
# The ``GLM`` class has a very useful method called ``simulate()``.
#
# Since a canonical link function is already specified by the distribution
# parameters, or provided by the user, ``simulate()`` requires
# only the independent variables ``X`` and the coefficients ``beta0``
# and ``beta``
