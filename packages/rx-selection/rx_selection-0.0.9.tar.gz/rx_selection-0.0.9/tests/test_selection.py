import sys
import ROOT

import read_selection as rs
import make_selection as ms

import utils_noroot   as utnr

log = utnr.getLogger(__name__)
#-----------------------------------------------------
def compare_cuts(cut_rs, cut_ms):
    if cut_rs != cut_ms:
        log.error('{0:<10}{1:<100}'.format('Reader', cut_rs))
        log.error('{0:<10}{1:<100}'.format('Maker' , cut_ms))
        raise
#-----------------------------------------------------
def dump_line(ofile, quantity, trigger, q2bin, year = None):
    val = rs.get(quantity, trigger, q2bin=q2bin, year = year)

    if year is None:
        year = 'None'

    line = '{0:<20}{1:<20}{2:<20}{3:<20}{4:<200}'.format(quantity, trigger, q2bin, year, val)

    ofile.write(line + '\n')
#-----------------------------------------------------
def test_run():
    l_hlt    = ['hlt1', 'hlt2']
    l_no_hlt = ['bdt', 'cascade', 'kinematics', 'mass', 'nspd', 'pid', 'q2', 'ghost']
    l_ee_cut = ['etos', 'gtis', 'xyecal', 'calo_rich']
    l_mm_cut = ['mtos', 'rich', 'acceptance'] 
    l_ee_trg = ['ETOS', 'HTOS', 'GTIS']

    l_q2bin  = ['central', 'jpsi', 'psi2', 'high']
    l_year   = ['2011', '2012', '2015', '2016', '2017', '2018']
    l_dset   = ['r1', 'r2p1']

    file_dir = utnr.make_dir_path('tests/read_selection/run')
    file_path= '{}/{}.txt'.format(file_dir, 'python')

    ofile = open(file_path, 'w')
    #-----------------------------------------------------
    #Non HLT
    #-----------------------------------------------------
    for quantity in l_no_hlt + l_ee_cut:
        for q2bin in l_q2bin:
            for trigger in l_ee_trg:
                for year in l_year + l_dset:
                    dump_line(ofile, quantity, trigger, q2bin=q2bin, year=year)

    for quantity in l_no_hlt + l_mm_cut:
        for q2bin in l_q2bin:
            for year in l_year + l_dset:
                dump_line(ofile, quantity, 'MTOS', q2bin=q2bin, year=year)
    #-----------------------------------------------------
    #HLT
    #-----------------------------------------------------
    for quantity in l_hlt:
        for q2bin in l_q2bin:
            for year in l_year:
                for trigger in l_ee_trg + ['MTOS']:
                    dump_line(ofile, quantity, trigger, q2bin=q2bin, year = year)
    #-----------------------------------------------------
    log.visible('Passed test_run')
    log.visible('Dumped to ' + file_path)

    ofile.close()
#-----------------------------------------------------
def test_cmp():
    l_hlt    = ['hlt1', 'hlt2']
    l_no_hlt = ['bdt', 'cascade', 'kinematics', 'mass', 'nspd', 'pid', 'q2', 'ghost']
    l_ee_cut = ['etos', 'gtis', 'xyecal', 'calo_rich']
    l_mm_cut = ['mtos', 'rich', 'acceptance'] 
    l_ee_trg = ['ETOS', 'HTOS', 'GTIS']

    l_q2bin  = ['central', 'jpsi', 'psi2', 'high']
    l_year   = ['2011', '2012', '2015', '2016', '2017', '2018']
    l_dset   = ['r1', 'r2p1']
    #-----------------------------------------------------
    #Non HLT
    #-----------------------------------------------------
    for quantity in l_no_hlt + l_ee_cut:
        for q2bin in l_q2bin:
            for trigger in l_ee_trg:
                for year in l_year + l_dset:
                    cut_rs = rs.get(quantity, trigger, q2bin=q2bin, year=year)
                    cut_ms = ms.get(quantity, trigger, q2bin=q2bin, year=year)
                    compare_cuts(cut_rs, cut_ms)

    for quantity in l_no_hlt + l_mm_cut:
        for q2bin in l_q2bin:
            for year in l_year + l_dset:
                cut_rs = rs.get(quantity, 'MTOS', q2bin=q2bin, year=year)
                cut_ms = ms.get(quantity, 'MTOS', q2bin=q2bin, year=year)
                compare_cuts(cut_rs, cut_ms)
    #-----------------------------------------------------
    #HLT
    #-----------------------------------------------------
    for quantity in l_hlt:
        for q2bin in l_q2bin:
            for year in l_year:
                for trigger in l_ee_trg + ['MTOS']:
                    cut_rs = rs.get(quantity, trigger, q2bin=q2bin, year = year)
                    cut_ms = ms.get(quantity, trigger, q2bin=q2bin, year = year)
                    compare_cuts(cut_rs, cut_ms)

    log.visible('Passed test_cmp')
#-----------------------------------------------------
if __name__ == '__main__':
    test_run()
    test_cmp()
#-----------------------------------------------------

