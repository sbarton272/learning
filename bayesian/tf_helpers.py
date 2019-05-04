import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set()

import tensorflow as tf
print(tf.__version__)
import tensorflow_probability as tfp
tfd = tfp.distributions

tf.enable_eager_execution()
print(f'Setup tf eager: {tf.executing_eagerly()}')

def eval_tensor(tensors):
    """
    https://nbviewer.jupyter.org/github/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers/blob/master/Chapter1_Introduction/Ch1_Introduction_TFP.ipynb
    
    
    Evaluates Tensor or EagerTensor to Numpy `ndarray`s.
    Args:
    tensors: Object of `Tensor` or EagerTensor`s; can be `list`, `tuple`,
      `namedtuple` or combinations thereof.
 
    Returns:
      ndarrays: Object with same structure as `tensors` except with `Tensor` or
        `EagerTensor`s replaced by Numpy `ndarray`s.
    """
    arrays = [t.numpy() if tf.contrib.framework.is_tensor(t) else t for t in tf.contrib.framework.nest.flatten(tensors)]
    return tf.contrib.framework.nest.pack_sequence_as(tensors, arrays)