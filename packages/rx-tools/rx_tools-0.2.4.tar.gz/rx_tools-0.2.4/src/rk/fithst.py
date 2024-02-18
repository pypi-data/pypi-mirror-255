import utils_noroot      as utnr
import matplotlib.pyplot as plt
import zutils.utils      as zut

import os 
import sys
import ROOT
import zfit
import math 
import tqdm
import numpy 
import utils
import logging 

from zutils.plot   import plot     as zfplot 
from data_splitter import splitter as dsplit
from fitter        import zfitter

#----------------------------------------
class extractor:
    log=utnr.getLogger('extractor')
    #----------------------------------------
    @property
    def data(self):
        return self._rdf_mc, self._rdf_dt

    @data.setter
    def data(self, value):
        self._rdf_mc, self._rdf_dt = value
    #----------------------------------------
    @property
    def model(self):
        return self._l_pdf

    @model.setter
    def model(self, value):
        self._l_pdf = value 
    #----------------------------------------
    @property
    def binning(self):
        return self._d_bin

    @binning.setter
    def binning(self, value):
        self._d_bin = value
    #----------------------------------------
    def __init__(self):
        self._d_bin       = None
        self._l_exp       = None
        self._l_var       = None
        self._l_pdf       = None
        self._res_dir     = None
        self._arr_all     = None 
        self._arr_xax     = None 
        self._arr_yax     = None 
        self._arr_zax     = None 

        self._one_dim     = False 
        self._d_res       = {}
        self._l_float     = ['mu', 'sg']
        self._mass_var    = 'B_const_mass_M[0]'
        self._fmax        = sys.float_info.max

        self._initialized = False
    #----------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        if self._one_dim not in [True, False]:
            self.log.error(f'Invalid value for one_dim: {self._one_dim}')
            raise ValueError

        if len(self._l_pdf) < 2:
            self.log.error(f'Found fewer than 2 PDFs:')
            print(self._l_pdf)
            raise

        zfitter.log.setLevel(logging.WARNING)
        dsplit.log.setLevel(logging.WARNING)

        ROOT.gROOT.ProcessLine(".L lhcbStyle.C")
        ROOT.lhcbStyle()

        self._initialized = True
    #----------------------------------------
    def _bound_filter_rdf(self, rdf):
        axis=0
        for var, arr in self._d_bin.items():
            min_var = min(arr)
            max_var = max(arr)

            cut = f'{min_var} < {var} && {var} < {max_var}'

            rdf = rdf.Filter(cut, f'{axis} bound')
            axis+=1

        return rdf
    #----------------------------------------
    def _get_pdf(self, kind):
        if kind == 'ctrl':
            pdf = self._l_pdf[0]
        elif kind == 'data':
            pdf = zfit.pdf.SumPDF(self._l_pdf)
        else:
            self.log.error(f'Invalid PDF kind: {kind}')
            raise

        return pdf
    #----------------------------------------
    def _is_yield(self, pdf, par_name):
        l_yld_nam = []

        par = pdf.get_yield()
        if   isinstance(par, zfit.Parameter):
            l_yld_nam = [par.name]
        elif isinstance(par, zfit.ComposedParameter):
            l_yld_nam = [par.name for _, par in par.params.items()]
        else:
            self.log.error(f'PDF parameter is invalid:')
            print(par)
            raise

        if len(l_yld_nam) == 0:
            self.log.error(f'No yields found in PDF:')
            print(pdf)
            raise

        is_yield = par_name in l_yld_nam

        self.log.debug(f'{is_yield} = {par_name} in {l_yld_nam}')

        return is_yield
    #----------------------------------------
    def _fix_pars(self, pdf, tup_bound):
        if tup_bound not in self._d_res:
            self.log.warning(f'Dataset {tup_bound} does not have simulation parameters to fix data fit')
            return pdf

        res = self._d_res[tup_bound]

        l_par = list(pdf.get_params(floating=True)) + list(pdf.get_params(floating=False))

        self.log.debug(f'Fixing parameeters')
        for par in l_par:
            if par.name not in res.params or par.name in self._l_float or self._is_yield(pdf, par.name):
                continue

            val = res.params[par.name]['value']
            par.assign(val)
            par.floating = False

            self.log.debug(f'{par.name:<20}{"->" :20}{val:>.3f}')

        return pdf
    #----------------------------------------
    def _get_bin_info(self, df, kind, tup_bound):
        arr = df['mass'].to_numpy()
        arr = numpy.asarray(arr).astype('float32')
        if len(arr) == 0:
            return None

        try:
            l_mean = [ 0.5 * (min_val + max_val) for min_val, max_val in tup_bound]
        except:
            self.log.error('Cannot extract mean list for bounds: {tup_bound}')
            raise

        self.log.debug(f'Fitting {tup_bound} dataset: {arr.shape}')

        pdf = self._get_pdf(kind)

        if kind == 'data':
            pdf = self._fix_pars(pdf, tup_bound)

        wgt     = df['weight'].to_numpy()
        wgt     = numpy.asarray(wgt).astype('float32')
        fit_dat = zfit.Data.from_numpy(obs=pdf.space, array=arr, weights=wgt)
        ftr     = zfitter(pdf, fit_dat)

        try:
            res = ftr.fit()
        except:
            self.log.warning(f'Fit failed, will assign yield as dataset size: {arr.size}')
            return [arr.size, 0] + l_mean + [None]

        with zfit.run.set_graph_mode(False):
            res.hesse(name='hesse_np')

        yld = res.params['nsg']['value']
        try:
            err = res.params['nsg']['hesse_np']['error']
        except:
            self.log.warning(f'Setting error 2 * sqrt(S), cannot recover hesse error:')
            err = 2 * math.sqrt(yld)

        self._plot_fit(pdf, arr, tup_bound, res, kind)
        self._save_res(pdf, tup_bound, res, kind)

        pdf.reset_cache_self()

        if kind != 'data': 
            yld = numpy.sum(wgt)
            err = 0

        return [yld, err] + l_mean + [res]
    #----------------------------------------
    def _save_res(self, pdf, tup_bound, res, kind):
        loc      = self._bound_to_loc(tup_bound)

        pkl_dir  = utnr.make_dir_path(f'{self._res_dir}/pickle/{kind}')
        pkl_path = f'{pkl_dir}/result_{loc}.pkl'

        res.freeze()
        utnr.dump_pickle(res, pkl_path)

        tex_dir  = utnr.make_dir_path(f'{self._res_dir}/latex/{kind}')
        tex_path = f'{tex_dir}/result_{loc}.tex'

        zut.pdf_to_latex(pdf, tex_path)
    #----------------------------------------
    def _plot_his(self, his, kind):
        if self._res_dir is None:
            return

        his_dir = utnr.make_dir_path(f'{self._res_dir}/plots/hist')
        his     = his.Project3D('yx')

        can = ROOT.TCanvas(f'c_{kind}', '', 1000, 1000)
        his.Draw('colz text')
        utils.Reformat2D(can)
        can.SaveAs(f'{his_dir}/his_{kind}.png')
    #----------------------------------------
    def _bound_to_text(self, tup_bound):
        l_text = []
        for minv, maxv in tup_bound:
            l_text.append(f'({minv:.2e}, {maxv:.2e})')

        return ','.join(l_text)
    #----------------------------------------
    def _plot_fit(self, pdf, arr, tup_bound, res, kind):
        if self._res_dir is None:
            return

        if len(arr) == 0:
            return

        fit_dir = utnr.make_dir_path(f'{self._res_dir}/plots/fits/{kind}')

        obj=zfplot(model=pdf, data=arr, result=res, suffix=str(tup_bound))

        loc       = self._bound_to_loc(tup_bound)
        plot_path = f'{fit_dir}/fit_{loc}.png'
        try:
            obj.plot(ext_text=self._bound_to_text(tup_bound))
            plt.savefig(plot_path)
            plt.close('all')
        except:
            self.log.warning(f'Could not save {plot_path}')
            self.log.warning(f'Data: {arr.shape}')
            self.log.warning(f'PDF: {pdf}')
    #----------------------------------------
    def _bound_to_loc(self, tup_bound):
        str_bound = str(tup_bound)
        loc       = utnr.get_var_name(str_bound)
        loc       = utnr.remove_consecutive(loc)
        loc       = loc.rstrip('_')
        loc       = loc.lstrip('_')

        return loc
    #----------------------------------------
    def _get_dset_binning(self, axis):
        if axis is None:
            return self._d_bin

        [var_x, var_y, var_z] = list(self._d_bin)

        d_bin = dict(self._d_bin)
        match axis:
            case 'x':
                d_bin[var_y] = self._arr_all
                d_bin[var_z] = self._arr_all
            case 'y':
                d_bin[var_x] = self._arr_all
                d_bin[var_z] = self._arr_all
            case 'z':
                d_bin[var_x] = self._arr_all
                d_bin[var_y] = self._arr_all
            case _:
                self.log.error(f'Invalid axis: {axis}')
                raise ValueError

        return d_bin
    #----------------------------------------
    def _get_datasets(self, kind, axis=None):
        rdf  = self._rdf_mc if kind == 'ctrl' else self._rdf_dt
        self.log.info(f'Splitting {rdf.Count().GetValue()} entries')

        d_bin        = self._get_dset_binning(axis)
        obj          = dsplit(rdf, d_bin, spectators=['mass', 'weight'])
        obj.plot_dir = f'{self._res_dir}/data_split' 
        d_df         = obj.get_datasets(as_type='dict', noflow=True)

        return d_df
    #----------------------------------------
    def _get_fit_info(self, kind, axis=None):
        d_df   = self._get_datasets(kind, axis=axis)
        d_info = { tup_bound : self._get_bin_info(df, kind, tup_bound) for tup_bound, df in tqdm.tqdm(d_df.items(), ascii=' -') }

        return d_info
    #----------------------------------------
    def _get_hist(self, kind, axis=None):
        arr_x = self._arr_xax if axis in ['x', None] else self._arr_all
        arr_y = self._arr_yax if axis in ['y', None] else self._arr_all 
        arr_z = self._arr_zax if axis in ['z', None] else self._arr_all 

        hist = ROOT.TH3F(f'h_{kind}', kind, arr_x.size - 1, arr_x, arr_y.size - 1, arr_y, arr_z.size - 1, arr_z)

        self.log.info(f'Bin contents for {kind}')
        d_info = self._get_fit_info(kind, axis=axis)
        for tup_bound, info in d_info.items():
            if info is None:
                continue

            [yld, err, xm, ym, zm, res] = info
            if kind == 'ctrl' and res is not None:
                self._d_res[tup_bound] = res

            i_bin = hist.FindBin(xm, ym, zm)
            hist.SetBinContent(i_bin, yld)
            hist.SetBinError  (i_bin, err)
            self.log.debug(f'{i_bin:<10}{yld:<20.0f}')

        if axis is not None:
            hist.SetName(f'h_{kind}_{axis}')

        return hist
    #----------------------------------------
    def _get_weights(self, d_hist, axis=None):
        hist = d_hist[axis]
        match axis:
            case 'x':
                ax = hist.GetXaxis()
            case 'y':
                ax = hist.GetYaxis()
            case 'z':
                ax = hist.GetZaxis()
            case _:
                self.log.error(f'Invalid axis: {axis}')
                raise ValueError

        nbins = ax.GetNbins()
        l_val_err_cen = []
        for i_bin in range(1, nbins + 1):
            cnt = ax.GetBinCenter(i_bin)
            match axis:
                case 'x':
                    j_bin = hist.FindBin(cnt,   1,   1)
                case 'y':
                    j_bin = hist.FindBin(  1, cnt,   1)
                case 'z':
                    j_bin = hist.FindBin(  1,   1, cnt)
                case _:
                    self.log.error(f'Invalid axis: {axis}')
                    raise ValueError

            val = hist.GetBinContent(j_bin)
            err = hist.GetBinError(j_bin)

            l_val_err_cen.append((val, err, cnt))

        return l_val_err_cen
    #----------------------------------------
    def _multiply_axes(self, d_hist, kind):
        hist = ROOT.TH3F(f'h_{kind}', kind, self._arr_xax.size - 1, self._arr_xax, self._arr_yax.size - 1, self._arr_yax, self._arr_zax.size - 1, self._arr_zax)

        l_val_err_cen_x = self._get_weights(d_hist, axis='x')
        l_val_err_cen_y = self._get_weights(d_hist, axis='y')
        l_val_err_cen_z = self._get_weights(d_hist, axis='z')

        for val_x, err_x, cen_x in l_val_err_cen_x:
            for val_y, err_y, cen_y in l_val_err_cen_y:
                for val_z, err_z, cen_z in l_val_err_cen_z:
                    i_bin = hist.FindBin(cen_x, cen_y, cen_z)
                    val = val_x * val_y * val_z
                    var = (val_x * val_y * err_z) ** 2 + (err_x * val_y * val_z) ** 2 + (val_x * err_y * val_z) ** 2 
                    err = math.sqrt(var)

                    hist.SetBinContent(i_bin, val)
                    hist.SetBinError(i_bin, err)

        return hist
    #----------------------------------------
    def get_histograms(self, force_redo=False):
        self._initialize()

        if not self._one_dim:
            h_mc = self._get_hist('ctrl')
            h_dt = self._get_hist('data')
        else:
            d_h_mc = {}
            d_h_dt = {}
            for axis in ['x', 'y', 'z']:
                self.log.info(f'Getting maps along {axis} axis')
                d_h_mc[axis] = self._get_hist('ctrl', axis=axis)
                d_h_dt[axis] = self._get_hist('data', axis=axis)

            self.log.info('Merging 1D maps')
            h_mc = self._multiply_axes(d_h_mc, 'ctrl')
            h_dt = self._multiply_axes(d_h_dt, 'data')

        self._plot_his(h_mc, 'ctrl')
        self._plot_his(h_dt, 'data')

        return h_mc, h_dt
#----------------------------------------

