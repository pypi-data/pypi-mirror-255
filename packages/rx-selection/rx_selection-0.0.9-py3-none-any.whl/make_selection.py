#!/usr/bin/env python3

import os
import json
import utils_noroot        as utnr
import selection.utilities as slut
import version_management  as vman

from importlib.resources import files

log=utnr.getLogger(__name__)
#-------------------------------------------
def get_bdt_str(bdt):
    bdt     = slut.transform_bdt(bdt)
    bdt_str = '{:.6f}'.format(bdt)

    return bdt_str
#-------------------------------------------
def get_hlt2(proc):
    d_hlt2 = {}
    if proc == 'ee':
        d_hlt2['2011'] = '(B_Hlt2Topo2BodyBBDTDecision_TOS || B_Hlt2Topo3BodyBBDTDecision_TOS || B_Hlt2TopoE2BodyBBDTDecision_TOS || B_Hlt2TopoE3BodyBBDTDecision_TOS)'
        d_hlt2['2012'] = '(B_Hlt2Topo2BodyBBDTDecision_TOS || B_Hlt2Topo3BodyBBDTDecision_TOS || B_Hlt2TopoE2BodyBBDTDecision_TOS || B_Hlt2TopoE3BodyBBDTDecision_TOS)'
        d_hlt2['2015'] = '(B_Hlt2Topo2BodyDecision_TOS     || B_Hlt2Topo3BodyDecision_TOS)'
        d_hlt2['2016'] = '(B_Hlt2Topo2BodyDecision_TOS     || B_Hlt2Topo3BodyDecision_TOS     || B_Hlt2TopoE2BodyDecision_TOS     || B_Hlt2TopoE3BodyDecision_TOS || B_Hlt2TopoEE2BodyDecision_TOS || B_Hlt2TopoEE3BodyDecision_TOS)'
        d_hlt2['2017'] = '(B_Hlt2Topo2BodyDecision_TOS     || B_Hlt2Topo3BodyDecision_TOS     || B_Hlt2TopoE2BodyDecision_TOS     || B_Hlt2TopoE3BodyDecision_TOS || B_Hlt2TopoEE2BodyDecision_TOS || B_Hlt2TopoEE3BodyDecision_TOS)'
        d_hlt2['2018'] = '(B_Hlt2Topo2BodyDecision_TOS     || B_Hlt2Topo3BodyDecision_TOS     || B_Hlt2TopoE2BodyDecision_TOS     || B_Hlt2TopoE3BodyDecision_TOS || B_Hlt2TopoEE2BodyDecision_TOS || B_Hlt2TopoEE3BodyDecision_TOS)'
    elif proc == 'mm':
        d_hlt2['2011'] = '(B_Hlt2Topo2BodyBBDTDecision_TOS || B_Hlt2Topo3BodyBBDTDecision_TOS || B_Hlt2TopoMu2BodyBBDTDecision_TOS || B_Hlt2TopoMu3BodyBBDTDecision_TOS)'
        d_hlt2['2012'] = '(B_Hlt2Topo2BodyBBDTDecision_TOS || B_Hlt2Topo3BodyBBDTDecision_TOS || B_Hlt2TopoMu2BodyBBDTDecision_TOS || B_Hlt2TopoMu3BodyBBDTDecision_TOS)'
        d_hlt2['2015'] = '(B_Hlt2Topo2BodyDecision_TOS     || B_Hlt2Topo3BodyDecision_TOS)'
        d_hlt2['2016'] = '(B_Hlt2Topo2BodyDecision_TOS     || B_Hlt2Topo3BodyDecision_TOS     || B_Hlt2TopoMu2BodyDecision_TOS     || B_Hlt2TopoMu3BodyDecision_TOS || B_Hlt2TopoMuMu2BodyDecision_TOS || B_Hlt2TopoMuMu3BodyDecision_TOS)'
        d_hlt2['2017'] = '(B_Hlt2Topo2BodyDecision_TOS     || B_Hlt2Topo3BodyDecision_TOS     || B_Hlt2TopoMu2BodyDecision_TOS     || B_Hlt2TopoMu3BodyDecision_TOS || B_Hlt2TopoMuMu2BodyDecision_TOS || B_Hlt2TopoMuMu3BodyDecision_TOS)'
        d_hlt2['2018'] = '(B_Hlt2Topo2BodyDecision_TOS     || B_Hlt2Topo3BodyDecision_TOS     || B_Hlt2TopoMu2BodyDecision_TOS     || B_Hlt2TopoMu3BodyDecision_TOS || B_Hlt2TopoMuMu2BodyDecision_TOS || B_Hlt2TopoMuMu3BodyDecision_TOS)'

    return d_hlt2
