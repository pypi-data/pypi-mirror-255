from rk.inclusive import corrector
import ROOT
import json
from importlib import resources
from logzero import logger
import numpy as np


def get_toy_rdf():
    b_id = [511] * 2 + [521] * 2 + [531] * 2
    jpsi_id = [443, 100443] * 3
    toy_data = {"B_TRUEID": np.array(b_id, dtype=np.int32), "Jpsi_TRUEID": np.array(jpsi_id, dtype=np.int32), "eventNumber": np.array([0, 1, 2, 3, 4, 5], dtype=np.int32)}
    toy_rdf = ROOT.RDF.FromNumpy(toy_data)
    return toy_rdf


def test_corrector():
    version = "v2"
    toy_rdf = get_toy_rdf()
    obj = corrector(toy_rdf)
    toy_rdf_wgt = obj.add_weight(name="wgt_br", version=version)
    sum_wgt = toy_rdf_wgt.Sum("wgt_br").GetValue()

    weight_path = resources.files("rk").joinpath(f"inclusive_weight/inclusive_weight_{version}.json")
    with open(weight_path) as f:
        weight = json.load(f)

    # Bu_psi2s not used
    weight["Bu_psi2s"] = 0

    sum_wgt_ref = sum(weight.values())

    assert sum_wgt == sum_wgt_ref, f"Sum of weight is not correct: {sum_wgt} != {sum_wgt_ref}"
    logger.info(f"Test passed! {sum_wgt} == {sum_wgt_ref}")

if __name__ == "__main__":
    test_corrector()
