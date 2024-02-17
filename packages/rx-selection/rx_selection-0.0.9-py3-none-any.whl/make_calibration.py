#!/usr/bin/env python3

from importlib.resources import files

import os
import json
import argparse

import utils_noroot       as utnr
import make_selection     as ms
import version_management as vmg

log=utnr.getLogger(__name__)

#-------------------------------------------
class data:
    l_year    = ['2011', '2012', '2015', '2016', '2017', '2018']
#-------------------------------------------
class calibration:
    log = utnr.getLogger(__name__)
    #-------------------------------------------
    def __init__(self):
        self.__l_kind = ['kin_cut', 'lzr_tag', 'hlt_tag']
        #The values are needed to deduce the channel (ee, mm) to read the HLT2 cut.
        #Beyond that, they are not meaningful
        self.__d_cut_kin = {'etos' : 'ETOS', 'gtis' : 'ETOS', 'gtis_inclusive' : 'ETOS', 'mtos' : 'MTOS'}
        self.__d_lzr_tag = {}
        if True:
            self.__d_lzr_tag['L0ElectronTIS'] = 'ETOS'
            self.__d_lzr_tag['L0ElectronHAD'] = 'ETOS'

            self.__d_lzr_tag['L0HadronMuMU' ] = 'MTOS'
            self.__d_lzr_tag['L0HadronMuTIS'] = 'MTOS'
            self.__d_lzr_tag['L0HadronElEL']  = 'ETOS'
            self.__d_lzr_tag['L0HadronElTIS'] = 'ETOS'

            self.__d_lzr_tag['L0TIS_EM']      = 'ETOS'
            self.__d_lzr_tag['L0TIS_MH']      = 'ETOS'
            self.__d_lzr_tag['L0TIS_MM']      = 'MTOS'

            self.__d_lzr_tag['L0MuonTIS']     = 'MTOS'
            self.__d_lzr_tag['L0MuonMU1']     = 'MTOS'
            self.__d_lzr_tag['L0MuonMU2']     = 'MTOS'
            self.__d_lzr_tag['L0MuonHAD']     = 'MTOS'
            self.__d_lzr_tag['L0MuonALL1']    = 'MTOS'
            self.__d_lzr_tag['L0MuonALL2']    = 'MTOS'
        self.__d_hlt_tag = {'HLT_MTOS' : 'mtos', 'HLT_ETOS' : 'etos', 'HLT_HTOS' : 'htos', 'HLT_GTIS' : 'gtis'}

        self.__l_year    = data.l_year 
    #-------------------------------------------
    def __get_kin_cut(self):
        d_data = {}
        for tag, trigger in self.__d_cut_kin.items():
            d_tag = {}
            for year in self.__l_year:
                lzr = ms.get(   tag, trigger, 'central', year)
                d_tag[year] = lzr

            d_data[tag] = d_tag

        return d_data
    #-------------------------------------------
    def __lzr_tag(self, tag):
        if   tag == 'L0MuonTIS':
            cut = '(B_L0ElectronDecision_TIS || B_L0HadronDecision_TIS || B_L0PhotonDecision_TIS)'
        elif tag == 'L0MuonMU1':
            pt_threshold = 1000
            cut = '(L1_L0MuonDecision_TOS  && L1_PT > {:.0f} && L0Data_Muon1_Pt >= threshold_mu)'.format(pt_threshold)
        elif tag == 'L0MuonMU2':
            pt_threshold = 1000
            cut = '(L2_L0MuonDecision_TOS  && L2_PT > {:.0f} && L0Data_Muon1_Pt >= threshold_mu)'.format(pt_threshold)
        elif tag == 'L0MuonHAD':
            cut = ms.get('htos_inclusive', trigger=None, q2bin=None, year=None, pt_threshold=2000)
        elif tag == 'L0MuonALL1':
            cut_1 = self.__lzr_tag('L0MuonTIS')
            cut_2 = self.__lzr_tag('L0MuonMU1')
            cut_3 = self.__lzr_tag('L0MuonHAD')

            cut   = '({} || {} || {})'.format(cut_1, cut_2, cut_3)
        elif tag == 'L0MuonALL2':
            cut_1 = self.__lzr_tag('L0MuonTIS')
            cut_2 = self.__lzr_tag('L0MuonMU2')
            cut_3 = self.__lzr_tag('L0MuonHAD')

            cut   = '({} || {} || {})'.format(cut_1, cut_2, cut_3)
        #-------------------------
        elif tag == 'L0ElectronTIS':
            cut = '(B_L0HadronDecision_TIS || B_L0MuonDecision_TIS)'
        elif tag == 'L0ElectronHAD':
            cut = ms.get('htos_inclusive', trigger=None, q2bin=None, year=None, pt_threshold=2000)
        #-------------------------
        elif tag == 'L0HadronMuMU':
            cut = ms.get('mtos'          , trigger=None, q2bin=None, year=None, pt_threshold=1000)
        elif tag == 'L0HadronMuTIS':
            cut = ms.get('gtis_inclusive', trigger=None, q2bin=None, year=None)
        elif tag == 'L0HadronElEL':
            cut = ms.get('etos'          , trigger=None, q2bin=None, year=None, pt_threshold=2000)
        elif tag in ['L0HadronMuTIS', 'L0HadronElTIS']:
            cut = ms.get('gtis_inclusive', trigger=None, q2bin=None, year=None)
        #-------------------------
        elif tag == 'L0TIS_MM':
            cut = ms.get('mtos'          , trigger=None, q2bin=None, year=None, pt_threshold=800)
        elif tag == 'L0TIS_EM':
            cut = ms.get('etos'          , trigger=None, q2bin=None, year=None, pt_threshold=2000)
        elif tag == 'L0TIS_MH':
            cut = '(B_L0MuonDecision_TIS)'
        #-------------------------
        else:
            self.log.error('Invalid tag: ' + tag)
            raise

        return cut
    #-------------------------------------------
    def __get_lzr_tag(self):
        d_data = {}
        for tag, trigger in self.__d_lzr_tag.items():
            d_tag = {}
            for year in self.__l_year:
                lzr = self.__lzr_tag(tag)
                d_tag[year] = lzr

            d_data[tag] = d_tag

        return d_data
    #-------------------------------------------
    def __get_lzr_prb(self):
        d_data = {}

        d_data['L0MuonMU1']     = '(L1_L0MuonDecision_TOS == 1)'
        d_data['L0MuonMU2']     = '(L2_L0MuonDecision_TOS == 1)'

        d_data['L0ElectronEL1'] = '(L1_L0ElectronDecision_TOS  == 1)'
        d_data['L0ElectronEL2'] = '(L2_L0ElectronDecision_TOS  == 1)'

        d_data['L0ElectronFAC'] = '(L1_L0ElectronDecision_TOS  == 1 || L2_L0ElectronDecision_TOS == 1)'
        d_data['L0Hadron']      = '(H_L0HadronDecision_TOS == 1)'

        d_data['L0TIS_EM']      = '(B_L0PhotonDecision_TIS || B_L0ElectronDecision_TIS)'
        d_data['L0TIS_MH']      = '(B_L0HadronDecision_TIS || B_L0MuonDecision_TIS    )'

        return d_data
    #-------------------------------------------
    def __get_hlt_prb(self):
        d_data = {}
        for tag, trig in [('HLTMuon', 'MTOS'), ('HLTElectron', 'ETOS')]:
            d_year = {}
            for year in self.__l_year:
                hlt1 = ms.get('hlt1', trig, q2bin=None, year=year)
                hlt2 = ms.get('hlt2', trig, q2bin=None, year=year)
                hlt  = '({} && {})'.format(hlt1, hlt2)

                d_year[year] = hlt

            d_data[tag] = d_year

        return d_data
    #-------------------------------------------
    def __get_hlt_tag(self):
        d_data = {}
        hlt = '(B_Hlt1Phys_TIS && B_Hlt2Phys_TIS)'
        for tag, trg in self.__d_hlt_tag.items():
            lzr = ms.get(trg, trigger=None, q2bin=None, year=None, pt_threshold = 0)
            cut = '({} && {})'.format(hlt, lzr)
            d_data[tag] = cut

        return d_data
    #-------------------------------------------
    def get_selection(self, kind):
        if   kind == 'kin_cut':
            d_sel = self.__get_kin_cut()
        elif kind == 'lzr_tag':
            d_sel = self.__get_lzr_tag()
        elif kind == 'lzr_prb':
            d_sel = self.__get_lzr_prb()
        elif kind == 'hlt_tag':
            d_sel = self.__get_hlt_tag()
        elif kind == 'hlt_prb':
            d_sel = self.__get_hlt_prb()
        else:
            self.log.error('Kind {} not found in:'.format(kind))
            self.log.error(self.__l_kind)
            raise

        return d_sel
