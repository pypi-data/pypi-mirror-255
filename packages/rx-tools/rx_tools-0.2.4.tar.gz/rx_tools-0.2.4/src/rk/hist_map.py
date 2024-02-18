import ROOT
import numpy
import style

import utils
import utils_noroot as utnr

#---------------------------------------
class hist_map:
    log = utnr.getLogger(__name__)
    #------------------------
    def __init__(self, d_opt = {}):
        self._d_opt        = d_opt

        self._d_h_yld_fail = {} 
        self._d_h_yld_pass = {} 
        self._d_h_eff      = {} 
        self._d_h_rat      = {} 

        self._nsamples     = None

        self._initialized = False
    #------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._nsamples = len(self._d_h_yld_fail)

        for sample in self._d_h_yld_pass:
            h_yld_pass = self._d_h_yld_pass[sample]
            h_yld_fail = self._d_h_yld_fail[sample]

            self._d_h_eff[sample] = self._get_eff_map(h_yld_pass, h_yld_fail)

        self._d_h_rat = self._get_eff_rat()

        self._initialized = True
    #------------------------
    def _get_eff_rat(self):
        d_h_rat = {}
        h_data = self._d_h_eff['Data']
        for sample,  h_sample in self._d_h_eff.items():
            if sample == 'Data':
                continue

            name_rat = f'h_rat_{sample}_data'
            h_rat = h_data.Clone(name_rat) 
            h_rat.Divide(h_data, h_sample)

            d_h_rat[sample] = h_rat

        return d_h_rat
    #------------------------
    def _get_eff_map(self, h_yld_pass, h_yld_fail):
        name_pass = h_yld_pass.GetName()
        name_fail = h_yld_fail.GetName()

        name_eff = 'h_eff_{}_{}'.format(name_pass, name_fail)
        h_eff = h_yld_pass.Clone(name_eff) 

        nbins = h_eff.GetNumberOfBins()
        for i_bin in range(1, nbins + 1) :
            npass = h_yld_pass.GetBinContent(i_bin)
            nfail = h_yld_fail.GetBinContent(i_bin)

            epass = h_yld_pass.GetBinError(i_bin)
            efail = h_yld_fail.GetBinError(i_bin)

            try:
                eff, err = utils.value_and_covariance('p / (p + f)', p = (npass, epass), f = (nfail, efail))
            except ZeroDivisionError:
                self.log.warning(f'Zero division found: pass/fail ({npass}/{nfail})')
                self.log.warning(f'bin/nbins : {i_bin}/{nbins}')
                eff = 0
                err = 0

            self.log.debug('{}+/-{}'.format(npass, epass))
            self.log.debug('{}+/-{}'.format(nfail, efail))

            h_eff.SetBinContent(i_bin, eff)
            h_eff.SetBinError(i_bin, err)

        return h_eff
    #------------------------
    def add_hist(self, h_pas, h_fal, data=None):
        if   data == True:
            self._d_h_yld_pass['Data'] = h_pas 
            self._d_h_yld_fail['Data'] = h_fal 
        elif data == False:
            self._d_h_yld_pass['Simulation'] = h_pas 
            self._d_h_yld_fail['Simulation'] = h_fal 
        elif isinstance(data, str):
            self._d_h_yld_pass[data] = h_pas 
            self._d_h_yld_fail[data] = h_fal 
        else:
            self.log.error('Invalid data flag')
            raise
    #------------------------
    def _check_sample_size(self, d_hist_1d):
        nbins = None
        for l_hist in d_hist_1d.values():
            nbins_now = len(l_hist)
            if   nbins is None:
                nbins = nbins_now
            elif nbins != nbins_now:
                self.log.error(f'Number of bins Y in different samples differs: {nbins}/{nbins_now}')
                raise
            else:
                pass

        return nbins
    #------------------------
    def _get_efficiency(self, arr_point, data=None):
        utnr.check_none(data)
    
        if   data == True:
            h_eff = self._d_h_eff['Data']
        elif data == False:
            h_eff = self._d_h_eff['Simulation']
        elif isinstance(data, str):
            h_eff = self._d_h_eff[data]
        else:
            self.log.error(f'Invalid efficiency type: {data}')
            raise ValueError
            
        arr_eff = utils.read_2Dpoly(arr_point, h_eff)
        
        return arr_eff
    #------------------------
    def get_yld_maps(self, data=None):
        if   data == True:
            return self._d_h_yld_pass['Data'      ], self._d_h_yld_fail['Data'      ]
        elif data == False:
            return self._d_h_yld_pass['Simulation'], self._d_h_yld_fail['Simulation']
        elif isinstance(data, str):
            return self._d_h_yld_pass[data        ], self._d_h_yld_fail[data        ]
        else:
            self.log.error(f'Invalid data type: {data}')
            raise ValueError
    #------------------------
    def get_efficiencies(self, arr_point, treename=None, replica=None, skip_direct=None):
        self._initialize()

        #TODO: treename will be introduced always, but not used, might use it somehow.
        if replica not in [0, None]:
            self.log.error('Replica {} not supported'.format(replica))
            raise

        if skip_direct not in [True, None]:
            self.log.error('Skip direct {} not supported'.format(skip_direct))
            raise

        arr_eff_dat = self._get_efficiency(arr_point, data=True)
        arr_eff_sim = self._get_efficiency(arr_point, data=False)

        arr_eff = numpy.array([arr_eff_dat, arr_eff_sim]).T

        return arr_eff
    #------------------------
    def plot_maps(self, outdir, d_opt=None):
        self._initialize()
        if d_opt is not None:
            self._d_opt.update(d_opt)

        self._do_plot_maps(self._d_h_eff     , 'eff', outdir)
        self._do_plot_maps(self._d_h_rat     , 'rat', outdir)
        self._do_plot_maps(self._d_h_yld_pass, 'pas', outdir)
        self._do_plot_maps(self._d_h_yld_fail, 'fal', outdir)
    #------------------------
    def _get_options(self, kind):
        if   kind in ['pas', 'fal']:
            d_opt           = {}
            d_opt['legend'] = +1
            d_opt['xgrid']  = True 
            d_opt['ygrid']  = True 
            d_opt['normalize']  = True 
            d_opt['yname']  = 'Signal yield'
        elif kind in 'eff':
            d_opt           = dict(self._d_opt)
            d_opt['legend'] = -1
            d_opt['yname']  = 'Efficiency'
            d_opt['yrange'] = 0.0, 1.1
        elif kind in 'rat':
            d_opt           = dict(self._d_opt)
            d_opt['legend'] = +1 
            d_opt['yname']  = 'Weights'
            d_opt['ratio']  = False 
        else:
            self.log.error(f'Kind of plot {kind} not recognized')
            raise

        d_opt['leg_head'] = self._d_opt['leg_head']

        return d_opt
    #------------------------
    def _do_plot_maps(self, d_hist, kind, outdir):
        d_opt     = self._get_options(kind)
        plot_id   = utnr.get_from_dic(self._d_opt, 'plot_id')
        d_hist_1d = { sample : utils.poly2D_to_1D(hist, f'{kind}_{sample}') for sample, hist in d_hist.items() }

        nbins = self._check_sample_size(d_hist_1d)

        for i_bin in range(nbins):
            l_hist_bin = []
            for sample, l_hist in d_hist_1d.items(): 
                hist = l_hist[i_bin]
                hist.SetTitle(sample)
                l_hist_bin.append(hist)

            plotpath = f'{outdir}/{kind}_{plot_id}_{i_bin:02}.png'
            utils.plot_histograms(l_hist_bin, plotpath, d_opt=d_opt)
#---------------------------------------

