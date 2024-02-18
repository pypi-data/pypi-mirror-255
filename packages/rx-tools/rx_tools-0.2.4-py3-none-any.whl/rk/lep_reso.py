import numpy
import math
import pandas            as pnd
import utils_noroot      as utnr
import matplotlib.pyplot as plt

from data_splitter import splitter as dsplit

#----------------------------
class calculator:
    log = utnr.getLogger('lep_reso')
    #----------------------------------
    def __init__(self, data=None, binning=None):
        self._rdf     = data
        self._binning = binning

        self._plot_dir= None
        self._suffix  = None

        self._initialized = False
    #----------------------------------
    @property
    def plot_dir(self):
        return self._plot_dir

    @plot_dir.setter
    def plot_dir(self, value):
        self._plot_dir = utnr.make_dir_path(value) 
    #----------------------------------
    def _get_data(self):
        rdf = self._rdf
        rdf = rdf.Filter('TMath::Abs(L1_TRUEID) == 11')
        rdf = rdf.Filter('TMath::Abs(L2_TRUEID) == 11')

        rdf = rdf.Define('L1_TRUE_P'  , 'TVector3 l1(L1_TRUEP_X, L1_TRUEP_Y, L1_TRUEP_Z); return l1.Mag();')
        rdf = rdf.Define('L2_TRUE_P'  , 'TVector3 l2(L2_TRUEP_X, L2_TRUEP_Y, L2_TRUEP_Z); return l2.Mag();')
        rdf = rdf.Define('L1_TRUE_ETA', 'TVector3 l1(L1_TRUEP_X, L1_TRUEP_Y, L1_TRUEP_Z); return l1.Eta();')
        rdf = rdf.Define('L2_TRUE_ETA', 'TVector3 l2(L2_TRUEP_X, L2_TRUEP_Y, L2_TRUEP_Z); return l2.Eta();')
        rdf = rdf.Redefine('L1_HasBremAdded', 'int(L1_HasBremAdded)')
        rdf = rdf.Redefine('L2_HasBremAdded', 'int(L2_HasBremAdded)')

        d_lep1 = rdf.AsNumpy(['L1_P', 'L1_ETA', 'L1_TRUE_P', 'L1_TRUE_ETA', 'L1_HasBremAdded'])
        d_lep2 = rdf.AsNumpy(['L2_P', 'L2_ETA', 'L2_TRUE_P', 'L2_TRUE_ETA', 'L2_HasBremAdded'])

        df_1 = pnd.DataFrame(d_lep1) 
        df_2 = pnd.DataFrame(d_lep2) 

        df_1.columns= ['p', 'eta', 'tp', 'teta', 'brem']
        df_2.columns= ['p', 'eta', 'tp', 'teta', 'brem']

        df = pnd.concat([df_1, df_2])
        df = df.reset_index(drop=True)

        return df 
    #----------------------------------
    def _get_resolution(self, df, bound):
        size = df.shape[0]

        p =df.p.to_numpy()
        tp=df.tp.to_numpy()

        dp = p - tp
        i_size = dp.size
        l_dp = utnr.remove_outliers(dp, l_zscore=[4, 4, 3])
        dp   = numpy.array(l_dp)
        f_size = dp.size

        if size > 0:
            rms2 = numpy.sum( dp ** 2 ) / size
        else:
            rms2 = math.nan

        rms  = math.sqrt(rms2)

        minp, maxp = bound
        self.log.info(f'{size:<20}{minp:<10.0f}{maxp:<10.0f}{rms:<20.0f}{i_size:<20}{f_size:<20}')

        if self._plot_dir is not None:
            self._plot_dist(dp, minp, maxp, rms)

        return rms
    #----------------------------------
    def _get_bounds(self):
        l_val = self._binning['p']
        size  = len(l_val)

        l_bound  = [ (- math.inf  ,         l_val[0]) ]
        l_bound += [ (l_val[index], l_val[index + 1]) for index in range(size - 1) ]
        l_bound += [ (l_val[-1]   ,         math.inf) ]

        return l_bound
    #----------------------------------
    def _plot_brem(self, d_res, label=None, ax=None):
        l_mom = [ (high + low) / 2.    for low, high in d_res ]
        l_err = [ (high - low) / 2.    for low, high in d_res ]
        l_res = [ 2 * res/(high + low) for (low, high), res in d_res.items() ]

        ax.errorbar(l_mom, l_res, xerr=l_err, marker='o', linestyle='None', label=label)
    #----------------------------------
    def _plot_reso(self, d_res_0, d_res_1):
        fig = plt.figure()
        ax  = fig.add_subplot(111)

        self._plot_brem(d_res_0, 'No brem', ax)
        self._plot_brem(d_res_1,    'Brem', ax)

        plt.ylabel('$\sigma(p)/p$')
        plt.legend()
        plt.savefig(f'{self._plot_dir}/resolution.png')
        plt.close('all')
    #----------------------------------
    def _plot_dist(self, dp, minp, maxp, sg):
        if dp.size == 0:
            return

        mu = numpy.mean(dp)

        plt.hist(dp, range=(mu-4*sg, mu+4*sg), alpha=0.7, bins=30, label='$p_{reco} - p_{true}$')
        plt.axvline(x=mu - sg, color='red', label='$\mu-\sigma$', linestyle='-')
        plt.axvline(x=mu + sg, color='red', label='$\mu+\sigma$', linestyle='-')
        plt.legend()
        plt.title(f'$p\in${minp:.0f}[MeV]-{maxp:.0f}[MeV]')

        plt.savefig(f'{self._plot_dir}/{self._suffix}/dist_{minp:.0f}_{maxp:.0f}.png')
        plt.close('all')
    #----------------------------------
    def _check_sizes(self, l_df, l_bound):
        size_df = len(l_df)
        size_bn = len(l_bound)

        if size_df != size_bn:
            self.log.error(f'Sizes of bounds and dataframe list differ: {size_bn}/{size_df}')
            raise
    #----------------------------------
    def get_resolution(self):
        df      = self._get_data()

        df_0    = df[df.brem == 0]
        df_1    = df[df.brem == 1]

        d_res_0 = self._calculate(df_0, 'nobrem')
        d_res_1 = self._calculate(df_1, 'brem')

        if self._plot_dir is not None:
            self._plot_reso(d_res_0, d_res_1)

        d_res_0 = {str(key) : val for key, val in d_res_0.items()}
        d_res_1 = {str(key) : val for key, val in d_res_1.items()}

        return d_res_0, d_res_1
    #----------------------------------
    def _calculate(self, df, suffix):
        self._suffix = suffix
        utnr.make_dir_path(f'{self._plot_dir}/{self._suffix}')

        self.log.info(f'Calculating {suffix} resolutions')

        obj     = dsplit(df, self._binning, spectators=['eta', 'tp', 'teta'])
        l_df    = obj.get_datasets()
        l_bound = self._get_bounds()

        self._check_sizes(l_df, l_bound)

        self.log.info(f'{"Dataset size":<20}{"Low":<10}{"High":<10}{"RMS [MeV]":<20}{"Original":<20}{"Filtered":<20}')
        d_res = { bound : self._get_resolution(df, bound) for df, bound in zip(l_df, l_bound) }

        return d_res
#----------------------------

