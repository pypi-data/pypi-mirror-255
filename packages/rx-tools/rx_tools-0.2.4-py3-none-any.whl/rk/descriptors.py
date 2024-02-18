from decaylanguage         import DecFileParser
from decaylanguage         import DecayMode 
from decaylanguage         import DaughtersDict 
from decaylanguage.dec.dec import get_branching_fraction

from rk.particle_dictionary import particle_dictionary as pdic

import utils_noroot as utnr
import os 

#-----------------------------------------
class descriptors:
    log=utnr.getLogger('decay_descriptors')
    #---------------------------
    def __init__(self, mother=None, dec_file=None):
        self._mother      = mother
        self._dec_file    = dec_file
        self._lhcb_dec    = 'DECAY_LHCB.DEC'
        self._inp_dir     = None
        self._out_dir     = None
        self._min_py_ver  = (3, 9)
        self._dfp         = None
        self._prefix_path = None
        self._renamer     = None
        self._initialized = False
    #---------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._renamer = pdic()

        try:
            self._inp_dir = os.environ['DECDIR']
        except:
            self.log.error(f'Cannot find "DECDIR" env variable pointing to directory with decay files')
            raise

        utnr.check_python_version(self._min_py_ver)

        utnr.check_none(self._mother)
        utnr.check_none(self._dec_file)

        self._dfp = DecFileParser(f'{self._inp_dir}/{self._lhcb_dec}')
        self._dfp.parse()

        self._set_prefix_path()

        self._initialized = True
    #---------------------------
    def _set_prefix_path(self):
        if self._out_dir is None:
            return

        pref_name=f'{self._mother}_{self._dec_file}'.replace('.dec', '')
        self._prefix_path=f'{self._out_dir}/{pref_name}'
    #---------------------------
    def _convert_to_dic(self, l_m_d): 
        d_m_d = {}
        for mother, l_dau in l_m_d:
            d_m_d[mother] = l_dau

        return d_m_d
    #---------------------------
    def _format_chain(self, d_m_d, mother=None):
        if mother not in d_m_d:
            return None

        l_dau = d_m_d[mother]

        if mother.endswith('sig'):
            mother=mother.replace('sig', '')

        pmother = self._renamer.get_particle_name(evtg_name = mother)

        if len(l_dau) == 1:
            return f'{pmother}'

        tot= f'({pmother}=>'
        for dau in l_dau:
            pdau = self._renamer.get_particle_name(evtg_name = dau)
            dec  = self._format_chain(d_m_d, mother=dau)
            if dec is None:
                tot+= f'{pdau} '
                continue

            tot+= f'{dec} '

        tot+= f')'

        return tot
    #---------------------------
    def _format_decay_chains(self, l_dec):
        l_form_dec = []
        for chain in l_dec:
            d_m_d = self._convert_to_dic(chain)
            chain = self._format_chain(d_m_d, self._mother)
            chain = chain[1 : -1]
            chain = f'[{chain}]CC'

            l_form_dec.append(chain)

        return l_form_dec
    #---------------------------
    def _save_decays(self, l_decay):
        if self._prefix_path is None:
            return

        filepath = f'{self._prefix_path}.json'
        self.log.visible(f'Saving to: {filepath}')
        utnr.dump_json(l_decay, filepath)
    #---------------------------
    @property
    def out_dir(self):
        return self._out_dir

    @out_dir.setter
    def out_dir(self, value):
        self._out_dir = value
    #---------------------------
    def get_descriptors(self, mother_alias=None):
        self._initialize()

        decay_path = f'{self._inp_dir}/{self._dec_file}'

        dfp = DecFileParser(decay_path)
        dfp.parse()
        l_dec = dfp.build_flat_chains(self._mother)

        if len(l_dec) == 0:
            self.log.error(f'No {self._mother} decays found in: {decay_path}')
            raise

        l_dec = self._format_decay_chains(l_dec)

        if mother_alias is not None:
            l_dec = [ chain.replace(self._mother, mother_alias) for chain in l_dec ]

        self._save_decays(l_dec)
    
        return l_dec
    #---------------------------
    def save_match(self, mother_alias=None):
        self._initialize()

        if self._prefix_path is None:
            self.log.error('Output directory not specified')
            raise

        l_decay = self.get_descriptors(mother_alias=mother_alias)

        filepath = f'{self._prefix_path}.txt'
        ofile    = open(filepath, 'w')
        for i_decay, decay in enumerate(l_decay):
            line=f'd_match[\'dec_{i_decay:03d}\'] = \"switch( MCMATCH(\'{decay:120}\', \'Relations/Rec/ProtoP/Charged\' ), 1, 0 )\"'
            ofile.write(f'{line}\n')
        ofile.close()
#-----------------------------------------

