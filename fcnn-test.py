import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import tensorflow as tf
from keras.models import save_model
import json
import os
import sys

#retrieves second argument "python fccn-test.py [fname]"
try:
    fname = sys.argv[1]
except IndexError:
    print("No filename specified.")

#reads data from csv
def read_data(fname):
    input_data = pd.read_csv("./" + fname + ".csv")
    input_data = input_data.values

    #confirm correct shape for data
    print(input_data.shape)

    #randomizes order of data
    #fixed seed is for testing purposes
    np.random.seed(1234)
    np.random.shuffle(input_data)

    #split into 70% training and 30% testing
    nrows = input_data.shape[0]
    ntrain = round(0.7 * nrows)

    train_x = input_data[:ntrain,:-1]
    train_y = input_data[:ntrain,-1]
    test_x = input_data[ntrain:,:-1]
    test_y = input_data[ntrain:,-1]

    return train_x, train_y, test_x, test_y

#used to normalize training data
def normalize_data(dataset):
    mu = np.mean(dataset, axis = 0)
    sigma = np.std(dataset, axis = 0)

    return (dataset - mu)/sigma, mu, sigma

#used to normalize testing data
def normalize_test(dataset, mu, sigma):
    return (dataset - mu)/sigma

####
#add in machine learning parts here

