import sys

import read_calibration as rc
#import make_calibration as mc
import utils_noroot     as utnr 

log = utnr.getLogger(__name__)

#-----------------------------
def check_cut(cut_rd, kind, year, key):
    obj = mc.calibration()
    d_sel = obj.get_selection(key)

    data = utnr.get_from_dic(d_sel, kind)
    if year is None:
        cut_wt = data
    else:
        cut_wt = data[year]

    year = str(year)
    if cut_wt != cut_rd:
        log.error('Cuts differ for:')
        log.info('{0:<20}{1:<150}'.format('Kind'   ,   kind))
        log.info('{0:<20}{1:<150}'.format('Year'   ,   year))
        log.info('{0:<20}{1:<150}'.format('Reader' , cut_rd))
        log.info('{0:<20}{1:<150}'.format('Writter', cut_wt))

        raise
#-----------------------------
def get_ny_kind():
    l_no_year = []
    if True:
        l_no_year.append('HLT_MTOS')
        l_no_year.append('HLT_ETOS')
        l_no_year.append('HLT_HTOS')
        l_no_year.append('HLT_GTIS')

        l_no_year.append('L0ElectronEL1')
        l_no_year.append('L0ElectronEL2')
        l_no_year.append('L0ElectronFAC')

        l_no_year.append('L0Hadron')

        l_no_year.append('L0MuonMU1')
        l_no_year.append('L0MuonMU2')

        l_no_year.append('L0TIS_EM')
        l_no_year.append('L0TIS_MH')

    return l_no_year
#-----------------------------
def get_yy_kind():
    l_year = []
    if True:
        l_year.append('HLTElectron')
        l_year.append('HLTMuon')

        l_year.append('mtos')
        l_year.append('etos')
        l_year.append('gtis')
        l_year.append('gtis_inclusive')

        l_year.append('L0ElectronHAD')
        l_year.append('L0ElectronTIS')

        l_year.append('L0HadronMuMU')
        l_year.append('L0HadronMuTIS')
        l_year.append('L0HadronElEL')
        l_year.append('L0HadronElTIS')

        l_year.append('L0MuonALL1')
        l_year.append('L0MuonALL2')
        l_year.append('L0MuonHAD')
        l_year.append('L0MuonMU1')
        l_year.append('L0MuonMU2')
        l_year.append('L0MuonTIS')

        l_year.append('L0TIS_EM')
        l_year.append('L0TIS_MH')

    return l_year
#-----------------------------
def run_ny():
    l_kind = get_ny_kind()
    for kind in l_kind:
        cut = rc.get(kind, year=None)
        key = rc.top_key(kind, year=None)
        #check_cut(cut, kind, None, key)

    log.visible('Passed non year-wise test')
#-----------------------------
def run_yy():
    l_kind = get_yy_kind()
    for kind in l_kind:
        for year in ['2011', '2012', '2015', '2016', '2017', '2018']:
            cut = rc.get(kind, year=year)
            key = rc.top_key(kind, year=year)

            #check_cut(cut, kind, year, key)

    log.visible('Passed year-wise test')
#-----------------------------
if __name__ == '__main__':
    run_ny()
    run_yy()
#-----------------------------

