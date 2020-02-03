import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import tensorflow as tf
from keras.models import save_model
import json
import os
import sys

def read_data(fname):
    input_data = pd.read_csv("./" + fname + ".csv")
    
