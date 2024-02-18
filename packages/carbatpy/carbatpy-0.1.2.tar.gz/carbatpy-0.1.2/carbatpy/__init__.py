"""Top-level package for carbatpy."""

__author__ = """Burak Atakan"""
__email__ = 'burak.atakan@uni-due.de'
__version__ = '0.1.2'

# __all__ =[]
import os
import sys

sys.path.insert(0,os.path.abspath('../carbatpy'))
sys.path.insert(0,os.path.abspath('..'))

try:
    from cb_config import _T_SURROUNDING, _RESULTS_DIR, _P_SURROUNDING
except:
    from .cb_config import _T_SURROUNDING, _RESULTS_DIR, _P_SURROUNDING
    


import src.models as models
import src.utils as utils
import src.helpers as helpers


from src.utils import exergy_loss as exlo
from src.helpers import file_copy

from src.models.fluids import fluid_props as fprop

from src.models.components import compressor_simple, throttle_simple
from src.models.components import heat_exchanger_thermo_v2 as hex_th

from src.models.coupled import heat_pump_simple_v2 as hp_simple
from src.models.coupled import orc_simple_v2 as orc_simple
from src.models.coupled import read_cycle_structure
from src.utils import curve_min_distance_finder, property_eval_mixture, optimize

