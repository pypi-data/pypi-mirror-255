import ROOT

import numpy
import array

import utils
import utils_noroot as utnr

from rk.collector import collector

log=utnr.getLogger(__name__)
#-------------------------------------
class mv_reweighter:
    def __init__(self, data=(), simulation=(), l_var=[]):
        self.data       = data
        self.simulation = simulation
        self.l_var      = l_var
        self._initialize= False
        self.plotsdir   = None
        self.storage    = collector()
        self.wgt_name   = 'mv_reweighter_event_weight'
    #-------------------------------------
    def __initialize(self):
        if self._initialize:
            return

        try:
            df_sim, sim_wgt = self.simulation
        except:
            log.error('Cannot unpack simulation and simulation weight')
            print(self.simulation)
            raise

        try:
            df_dat, dat_wgt = self.data
        except:
            log.error('Cannot unpack data and data weight')
            print(self.data)
            raise

        utils.is_type(dat_wgt, type('     '))
        utils.is_type(sim_wgt, type('     '))

        #self.__check_weights(df_sim, sim_wgt)
        #self.__check_weights(df_dat, dat_wgt)

        #df_dummy=ROOT.RDataFrame(1)
        #df_dummy=df_dummy.Define('x', '1')

        #utils.is_type(df_dat, type(df_dummy))
        #utils.is_type(df_sim, type(df_dummy))

        df_sim = df_sim.Define(self.wgt_name, sim_wgt)
        df_dat = df_dat.Define(self.wgt_name, dat_wgt)

        self.df_sim = df_sim
        self.df_dat = df_dat

        utils.is_type(self.l_var, type([]      ))

        l_var_name=[]
        for var_name, dummy in self.l_var:
            l_var_name.append(var_name)

        self.identifier = '_'.join(l_var_name)

        self._initialize=True
    #-------------------------------------
    def __check_weights(self, df, wgt):
        df=df.Range(1000)

        arr_wgt = df.AsNumpy([wgt])[wgt]

        if numpy.all(arr_wgt == 1):
            log.warning('Weight {} is only made of 1s'.format(wgt))

        if numpy.all(arr_wgt == 0):
            log.error('Weight {} is only made of 1s'.format(wgt))
            raise
    #-------------------------------------
    def __get_1d_weights(self, tp_var):
        var_name, h_mod = tp_var

        if   type(h_mod) == ROOT.TH1D:
            mod_var = ROOT.RDF.TH1DModel(h_mod)
        elif type(h_mod) == ROOT.TH1F:
            mod_var = ROOT.RDF.TH1FModel(h_mod)
        else:
            try:
                h_mod = utils.cont_to_hist('h_mod', h_mod)
            except:
                log.error('Cannot convert object to histogram')
                print(h_mod)
                raise

            mod_var = ROOT.RDF.TH1DModel(h_mod)

        h_dat = self.df_dat.Histo1D(mod_var, var_name, self.wgt_name)
        h_dat.SetTitle('Data')

        h_sim = self.df_sim.Histo1D(mod_var, var_name, self.wgt_name)
        h_sim.SetTitle('Simulation')

        h_wgt = utils.get_weights(h_dat, h_sim)
        h_wgt.SetTitle('Weights')

        arr_val = self.df_sim.AsNumpy([var_name])[var_name] 

        l_wgt=[]
        for val in arr_val:
            i_bin = h_wgt.FindBin(val)
            wgt   = h_wgt.GetBinContent(i_bin)
            l_wgt.append(wgt)

        if self.plotsdir is not None:
            d_opt={}
            d_opt['legend'] = 1 
            self.__plot_var(var_name, mod_var, d_opt)

            d_opt={}
            d_opt['normalize'] = True 
            d_opt['legend']    = 1 
            d_opt['extra_pad'] = h_wgt
            d_opt['width'    ] = 1200 
            try:
                utils.plotHistograms([h_dat, h_sim], self.plotsdir + '/weighted_{}.png'.format(var_name), d_opt=d_opt)
            except:
                log.error('Variable {} could not be saved'.format(var_name))
                print(h_mod)
                print(var_name)
                print(self.wgt_name)
                raise

        arr_wgt = numpy.array(l_wgt)

        return arr_wgt 
    #-------------------------------------
    def __plot_var(self, varname, model, d_opt):
        h_dat_var = self.df_dat.Histo1D(model, varname)
        h_sim_var = self.df_sim.Histo1D(model, varname)

        h_dat_var = h_dat_var.GetValue()
        h_sim_var = h_sim_var.GetValue()

        h_dat_var.SetTitle('Data')
        h_sim_var.SetTitle('Simulation')

        plotpath='{}/{}.png'.format(self.plotsdir, varname)
        log.info(plotpath)
        utils.plotHistograms([h_dat_var, h_sim_var], plotpath, d_opt=d_opt)
    #-------------------------------------
    def __get_stats(self, arr_wgt):
        sm = numpy.sum(arr_wgt)
        nu = arr_wgt.size

        nz =  100 * numpy.count_nonzero(abs(arr_wgt- 0) < 1e-5) / sm
        nn =  100 * numpy.count_nonzero(numpy.isnan(arr_wgt))   / sm
        ni =  100 * numpy.count_nonzero(numpy.isinf(arr_wgt))   / sm

        row= [sm, nu, nz, nn, ni]

        return row
    #-------------------------------------
    def get_weights(self, kind='1d'):
        self.__initialize()

        if self.plotsdir is not None:
            arr_wgt_bin = numpy.linspace(-2, 2, 100)
            wgt_mod     = ROOT.RDF.TH1DModel('h_wgt', '', arr_wgt_bin.size - 1, arr_wgt_bin)

            d_opt={}
            d_opt['legend'] = 'auto' 
            d_opt['logy']   = True 
            self.__plot_var(self.wgt_name, wgt_mod, d_opt)

        arr_wgt=None

        self.storage.add_list('wgt_stat', ['Var', 'Sum', 'Size', 'Frac Zeros', 'Frac NaNs', 'Frac Infs'])
        if kind == '1d':
            for tp_var in self.l_var:
                var_name, dummy = tp_var

                arr_tmp=self.__get_1d_weights(tp_var)
                row = self.__get_stats(arr_tmp)
                row = [var_name] + row

                self.storage.add_list('wgt_stat', row)

                if arr_wgt is None:
                    arr_wgt = arr_tmp
                else:
                    arr_wgt*= arr_tmp
        else:
            log.error('Unrecognized kind ' + kind)
            raise

        row = self.__get_stats(arr_wgt)
        row = ['Total'] + row
        self.storage.add_list('wgt_stat', row)

        if self.plotsdir is not None:
            tablepath='{}/stats_{}.tex'.format(self.plotsdir, self.identifier)
            tab=self.storage.get('wgt_stat')
            utils.makeTable(tablepath, tab)

        return arr_wgt
#-------------------------------------