#-------------------------------------------
def get_hlt1_part(particle, year):
    if   year in ['2011', '2012']:
        hlt_kind = 'Hlt1TrackAllL0Decision_TOS'
    elif year in ['2015', '2016', '2017', '2018']:
        hlt_kind = 'Hlt1TrackMVADecision_TOS'
    else:
        log.error('Invalid year: ' + year)
        raise

    return '({0}_{1} && ( TMath::Log({0}_IPCHI2_OWNPV)  > (1.0/TMath::Power(0.001*{0}_PT-1., 2))  + (threshold_b/25000)*(25000-{0}_PT) + TMath::Log(7.4) ))'.format(particle, hlt_kind)
#-------------------------------------------
def get_hlt1():
    d_hlt1 = {}
    for year in ['2011', '2012', '2015', '2016', '2017', '2018']:
        l1 = get_hlt1_part('L1', year)
        l2 = get_hlt1_part('L2', year)
        kp = get_hlt1_part('H' , year)

        d_hlt1[year] = '({} || {} || {})'.format(l1, l2, kp)

    return d_hlt1
#-------------------------------------------
def get_lz_trig(trigger, pt_threshold=0):
    if   trigger in ['mtos', 'mtos_inclusive']:
        pt_threshold = 800 if pt_threshold == 0 else pt_threshold
        return '( ((L1_L0MuonDecision_TOS && L1_PT > {0:.0f}) || (L2_L0MuonDecision_TOS && L2_PT > {0:.0f})) && L0Data_Muon1_Pt >= threshold_mu)'.format(pt_threshold)
    elif trigger in ['etos', 'etos_inclusive']:
        return '((L1_L0ElectronDecision_TOS==1 && L1_L0Calo_ECAL_realET > threshold_el && L1_PT > {0:0.0f}) || (L2_L0ElectronDecision_TOS==1 && L2_L0Calo_ECAL_realET > threshold_el && L2_PT > {0:0.0f}) )'.format(pt_threshold)
    elif trigger == 'htos_inclusive':
        return '(H_L0HadronDecision_TOS==1 && H_L0Calo_HCAL_realET > threshold_kp && H_PT > {0:0.0f})'.format(pt_threshold)
    elif trigger == 'htos':
        htos = get_lz_trig('htos_inclusive')
        etos = get_lz_trig('etos_inclusive')

        return '( {} && !{} )'.format(htos, etos)
    elif trigger == 'gtis_inclusive':
        return '( B_L0PhotonDecision_TIS || B_L0ElectronDecision_TIS || B_L0HadronDecision_TIS || B_L0MuonDecision_TIS )'
    elif trigger == 'gtis':
        gtis = get_lz_trig('gtis_inclusive')
        htos = get_lz_trig('htos_inclusive')
        etos = get_lz_trig('etos_inclusive')

        return '( {} && !{} && !{} )'.format(gtis, htos, etos)
    else:
        log.error('Invalid trigger: ' +  trigger)
        raise
