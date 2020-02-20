from IPython.display import Image
from IPython import get_ipython

ipython = get_ipython()
ipython.magic('matplotlib inline')
ipython.magic('load_ext autoreload')
ipython.magic('autoreload 2')

from functools import partial
from pathlib import Path
import subprocess as sp
import pickle as pkl
import warnings
import shutil
import yaml
import os

from statsmodels.iolib.smpickle import load_pickle
from matplotlib.ticker import FormatStrFormatter
from matplotlib.ticker import MaxNLocator
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import matplotlib as mpl
import pygraphviz as pgv
import numpy.ma as ma
import seaborn as sns
import pandas as pd
import numpy as np

import respy as rp

pd.set_option('display.max_rows', 500)

from config import ABILITY_LABELS_EXT
from config import ABILITY_LABELS
from config import DIR_FIGURES
from config import OV_PROJECT
