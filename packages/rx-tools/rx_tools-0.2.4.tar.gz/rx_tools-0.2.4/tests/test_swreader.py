import ROOT

import rk.swreader as swrdr

#----------------------------
def get_sweights(year, trigger):
    if trigger == 'MTOS':
        picklepath='/publicfs/ucas/user/campoverde/EfficiencyMaps/sweights/v10.11tf.1.1.x.x.0_v1/{}_dt_trigger_weights_sweighted_KMM.pickle'.format(year)
        filepath='/publicfs/ucas/user/campoverde/Data/RK/data_mm/v10.11tf.a0v0x8y7z0.1.1.1.0.0/{}_reso.root'.format(year)
    else:
        picklepath='/publicfs/ucas/user/campoverde/EfficiencyMaps/sweights/v10.11tf.3.0.x.x.0_v1/{}_dt_trigger_weights_sweighted_KEE.pickle'.format(year)
        filepath='/publicfs/ucas/user/campoverde/Data/RK/data_ee/v10.11tf.a0v1x7y4z4.3.0.1.0.0/{}_reso.root'.format(year)
    
    rdr=swrdr.swreader(picklepath)
    
    df=ROOT.RDataFrame(trigger, filepath)
    df=df.Filter('pid_eff > 0.5')
    
    arr_event=df.AsNumpy(['eventNumber'])['eventNumber']
    
    df=rdr.attach_weights(df, 'sw_' +  trigger)

    df.Display().Print()
#----------------------------
l_year=['2011', '2012', '2015', '2016', '2017', '2018']
for year in l_year:
    get_sweights(year, 'MTOS')
    get_sweights(year, 'ETOS')
    get_sweights(year, 'HTOS')
    get_sweights(year, 'GTIS')

