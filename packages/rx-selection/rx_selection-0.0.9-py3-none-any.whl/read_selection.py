import json
import os
import version_management as vman

from importlib.resources import files

from log_store import log_store

log = log_store.add_logger(name='rk_selection:read_selection')
#------------------------------------------
class read_selection:
    def __init__(self, quantity, trigger, q2bin=None, year=None):
        self.__quantity    = quantity
        self.__trigger     = trigger
        self.__q2bin       = q2bin
        self.__year        = year
 
        self.__sel_path    = None
        self.__initialized = False
        self.__d_data      = {}

        self.__l_ee_trig   = ['ETOS', 'HTOS', 'GTIS', 'GTIS_ee']
        self.__l_mm_trig   = ['MTOS', 'GTIS_mm']
        self.__l_trigger   = self.__l_ee_trig +  self.__l_mm_trig 
        self.__l_q2bin     = ['central', 'high', 'jpsi', 'psi2']
        self.__l_year      = ['2011', '2012', '2015', '2016', '2017', '2018']

        #Cuts
        self.__l_common    = ['bdt', 'bdt_cmb', 'bdt_prc', 'cascade', 'kinematics', 'mass', 'nspd', 'pid', 'q2', 'ghost']
        self.__l_ee_cut    = ['etos', 'htos', 'gtis', 'hlt1', 'hlt2', 'xyecal', 'calo_rich'] 
        self.__l_mm_cut    = ['L0', 'Hlt1', 'Hlt2', 'rich', 'acceptance', 'jpsi_misid'] 
        self.__l_hl1trig   = ['hlt1', 'Hlt1']
        self.__l_hl2trig   = ['hlt2', 'Hlt2']
        self.__l_hlttrig   = self.__l_hl1trig + self.__l_hl2trig 

        self.__l_cby_trig  = ['bdt', 'bdt_cmb', 'bdt_prc']
        self.__l_cby_q2bin = ['q2', 'mass']
        self.__l_cby_year  = ['Hlt1', 'Hlt2', 'hlt1', 'hlt2']
 
        self.__channel     = None
    #------------------------------------------
    def __initialize(self):
        if self.__initialized:
            return

        sel_dir = files('selection_data')
        self.__sel_path = vman.get_latest_file(dir_path=sel_dir, wc='selection_v*.json')
        log.debug(f'Picking up selection from: {self.__sel_path}')
 
        self.__check_args()
        self.__channel = self.__get_channel() 
 
        if not os.path.isfile(self.__sel_path):
            log.error(f'Cannot find: {self.__sel_path}')
            raise
 
        d_tmp = json.load(open(self.__sel_path))
        try:
            self.__d_data = d_tmp[self.__channel]
        except:
            log.error(f'Channel {self.__channel} not found in selection file {self.__sel_path}')
            raise
 
        if self.__quantity not in self.__d_data:
            log.error(f'Unsupported quantity: {self.__quantity} for channel {self.__channel}')
            raise
 
        self.__initialized = True
    #------------------------------------------
    def __check_args(self): 
        self.__rename_quantity()
        #---------------------
        if self.__year    not in self.__l_year    + ['none']: 
            log.error(f'Invalid year bin: {self.__year}')
            log.error(f'Allowed: {self.__l_year}')
            raise

        if self.__q2bin   not in self.__l_q2bin   + ['none']: 
            log.error(f'Invalid q2 bin: {self.__q2bin}')
            log.error(f'Allowed: {self.__l_q2bin}')
            raise
 
        if self.__trigger not in self.__l_trigger + ['none']: 
            log.error(f'Invalid trigger: {self.__trigger}')
            log.error(f'Allowed: {self.__l_trigger}')
            raise
        #---------------------
        if self.__trigger != 'MTOS' and self.__quantity not in self.__l_common + self.__l_ee_cut:
            log.error(f'Cut {self.__quantity} not found for trigger {self.__trigger}')
            raise
 
        if self.__trigger == 'MTOS' and self.__quantity not in self.__l_common + self.__l_mm_cut:
            log.error(f'Cut {self.__quantity} not found for trigger {self.__trigger}')
            raise
        #---------------------
        if self.__quantity in self.__l_hl1trig and self.__year not in self.__l_year: 
            log.error('HLT1 was requested, but no valid year was provided')
            raise

        if self.__quantity in self.__l_hl2trig and (self.__year not in self.__l_year or self.__trigger not in self.__l_trigger): 
            log.error('HLT2 was requested, but no valid year or trigger was provided')
            raise
    #------------------------------------------
    def __get_channel(self):
        if   self.__trigger in self.__l_ee_trig:
            chan = 'ee'
        elif self.__trigger in self.__l_mm_trig:
            chan = 'mm'
        else:
            log.error(f'Invalid trigger {self.__trigger}')
            log.error(self.__l_ee_trig)
            log.error(self.__l_mm_trig)
            raise

        return chan
    #------------------------------------------
    def __rename_quantity(self):
        if self.__quantity == 'mtos':
            self.__quantity = 'L0'

        if self.__quantity == 'hlt1' and self.__trigger == 'MTOS':
            self.__quantity = 'Hlt1'

        if self.__quantity == 'hlt2' and self.__trigger == 'MTOS':
            self.__quantity = 'Hlt2'
    #------------------------------------------
    def show(self):
        self.__initialize()
 
        log.info(json.dumps(self.__d_data, indent=4, sort_keys=True))
    #------------------------------------------
    def get(self):
        self.__initialize()
 
        obj = self.__d_data[self.__quantity]
        if   self.__quantity in self.__l_cby_trig:
            try:
                cut  = obj[self.__trigger]
            except:
                log.error(f'Invalid trigger: {self.__trigger}')
                log.error(obj.keys())
                raise
        elif self.__quantity in self.__l_cby_q2bin:
            try:
                cut  = obj[self.__q2bin]
            except:
                log.error(f'Invalid q2 bin: {self.__q2bin}')
                log.error(obj.keys())
                raise
        elif self.__quantity in self.__l_cby_year:
            try:
                cut  = obj[self.__year]
            except:
                log.error(f'Invalid year: {self.__year}')
                log.errof(obj.keys())
                raise
        else:
            cut = obj

        if type(cut) != str:
            log.error(f'Cannot extract string for cut: {self.__quantity}')
            log.error(cut)
            raise

        return cut
