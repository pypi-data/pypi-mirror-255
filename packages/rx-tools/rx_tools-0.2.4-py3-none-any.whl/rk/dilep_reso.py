import numpy
import re
import math
import logging
import pandas            as pnd
import utils_noroot      as utnr
import matplotlib.pyplot as plt
import zutils.utils      as zut

from fitter        import zfitter
from rk.boundaries import boundaries

from data_splitter import splitter  as dsplit
from zutils.plot   import plot      as zfp
from zutils.pdf    import SUJohnson as zpdf_jh

import zfit

#----------------------------
class calculator:
    log = utnr.getLogger('lep_reso')
    #----------------------------------
    def __init__(self, data=None, binning=None, fit=False, d_par={}, signal='dscb', l_ibin=[]):
        self._rdf         = data
        self._binning     = binning
        self._jpsi_mass   = 3097
        self._nsam_var    = 10000
        self._fit         = fit
        self._d_par       = d_par
        self._d_dat_res   = {}
        self._signal      = signal
        self._l_ibin      = l_ibin

        self._plot_dir    = None
        self._suffix      = None
        self._is_mc       = None

        self._obs         = zfit.Space('mass', limits=(2450, 3600))
        self._mu          = zfit.Parameter('mu', 3000,  3000, 3100)
        self._sg          = zfit.Parameter('sg',   40,    10,  120)
        self._sig_pdf     = None
        self._bkg_pdf     = None

        self._initialized = False
    #----------------------------------
    @property
    def plot_dir(self):
        return self._plot_dir

    @plot_dir.setter
    def plot_dir(self, value):
        self._plot_dir = utnr.make_dir_path(value) 
    #----------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._cast_ibin()

        zfit.settings.changed_warnings.hesse_name = False

        v_name = self._rdf.GetColumnNames()
        l_name = [ name.c_str() for name in v_name ]
        self._is_mc = 'Jpsi_TRUEID' in l_name

        self._initialized = True
    #----------------------------------
    def _cast_ibin(self):
        try:
            self._l_ibin = [ int(ibin) for ibin in self._l_ibin ]
        except:
            self.log.error(f'Cannnot transform index of bins to index of int:')
            self.log.error(self._l_ibin)
            raise

        if len(self._l_ibin) > 0:
            self.log.info(f'Fitting only bins: {self._l_ibin}')
    #----------------------------------
    def _get_data(self):
        rdf = self._rdf

        if self._is_mc:
            self.log.info(f'Found MC, truth matching')
            rdf = rdf.Filter('TMath::Abs(L1_TRUEID)   == 11')
            rdf = rdf.Filter('TMath::Abs(L2_TRUEID)   == 11')
            rdf = rdf.Filter('TMath::Abs(Jpsi_TRUEID) == 443')
        else:
            self.log.info(f'Found data, not truth matching')

        rdf = rdf.Redefine('L1_HasBremAdded', 'int(L1_HasBremAdded)')
        rdf = rdf.Redefine('L2_HasBremAdded', 'int(L2_HasBremAdded)')

        d_data = rdf.AsNumpy(['Jpsi_M', 'L1_P', 'L2_P', 'L1_HasBremAdded', 'L2_HasBremAdded'])
        df = pnd.DataFrame(d_data) 

        df.columns= ['mass', 'p1', 'p2', 'brem1', 'brem2']
        df = df.reset_index(drop=True)

        return df 
    #----------------------------------
    def _get_bin_resolution(self, df, bound):
        if df is None:
            return None

        size = df.shape[0]

        mass=df.mass.to_numpy()

        arr_dmass = mass - numpy.mean(mass) 
        i_size    = arr_dmass.size
        l_dmass   = utnr.remove_outliers(arr_dmass, l_zscore=[4, 4, 3])
        arr_dmass = numpy.array(l_dmass)
        f_size    = arr_dmass.size

        if size > 0:
            rms2 = numpy.sum( arr_dmass ** 2 ) / size
        else:
            rms2 = math.nan

        rms  = math.sqrt(rms2)

        bnd  = boundaries(bound) 
        self.log.info(f'{size:<20}{bnd.sbounds:<40}{rms:<20.0f}{i_size:<20}{f_size:<20}')

        if self._plot_dir is not None:
            self._plot_dist(arr_dmass, bnd.sbounds, rms)

        return rms
    #----------------------------------
    def _plot_dist(self, arr_dmass, sbound, sg):
        if arr_dmass.size == 0:
            return

        mu = numpy.mean(arr_dmass)

        plt.hist(arr_dmass, range=(mu-4*sg, mu+4*sg), alpha=0.7, bins=30, label='$m(e,e) - m_{J/\psi}$')
        plt.axvline(x=mu - sg, color='red', label='$\mu-\sigma$', linestyle='--')
        plt.axvline(x=mu + sg, color='red', label='$\mu+\sigma$', linestyle='--')
        plt.legend()
        bnd=boundaries(sbound)
        label=bnd.identifier
        sbnds=bnd.sbounds

        plt.title(f'$(p_1, p_2)\in${sbnds}')

        label=re.sub('_+', '_', label)
        plot_dir = utnr.make_dir_path(f'{self._plot_dir}/{self._suffix}/dist')
        plt.savefig(f'{plot_dir}/{label}.png')
        plt.close('all')
    #----------------------------------
    def _get_sig_pdf(self):
        if self._sig_pdf is not None:
            return self._sig_pdf

        if   self._signal == 'gauss':
            pdf = self._get_gauss_pdf()
        elif self._signal == 'dscb':
            pdf = self._get_dscb_pdf()
        elif self._signal == 'cb':
            pdf = self._get_cb_pdf()
        elif self._signal == 'johnson':
            pdf = self._get_johnson_pdf()
        else:
            self.log.error(f'Invalid signal PDF: {self._signal}')
            raise

        if self._rdf.is_mc:
            self._sig_pdf = pdf
            return self._sig_pdf

        nsg           = zfit.Parameter('nsg', 100, 0.0, 200000)
        self._sig_pdf = pdf.create_extended(nsg)

        return self._sig_pdf 
    #----------------------------------
    def _get_cb_pdf(self):
        al  = zfit.Parameter('al', 1, 0.1,  5.0)
        ar  = zfit.Parameter('ar',-1,-5.0, -0.1)

        nl  = zfit.Parameter('nl', 1, 0.1,  8.0)
        nr  = zfit.Parameter('nr', 1, 0.1, 10.0)

        fr  = zfit.Parameter('fr', 1, 0.0,  1.0)

        pdf_1 = zfit.pdf.CrystalBall(obs=self._obs, mu=self._mu, sigma=self._sg, alpha=al, n=nl)
        pdf_2 = zfit.pdf.CrystalBall(obs=self._obs, mu=self._mu, sigma=self._sg, alpha=ar, n=nr)

        pdf   = zfit.pdf.SumPDF([pdf_1, pdf_2], fr)

        return pdf
    #----------------------------------
    def _get_johnson_pdf(self):
         gm = zfit.Parameter("gm", 1, 0.1, 10)
         dl = zfit.Parameter("dl", 1, 0.1, 10)

         pdf= zpdf_jh(obs=self._obs, mu=self._mu, lm=self._sg, gamma=gm, delta=dl)

         return pdf
    #----------------------------------
    def _get_dscb_pdf(self):
        al  = zfit.Parameter('al', 0.6, 0.1,  5.0)
        ar  = zfit.Parameter('ar',-0.2,-5.0, -0.1)

        nl  = zfit.Parameter('nl', 5.0, 0.1,  8.0)
        nr  = zfit.Parameter('nr', 2.0, 0.1, 10.0)

        pdf = zfit.pdf.DoubleCB(obs=self._obs, mu=self._mu, sigma=self._sg, alphal=al, nl=nl, alphar=ar, nr=nr)

        return pdf
    #----------------------------------
    def _get_gauss_pdf(self):
        pdf = zfit.pdf.Gauss(obs=self._obs, mu=self._mu, sigma=self._sg)

        return pdf
    #----------------------------------
    def _get_bkg_pdf(self):
        if self._bkg_pdf is not None:
            return self._bkg_pdf

        lam = zfit.Parameter('lam', -0.001, -0.1, 0.0)

        bkg = zfit.pdf.Exponential(lam=lam, obs=self._obs, name='Combinatorial')
        nbk = zfit.Parameter('nbk', 100, 0.0, 200000)

        self._bkg_pdf = bkg.create_extended(nbk)

        return self._bkg_pdf 
    #----------------------------------
    def _get_tot_pdf(self):
        sig = self._get_sig_pdf()
        bkg = self._get_bkg_pdf()
        pdf = zfit.pdf.SumPDF([sig, bkg])

        return pdf
    #----------------------------------
    def _fit_df(self, df, bound):
        bnd = boundaries(bound)
        if bnd.has_inf():
            self.log.debug(f'Skipping fit in {bound}')
            return {}

        if self._is_mc:
            pdf = self._get_sig_pdf()
        else:
            pdf = self._get_tot_pdf()

        dat = df['mass'].to_numpy()
        if dat.size == 0: 
            self.log.info(f'Skipping empty data dataset for: {bound}')
            if not self._is_mc:
                self._d_dat_res[bound] = {} 

            return {} 

        self.log.info(f'Fitting {bound}')

        if not self._is_mc and len(self._d_par) > 0:
            zut.fix_pars(pdf, self._d_par[bnd])

        obj = zfitter(pdf, dat)
        if self._is_mc:
            res = obj.fit(ntries=30, pval_threshold=0.04)
        else:
            res = obj.fit()

        if res.status != 0:
            self.log.error(f'Finished with status: {res.status}')
            print(res)

        d_par = self._get_pars(res)

        text = f'Bin:{df.ibin}\n{bnd.sbounds}'
        self._plot_fit(dat, pdf, res, bnd.identifier, text)

        if not self._is_mc:
            self._d_dat_res[bound] = self._get_dat_resolution()

        return d_par
    #-------------------
    def _get_pars(self, res, method='minuit_hesse'):
        res.hesse(method=method)
        res.freeze()

        try:
            d_par = { name : [d_val['value'], d_val['hesse']['error']] for name, d_val in res.params.items() }
        except:
            self.log.warning(f'Cannot calculate errors, using zeros')
            d_par = { name : [d_val['value'], 0] for name, d_val in res.params.items() }

        return d_par
    #-------------------
    def _plot_fit(self, dat, pdf, res, identifier, text):
        if self._plot_dir is None:
            return

        [[minv]], [[maxv]] = self._obs.limits

        tp_rng = (minv, maxv)

        obj=zfp(data=dat, model=pdf, result=res)
        obj.plot(d_leg={}, plot_range=tp_rng, ext_text=text)
    
        obj.axs[1].plot(tp_rng, [0, 0], linestyle='--', color='black')
    
        plot_dir = utnr.make_dir_path(f'{self._plot_dir}/{self._suffix}/fits')
        plot_path= f'{plot_dir}/{identifier}.png'
        self.log.visible(f'Saving to: {plot_path}')
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close('all')
    #----------------------------------
    def _get_dat_resolution(self):
        dat      = self._sig_pdf.create_sampler(n=self._nsam_var)
        arr_mass = dat.value().numpy()

        return numpy.std(arr_mass)
    #----------------------------------
    def _trim_dataset(self, d_df):
        if len(self._l_ibin) == 0:
            self.log.info(f'Using {len(d_df)} datasets, after skipping trimming')
            return d_df

        d_df_trimmed = {}

        counter=0
        for key, val in d_df.items():
            if counter not in self._l_ibin:
                counter += 1
                continue

            self.log.debug(f'Keeping dataset for bin: {counter}')
            counter += 1

            d_df_trimmed[key] = val

        self.log.info(f'Using {len(d_df_trimmed)} datasets, after trimming')

        return d_df_trimmed
    #----------------------------------
    def _calculate(self, df, suffix):
        self._suffix = suffix
        utnr.make_dir_path(f'{self._plot_dir}/{self._suffix}')

        self.log.info(f'Calculating {suffix} resolutions')

        obj     = dsplit(df, self._binning, spectators=['mass'])
        d_df    = obj.get_datasets(as_type='dict', symmetrize=True)
        d_df    = self._trim_dataset(d_df)

        if self._fit:
            d_par = { bound : self._fit_df(df, bound)             for bound, df in d_df.items() }
        else:
            d_par = {}

        if self._is_mc:
            self.log.info(f'{"Dataset size":<20}{"Bounds":<40}{"RMS [MeV]":<20}{"Original":<20}{"Filtered":<20}')
            d_res = { bound : self._get_bin_resolution(df, bound) for bound, df in d_df.items() }
        else:
            d_res = self._d_dat_res

        return d_res, d_par
    #----------------------------------
    def get_resolution(self, brem=None):
        self._initialize()

        df = self._get_data()
        df = df[df.brem1 + df.brem2 == brem]

        d_res, d_par= self._calculate(df, f'{brem}_brem')

        return d_res, d_par
