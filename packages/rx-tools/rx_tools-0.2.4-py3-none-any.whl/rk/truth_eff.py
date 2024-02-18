import utils_noroot as utnr
import os

#---------------------------------------
class data:
    log = utnr.getLogger(__name__)
#---------------------------------------
def get_eff(sample, year, trig, version, kind):
    cas_dir   = os.environ['CASDIR']
    file_path = f'{cas_dir}/monitor/truth_eff/{version}/{kind}/{sample}_{trig}_{year}.json'

    data.log.visible(f'Loading truth matching efficiencies from: {file_path}')
    [pas, fal] = utnr.load_json(file_path)
    
    return pas / (pas + fal)
#---------------------------------------