#------------------------------------------
def get_dset(quantity, trigger, q2bin=None, year_1=None, year_2=None):
    c_11 = get(quantity, trigger, q2bin=q2bin, year=year_1)
    c_12 = get(quantity, trigger, q2bin=q2bin, year=year_2)

    if c_11 == c_12:
        return c_11
    else:
        log.error('Cuts between years differ')
        log.error(f'{"Quantity":<20}{quantity:<50}')
        log.error(f'{"Tritter ":<20}{trigger :<50}')
        log.error(f'{"Q2 bin  ":<20}{q2bin   :<50}')
        log.error(f'Cut {year_1}: {c_11}')
        log.error(f'Cut {year_2}: {c_12}')
        raise
#------------------------------------------
def get(quantity, trigger, q2bin=None, year=None):
    if   year == 'r1':
        cut = get_dset(quantity, trigger, q2bin = q2bin, year_1 = '2011', year_2 = '2012')
    elif year == 'r2p1':
        cut = get_dset(quantity, trigger, q2bin = q2bin, year_1 = '2015', year_2 = '2016')
    else:
        rs  = read_selection(quantity, trigger, q2bin=q2bin, year=year)
        cut = rs.get()

    return cut
#------------------------------------------
def get_truth(event_type):
    if isinstance(event_type, int):
        event_type=str(event_type)

    if     event_type in ['data_ee', 'data_mm', 'cmb_ss', 'cmb_em']:
        cut = '(1)'
    elif   event_type == '12113001' or event_type == '12113002' or event_type == 'sign_mm':
        #rare mumu
        cut= 'TMath::Abs(B_TRUEID) == 521 && TMath::Abs(L1_TRUEID) == 13 && TMath::Abs(L2_TRUEID) == 13 && TMath::Abs(L1_MC_MOTHER_ID) == 521 && TMath::Abs(L2_MC_MOTHER_ID) == 521 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 521'
    elif event_type == '12123002' or event_type == '12123003' or event_type == '12123005' or event_type == 'sign_ee':
        #rare ee
        cut= 'TMath::Abs(B_TRUEID) == 521 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 521 && TMath::Abs(L2_MC_MOTHER_ID) == 521 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 521'
    elif event_type == '12143001' or event_type == 'ctrl_mm':
        #reso Jpsi mumu
        cut= 'TMath::Abs(B_TRUEID) == 521 && TMath::Abs(Jpsi_TRUEID) == 443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 521 && TMath::Abs(L1_TRUEID) == 13 && TMath::Abs(L2_TRUEID) == 13 && TMath::Abs(L1_MC_MOTHER_ID) == 443 && TMath::Abs(L2_MC_MOTHER_ID) == 443 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 521'#reso Jpsi mumu
    elif event_type == '12153001' or event_type == 'ctrl_ee':
        #reso Jpsi ee
        cut= 'TMath::Abs(B_TRUEID) == 521 && TMath::Abs(Jpsi_TRUEID) == 443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 521 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 443 && TMath::Abs(L2_MC_MOTHER_ID) == 443 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 521'#reso Jpsi ee
    elif event_type == '12143020' or event_type == 'psi2_mm':
        #reso Psi mumu
        cut= 'TMath::Abs(B_TRUEID) == 521 && TMath::Abs(Jpsi_TRUEID) == 100443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 521 && TMath::Abs(L1_TRUEID) == 13 && TMath::Abs(L2_TRUEID) == 13 && TMath::Abs(L1_MC_MOTHER_ID) == 100443 && TMath::Abs(L2_MC_MOTHER_ID) == 100443 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 521'#reso Psi mumu
    elif event_type == '12153011' or event_type == '12153012' or event_type == 'psi2_ee':
        #reso Psi ee, 12153011 corresponds to buggy sample, 12153012 to fixed one
        cut= 'TMath::Abs(B_TRUEID) == 521 && TMath::Abs(Jpsi_TRUEID) == 100443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 521 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 100443 && TMath::Abs(L2_MC_MOTHER_ID) == 100443 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 521'#reso Psi ee
    elif event_type == '12143010' or event_type == 'ctrl_pi_mm':
        #reso jpsi pi mumu
        cut= 'TMath::Abs(B_TRUEID) == 521 && TMath::Abs(Jpsi_TRUEID) == 443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 521 && TMath::Abs(L1_TRUEID) == 13 && TMath::Abs(L2_TRUEID) == 13 && TMath::Abs(L1_MC_MOTHER_ID) == 443 && TMath::Abs(L2_MC_MOTHER_ID) == 443 && TMath::Abs(H_TRUEID) == 211 && TMath::Abs(H_MC_MOTHER_ID) == 521'#reso jpsi pi mumu
    elif event_type == '12153020' or event_type == 'ctrl_pi_ee':
        #reso jpsi pi ee
        cut= 'TMath::Abs(B_TRUEID) == 521 && TMath::Abs(Jpsi_TRUEID) == 443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 521 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 443 && TMath::Abs(L2_MC_MOTHER_ID) == 443 && TMath::Abs(H_TRUEID) == 211 && TMath::Abs(H_MC_MOTHER_ID) == 521'#reso jpsi pi ee
    #-------------------------------------------------------------
    elif event_type == '12952000' or event_type == 'bpXcHs_ee':
        #B+->XcHs
        ctrl_ee    = get_truth('ctrl_ee')
        psi2_ee    = get_truth('psi2_ee')
        ctrl_pi_ee = get_truth('ctrl_pi_ee')
        fail       = get_truth('fail')

        cut= f'!({fail}) && !({ctrl_ee}) && !({psi2_ee}) && !({ctrl_pi_ee})'
    elif event_type == '11453001' or event_type == 'bdXcHs_ee':
        #Bd->XcHs
        ctrl_ee    = get_truth('ctrl_ee')
        psi2_ee    = get_truth('psi2_ee')
        ctrl_pi_ee = get_truth('ctrl_pi_ee')
        fail       = get_truth('fail')

        cut= f'!({fail}) && !({ctrl_ee}) && !({psi2_ee}) && !({ctrl_pi_ee})'
    elif event_type == '12442001' or event_type == 'bpXcHs_mm':
        fail            = get_truth('fail')
        mm              = '((TMath::Abs(L1_TRUEID)==13) && (TMath::Abs(L2_TRUEID)==13))'
        ll_mother       = '(((TMath::Abs(Jpsi_TRUEID)==443) && (TMath::Abs(L1_MC_MOTHER_ID)==443) && (TMath::Abs(L2_MC_MOTHER_ID)==443)) || ((TMath::Abs(Jpsi_TRUEID)==100443) && (TMath::Abs(L1_MC_MOTHER_ID)==100443) && (TMath::Abs(L2_MC_MOTHER_ID)==100443)))'
        Bx              = "TMath::Abs(B_TRUEID)==521"
        Bx_psi2s_mother = "((TMath::Abs(Jpsi_MC_MOTHER_ID)==521 && TMath::Abs(Jpsi_TRUEID)==100443) || (TMath::Abs(Jpsi_TRUEID) != 100443))"

        cut             = f"!({fail}) && ({mm}) && ({ll_mother}) && ({Bx}) && ({Bx_psi2s_mother})"
    elif event_type == '11442001' or event_type == 'bdXcHs_mm':
        fail            = get_truth('fail')
        mm              = '((TMath::Abs(L1_TRUEID)==13) && (TMath::Abs(L2_TRUEID)==13))'
        ll_mother       = '(((TMath::Abs(Jpsi_TRUEID)==443) && (TMath::Abs(L1_MC_MOTHER_ID)==443) && (TMath::Abs(L2_MC_MOTHER_ID)==443)) || ((TMath::Abs(Jpsi_TRUEID)==100443) && (TMath::Abs(L1_MC_MOTHER_ID)==100443) && (TMath::Abs(L2_MC_MOTHER_ID)==100443)))'
        Bx              = "TMath::Abs(B_TRUEID)==511" 
        Bx_psi2s_mother = "((TMath::Abs(Jpsi_MC_MOTHER_ID)==511 && TMath::Abs(Jpsi_TRUEID)==100443) || (TMath::Abs(Jpsi_TRUEID) != 100443))"

        cut             = f"!({fail}) && ({mm}) && ({ll_mother}) && ({Bx}) && ({Bx_psi2s_mother})"
    elif event_type == '13442001' or event_type == 'bsXcHs_mm':
        fail            = get_truth('fail')
        mm              = '((TMath::Abs(L1_TRUEID)==13) && (TMath::Abs(L2_TRUEID)==13))'
        ll_mother       = '(((TMath::Abs(Jpsi_TRUEID)==443) && (TMath::Abs(L1_MC_MOTHER_ID)==443) && (TMath::Abs(L2_MC_MOTHER_ID)==443)) || ((TMath::Abs(Jpsi_TRUEID)==100443) && (TMath::Abs(L1_MC_MOTHER_ID)==100443) && (TMath::Abs(L2_MC_MOTHER_ID)==100443)))'
        Bx              = "TMath::Abs(B_TRUEID)==531" 
        Bx_psi2s_mother = "((TMath::Abs(Jpsi_MC_MOTHER_ID)==531 && TMath::Abs(Jpsi_TRUEID)==100443) || (TMath::Abs(Jpsi_TRUEID) != 100443))" 

        cut             = f"!({fail}) && ({mm}) && ({ll_mother}) && ({Bx}) && ({Bx_psi2s_mother})"
    #-------------------------------------------------------------
    elif event_type == '12155100':
        #exclusive jpsi kst ee Bu
        cut= 'TMath::Abs(B_TRUEID) == 521 && TMath::Abs(Jpsi_TRUEID) == 443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 521 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 443 && TMath::Abs(L2_MC_MOTHER_ID) == 443 && TMath::Abs(H_TRUEID) == 211 && (TMath::Abs(H_MC_MOTHER_ID) == 323 or TMath::Abs(H_MC_MOTHER_ID) == 310) && (TMath::Abs(H_MC_GD_MOTHER_ID) == 521 or TMath::Abs(H_MC_GD_MOTHER_ID) == 323)'#exclusive Jpsi kst ee
    elif event_type == '11154001':
        #exclusive jpsi kst ee Bd
        cut= 'TMath::Abs(B_TRUEID) == 511 && TMath::Abs(Jpsi_TRUEID) == 443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 511 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 443 && TMath::Abs(L2_MC_MOTHER_ID) == 443 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 313'#exclusive Jpsi kst ee Bd
    elif event_type == '13454001':
        #reso jpsi kst ee Bs
        cut= 'TMath::Abs(B_TRUEID) == 531 && TMath::Abs(Jpsi_TRUEID) == 443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 531 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 443 && TMath::Abs(L2_MC_MOTHER_ID) == 443 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 313'#reso Jpsi kst ee
    elif event_type == '11154011' or event_type == 'psi2Kstr_ee':
        #Bd->psi2S(=>ee) K*
        cut= 'TMath::Abs(B_TRUEID) == 511 && TMath::Abs(Jpsi_TRUEID) == 100443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 511 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 100443 && TMath::Abs(L2_MC_MOTHER_ID) == 100443 && TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 313'#reso Psi kst ee
    elif event_type == '11453012':
        #reso Psi X
        cut= 'TMath::Abs(B_TRUEID) == 511 && TMath::Abs(Jpsi_TRUEID) == 100443 && TMath::Abs(Jpsi_MC_MOTHER_ID) == 511 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 100443 && TMath::Abs(L2_MC_MOTHER_ID) == 100443'#reso Psi(ee) X
    elif event_type == '11124002' or event_type == 'bdks_ee':
        #Bd K*(k pi) ee.
        cut= 'TMath::Abs(B_TRUEID) == 511 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 511 && TMath::Abs(L2_MC_MOTHER_ID) == 511 && (TMath::Abs(H_TRUEID) == 321 or TMath::Abs(H_TRUEID) == 211) && TMath::Abs(H_MC_MOTHER_ID) == 313'
    elif event_type == '11124037' or event_type == 'bdkpi_ee':
        #Bd (k pi) ee.
        cut= 'TMath::Abs(B_TRUEID) == 511 && TMath::Abs(L1_TRUEID) == 11 && TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID) == 511 && TMath::Abs(L2_MC_MOTHER_ID) == 511 && (TMath::Abs(H_TRUEID) == 321 or TMath::Abs(H_TRUEID) == 211) && TMath::Abs(H_MC_MOTHER_ID) == 511'
    elif event_type == '12123445' or event_type == 'bpks_ee':
        #B+ -> K*+ ee
        cut= 'TMath::Abs(B_TRUEID) == 521 &&  TMath::Abs(L1_TRUEID) ==  11 &&  TMath::Abs(L2_TRUEID) == 11 &&  TMath::Abs(L1_MC_MOTHER_ID)  == 521 &&  TMath::Abs(L2_MC_MOTHER_ID) == 521 &&  TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 323'
    elif event_type == '13124006' or event_type == 'bsphi_ee':
        #Bs -> phi(-> KK) ee
        cut= 'TMath::Abs(B_TRUEID) == 531 &&  TMath::Abs(L1_TRUEID) ==  11 &&  TMath::Abs(L2_TRUEID) == 11 &&  TMath::Abs(L1_MC_MOTHER_ID)  == 531 &&  TMath::Abs(L2_MC_MOTHER_ID) == 531 &&  TMath::Abs(H_TRUEID) == 321 && TMath::Abs(H_MC_MOTHER_ID) == 333'
    elif event_type == '12425000' or event_type == 'bpk1_ee':
        #B+ -> K_1(K pipi) ee
        cut= 'TMath::Abs(B_TRUEID) == 521 &&  TMath::Abs(L1_TRUEID) ==  11 &&  TMath::Abs(L2_TRUEID) == 11 &&  TMath::Abs(L1_MC_MOTHER_ID)  == 521 &&  TMath::Abs(L2_MC_MOTHER_ID) == 521 &&  (TMath::Abs(H_TRUEID) == 321 || TMath::Abs(H_TRUEID) == 211) && (TMath::Abs(H_MC_MOTHER_ID) == 10323 || TMath::Abs(H_MC_MOTHER_ID) == 113 || TMath::Abs(H_MC_MOTHER_ID) == 223 || TMath::Abs(H_MC_MOTHER_ID) == 313)'
    elif event_type == '12425011' or event_type == 'bpk2_ee':
        #B+ -> K_2(X -> K pipi) ee
        cut= 'TMath::Abs(B_TRUEID) == 521 &&  TMath::Abs(L1_TRUEID) ==  11 &&  TMath::Abs(L2_TRUEID) == 11 &&  TMath::Abs(L1_MC_MOTHER_ID)  == 521 &&  TMath::Abs(L2_MC_MOTHER_ID) == 521 &&  (TMath::Abs(H_TRUEID) == 321 || TMath::Abs(H_TRUEID) == 211) && (TMath::Abs(H_MC_MOTHER_ID) ==   325 || TMath::Abs(H_MC_MOTHER_ID) == 113 || TMath::Abs(H_MC_MOTHER_ID) == 223 || TMath::Abs(H_MC_MOTHER_ID) == 313)' 
    elif event_type == '12155110':
        #B+->K*+ psi2S(-> ee)
        cut= 'TMath::Abs(B_TRUEID) == 521 &&  TMath::Abs(L1_TRUEID) ==  11 &&  TMath::Abs(L2_TRUEID) == 11 && TMath::Abs(L1_MC_MOTHER_ID)  == 100443 && TMath::Abs(L2_MC_MOTHER_ID) == 100443 && TMath::Abs(H_TRUEID) == 211 && (TMath::Abs(H_MC_MOTHER_ID) == 323 or TMath::Abs(H_MC_MOTHER_ID) == 310)'
    elif event_type == '12103025' or event_type == 'bpkpipi':
        #B+ -> K+ pi pi
        cut= 'TMath::Abs(B_TRUEID)  == 521 &&  TMath::Abs(L1_TRUEID)  == 211 &&  TMath::Abs(L2_TRUEID) == 211 &&  TMath::Abs(L1_MC_MOTHER_ID)  == 521 &&  TMath::Abs(L2_MC_MOTHER_ID) == 521 &&  TMath::Abs(H_TRUEID) == 321 &&  TMath::Abs(H_MC_MOTHER_ID) == 521'
    elif event_type == 'bpkkk':
        #B+ -> K+ K K
        cut= 'TMath::Abs(B_TRUEID)  == 521 &&  TMath::Abs(L1_TRUEID)  == 321 &&  TMath::Abs(L2_TRUEID) == 321 &&  TMath::Abs(L1_MC_MOTHER_ID)  == 521 &&  TMath::Abs(L2_MC_MOTHER_ID) == 521 &&  TMath::Abs(H_TRUEID) == 321 &&  TMath::Abs(H_MC_MOTHER_ID) == 521'
    elif event_type == 'fail':
        cut= 'TMath::Abs(B_TRUEID) == 0 || TMath::Abs(Jpsi_TRUEID) == 0 || TMath::Abs(Jpsi_MC_MOTHER_ID) == 0 || TMath::Abs(L1_TRUEID) == 0 || TMath::Abs(L2_TRUEID) == 0 || TMath::Abs(L1_MC_MOTHER_ID) == 0 || TMath::Abs(L2_MC_MOTHER_ID) == 0 || TMath::Abs(H_TRUEID) == 0 || TMath::Abs(H_MC_MOTHER_ID) == 0'
    else:
        log.error(f'Event type {event_type} not recognized')
        raise

    return cut
#------------------------------------------

