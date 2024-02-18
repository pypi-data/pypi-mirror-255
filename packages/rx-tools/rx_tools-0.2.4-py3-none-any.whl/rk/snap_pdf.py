import zfit
import logzero

from logzero import logger as log

#----------------------------
class snap_pdf: 
    def __init__(self, pdf):
        self._pdf = pdf 

        self._log_level = logzero.INFO
        self._d_snap    = {} 

        self._initialized = False
    #----------------------------
    def _initialize(self):
        if self._initialized:
            return

        log.setLevel(self._log_level)

        self._initialized = True
    #----------------------------
    @property
    def log_level(self):
        return self._log_level

    @log_level.setter
    def log_level(self, value):
        self._log_level = value
        log.setLevel(self._log_level)
    #----------------------------
    def save(self, name):
        if name in self._d_snap:
            log.error(f'Snapshot with name "{name}" already taken')
            raise ValueError

        self._d_snap[name] = self._get_snapshot()
    #----------------------------
    def load(self, name):
        if name not in self._d_snap:
            log.error(f'Snapshot with name "{name}" not found')
            raise ValueError

        d_par = self._d_snap[name]

        self._set_snapshot(d_par)
    #----------------------------
    def _get_snapshot(self):
        s_par_flt = self._pdf.get_params(floating= True)
        s_par_fix = self._pdf.get_params(floating=False)

        d_par = {}
        for par in s_par_flt:
            d_par[par.name] = par.value().numpy(),  True

        for par in s_par_fix:
            d_par[par.name] = par.value().numpy(), False 

        log.debug(f'{"Name":<20}{"Value":<20.3}{"Floating"}')
        for name, (val, fix) in d_par.items():
            log.debug(f'{name:<20}{val:<20.3}{fix}')

        return d_par
    #----------------------------
    def _set_snapshot(self, d_par):
        s_par_flt = self._pdf.get_params(floating= True)
        s_par_fix = self._pdf.get_params(floating=False)

        s_par_all = set()
        s_par_all = s_par_all.union(s_par_flt, s_par_fix)

        log.debug(f'{"Name":<20}{"Value":<20}{"Floating":<20}')
        for par in s_par_all:
            if par.name not in d_par:
                log.error(f'Cannot find parameter "{par.name}" in snapshot')
                log.error(d_par)
                raise ValueError

            val, is_floating = d_par[par.name]

            par.set_value(val)
            par.floating = is_floating

            log.debug(f'{par.name:<20}{val:<20.3}{is_floating:<20}')
#----------------------------

