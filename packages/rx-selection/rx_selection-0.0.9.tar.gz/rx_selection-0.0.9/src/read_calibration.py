import os
import json

import utils_noroot as utnr
import logzero

from logzero             import logger          as log
from importlib.resources import files
from version_management  import get_latest_file
#--------------------------
class read_calibration:
    log = utnr.getLogger(__name__)
    #--------------------------
    def __init__(self):
        self.__cal_path = None 

        #Dic between cut and top key for year wise cuts
        self.__d_top_yy = {}
        if True:
            self.__d_top_yy['etos']           = 'kin_cut'
            self.__d_top_yy['mtos']           = 'kin_cut'
            self.__d_top_yy['gtis']           = 'kin_cut'
            self.__d_top_yy['gtis_inclusive'] = 'kin_cut'
            #--------------------------
            self.__d_top_yy['HLTElectron']    = 'hlt_prb'
            self.__d_top_yy['HLTMuon']        = 'hlt_prb'

            self.__d_top_yy['HLT_MTOS']       = 'hlt_tag'
            self.__d_top_yy['HLT_ETOS']       = 'hlt_tag'
            self.__d_top_yy['HLT_HTOS']       = 'hlt_tag'
            self.__d_top_yy['HLT_GTIS']       = 'hlt_tag'
            #--------------------------
            self.__d_top_yy['L0ElectronHAD']  = 'lzr_tag'
            self.__d_top_yy['L0ElectronTIS']  = 'lzr_tag'

            self.__d_top_yy['L0HadronMuMU']   = 'lzr_tag'
            self.__d_top_yy['L0HadronMuTIS']  = 'lzr_tag'
            self.__d_top_yy['L0HadronElEL']   = 'lzr_tag'
            self.__d_top_yy['L0HadronElTIS']  = 'lzr_tag'

            self.__d_top_yy['L0MuonALL1']     = 'lzr_tag'
            self.__d_top_yy['L0MuonALL2']     = 'lzr_tag'
            self.__d_top_yy['L0MuonHAD']      = 'lzr_tag'
            self.__d_top_yy['L0MuonMU1']      = 'lzr_tag'

            self.__d_top_yy['L0MuonMU2']      = 'lzr_tag'
            self.__d_top_yy['L0MuonTIS']      = 'lzr_tag'

            self.__d_top_yy['L0TIS_EM']       = 'lzr_tag'
            self.__d_top_yy['L0TIS_MH']       = 'lzr_tag'
            self.__d_top_yy['L0TIS_MM']       = 'lzr_tag'

        #Dic between cut and top key for non-year wise cuts
        self.__d_top_ny = {}
        if True:
            self.__d_top_ny['L0ElectronEL1']  = 'lzr_prb'
            self.__d_top_ny['L0ElectronEL2']  = 'lzr_prb'
            self.__d_top_ny['L0ElectronFAC']  = 'lzr_prb'
            self.__d_top_ny['L0Hadron']       = 'lzr_prb'

            self.__d_top_ny['L0MuonMU1']      = 'lzr_prb'
            self.__d_top_ny['L0MuonMU2']      = 'lzr_prb'

            self.__d_top_ny['L0TIS_EM']       = 'lzr_prb'
            self.__d_top_ny['L0TIS_MH']       = 'lzr_prb'

        self.__d_data      = None

        self.__initialized = False
    #--------------------------
    def __initialize(self):
        if self.__initialized:
            return

        self.__cal_path = self._get_cal_path()
        self.__d_data   = utnr.load_json(self.__cal_path)

        logzero.loglevel(logzero.INFO)

        self.__initialized = True
    #--------------------------
    def _get_cal_path(self):
        dat_dir = files('selection_data')

        cal_path = get_latest_file(dir_path = dat_dir, wc='calibration_*.json')

        if not os.path.isfile(cal_path):
            log.error(f'Cannot find: {cal_path}')
            raise
        else:
            log.debug(f'Using: {cal_path}')

        return cal_path
    #--------------------------
    def get_top_key(self, kind, year):
        key_yy = utnr.get_from_dic(self.__d_top_yy , kind, fall_back='', now=True)
        key_ny = utnr.get_from_dic(self.__d_top_ny , kind, fall_back='', now=True)

        if   key_yy != '' and key_ny != '' and year is     None:
            key = key_ny
        elif key_yy != '' and key_ny != '' and year is not None:
            key = key_yy
        elif key_yy != '':
            key = key_yy
        elif key_ny != '':
            key = key_ny
        else:
            self.log.error(f'Cannot retrieve right top key for kind/year: {kind}/{year}')
            raise

        return key
    #--------------------------
    def get(self, kind, year=None):
        self.__initialize()

        key   = self.get_top_key (kind,          year)
        d_tag = utnr.get_from_dic(self.__d_data,  key)

        obj   = utnr.get_from_dic(        d_tag, kind)
        year  = str(year)
        if   type(obj) == dict and year is not None:
            cut = utnr.get_from_dic(obj, year)
        elif type(obj) == str:
            cut = obj
        else:
            self.log.error(f'Cannot extract cut from object')
            self.log.error(f'Obj : {obj}')
            self.log.error(f'Year: {year}')
            raise

        return cut
#--------------------------
def get(kind, year=None):
    obj=read_calibration()
    cut=obj.get(kind, year)

    return cut
#--------------------------
def top_key(kind, year=None):
    obj=read_calibration()
    key=obj.get_top_key(kind, year)

    return key 
#--------------------------

