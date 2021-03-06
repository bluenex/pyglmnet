# -*- coding: utf-8 -*-
"""
============================
Elastic net regularized GLMs
============================
This is an example demonstrating the internals of glmnet.

Jerome Friedman, Trevor Hastie and Rob Tibshirani. (2010).
Regularization Paths for Generalized Linear Models via Coordinate Descent.
Journal of Statistical Software, Vol. 33(1), 1-22 `[pdf]
<https://core.ac.uk/download/files/153/6287975.pdf>`_.
"""

# Author: Pavan Ramkumar
# License: MIT

import numpy as np
from scipy.special import expit
import scipy.sparse as sps
import matplotlib.pyplot as plt

########################################################
# GLM with elastic net penalty
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Poisson-like GLM
# ----------------
# The `pyglmnet` implementation comes with `poisson`, `binomial`
# and `normal` distributions, but for illustration, we will walk you
# through a particular adaptation of the canonical Poisson generalized
# linear model (GLM).
#
# For the Poisson GLM, :math:`\lambda_i` is the rate parameter of an
# inhomogeneous linear-nonlinear Poisson (LNP) process with instantaneous
# mean given by:
#
# .. math::   \lambda_i = \exp(\beta_0 + \beta^T x_i)
#
# where :math:`x_i \in \mathcal{R}^{p \times 1}, i = \{1, 2, \dots, n\}` are
# the observed independent variables (predictors),
# :math:`\beta_0 \in \mathcal{R}^{1 \times 1}`,
# :math:`\beta \in \mathcal{R}^{p \times 1}`
# are linear coefficients. :math:`\lambda_i` is also known as the conditional
# intensity function, conditioned on :math:`(\beta_0, \beta)` and
# :math:`q(z) = \exp(z)` is the nonlinearity.
#
# For numerical reasons, let's adopt a stabilizing non-linearity, known as the
# softplus or the smooth rectifier `Dugas et al., 2001
# <http://papers.nips.cc/paper/1920-incorporating-second-order-functional-knowledge-for-better-option-pricing.pdf>`_,
# and adopted by Jonathan Pillow's and Liam Paninski's groups for neural data
# analysis.
# See for instance: `Park et al., 2014
# <http://www.nature.com/neuro/journal/v17/n10/abs/nn.3800.html>`_.
#
# .. math::    q(z) = \log(1+\exp(z))
#
# The softplus prevents :math:`\lambda` in the canonical inverse link function
# from exploding when the argument to the exponent is large. In this
# modification, the formulation is no longer an exact LNP, nor an exact GLM,
# but :math:\pm\mathcal{L}(\beta_0, \beta)` is still concave (convex) and we
# can use gradient ascent (descent) to optimize it.
#
# .. math::    \lambda_i = q(\beta_0 + \beta^T x_i) = \log(1 + \exp(\beta_0 +
#                            \beta^T x_i))
#
# [There is more to be said about this issue; ref. Sara Solla's GLM lectures
# concerning moment generating functions and strict definitions of GLMs]

########################################################

# Let's define the conditional intensity function
def qu(z):
    eps = np.spacing(1)
    return np.log(1 + eps + np.exp(z))

def lmb(beta0, beta, x):
    eps = np.spacing(1)
    z = beta0 + np.dot(x, beta)
    return np.log(1 + eps + np.exp(z))

########################################################
#
# Log-likelihood
# ^^^^^^^^^^^^^^
# The likelihood of observing the spike count :math:`y_i` under the Poisson
# likelihood function with inhomogeneous rate :math:`\lambda_i` is given by:
#
# .. math::    \prod_i P(y = y_i) = \prod_i \frac{e^{-\lambda_i} \lambda_i^{y_i}}{y_i!}
#
# The log-likelihood is given by:
#
# .. math::    \mathcal{L} = \sum_i \bigg\{y_i \log(\lambda_i) - \lambda_i
#                            - log(y_i!)\bigg\}
#
# However, we are interested in maximizing the log-likelihood as a function of
# :math:`\beta_0` and :math:`\beta`. Thus, we can drop the factorial term:
#
# .. math::    \mathcal{L}(\beta_0, \beta) = \sum_i \bigg\{y_i \log(\lambda_i)
#                                            - \lambda_i\bigg\}

########################################################
# Elastic net penalty
# ^^^^^^^^^^^^^^^^^^^
# For large models we need to penalize the log likelihood term in order to
# prevent overfitting. The elastic net penalty is given by:
#
# .. math::    \mathcal{P}_\alpha(\beta) = (1-\alpha)\frac{1}{2} \|\beta\|^2_{\mathcal{l}_2} + \alpha\|\beta\|_{\mathcal{l}_1}
#
# The elastic net interpolates between two extremes.
# :math:`\alpha = 0` is known as ridge regression and :math:`\alpha = 1`
# is known as LASSO. Note that we do not penalize the baseline term
# :math:`\beta_0`.

########################################################
# Let's define the penalty term
def penalty(alpha, beta):
    P = 0.5 * (1 - alpha) * np.linalg.norm(beta, 2) + \
        alpha * np.linalg.norm(beta, 1)
    return P

########################################################