#----------------------------
log = utnr.getLogger(__name__)
#----------------------------
def get_axis_labels(d_res):
    regex = r'\(\((\d+)\.0,\s(\d+)\.0\).*'

    s_lab = set()
    for key in d_res:
        mtch = re.match(regex, key)
        if not mtch:
            log.error(f'Cannot match "{key}" with "{regex}"')
            raise

        low = mtch.group(1)
        hig = mtch.group(2)

        low = int(int(low) / 1000)
        hig = int(int(hig) / 1000)

        s_lab.add(f'{low}-{hig}')

    l_lab = list(s_lab)

    return sorted(l_lab, key = lambda label : int(label.split('-')[0]))
#----------------------------
def get_ndim(d_res):
    size = len(d_res)
    sqrt = math.sqrt(size)
    sqrt = math.floor(sqrt)

    if sqrt ** 2 != size:
        log.error(f'{size} is not a perfect square')
        raise ValueError

    return sqrt
#----------------------------
def get_resolution(d_res):
    ndim = get_ndim(d_res)

    counter=0
    l_row = [[]]
    for reso in d_res.values():
        if counter == ndim:
            l_row.append([])
            counter=0

        l_row[-1].append(reso/1000.)

        counter+=1

    mat = numpy.array(l_row)

    if mat.shape != (ndim, ndim):
        log.error(f'Wrong shape for resolution matrix: {mat.shape}')
        raise

    return 1000 * mat
#----------------------------
def plot_reso(d_res_str, plot_dir, title=None, suffix=None, rng=None):
    d_res_str = { key : val for key, val in d_res_str.items() if 'inf' not in key}
    l_x = get_axis_labels(d_res_str)

    d_res = {boundaries(key) : val for key, val in d_res_str.items()} 
    d_res = dict(sorted(d_res.items()))
    mat   = get_resolution(d_res)

    plot_path = f'{plot_dir}/{suffix}.png'
    log.visible(f'Saving to: {plot_path}')

    if rng is not None:
        vmin, vmax = rng
    else:
        vmin, vmax = None, None 

    cb=plt.pcolor(l_x, l_x, mat, vmin=vmin, vmax=vmax)
    plt.colorbar(cb)
    plt.title(title)
    plt.xlabel('$\min(p(e^+), p(e^-))$[MeV]')
    plt.ylabel('$\max(p(e^+), p(e^-))$[MeV]')

    nbins = len(l_x)
    for i in range(nbins):
        for j in range(nbins):
            val  = mat[i,j]
            if numpy.isnan(val):
                sval = ''
            else:
                sval = f'{val:.2f}'

            plt.text(j - 0.3, i, sval, color="k")

    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close('all')
#----------------------------

