import utils_noroot as utnr
import pandas       as pnd
import numpy 
import re
import os 

from ndict                      import ndict
from rk.efficiency              import efficiency
from rk.differential_efficiency import defficiency as deff
#-----------------------------------
class dyield_calculator:
    log=utnr.getLogger('dyield_calculator')
    #-----------------------------------
    def __init__(self, rdf, arr_wgt, bins, label='yield_calc_label'):
        self._rdf     = rdf
        self._arr_wgt = arr_wgt
        self._bins    = bins
        self._label   = label

        self._l_var   = None

        self._initialized = False
    #-----------------------------------
    def _initialize(self):
        if self._initialized:
            return

        if not isinstance(self._label, str):
            self.log.error(f'Invalid value for label: {self._label}')
            raise

        self._l_var = self._bins.vars
        self._check_rdf_vars()

        self._initialized=True
    #-----------------------------------
    def _check_rdf_vars(self):
        '''
        Will make sure that all variables in binning object, exist in dataframe
        '''
        l_rdf_var = self._rdf.GetColumnNames()

        missing=False
        for var in self._l_var:
            if var not in l_rdf_var:
                missing=True
                self.log.error(f'Variable {var} not found in RDF')
            else:
                self.log.debug(f'Variable {var} found in RDF')

        if not missing:
            return

        self.log.error(f'RDF vars:')
        l_rdf_pyvar = [ str(rdf_var.c_str()) for rdf_var in l_rdf_var]
        self.log.error(sorted(l_rdf_pyvar))
        raise
    #-----------------------------------
    def _get_dyield(self, var):
        arr_val = self._rdf.AsNumpy([var])[var]

        if arr_val.size != self._arr_wgt.size:
            self.log.error(f'For {var}, arrays with weights and values have different shapes, val/wgt:{arr_val.shape}/{self._arr_wgt.shape}')
            raise

        d_bnd_wgt = ndict()
        for val, wgt in zip(arr_val, self._arr_wgt):
            low, hig = self._bins.find_bin_bounds(var, val)
            if (low, hig) not in d_bnd_wgt:
                d_bnd_wgt[low, hig] = [wgt]
            else:
                d_bnd_wgt[low, hig].append(wgt)

        d_bnd_wgt_arr = ndict()
        for bnd, l_wgt in d_bnd_wgt.items():
            arr_wgt            = numpy.array(l_wgt)
            d_bnd_wgt_arr[bnd] = arr_wgt

        dy = dyield(d_bnd_wgt_arr, label=self._label, varname=var)

        return dy
    #-----------------------------------
    def get_yields(self, var=None):
        self._initialize()

        if not isinstance(var, str):
            self.log.error(f'Invalid variable value: {var}')
            raise

        if var not in self._l_var:
            self.log.error(f'Variable {var} not among: {self._l_var}')
            raise

        return self._get_dyield(var)
#-----------------------------------
class dyield:
    log = utnr.getLogger('dyield')
    #-----------------------------------
    def __init__(self, arg, label='yield_label', varname=None):
        if   isinstance(arg, str):
            d_bnd_wgt, varname = self._get_data(arg)
        elif isinstance(arg, ndict):
            d_bnd_wgt = arg 
        else:
            self.log.error(f'Invalid first argument type: {type(arg)}')
            raise

        self._d_bnd_wgt   = d_bnd_wgt
        self._label       = label 
        self._varname     = varname 

        self._df          = None
        self._total       = None

        self._initialized = False
    #-----------------------------------
    def _get_data(self, json_path):
        '''
        Will pick up JSON file and build {minv, maxv -> yield} dictionary.
        Will extract variable name from file with regex

        Both are returned in tuple (d_data, varname)
        '''
        regex = '(ctrl|psi2)_(MTOS|ETOS|GTIS)_(r1|r1p2|2017|2018)_(.*)\.json'
        json_name = os.path.basename(json_path)
        mtch = re.match(regex, json_name)
        if not mtch:
            self.log.error(f'Cannot match {json_name} to {regex}')
            raise

        varname   = mtch.group(4)
        l_data    = utnr.load_json(json_path)
        d_bnd_yld = ndict() 
        for [minv, maxv, yld, err] in l_data:
            d_bnd_yld[minv, maxv] = yld

        return d_bnd_yld, varname
    #-----------------------------------
    def __truediv__(self, obj):
        if   isinstance(obj,          deff):
            return self._div_by_deff(obj)
        elif isinstance(obj, numpy.ndarray):
            return self._div_by_arr(obj)
        else:
            return NotImplemented
    #-----------------------------------
    def __getitem__(self, key):
        try:
            return self._d_bnd_wgt[key]
        except:
            self.log.error(f'Cannot find key {key} in container, choose from: {list(self._d_bnd_wgt.keys())}')
            raise ValueError
    #-----------------------------------
    def _div_by_arr(self, arr_tot):
        self._initialize()

        total = numpy.sum(arr_tot)
        if total < self._total:
            self.log.error(f'Total differential yield is larger than denominator: {total:.3f} > {self._total:.3f}')
            raise

        obj = deff(lab=self._label, varname=self._varname)
        for (low, hig), arr_pas in self._d_bnd_wgt.items():
            obj[low, hig] = efficiency(arr_pas, arg_tot=arr_tot, cut=f'{low:.3f} < {self._varname} < {hig:.3f}', lab=self._label)

        return obj
    #-----------------------------------
    def _div_by_deff(self, deff):
        self._initialize()

        bnd_eff = deff.data.keys()
        bnd_yld = self._d_bnd_wgt.keys() 

        if bnd_eff != bnd_yld:
            self.log.error(f'Cannot divide incompatible yields and efficiencies')
            self.log.error(bnd_yld)
            self.log.error(bnd_eff)
            raise

        d_cor_yld = ndict()
        for (low, hig), arr_wgt in self._d_bnd_wgt.items():
            yld       = numpy.sum(arr_wgt)
            eff_obj   = deff.data[low,hig]
            eff, _, _ = eff_obj.val
            cor       = yld / eff

            self.log.debug(f'{cor:<10.3f}={yld:<10.3f}/{eff:<10.3f}')

            d_cor_yld[low, hig] = cor

        res = dyield(d_cor_yld, label=self._label, varname=self._varname)

        return res
    #-----------------------------------
    def _initialize(self):
        if self._initialized:
            return

        if not isinstance(self._varname, str):
            self.log.error(f'Invalid variable name: {self._varname}')
            raise

        self._df    = self._get_df()
        self._total = self._df['Yield'].sum()

        self._initialized = True
    #-----------------------------------
    def _get_df(self):
        df = pnd.DataFrame(columns=['Low', 'High', 'Yield'])

        ibin=1
        for (low, hig), arr_val in sorted(self._d_bnd_wgt.items()): 
            val  = arr_val if isinstance(arr_val, float) else numpy.sum(arr_val)
            df   = utnr.add_row_to_df(df, [low, hig, val], index=ibin)
            ibin+= 1

        return df
    #-----------------------------------
    def __str__(self):
        self._initialize()

        msg = '\n--------------\n'
        msg = f'{self._label}, {self._varname}\n'
        msg+= self._df.__str__()

        return msg
#-----------------------------------

