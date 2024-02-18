import utils_noroot as utnr

from rk.efficiency import cutflow

#-------------------------------------------
class merger:
    log=utnr.getLogger(__name__)
    #-----------------------
    def __init__(self):
        self._initialized = False

        self._l_lm_cf = []
    #-----------------------
    def _initialize(self):
        if self._initialized:
            return

        if len(self._l_lm_cf) != 2:
            self.log.error(f'Could not find exactly two elements in container of luminosities and cutflows')
            print(self._l_lm_cf)
            raise

        [(cf_1, _), (cf_2, _)] = self._l_lm_cf

        try:
            cf_3 = cf_1 + cf_2
        except:
            self.log.error(f'Cutflows cannot be added, not compatible.')
            print(cf_1.df_eff)
            print(cf_2.df_eff)
            raise

        self._initialized = True
    #-----------------------
    def add_input(self, cf, lumi, stats=None):
        utnr.check_type(lumi, float)
        utnr.check_type(cf  , cutflow)

        if stats is not None:
            utnr.check_type(stats, int)
            cf.stats = stats

        self._l_lm_cf.append((cf, lumi))
    #-----------------------
    def _get_org_yld(self, cf):
        if hasattr(cf, 'stats'):
            self.log.debug(f'Picking up attached yield: {cf.stats}')
            return cf.stats

        self.log.warning('Extracting yield from cutflow')
        (cut, eff) = list(cf.items())[0]

        yld = eff.pas + eff.fal

        self.log.debug(f'Total yield for {cut}: {yld:>20.0f} = {eff.pas:>20.0f} + {eff.fal:>20.0f}')

        return yld
    #-----------------------
    def _weight_cutflow(self, cf, wgt):
        self.log.info(f'Weighting cutflow with: {wgt:.3f}')

        cf_rwt = cutflow()
        for cut, eff in cf.items():
            eff         = eff.scale(wgt)
            cf_rwt[cut] = eff

        return cf_rwt
    #-----------------------
    def _get_weighted_average(self):
        [(cf_1, lm_1), (cf_2, lm_2)] = self._l_lm_cf

        org_yld_1 = self._get_org_yld(cf_1)
        org_yld_2 = self._get_org_yld(cf_2)

        tot_yld   = org_yld_1 + org_yld_2

        wgt_sta_1 = org_yld_2 / tot_yld
        wgt_sta_2 = org_yld_1 / tot_yld

        tot_lum   = lm_1 + lm_2

        wgt_lum_1 = lm_1 / tot_lum
        wgt_lum_2 = lm_2 / tot_lum

        wgt_tot_1 = wgt_sta_1 * wgt_lum_1
        wgt_tot_2 = wgt_sta_2 * wgt_lum_2

        cf_1 = self._weight_cutflow(cf_1, wgt_tot_1)
        cf_2 = self._weight_cutflow(cf_2, wgt_tot_2)

        cf_3 = cf_1 + cf_2

        return cf_3
    #-----------------------
    def get_cutflow(self, kind=None):
        self._initialize()

        if   kind == 'sum':
            [(cf_1, _), (cf_2, _)] = self._l_lm_cf
            cf_3 = cf_1 + cf_2
        elif kind == 'weighted':
            cf_3 = self._get_weighted_average()
        else:
            self.log.error(f'Invalid merge kind: {kind}')
            raise

        return cf_3 
#-------------------------------------------