#-------------------------------------------
def get_next_path():
    sel_dir   = files('selection_data')
    file_path = vmg.get_latest_file(dir_path=f'{sel_dir}', wc='calibration_v*.json')
    file_name = os.path.basename(file_path)
    old_ver   = file_name.replace('calibration_', '').replace('.json', '')
    nxt_ver   = vmg.get_next_version(old_ver)
    file_path = f'{sel_dir}/calibration_{nxt_ver}.json'

    return file_path
#-------------------------------------------
def get_args():
    parser = argparse.ArgumentParser(description='Used to make JSON file with selection used for calibration maps')
    parser.add_argument('-y','--year', nargs='+', help='Years', default=data.l_year, choices=data.l_year)
    args = parser.parse_args()

    data.l_year = args.year
#-------------------------------------------
def main():
    d_sel       = {}    

    obj = calibration()
    d_sel['kin_cut'] = obj.get_selection('kin_cut')

    d_sel['lzr_tag'] = obj.get_selection('lzr_tag')
    d_sel['lzr_prb'] = obj.get_selection('lzr_prb')

    d_sel['hlt_tag'] = obj.get_selection('hlt_tag')
    d_sel['hlt_prb'] = obj.get_selection('hlt_prb')

    file_path = get_next_path()
    utnr.dump_json(d_sel, file_path, sort_keys=True)
#-------------------------------------------
if __name__ == '__main__':
    get_args()
    main()

