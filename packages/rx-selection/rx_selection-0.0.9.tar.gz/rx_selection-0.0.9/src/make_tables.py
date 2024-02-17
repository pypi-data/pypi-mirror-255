from logzero             import logger as log
from importlib.resources import files

import os
import re 
import warnings
import argparse
import pandas         as pnd
import utils_noroot   as utnr
import read_selection as rs

#----------------------------------------
class data:
    version = None
    sel_dir = None
    l_table = None
    d_cuts  = None

    hltr1       = 'Hlt1TrackAllL0Decision_TOS'
    hltr2       = 'Hlt1TrackMVADecision_TOS'

    regx_hlt1   = f'\w+_({hltr1}|{hltr2}) && \( TMath::Log\(\w+_IPCHI2_OWNPV\)  > \(1.0\/TMath::Power\(0\.001\*\w+_PT-1\., 2\)\)  \+ \(threshold_b\/25000\)\*\(25000-\w+_PT\) \+ TMath::Log\(7\.4\) \)'
    hlt1_ptip   = '&& ( TMath::Log(IPCHI2_OWNPV)  > (1.0/TMath::Power(0.001*PT-1., 2))  + (threshold_b/25000)*(25000-PT) + TMath::Log(7.4) )'

    warnings.simplefilter(action='ignore', category=FutureWarning)

    l_all_table = ['trig']
    l_year      = ['2011', '2012', '2015', '2016', '2017', '2018']
#----------------------------------------
def format_lzero_tos(cut):
    cut = cut.replace(' && L1_L0Calo_ECAL_realET > threshold_el', '')
    cut = cut.replace(' && L2_L0Calo_ECAL_realET > threshold_el', '')
    cut = cut.replace(' && L0Data_Muon1_Pt >= threshold_mu'     , '')

    cut = cut.replace('_L0ElectronDecision_TOS==1', ' eTOS')
    cut = cut.replace('_L0MuonDecision_TOS'       , ' mTOS')
    cut = cut.replace('(' ,   '')
    cut = cut.replace(')' ,   '')

    rgx_lzr = '\s*(L1 .TOS && L1_PT > \d+) \|\| (L2 .TOS && L2_PT > \d+)'
    mtch = re.match(rgx_lzr, cut)
    if not mtch:
        log.error(f'Invalid cut: "{cut}"')
        raise

    cut = mtch.group(1)
    cut = cut.replace('L1 ',    '')
    cut = cut.replace('L1_',    '')
    cut = cut.replace( '&&', 'and')

    return cut
#----------------------------------------
def format_lzero_tis(cut, year):
    lzr_etos = rs.get('etos', 'ETOS', q2bin='none', year = year)
    lzr_htos = rs.get('htos', 'HTOS', q2bin='none', year = year)

    lzr_htos = lzr_htos.replace(lzr_etos, 'eTOS')
    mtch     = re.match('\( \((.*)\) && !eTOS \)', lzr_htos)
    if not mtch:
        log.error(f'Cannot extract exclusive hTOS from: {lzr_htos}')
        raise
    lzr_htos = mtch.group(1)

    cut = cut.replace(lzr_etos   , 'eTOS')
    cut = cut.replace(lzr_htos   , 'hTOS')
    cut = cut.replace('Decision_',    ' ')
    cut = cut.replace('B_L0'     ,     '')
    cut = cut.replace(' || '     ,    '/')
    cut = cut.replace('(hTOS)'   , 'hTOS')
    cut = cut.replace('Photon '  ,    'g')
    cut = cut.replace('Electron ',    'e')
    cut = cut.replace('Hadron '  ,    'h')
    cut = cut.replace('Muon '    ,    'm')
    cut = cut.replace('&&'       ,  'and')
    cut = cut[2:]
    cut = cut[:-1]

    return cut
#----------------------------------------
def format_lzero(cut, trig, year):
    if trig in ['ETOS', 'MTOS']:
        cut = format_lzero_tos(cut)
    elif trig == 'GTIS':
        cut = format_lzero_tis(cut, year)
    else:
        log.error(f'Invalid trigger: {trig}')
        raise

    return cut
#----------------------------------------
def format_hlt1(cut):
    l_tcut = re.findall(data.regx_hlt1, cut)
    l_tcut = [ tcut.replace('L1_', '').replace('L2_', '').replace('H_', '') for tcut in l_tcut]

    try:
        tcut, = set(l_tcut)
    except:
        log.error(f'Different HLT1 requirements used for different tracks')
        log.error(l_tcut)
        raise

    tcut = tcut.replace(data.hlt1_ptip,  '')
    tcut = tcut.replace('Decision_TOS',  '')
    tcut = tcut.replace('Hlt1'        , ' ')
    tcut = tcut.replace('Hlt1'        , ' ')

    return tcut