#-------------------------------------------
def get_mass(chan):
    expr_bare = '(B_M                     > {}) && (B_M                     < {})'
    expr_jpsi = '(B_const_mass_M[0]       > {}) && (B_const_mass_M[0]       < {})'
    expr_psi2 = '(B_const_mass_psi2S_M[0] > {}) && (B_const_mass_psi2S_M[0] < {})'

    d_mass = {}
    if   chan == 'ee':
        d_mass['central'] = expr_bare.format(4880, 6200) 
        d_mass['high'   ] = expr_bare.format(4880, 6200) 
        d_mass['jpsi']    = expr_jpsi.format(5080, 5680) 
        d_mass['psi2']    = expr_psi2.format(5080, 5680) 
    elif chan == 'mm':
        d_mass['central'] = expr_bare.format(5180, 5600) 
        d_mass['high'   ] = expr_bare.format(5180, 5600) 
        d_mass['jpsi'   ] = expr_jpsi.format(5180, 5600) 
        d_mass['psi2'   ] = expr_psi2.format(5180, 5600) 
    else:
        log.error('Invalid channel: {}'.format(chan))
        raise

    return d_mass
#-------------------------------------------
def get_bdt(kind=None):
    d_bdt = {}

    bdt = slut.inverse_transform_bdt(0.977)

    if   kind == 'all':
        d_bdt['MTOS'] = f'BDT_cmb > {get_bdt_str(bdt)} && BDT_prc > {get_bdt_str(-0.20)}'
        d_bdt['ETOS'] = f'BDT_cmb > {get_bdt_str(bdt)} && BDT_prc > {get_bdt_str(-0.20)}'
        d_bdt['HTOS'] = f'BDT_cmb > {get_bdt_str(0.97)} && BDT_prc > {get_bdt_str(-0.20)}'
        d_bdt['GTIS'] = f'BDT_cmb > {get_bdt_str(0.97)} && BDT_prc > {get_bdt_str(-0.20)}'
    elif kind == 'cmb':
        d_bdt['MTOS'] = f'BDT_cmb > {get_bdt_str(bdt)}'
        d_bdt['ETOS'] = f'BDT_cmb > {get_bdt_str(bdt)}'
        d_bdt['HTOS'] = f'BDT_cmb > {get_bdt_str(0.97)}'
        d_bdt['GTIS'] = f'BDT_cmb > {get_bdt_str(0.97)}'
    elif kind == 'prc':
        d_bdt['MTOS'] = f'BDT_prc > {get_bdt_str(-0.20)}'
        d_bdt['ETOS'] = f'BDT_prc > {get_bdt_str(-0.20)}'
        d_bdt['HTOS'] = f'BDT_prc > {get_bdt_str(-0.20)}'
        d_bdt['GTIS'] = f'BDT_prc > {get_bdt_str(-0.20)}'
    else:
        log.error(f'Invalid BDT kind: {kind}')
        raise ValueError

    return d_bdt
#-------------------------------------------
def get_ghost(chan):
    if   chan == 'mm':
        return 'L1_TRACK_GhostProb <0.3 && L2_TRACK_GhostProb<0.3'
    elif chan == 'ee':
        return 'H_TRACK_GhostProb<0.3 && L1_TRACK_GhostProb <0.3 && L2_TRACK_GhostProb<0.3'
    else:
        log.error('Invalid channel: {}'.format(chan))
        raise
#-------------------------------------------
def get_cascade(chan):
    if   chan == 'mm':
        return 'kl_M_l2pi > 1885 && kl >1885'
    elif chan == 'ee':
        return 'kl > 1885 && (kl_M_ltrack2pi < 1825 || kl_M_ltrack2pi > 1905)'
    else:
        log.error('Invalid channel: {}'.format(chan))
        raise
