import utils_noroot as utnr
import os

from importlib.resources import files
from logzero             import logger as log

#------------------------------
def get_evt_dec():
    evt_dsc_path = files('tools_data').joinpath('evt_dsc.json')
    if not os.path.isfile(evt_dsc_path):
        log.error(f'File {evt_dsc_path} not found, run make_evt_dsc')
        raise FileNotFoundError

    d_evt_dsc = utnr.load_json(evt_dsc_path)

    return d_evt_dsc
#------------------------------
class data:
    d_evt_dec = get_evt_dec()
#------------------------------
def get_decay_from_evt(evt):
    evt = str(evt)

    if evt not in data.d_evt_dec:
        log.warning(f'Cannot find {evt}')
        return evt

    decay = data.d_evt_dec[evt]

    return decay
#------------------------------

