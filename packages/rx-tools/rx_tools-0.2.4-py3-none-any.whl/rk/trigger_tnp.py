import ROOT
import utils_noroot as utnr
import utils
import array
import pickle
import style
import numpy

import plot_fit    as pf

from fit_manager import fit_manager as fm
from rk.hist_map import hist_map

#-------------------------------------
class trigger_tnp:
    log = utnr.getLogger(__name__)
    #----------------------------
    @property
    def pars_fail(self):
        return self._d_par_fal

    @property
    def pars_pass(self):
        return self._d_par_pas
    #----------------------------
    def __init__(self, tp_dat, tp_sim, d_opt_fit, d_opt_plt={}):
        self.__d_opt_fit      = d_opt_fit
        self.__d_opt_plt      = d_opt_plt

        self.__tp_dat         = tp_dat
        self.__tp_sim         = tp_sim

        self.__l_tag          = ['HLT_MTOS', 'HLT_ETOS', 'HLT_HTOS', 'HLT_GTIS', 'L0MuonALL1', 'L0MuonHAD', 'L0MuonTIS', 'L0MuonMU1', 'L0TIS_EM', 'L0TIS_MH', 'L0ElectronTIS', 'L0HadronElEL']
        self.__fit_attempts   = 5 
        self.__print_level    = -1 
        self.__weight         = ''
        self.__pval_threshold = 0.05
        self.__bin_threshold  = 30000
        self.__gof_dof        = 10
        self.__shuffle_rate   = 0.1 
        self.__ncpu           = 1
        self._sim_wgt         = 'weight'

        self.__modelpath      = None
        self.__model          = None
        self.__tag            = None
        self.__outdir         = None
        self.__plotdir        = None
        self.__version        = None
        self.__nsig           = None
        self.__nbins          = None

        self.__wks            = None
        self.__h_pass_data    = None
        self.__h_fail_data    = None
        self.__fix_fal        = None
        self.__fix_pas        = None
        self.__fix_lst        = None
        self.__tp_slice       = None
        self.__h_binning      = None
        self.__x_binning      = None
        self.__y_binning      = None

        self._d_par_pas       = None
        self._d_par_fal       = None

        self.__initialized    = False
    #----------------------------
    def __initialize(self):
        if self.__initialized:
            return

        self.__modelpath     = self.__d_opt_fit['modelpath']
        self.__tag           = self.__d_opt_fit['tag']
        self.__outdir        = self.__d_opt_fit['outdir']
        self.__plotdir       = self.__d_opt_fit['plotdir']
        self.__version       = self.__d_opt_fit['version']
        self.__nsig          = self.__d_opt_fit['sigvar'] 
        self.__tp_slice      = self.__d_opt_fit['slicing'] 
        self.__nbins         = self.__d_opt_fit['nbins'] 
        self.__fix_pas       = self.__d_opt_fit['fix_pass']
        self.__fix_fal       = self.__d_opt_fit['fix_fail']
        self.__fix_lst       = self.__d_opt_fit['fix_list']
        #--------------------------------------------------
        histpath, self.__x_binning, self.__y_binning = self.__tp_slice
        ifile = ROOT.TFile(histpath)
        self.__h_binning = ifile.h_poly.Clone('h_poly')
        self.__h_binning.SetDirectory(0)
        ifile.Close()
        #--------------------------------------------------
        if 'print_level' in self.__d_opt_fit:
            self.__print_level = self.__d_opt_fit['print_level']
            self.log.visible('Using printing level {}'.format(self.__print_level))

        if 'max_attempts' in self.__d_opt_fit:
            self.__fit_attempts = self.__d_opt_fit['max_attempts']
            self.log.visible('Using {} fit attempts'.format(self.__fit_attempts))

        if 'weight' in self.__d_opt_fit:
            self.__weight = self.__d_opt_fit['weight']
            self.log.visible('Using weighted fit with weight: {}'.format(self.__weight))

        if 'pval_threshold' in self.__d_opt_fit:
            self.__pval_threshold = self.__d_opt_fit['pval_threshold']

        if 'bin_threshold' in self.__d_opt_fit:
            self.__bin_threshold = self.__d_opt_fit['bin_threshold']

        if 'gof_dof' in self.__d_opt_fit:
            self.__gof_dof = self.__d_opt_fit['gof_dof']

        if 'shuffle_rate' in self.__d_opt_fit:
            self.__shuffle_rate = self.__d_opt_fit['shuffle_rate']

        if 'ncpu' in self.__d_opt_fit:
            self.__ncpu = self.__d_opt_fit['ncpu']

        #--------------------------------------------------
        utnr.make_dir_path(self.__outdir)
        utnr.make_dir_path(self.__plotdir)
        utnr.check_file(self.__modelpath)

        if self.__tag not in self.__l_tag:
            self.log.error('Invalid tag ' + self.__tag)
            raise

        ifile = ROOT.TFile(self.__modelpath)
        try:
            self.__wks   = ifile.wks
            self.__model = self.__wks.pdf('model')
            ifile.Close()
        except:
            self.log.error('Cannot retrieve PDF "model" from ' + self.__modelpath)
            ifile.Close()
            raise

        self.__initialized = True
    #----------------------------
    def __check_empty(self, df, tag):
        nentries = df.Count().GetValue()
        if nentries <= 0:
            self.log.error('No entries found in dataframe ' + tag)
            raise
    #----------------------------
    def __make_histogram(self, name, l_val):
        hist = self.__h_binning.Clone(name)
        for i_bin, (val, err) in enumerate(l_val):
            hist.SetBinContent(i_bin + 1, val)
            hist.SetBinError(i_bin + 1, err)

        return hist
    #----------------------------
    def __get_fix_dict(self, sample):
        key = f'fix_{sample}'

        results_path = utnr.get_from_dic(self.__d_opt_fit,        key)
        if results_path is not None:
            utnr.check_file(results_path)
        else:
            self.log.warning(f'{key} not passed to config dictionary, not fixing any parameter')
            return {}

        fix_list     = utnr.get_from_dic(self.__d_opt_fit, 'fix_list')
        if fix_list is not None:
            utnr.check_file(fix_list)
        else:
            self.log.warning(f'"fix_list" not passed to config dictionary, not fixing any parameter')
            return {}

        d_par = utils.get_fit_res_par(results_path, fix_list)

        return d_par 
    #----------------------------
    def __get_dat_map(self, df, tag):
        outdir_fit = self.__plotdir + '/dt/' + tag
        utnr.make_dir_path(outdir_fit)

        d_opt                   = {}
        d_opt['weight']         = 'weight' 
        d_opt['nbins']          = self.__nbins 
        d_opt['max_attempts']   = self.__fit_attempts
        d_opt['bin_threshold']  = self.__bin_threshold
        d_opt['pval_threshold'] = self.__pval_threshold
        d_opt['fix_par']        = self.__get_fix_dict(tag)
        d_opt['print_level']    = self.__print_level
        d_opt['ncpu']           = self.__ncpu 
        d_opt['gof_dof']        = self.__gof_dof
        d_opt['shuffle_rate']   = self.__shuffle_rate
        d_opt['slicing']        = self.__tp_slice
        d_opt['outdir']         = outdir_fit 

        tree, _ = utils.df_to_tree(df, include_regex='(B_const_mass_M|B_PT|B_ETA|nTracks|weight)')
        obj     = fm(self.__model, tree, d_opt)
        l_stat  = obj.fit()
        d_par   = obj.get_pars()

        resultspath = '{}/dt/{}/fit_results.root'.format(self.__plotdir, tag)
        utnr.check_file(resultspath)
        hist = self.__get_histogram('h_data_' + tag, resultspath)

        l_text = self.__get_text(l_stat)
        pf.doPlot(outdir_fit, d_opt={'slice_text' : l_text})

        return hist, d_par
    #----------------------------
    def __get_text(self, l_stat):
        utnr.check_nonempty(l_stat)
        l_text = []
        for d_stat in l_stat:
            d_stat=l_stat[0]
            nattempt = utnr.get_from_dic(d_stat, 'nattempt')
            status   = utnr.get_from_dic(d_stat,   'status')
    
            text = 'attempts={}/{}; status={}'.format(nattempt, self.__fit_attempts, status)
            l_text.append(text)

        return l_text
    #----------------------------
    def __get_histogram(self, name, resultspath):
        ifile = ROOT.TFile(resultspath)

        index = 0

        l_val = []
        while True:
            resultsname = 'result_tree_{:02}'.format(index)

            results = ifile.Get(resultsname)
            index+=1
            try:
                l_pars = results.floatParsFinal()
            except:
                self.log.info('Last file: ' + resultsname)
                break

            par = l_pars.find(self.__nsig)
            val = par.getValV() 
            err = par.getError() 

            l_val.append((val, err))

        ifile.Close()

        h = self.__make_histogram(name, l_val)

        return h
    #----------------------------
    def __get_sim_map(self, df, tag):
        nentries = df.Count().GetValue()

        hist = self.__h_binning.Clone(f'h_sim_{tag}')

        self.log.info(f'Filling simulation map with weight: {self._sim_wgt}')

        d_data = df.AsNumpy([self.__x_binning, self.__y_binning, self._sim_wgt])
        arr_x  = d_data[self.__x_binning]
        arr_y  = d_data[self.__y_binning]
        arr_w  = d_data[self._sim_wgt]

        arr_x  = arr_x.astype('double')
        arr_y  = arr_y.astype('double')
        arr_w  = arr_w.astype('double')

        hist.FillN(nentries, arr_x, arr_y, arr_w)

        return hist
    #----------------------------
    def save_map(self, root_path):
        self.__initialize()

        df_dat_prb, df_dat_ant = self.__tp_dat
        df_sim_prb, df_sim_ant = self.__tp_sim 

        h_eff_pass_sim = self.__get_sim_map(df_sim_prb, 'pass')
        h_eff_fail_sim = self.__get_sim_map(df_sim_ant, 'fail')

        h_eff_pass_dat, self._d_par_pas = self.__get_dat_map(df_dat_prb, 'pass')
        h_eff_fail_dat, self._d_par_fal = self.__get_dat_map(df_dat_ant, 'fail')

        self.log.visible(f'Saving: {root_path}')
        ofile = ROOT.TFile(root_path, 'recreate')
        h_eff_pass_sim.Write()
        h_eff_fail_sim.Write()
        h_eff_pass_dat.Write()
        h_eff_fail_dat.Write()
        ofile.Close()
#-------------------------------------