#-------------------------------------------
def get_q2(chan):
    expr = '(Jpsi_M * Jpsi_M > {}) && (Jpsi_M * Jpsi_M < {})'

    d_q2 = {}
    d_q2['central'] = expr.format( 1.1e6,  6.0e6) 
    d_q2['high']    = expr.format(15.5e6, 22.0e6) 

    if   chan == 'ee':
        d_q2['jpsi']    = expr.format( 6.00e6, 12.96e6) 
        d_q2['psi2']    = expr.format( 9.92e6, 16.40e6) 
    elif chan == 'mm':
        d_q2['jpsi']    = expr.format( 8.68e6, 10.09e6) 
        d_q2['psi2']    = expr.format(12.50e6, 14.20e6) 
    else:
        log.error('Invalid channel: {}'.format(chan))
        raise

    return d_q2
#-------------------------------------------
def get_kinematics(chan):
    if   chan == 'ee':
        return '(1)'
    elif chan == 'mm':
        return 'L1_PT > 800 && L2_PT > 800'
    else:
        log.error('Invalid channel: ' + chan)
        raise
#-------------------------------------------
def get_nspd():
    return 'nSPDHits < 450'
#-------------------------------------------
def get_pid(chan):
    if   chan == 'ee':
        return 'H_ProbNNk > 0.200 && H_PIDe <  0.000 && L1_PIDe  > 3.000 && L2_PIDe  > 3.000'
    elif chan == 'mm':
        return 'H_ProbNNk > 0.200 && L1_isMuon && L2_isMuon && L1_PIDmu>-3. && L2_PIDmu > -3'
    else:
        log.error('Wrong channel: ' + chan)
        raise
#-------------------------------------------
def get_xyecal():
    return '(TMath::Abs(L2_L0Calo_ECAL_xProjection) > 363.6 || TMath::Abs(L2_L0Calo_ECAL_yProjection)>282.6) && (TMath::Abs(L1_L0Calo_ECAL_xProjection)>363.6 || TMath::Abs(L1_L0Calo_ECAL_yProjection) > 282.6)' 
#-------------------------------------------
def get_calo_rich():
    return 'L1_hasCalo == 1 && L1_hasRich == 1 && H_hasRich == 1 && L2_hasCalo == 1 && L2_hasRich == 1' 
#-------------------------------------------
def get_rich():
    return 'L1_hasRich == 1 && L2_hasRich == 1 && H_hasRich == 1'
#-------------------------------------------
def get_acceptance():
    return 'L1_InMuonAcc == 1 && L2_InMuonAcc == 1'
#-------------------------------------------
def get_jpsi_misid(chan):
    if chan != 'mm':
        log.error('Jpsi Mis-ID only used for mm channel, not ' + chan)
        raise

    return 'abs(kl_M_k2l -  3097.) > 60 && abs(kl_M_k2l -  3686.) > 60'
#-------------------------------------------
def get_selection_dict(chan):
    d_sel = {}
    d_sel['q2']            = get_q2(chan)
    d_sel['mass']          = get_mass(chan)
    d_sel['cascade']       = get_cascade(chan)
    d_sel['ghost']         = get_ghost(chan)
    d_sel['kinematics']    = get_kinematics(chan) 
    d_sel['pid']           = get_pid(chan) 
    d_sel['nspd']          = get_nspd() 
    d_sel['bdt']           = get_bdt(kind='all')
    d_sel['bdt_cmb']       = get_bdt(kind='cmb')
    d_sel['bdt_prc']       = get_bdt(kind='prc')
    #Needs to be done due to bad naming in spectrum.cxx
    if chan == 'ee':
        d_sel['hlt1']          = get_hlt1()
        d_sel['hlt2']          = get_hlt2(chan)
    else:
        d_sel['Hlt1']          = get_hlt1()
        d_sel['Hlt2']          = get_hlt2(chan)

    if chan == 'ee':
        d_sel['xyecal']    = get_xyecal() 
        d_sel['calo_rich'] = get_calo_rich() 
        d_sel['etos']      = get_lz_trig('etos')
        d_sel['htos']      = get_lz_trig('htos')
        d_sel['gtis']      = get_lz_trig('gtis')
    elif chan == 'mm':
        d_sel['rich']      = get_rich() 
        d_sel['L0']        = get_lz_trig('mtos')
        d_sel['acceptance']= get_acceptance()
        d_sel['jpsi_misid']= get_jpsi_misid(chan)

    return d_sel
