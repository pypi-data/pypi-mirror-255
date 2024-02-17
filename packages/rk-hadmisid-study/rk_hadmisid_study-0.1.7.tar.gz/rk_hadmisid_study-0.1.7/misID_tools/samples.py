import uproot
import os

import pandas as pd

from tools.fail_to_pass import fail_to_pass
import utils_noroot    as utnr

log=utnr.getLogger(__name__)
# log.setLevel('DEBUG')

def read_root(year: str, trig: str, channel: str, sel, pbdt=False) -> pd.DataFrame:
    """
    Function to read root for the hadron mis-ID study.
    input : year, trigger category of samples you want.
            sel: additional selection.
    output: pandas.DataFrame that contents events.
    """
    force_remake_samples = True

    version = 'v10.18is' if channel in [ 'cmb' ] else 'v10.21p2'
    
    cached_path = '/afs/ihep.ac.cn/users/x/xzh6313/xzh/RKst/dev_zhihao/differential-crosscheck-fits/data/tools/apply_selection'

    if pbdt == False:
        roots_path = f'{cached_path}/noPID/high/{channel}/{version}/{year}_{trig}'
    elif pbdt == True and channel in ['cmb', 'data']:
        roots_path = f'{cached_path}/noPID/high_allsel/{channel}/{version}/{year}_{trig}'
    else:
        raise KeyError(f'For channel {channel}, full selected sample is not supported now.')

    desired_branches  = [ 
                          "B_M", "BDT_cmb",
                          "L1_PIDe", "L1_P", "L1_PT", "L1_ETA", "L1_ProbNNk",
                          "L2_PIDe", "L2_P", "L2_PT", "L2_ETA", "L2_ProbNNk",
                          "H_PIDe" , "H_ProbNNk"    , "Polarity"
                        ]
    
    merged_root_file = f'{roots_path}/merged_10.root'

    if os.path.exists(merged_root_file) and force_remake_samples == False:
            log.debug('Washed&Merged samples exists, loading...')
    else:

        with uproot.recreate(merged_root_file) as merged_file:
            log.debug('Washing and Merging input samples...')
            merged_tree = []

            for i in range(10):
                tem_rt_name = f'{roots_path}/{i}_10.root'
            
                with uproot.open(f'{tem_rt_name}:{trig}') as tree:
                    tree_sel = tree.arrays(desired_branches, library='pd')
                merged_tree.append(tree_sel)

            merged_tree = pd.concat(merged_tree)
            merged_file[trig] = merged_tree

    with uproot.open(f'{merged_root_file}:{trig}') as tree:
        df = tree.arrays(library='pd')
        log.debug(df.columns.to_list())
    
    if sel is not None:
        log.debug(f'Appling "{sel}')
        log.debug(f'Before: {len(df)}')
        df = df.query(sel)
        log.debug(f'After: {len(df)}')

    return df

def read_weight(year: str, mag: str, particle: str, trig: str):
    """
    Function to read weight maps.
    input : year, magnet and particle of samples you want.
    output: Hist that contents weight.
    """
    file_path = f"/afs/ihep.ac.cn/users/x/xzh6313/xzh/RK/dev_zhihao/hadron-mis-id/storage/map/v1.0/{year}_{mag}_{trig}_{particle}_w_map.root"
    with uproot.open(file_path) as f:
        hist = f[f"{particle}_DLLe>3_All"].to_hist()
    return hist

def add_kinematic_weight(df):
    ...

def add_pid_effciency_weight(df):
    ...

