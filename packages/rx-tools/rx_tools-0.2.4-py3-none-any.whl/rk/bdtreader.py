import ROOT
import os
import numpy
import tqdm

import utils_noroot as utnr

log=utnr.getLogger(__name__)

class reader:
    def __init__(self, bdtdir):
        self.bdtdir      = bdtdir
        self.initialized = False
        self.l_head      = []
        self.l_lib       = []

        if True:
            self.l_head.append('/publicfs/ucas/user/campoverde/bplusfit/include/bdtreader.h')
            self.l_head.append('/publicfs/ucas/user/campoverde/tools/include/utils.h')
            self.l_head.append('/publicfs/ucas/user/campoverde/tools/include/tmva_reader.h')

            self.l_lib.append('/publicfs/ucas/user/campoverde/bplusfit/lib/libbplusfit.so')
            self.l_lib.append('/publicfs/ucas/user/campoverde/tools/lib/libtools.so')

        log.visible('Using classifier in ' + self.bdtdir)
    #------------------------------------------
    def __checkFiles(self):
        for filepath in self.l_head + self.l_lib:
            if not os.path.isfile(filepath):
                log.error('File {} not found'.format(filepath))
                exit(1)

        if not os.path.isdir(self.bdtdir):
            log.error('Directory {} not found'.format(self.bdtdir))
            exit(1)
    #------------------------------------------
    def __loadLibraries(self):
        self.__checkFiles()
        for libpath in self.l_lib:
            ROOT.gSystem.Load(libpath)

        for headpath in self.l_head:
            ROOT.gInterpreter.ProcessLine('#include "{}"'.format(headpath))
    #------------------------------------------
    def __initialize(self):
        if self.initialized:
            return

        self.__loadLibraries()

        self.initialized = True
    #------------------------------------------
    def predict_weights(self, *arg):
        if   len(arg) == 2:
            tree    = arg[0]
            trigger = arg[1]
        elif len(arg) == 3:
            ifile=ROOT.TFile(arg[0])
            tree=ifile.Get(arg[1])
            trigger=arg[2]

            log.visible('-----------------------------------')
            log.visible('Predicting BDT scores for:')
            log.visible('')
            log.visible('{0:<20}{1:<100}'.format('Filepath', arg[0]))
            log.visible('{0:<20}{1:<100}'.format('Treename', arg[1]))
            log.visible('{0:<20}{1:<100}'.format('Trigger' , arg[2]))
            log.visible('-----------------------------------')
        else:
            log.error('Invalid arguments: ' + str(arg))
            exit(1)

        self.__initialize()

        self.cpp_reader = ROOT.bdtreader(self.bdtdir, tree, trigger)

        l_bdt_score=[]
        nentries=tree.GetEntries()

        log.info('Predicting BDT weights')
        for entry in tqdm.tqdm(tree, total=nentries):
            bdt_score = self.cpp_reader.evaluate()
            l_bdt_score.append(bdt_score)

        return numpy.array(l_bdt_score)
    #------------------------------------------
    def get_distributions(self, suffix, nbins=100):
        return self.cpp_reader.get_distributions(suffix, nbins)
    #------------------------------------------