#-------------------------------------------
def get_dset(quantity, trigger, q2bin=None, year_1=None, year_2=None):
    c_11 = get(quantity, trigger, q2bin=q2bin, year=year_1)
    c_12 = get(quantity, trigger, q2bin=q2bin, year=year_2)

    if c_11 == c_12:
        return c_11
    else:
        log.error('Cuts between years differ')
        log.info('{0:<20}{1:<50}'.format('Quanity', quantity))
        log.info('{0:<20}{1:<50}'.format('Trigger',  trigger))
        log.info('{0:<20}{1:<50}'.format('Q2 bin' ,    q2bin))
        log.info('Cut {}: {}'.format(year_1, c_11))
        log.info('Cut {}: {}'.format(year_2, c_12))
        raise
#-------------------------------------------
def get(quantity, trigger=None, q2bin=None, year=None, pt_threshold=0):
    if   year == 'r1':
        cut = get_dset(quantity, trigger, q2bin = q2bin, year_1 = '2011', year_2 = '2012')
        return cut
    elif year == 'r2p1':
        cut = get_dset(quantity, trigger, q2bin = q2bin, year_1 = '2015', year_2 = '2016')
        return cut

    if trigger in ['ETOS', 'HTOS', 'GTIS']:
        chan = 'ee'
    else:
        chan = 'mm'

    if   quantity == 'q2':
        cut = get_q2(chan)[q2bin]
    elif quantity == 'mass':
        cut = get_mass(chan)[q2bin]
    elif quantity == 'cascade':
        cut = get_cascade(chan)
    elif quantity == 'ghost':
        cut = get_ghost(chan)
    elif quantity == 'bdt':
        cut = get_bdt(kind='all')[trigger]
    elif quantity == 'bdt_cmb':
        cut = get_bdt(kind='cmb')[trigger]
    elif quantity == 'bdt_prc':
        cut = get_bdt(kind='prc')[trigger]
    elif quantity in ['etos', 'htos', 'htos_inclusive', 'gtis', 'gtis_inclusive', 'mtos']:
        cut = get_lz_trig(quantity, pt_threshold)
    elif quantity == 'hlt1':
        cut = get_hlt1()[year]
    elif quantity == 'hlt2':
        cut = get_hlt2(chan)[year]
    elif quantity == 'kinematics':
        cut = get_kinematics(chan)
    elif quantity == 'nspd':
        cut = get_nspd()
    elif quantity == 'xyecal':
        cut = get_xyecal()
    elif quantity == 'pid':
        cut = get_pid(chan)
    elif quantity == 'calo_rich':
        cut = get_calo_rich()
    elif quantity == 'rich':
        cut = get_rich()
    elif quantity == 'acceptance':
        cut = get_acceptance()
    elif quantity == 'jpsi_misid':
        cut = get_jpsi_misid(chan)
    else:
        log.error('Invalid quantity: ' + quantity)
        raise

    return cut
#-------------------------------------------
def get_file_path():
    path        = files('selection_data')
    file_path   = vman.get_latest_file(dir_path=path, wc='selection_v*.json')
    file_name   = os.path.basename(file_path)
    old_version = file_name.replace('selection_', '').replace('.json', '')
    nxt_version = vman.get_next_version(old_version)
    file_path   = file_path.replace(old_version, nxt_version)

    return file_path
#-------------------------------------------
def main():
    d_sel       = {}    
    d_sel['ee'] = get_selection_dict('ee')
    d_sel['mm'] = get_selection_dict('mm')
    file_path   = get_file_path()

    log.visible(f'Saving to: {file_path}')
    utnr.dump_json(d_sel, file_path, sort_keys=True) 
#-------------------------------------------
if __name__ == '__main__':
    main()