#----------------------------------------
def format_hlt2(cut):
    cut = cut.replace('('           , '')
    cut = cut.replace(')'           , '')
    cut = cut.replace('B_'          , '')
    cut = cut.replace('B_'          , '')
    cut = cut.replace('||'          , '')
    cut = cut.replace('Body'        , '')
    cut = cut.replace('Hlt2Topo'    , '')
    cut = cut.replace('Decision_TOS', '')

    l_val = re.findall('\w+', cut)

    cut = '/'.join(l_val)

    return cut
#----------------------------------------
def format_anycut(cut):
    cut = cut.replace('abs(kl_M_k2l -  3097.) > 60 && abs(kl_M_k2l -  3686.) > 60', '|kl_M_k2l -  3097.| > 60 && |kl_M_k2l -  3686.| > 60')
    cut = cut.replace('(', '')
    cut = cut.replace(')', '')
    cut = cut.replace('H_ProbNNk'              , '$ProbNNk(K)$')

    cut = cut.replace('L1_PIDe'                , '$PIDe(L_1)$')
    cut = cut.replace('L2_PIDe'                , '$PIDe(L_2)$')

    cut = cut.replace('L1_PIDmu'               , '$PIDmu(L_1)$')
    cut = cut.replace('L2_PIDmu'               , '$PIDmu(L_2)$')

    cut = cut.replace('L1_PT'                  , '$p_T(L_1)$')
    cut = cut.replace('L2_PT'                  , '$p_T(L_2)$')

    cut = cut.replace('L1_hasCalo'             , '$hasCalo(L_1)$')
    cut = cut.replace('L2_hasCalo'             , '$hasCalo(L_2)$')

    cut = cut.replace('L1_InMuonAcc'           , '$inMuonAcc(L_1)$')
    cut = cut.replace('L2_InMuonAcc'           , '$inMuonAcc(L_2)$')

    cut = cut.replace('L1_isMuon'              , '$isMuon(L_1)$')
    cut = cut.replace('L2_isMuon'              , '$isMuon(L_2)$')

    cut = cut.replace( 'H_hasRich'             , '$hasRich(K)$')
    cut = cut.replace('L1_hasRich'             , '$hasRich(L_1)$')
    cut = cut.replace('L2_hasRich'             , '$hasRich(L_2)$')

    cut = cut.replace('H_PIDe'                 , '$PIDe(K)$')

    cut = cut.replace('L1_TRACK_GhostProb'     , '$GhostProb(L_1)$')
    cut = cut.replace('L2_TRACK_GhostProb'     , '$GhostProb(L_2)$')
    cut = cut.replace('H_TRACK_GhostProb'      , '$GhostProb(K)$')

    cut = cut.replace('kl_M_l2pi'              ,r'$m(K,\ell)_{\ell\to\pi}$')
    cut = cut.replace('kl_M_k2l'               ,r'$m(K,\ell)_{K\to\ell}$')
    cut = cut.replace('kl_M_ltrack2pi'         ,r'$m(K,\ell)_{\ell\to\pi}$')
    cut = cut.replace('kl'                     ,r'$m(K,\ell)$')

    cut = cut.replace('AbsL1_L0Calo_ECAL_yProjection', '$|y_{ECAL}(L_1)|$')
    cut = cut.replace('AbsL2_L0Calo_ECAL_yProjection', '$|y_{ECAL}(L_2)|$')

    cut = cut.replace('AbsL1_L0Calo_ECAL_xProjection', '$|x_{ECAL}(L_1)|$')
    cut = cut.replace('AbsL2_L0Calo_ECAL_xProjection', '$|x_{ECAL}(L_2)|$')

    cut = cut.replace('B_M'                    , '$m(B)$')
    cut = cut.replace('Jpsi_M'                 , '$m(\ell\ell)$')

    cut = cut.replace('B_const_mass_psi2S_M[0]', '$m(B)_{\psi(2S)}$')
    cut = cut.replace('B_const_mass_M[0]'      , '$m(B)_{J/\psi}$')
    cut = cut.replace('$m(\ell\ell)$ * $m(\ell\ell)$', '$m^2(\ell\ell)$')

    cut = cut.replace('&&'     ,  'and')
    cut = cut.replace('||'     ,   'or')
    cut = cut.replace('TMath::',     '')
    cut = cut.replace(' == 1'  ,     '')
    cut = re.sub(r'\.(\d*?)0+', r'.\1', cut)

    return cut
