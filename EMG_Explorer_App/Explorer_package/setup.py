import h5py
import os
import inspect
import importlib
from pathlib import Path
import subprocess
import sys
import json
import logging


from scipy import signal
import numpy as np
import pandas as pd

import pyqtgraph as pg
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree

from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QListWidgetItem

from matplotlib.figure import Figure
from PyQt5.uic import loadUi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg,NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QToolButton
from pyqtgraph.parametertree import Parameter, ParameterTree, parameterTypes, registerParameterItemType,registerParameterType

from qtpy import QtGui, QtCore,QtWidgets
from qtpy.QtWidgets import *

from functools import partial,wraps

import xarray as xr
from datatree import DataTree
import datatree
from abc import ABC, abstractmethod

from jinja2 import Template

# CONSTANT
PATH_PIPELINE = 'EMG_Explorer_App/Explorer_package/processing pipelines/'
PATH_GLOBAL_PIPELINE = 'EMG_Explorer_App/Explorer_package/global_processing_pipelines/'

from .processing_function import MEASUREMENT,MEASUREMENT_NAME,DISPLAY,DISPLAY_NAME,PROCESSING,PROCESSING_NAME




