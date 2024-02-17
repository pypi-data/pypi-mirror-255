from os.path import dirname, abspath
import sys

from hestia_earth.models.utils import _run_in_serie
from . import site, startDate, cache_sources

CURRENT_DIR = dirname(abspath(__file__)) + '/'
sys.path.append(CURRENT_DIR)

MODELS = [
    site.run,
    startDate.run,
    cache_sources.run
]


def run(data: dict): return _run_in_serie(data, MODELS)
