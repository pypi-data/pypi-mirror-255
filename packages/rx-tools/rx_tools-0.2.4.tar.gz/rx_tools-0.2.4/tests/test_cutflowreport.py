import ROOT

import numpy

#------------------------------------------------------
def get_data(nentries):
    arr_x = numpy.random.normal(0, 0.1, nentries)
    arr_y = numpy.random.normal(0, 0.1, nentries)
    
    d_data={'x' : arr_x, 'y' : arr_y}
    
    df = ROOT.RDF.MakeNumpyDataFrame(d_data)

    return df
#------------------------------------------------------

df=get_data(1000)

df=df.Filter('x > 0', 'xcut')
df=df.Filter('y < 0', 'ycut')

rep=df.Report()
nrep=ROOT.CutFlowReport(rep, "", {'x > 0', 'y < 0'})
nrep.Print(1)

