import utils_noroot as utnr

import os
import pandas as pnd
import tqdm 
#--------------------------------
class event_dictionary:
    log=utnr.getLogger('event_dictionary')
    #--------------------------------
    def __init__(self):
        self._dic_path    = None
        self._dec_dir     = None

        self._initialized = False
    #--------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._dic_path = get_dic_path()
        self._get_pkg_path()

        self._initialized = True
    #--------------------------------
    def _get_pkg_path(self):
        try:
            pkg_dir = os.environ['PKGDIR']
        except:
            self.log.error(f'Cannot retrieve caching directory from PKGDIR')
            raise

        self._dec_dir = f'{pkg_dir}/DecFiles/dkfiles'

        utnr.check_dir(self._dec_dir)
    #--------------------------------
    def _get_str(self, line, info):
        if info not in line:
            return None

        info = line.replace(f'# {info}: ', '')
        info = info.replace('\n', '')

        return info 
    #--------------------------------
    def _get_value(self, dec_path):
        evt = None
        dec = None

        f=open(dec_path)
        l_line=f.read().splitlines()
        for line in l_line:
            tmp = self._get_str(line, 'Descriptor')
            if tmp is not None:
                dec = tmp

            tmp = self._get_str(line, 'EventType')
            if tmp is not None:
                evt = tmp

            if evt is not None and dec is not None:
                return [evt, dec]
    #--------------------------------
    def _print_missing(self, l_missing):
        self.log.warning(f'Cannot extract event type from:')
        for file_name in l_missing:
            print(f'    {file_name}')
    #--------------------------------
    def get(self):
        self._initialize()

        l_dec_path = utnr.glob_wc(f'{self._dec_dir}/*.dec')

        d_data = {}
        l_missing = []
        for dec_path in tqdm.tqdm(l_dec_path, ascii=' -'):
            file_name = os.path.basename(dec_path)
            try:
                value = self._get_value(dec_path)
            except:
                l_missing.append(file_name)
                continue

            d_data[file_name] = value 

        self._print_missing(l_missing)

        self.log.visible(f'Saving to: {self._dic_path}')
        utnr.dump_json(d_data, self._dic_path)

        return d_data
#--------------------------------
class decay_list():
    '''
    Class that takes list of particle names and returns a dataframe with
    the names of the decay files, event types and decay descriptors
    '''
    log=utnr.getLogger('decay_list')
    #--------------------------------
    def __init__(self):
        self._dic_path  = None

        self._initialized = False
    #--------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._dic_path = get_dic_path()

        self._initialized = True
    #--------------------------------
    def _get_decays(self):
        if os.path.isfile(self._dic_path):
            return utnr.load_json(self._dic_path)

        obj   = event_dictionary()
        d_evt = obj.get()

        return d_evt
    #--------------------------------
    def _get_df(self, d_dec):
        d_ref = {'Decay' : [], 'Event' : [], 'Descriptor' : []}

        for dec, [evt, dsc] in d_dec.items():
            dsc = f'\\verb|{dsc}|'

            d_ref['Decay']      += [dec]
            d_ref['Event']      += [evt]
            d_ref['Descriptor'] += [dsc]

        df = pnd.DataFrame(d_ref)

        return df
    #--------------------------------
    def _filter_df(self, df, l_part):
        for part in l_part:
            df = df[df.Decay.str.contains(part)]

        return df
    #--------------------------------
    def get_decays(self, l_part):
        self._initialize()

        d_dec = self._get_decays()
        df = self._get_df(d_dec)
        df = self._filter_df(df, l_part)

        return df
#--------------------------------
def get_dic_path():
    try:
        cas_dir = os.environ['CASDIR']
    except:
        log.error(f'Cannot retrieve chaching directory from CASDIR')
        raise

    dic_dir = utnr.make_dir_path(f'{cas_dir}/decay_finder')

    return f'{dic_dir}/decays.json'
#--------------------------------

