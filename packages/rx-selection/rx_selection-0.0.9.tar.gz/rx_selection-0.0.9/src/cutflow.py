import ROOT

#------------------------------------
def renameVars(cut):
    cut=cut.replace("e_plus"    , "L1")
    cut=cut.replace("e_minus"   , "L2")
    cut=cut.replace("B_plus"    , "B" )
    cut=cut.replace("K_Kst"     , "H" )
    cut=cut.replace("J_psi_1S_M", "Jpsi")

    return cut
#------------------------------------
ROOT.gSystem.Load("/afs/ihep.ac.cn/users/c/campoverde/storage/Test/preselection/lib/libpres.so")
ROOT.gROOT.ProcessLine("#include \"include/getPreselection.h\"")
#------------------------------------
cut=ROOT.getCommonPreselMuMuNoPidNoIsMuonCutRun2()
cut=renameVars(cut)
print(cut)

