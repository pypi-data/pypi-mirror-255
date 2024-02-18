from importlib import resources
import json
from logzero import logger
import numpy as np
import ROOT
import utils


class corrector:
    def __init__(self, rdf):
        self._rdf = rdf
        self._package_root = resources.files("rk")

    def _get_weight_func(self, version):
        weight_path = self._package_root.joinpath(f"inclusive_weight/inclusive_weight_{version}.json")
        with open(weight_path) as f:
            weight_dict = json.load(f)

        def weight_func(b_trueid, jpsi_trueid):
            nonlocal weight_dict
            # default weight is 1
            weight=0
            if   abs(b_trueid) == 511:
                if   jpsi_trueid == 443:
                    weight = weight_dict["Bd_x_jpsi"]
                elif jpsi_trueid == 100443:
                    weight = weight_dict["Bd_x_psi2s"]
            elif abs(b_trueid) == 521:
                if   jpsi_trueid == 443:
                    weight = weight_dict["Bu_x_jpsi"]
                elif jpsi_trueid == 100443:
                    weight = weight_dict["Bu_x_psi2s"]
            elif abs(b_trueid) == 531:
                if   jpsi_trueid == 443:
                    weight = weight_dict["Bs_x_jpsi"]
                elif jpsi_trueid == 100443:
                    weight = weight_dict["Bs_x_psi2s"]

            if weight == 0:
                logger.warning(f'{"B ID ->":<10}{b_trueid:<20}{"Jpsi ID -> ":<10}{jpsi_trueid:<20}')

            return weight

        return weight_func

    def add_weight(self, name="incl_wgt_br", version="v2"):
        rdf_np       = self._rdf.AsNumpy(['B_TRUEID', 'Jpsi_TRUEID'])
        weight_func  = self._get_weight_func(version)
        weight       = np.array([weight_func(b_id, jpsi_id) for b_id, jpsi_id  in zip(rdf_np["B_TRUEID"], rdf_np["Jpsi_TRUEID"])])
        rdf_wgt      = utils.add_df_column(self._rdf, weight, name, d_opt={'exclude_re' : 'tmva_\d+_\d+'})

        return rdf_wgt