def cal_weighted_sample(kind, year, trig, channel, pbdt=False, wgt=True)-> tuple[pd.DataFrame, tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame]]:
    public_sel = 'H_ProbNNk>0.2&H_PIDe<0&L1_PIDe>-2&L2_PIDe>-2'

    log.debug(f'{kind}')
    if '_loose' not in kind:
        log.debug(f'Tighter BDT cut mode.')
        public_sel = f'{public_sel}&BDT_cmb>0.977'
    else:
        log.debug(f'Loose BDT cut mode.')

    if 'K' in kind:
        sel = f'L1_ProbNNk>0.1&L2_ProbNNk>0.1&{public_sel}'
    elif 'Pi' in kind:
        sel = f'L1_ProbNNk<0.1&L2_ProbNNk<0.1&{public_sel}'
    elif 'H' in kind:
        sel = f'{public_sel}'
    else:
        raise ValueError(f'Kind {kind} is not supported now.')

    data = read_root(year, trig, channel, sel, pbdt=pbdt)
    if wgt == False:
        return data
    # if channel in [ 'bpkkk', 'bpkpipi' ]:
    #     # For sample bpKKk and bpkpipi
    #     # Kinematic weight should be added
    #     # PID efficiencies calculated by PIDCalib added instead of PID cut.

    #     data = add_kinematic_weight(data)
    #     data_K, data_Pi = add_pid_effciency_weight(data)

    #     def replace_probNNk(df, pacticle, value):
    #         row = f'{pacticle}_probNNk'
    #         df[row] = df.apply(lambda x: value)

    #         return df

    #     data_K = replace_probNNk(data, 'L1', 1)
    #     data_K = replace_probNNk(data, 'L2', 1)

    #     data_Pi = replace_probNNk(data, 'L1', 0)
    #     data_Pi = replace_probNNk(data, 'L2', 0)

    #     data = pd.concat( [data_K, data_Pi] )

    data_MD = data.query("Polarity==-1")
    data_MU = data.query("Polarity==1")

    MD_maps = { "K": read_weight(year, "MagDown", "K", trig), "Pi": read_weight(year, "MagDown", "Pi", trig) }
    MU_maps = { "K": read_weight(year, "MagUp", "K", trig)  , "Pi": read_weight(year, "MagUp", "Pi", trig) }

    selector = lambda row, p: row[f"{p}_PIDe"] > 3
    map_selector = lambda row, p, maps: maps["K"] if row[f"{p}_ProbNNk"] > 0.1 else maps["Pi"]

    ftp = fail_to_pass(data_MD, "L1", "L2", selector, MD_maps, map_selector, ["PT", "ETA"])
    data_MD    = ftp.get_weighted_sample()
    data_MD_FP = ftp.df_fp
    data_MD_PF = ftp.df_pf
    data_MD_FF = ftp.df_ff

    ftp = fail_to_pass(data_MU, "L1", "L2", selector, MU_maps, map_selector, ["PT", "ETA"])
    data_MU    = ftp.get_weighted_sample()
    data_MU_FP = ftp.df_fp
    data_MU_PF = ftp.df_pf
    data_MU_FF = ftp.df_ff

    data    = pd.concat( [data_MU   , data_MD   ] )
    data_fp = pd.concat( [data_MU_FP, data_MD_FP] )
    data_pf = pd.concat( [data_MU_PF, data_MD_PF] )
    data_ff = pd.concat( [data_MU_FF, data_MD_FF] )

    if len(data_ff) != 0:
        data_ff['w'] = -1 * data_ff['w']

    return data, (data_fp, data_pf, data_ff)

def get_weighted_sample(kind, year, trig, channel, pbdt=False, wgt=True)-> tuple[pd.DataFrame, tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame]]:
    """
    output: pp_df, ( fp_df, pf_df, ff_df )
    sample isself is not weighted.
    use df['w'] to apply weight manually.
    """
    if year not in ['all_int']:
        return cal_weighted_sample(kind=kind, year=year, trig=trig, channel=channel, pbdt=pbdt, wgt=wgt)
    else:
        if wgt == False:
            data_list = []

            for y in [ '2011', '2012', '2015', '2016', '2017', '2018' ]:
                data_list.append( cal_weighted_sample(kind=kind, year=y, trig=trig, channel=channel, pbdt=pbdt, wgt=False) )
            
            return pd.concat(data_list)
        else:
            data_list    = []
            data_fp_list = []
            data_pf_list = []
            data_ff_list = []

            for y in [ '2011', '2012', '2015', '2016', '2017', '2018' ]:
                data_tmp, (data_fp_tmp, data_pf_tmp, data_ff_tmp) = cal_weighted_sample(kind=kind, year=y, trig=trig, channel=channel, pbdt=pbdt, wgt=True)

                data_list.append(data_tmp)
                data_fp_list.append(data_fp_tmp)
                data_pf_list.append(data_pf_tmp)
                data_ff_list.append(data_ff_tmp)

            return pd.concat(data_list), ( pd.concat(data_fp_list), pd.concat(data_pf_list), pd.concat(data_ff_list) )

