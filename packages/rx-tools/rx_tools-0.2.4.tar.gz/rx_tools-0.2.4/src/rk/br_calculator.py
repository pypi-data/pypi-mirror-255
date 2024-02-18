from decaylanguage import DecFileParser
from decaylanguage import DecayMode 
from decaylanguage import DaughtersDict 

from decaylanguage.dec.dec import get_branching_fraction

import utils_noroot as utnr
import pandas       as pnd
import tqdm
import os 

#-----------------------------------------
class br_calculator:
    output_dir = None
    input_dir  = None

    log=utnr.getLogger(__name__)
    #---------------------------
    def __init__(self, mother=None, dec_file=None):
        self._mother   = mother
        self._dec_file = dec_file
        self._lhcb_dec = 'DECAY_LHCB.DEC'
        self._min_py_ver=(3, 9)
        self._dfp      = None
        pnd.options.display.float_format = '${:,.3e}'.format

        self._initialized = False
    #---------------------------
    def _initialize(self):
        if self._initialized:
            return

        try:
            self.input_dir = os.environ['DECDIR']
        except:
            self.log.error(f'Cannot find "DECDIR" env variable pointing to directory with decay files')
            raise

        utnr.make_dir_path(self.output_dir)

        utnr.check_python_version(self._min_py_ver)

        utnr.check_none(self._mother)
        utnr.check_none(self._dec_file)

        self._dfp = DecFileParser(f'{self.input_dir}/{self._lhcb_dec}')
        self._dfp.parse()

        self._initialized = True
    #---------------------------
    def get_br(self):
        self._initialize()

        decay_path = f'{self.input_dir}/{self._dec_file}'
        l_chain    = self._get_decay_chains(decay_path)

        bf = 0
        suffix = self._dec_file.replace('.dec', '')
        suffix = f'{suffix}_{self._mother}'

        dir_path = utnr.make_dir_path(f'{self.output_dir}/{suffix}')
        ofile=open(f'{dir_path}/decays.txt', 'w')
        for i_chain, chain in enumerate(tqdm.tqdm(l_chain, ascii=' -')):
            bf += self._get_chain_bf(i_chain, chain, suffix)

            ofile.write(str(chain) + '\n')
        ofile.close()

        return bf
    #-----------------------------------------
    def _get_decay_chains(self, dec_path):
        dfp = DecFileParser(dec_path)
        dfp.parse()
        l_dec = dfp.build_flat_chains(self._mother)
    
        return l_dec
    #-----------------------------------------
    def _get_chain_bf(self, i_chain, chain, suffix):
        l_decay = []
        l_bf    = []
    
        tot     = 1
        for (mother, l_dau) in chain:
            decay = f'{mother}->{l_dau}'

            if mother.endswith('sig'):
                mother = mother[:-3]
            bf = self._get_dau_bf(mother, l_dau)
    
            l_decay.append(decay)
            l_bf.append(bf)
    
            tot *= bf
    
        l_decay.append('Total')
        l_bf.append(tot)
    
        df=pnd.DataFrame({'Decay': l_decay, 'Branching Fraction' : l_bf})
        txt = df.to_latex(index=False)
    
        dir_path = utnr.make_dir_path(f'{self.output_dir}/{suffix}')
    
        ofile=open(f'{dir_path}/decay_{i_chain:03}.tex', 'w')
        ofile.write(txt)
        ofile.close()
    
        return tot 
    #-----------------------------------------
    def _get_dau_bf(self, mother, l_dau):
        l_dm = self._dfp.get_decay_modes(mother)
    
        val = None
        for (bf, l_lhcb_dau, _, _) in l_dm:
            if l_dau == l_lhcb_dau:
                val = bf
                break
    
        if val is None:
            self.log.error(f'Could not find {l_dau} among daughters of {mother}')
            raise
    
        return val
#-----------------------------------------