#----------------------------------------
def make_trigger(trig):
    df = pnd.DataFrame(columns=['Year', 'L0', 'HLT1 TOS', 'HLT2Topo*body'])
    for year in data.l_year:
        lzr = rs.get(trig.lower(), trig, q2bin='none', year = year)
        lzr = format_lzero(lzr, trig, year)

        hl1 = rs.get('hlt1', trig, q2bin='none', year = year)
        hl1 = format_hlt1(hl1)

        hl2 = rs.get('hlt2', trig, q2bin='none', year = year)
        hl2 = format_hlt2(hl2)

        df  = df.append({'Year' : year, 'L0' : lzr, 'HLT1 TOS' : hl1, 'HLT2Topo*body' : hl2}, ignore_index=True)

    return df
#----------------------------------------
def get_args():
    parser = argparse.ArgumentParser(description='Used to perform several operations on TCKs')
    parser.add_argument('-k', '--kind', nargs='+', help='Tables to make', choices=data.l_table, default=data.l_table)
    parser.add_argument('-v', '--vers', type=str , help='Version of selection', required=True) 
    args = parser.parse_args()

    data.l_table = args.kind
    data.version = args.vers
#----------------------------------------
def get_data():
    json_path   = files('selection_data').joinpath(f'selection_{data.version}.json')
    data.d_cuts = utnr.load_json(json_path)

    log.info(f'Using selection from: {json_path}')
#----------------------------------------
def format_table(table):
    table = table.replace(r'caption{', r'caption*{\tiny ')

    return table
#----------------------------------------
def save_table(table, path):
    f = open(path, 'w')
    f.write(table)
    f.close()
#----------------------------------------
def trigger():
    out_dir = utnr.make_dir_path('tables/trigger')

    df = make_trigger('GTIS')
    table = utnr.df_to_tex(df, None, hide_index=True, caption='gTIS!')
    table = format_table(table)
    save_table(table, f'{out_dir}/gtis.tex')

    df = make_trigger('ETOS')
    table = utnr.df_to_tex(df, None, hide_index=True, caption='eTOS')
    table = format_table(table)
    save_table(table, f'{out_dir}/etos.tex')

    df = make_trigger('MTOS')
    table = utnr.df_to_tex(df, None, hide_index=True, caption='mTOS')
    table = format_table(table)
    save_table(table, f'{out_dir}/mtos.tex')
#----------------------------------------
def make_preselection(channel):
    d_cut = data.d_cuts[channel]

    d_dat = {'Quantity' : [], 'Cut' : []}
    for key, cut in d_cut.items():
        if key in ['L0', 'Hlt1', 'Hlt2', 'etos', 'mtos', 'htos', 'gtis', 'hlt1', 'hlt2', 'bdt']:
            continue

        if cut == '(1)':
            continue

        key = key.replace('_', ' ')

        if isinstance(cut, str):
            cut = format_anycut(cut)

        if key in ['q2', 'mass']:
            for mkey, mval in cut.items():
                mval = format_anycut(mval)
                d_dat['Quantity'].append(f'{key} {mkey}')
                d_dat['Cut'     ].append(mval)
        else:
            d_dat['Quantity'].append(key)
            d_dat['Cut'     ].append(cut)

    df = pnd.DataFrame(d_dat)

    #l_key =['nspd', 'calo rich', 'cascade', 'ghost', 'pid', 'xyecal', 'q2 central', 'q2 jpsi', 'q2 psi2', 'q2 high']
    #l_key+=['mass central', 'mass jpsi', 'mass psi2', 'mass high']
    #df['Quantity'] = pnd.Categorical(df['Quantity'], l_key)

    return df
#----------------------------------------
def preselection(channel):
    out_dir = utnr.make_dir_path('tables/preselection')

    df    = make_preselection(channel)
    table = utnr.df_to_tex(df, None, hide_index=True, caption=f'{channel} channel')
    table = format_table(table)
    save_table(table, f'{out_dir}/{channel}.tex')
#----------------------------------------
def main():
    get_args()
    get_data()

    if 'trig' in data.l_table:
        trigger()

    if 'pres' in data.l_table:
        preselection('ee')
        preselection('mm')
#----------------------------------------
if __name__ == '__main__':
    main()

