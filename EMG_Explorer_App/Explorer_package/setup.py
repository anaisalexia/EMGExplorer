import h5py
import os
import sys
import inspect
import importlib
from pathlib import Path
import subprocess
import sys
import json
import logging
from datetime import datetime


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
from PyQt5.QtWidgets import QListWidgetItem, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

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
PATH_QT_UI = 'EMG_Explorer_App/QT_Ui/Layouts/'


PATH_PIPELINE = 'EMG_Explorer_App/Explorer_package/processing_pipelines/'
PATH_GLOBAL_PIPELINE = 'EMG_Explorer_App/Explorer_package/global_processing_pipelines/'
PAHT_LOG = 'EMG_Explorer_App/Log/'

ROOT = 'EMG_Explorer_App\Explorer_package\processing'
ROOT_PROCESSINGGLOBAL = 'EMG_Explorer_App\Explorer_package\global_processing'
ROOT_MEASUREMENT = 'EMG_Explorer_App\Explorer_package\summary_measurement'
ROOT_DISPLAY = 'EMG_Explorer_App\Explorer_package\summary_display'
ROOT_RANGEDISPLAY = 'EMG_Explorer_App\Explorer_package\summary_rangeDisplay'
ROOT_GLOBALPROCESSING = 'EMG_Explorer_App\Explorer_package\global_processing_pipelines'


ROOT_REPORT = "EMG_Explorer_App/Explorer_package/global_processing_pipelines/"
DEFAULT_PATH_SAVE_SUMMARY = 'EMG_Explorer_App/Template/template'

ROOT_TEMPLATE = r"EMG_Explorer_App/Template/template/templateSummary.html"

# from .processing_function import MEASUREMENT,MEASUREMENT_NAME,DISPLAY,DISPLAY_NAME,PROCESSING,PROCESSING_NAME




