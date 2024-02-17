import ROOT
import os

import numpy           as np
import pandas          as pd
import utils_noroot    as utnr
import rk.calc_utility as rkcu

from rk.ds_getter import ds_getter as ds_getter
from data_splitter import splitter as df_spliter

log=utnr.getLogger(__name__)
# log.setLevel('DEBUG')
#--------------------------------------
class data_preprocessor:
    def __init__(self, year, trig, d_bound, kind, q2):
        self.year   = year
        self.trig   = trig
        self.kind   = kind
        self.q2     = q2
        self.data_kind = 'yBDT'

        self.d_bound = d_bound

        trig_data_mapping = { 'ETOS' : 'v10.18is',
                              'GTIS' : 'v10.18is',
                              'MTOS' : 'v10.18is' }

        self.version    = trig_data_mapping[self.trig]

        if self.kind == 'ctrl_pi':
            self.version = 'v10.21'

        self.selection  = 'all_gorder'
        self.partition  = (1, 200)

        self.d_year_map = { "r1" : ["2011", "2012"], "r2p1" : ["2015", "2016"], "2017" : ["2017"], "2018" : ["2018"] }
        # self.l_vars     = [ 'mass', 'll_max_P', 'll_min_P', 'll_max_PT', 'll_min_PT', 'll_max_ETA', 'll_min_ETA', 'll_angle', 'Kl1_angle', 'Kl2_angle', 'cos_theta_L', 'B_ENDVTX_Z', 'log_B_IPCHI2_PV', 'log_B_VTXCHI2', 'K_P', 'K_PT', 'K_ETA', 'l1_PT', 'l2_PT', 'l1_ETA', 'l2_ETA', 'B_P', 'B_PT', 'B_ETA', 'BDT_cmb', 'BDT_prc', 'cos_dira' ]
        # self.l_vars_mu  = [ 'mass', 'll_max_P', 'll_min_P', 'll_max_PT', 'll_min_PT', 'll_max_ETA', 'll_min_ETA', 'll_angle', 'Kl1_angle', 'Kl2_angle', 'cos_theta_L', 'B_ENDVTX_Z', 'log_B_IPCHI2_PV', 'log_B_VTXCHI2', 'K_P', 'K_PT', 'K_ETA', 'l1_PT', 'l2_PT', 'l1_ETA', 'l2_ETA', 'B_P', 'B_PT', 'B_ETA', 'BDT_cmb', 'BDT_prc', 'cos_dira' ]
    #-----------------------------------------
    def _RDF_to_DF(self, rdf):
        return pd.DataFrame(rdf.AsNumpy())
    # #-----------------------------------------
    # def _DF_to_RDF(self, df):
    #     df_dict = df.to_dict("list")
        
    #     out_dict = {}
        
    #     for var, values_dict in df_dict.items():
    #         values_array = np.array(values_dict)
    #         out_dict[var] = values_array
        
    #     rdf = ROOT.RDF.MakeNumpyDataFrame(out_dict)
        
    #     return rdf
    #-----------------------------------------
    def _get_data(self, kind='yBDT'):
        
        l_year = self.d_year_map[self.year]
        
        out_df_list = []
        
        data_cached_path = '/afs/ihep.ac.cn/users/x/xzh6313/xzh/RKst/dev_zhihao/differential-crosscheck-fits/data/tools/apply_selection'

        match kind:
            case 'yBDT':
                BDT_flag = ''
            case 'nBDT':
                BDT_flag = 'noBDT_'
        
        for year in l_year:
            if self.kind == 'data':
                roots_path = f'{data_cached_path}/{BDT_flag}dat/{self.q2}/{self.kind}/{self.version}/{year}_{self.trig}'
            else:
                roots_path = f'{data_cached_path}/{BDT_flag}sim/{self.kind}/{self.version}/{year}_{self.trig}'
            
            names = []

            vars  = ['L1_P', 'L2_P', 'L1_PT', 'L2_PT', 'L1_ETA', 'L2_ETA',
                     'L1_PX', 'L1_PY', 'L1_PZ', 'L2_PX', 'L2_PY', 'L2_PZ',
                     'H_PX', 'H_PY', 'H_PZ', 'L1_PE', 'L2_PE', 'B_ENDVERTEX_Z',
                     'B_IPCHI2_OWNPV', 'B_ENDVERTEX_CHI2', 'H_PT', 'H_ETA', 
                     'B_const_mass_M', 'B_const_mass_psi2S_M',
                     'B_P', 'B_PT', 'B_ETA', 'BDT_cmb', 'BDT_prc', 'B_DIRA_OWNPV', 'Jpsi_DIRA_OWNPV',
                     'B_FDCHI2_OWNPV', 'H_IPCHI2_OWNPV', 'L1_IPCHI2_OWNPV', 'L2_IPCHI2_OWNPV', 'Jpsi_PT',
                     'B_VTXISODCHI2ONETRACK', 'B_VTXISODCHI2TWOTRACK', 'Jpsi_IPCHI2_OWNPV',
                     'B_L1_CC_SPT', 'B_L2_CC_SPT', 'B_L1_CC_IT', 'B_L2_CC_IT',
                     'B_L1_CC_MULT', 'B_L2_CC_MULT'
                     ]
            
            for i in range(10):
                tem_rt_name = f'{roots_path}/{i}_10.root'
                tem_rdf     = ROOT.RDataFrame(f'{self.trig}', tem_rt_name)
                log.debug(f'Checking {roots_path}/{i}_10_washed.root:{self.trig}')
                
                if os.path.exists(f'{roots_path}/{i}_10_washed.root'):
                    log.debug('Washed samples exists, loading...')
                    pass
                else:
                    log.debug('Washing input samples...')
                    tem_rdf.Snapshot( f'{self.trig}', f'{roots_path}/{i}_10_washed.root', vars )
                names.append(f'{roots_path}/{i}_10_washed.root')

            out_df_list += names



        rdf_sel      = ROOT.RDataFrame(f'{self.trig}', names)
        rdf_sel.q2   = self.q2
        rdf_sel.trig = self.trig
        rdf_sel      = rkcu.addDiffVars(rdf_sel, kind='all')

        return rdf_sel
    #-----------------------------------------
    def _get_splited_data(self):
        
        if self.data_kind == 'nBDT':
            df_sel_nBDT = self._get_data(kind='nBDT')
            df_sel_yBDT = df_sel_nBDT
        else:
            df_sel_yBDT = self._get_data(kind='yBDT')
            df_sel_nBDT = self._get_data(kind='nBDT')

        d_out_df = {}

        for k, v in self.d_bound.items():
            i_bound = { k : v }
            if k == 'nBrem' and self.trig == 'MTOS':
                continue
            
            if 'BDT' in k or self.kind=='nBDT':
                df_sel = df_sel_nBDT
            else:
                df_sel = df_sel_yBDT

            obj  = df_spliter(df_sel, i_bound, spectators=['mass'])
            i_d_df = obj.get_datasets(as_type='dict')
            
            out_i_d_df = {}
            
            for kk, v in i_d_df.items():
                if 'inf' not in str(kk):
                    out_i_d_df[kk] = v

            d_out_df[k] = out_i_d_df
        
        return d_out_df
    #-----------------------------------------
    def get_splited_data(self):
        return self._get_splited_data()
    #-----------------------------------------
    def get_integral_data(self, df_kind='root'):
        if self.data_kind == 'nBDT':
            out_df = self._get_data(kind='nBDT')
        elif self.data_kind == 'yBDT':
            out_df = self._get_data(kind='yBDT')
        else:
            log.error(f'Data kind of {self.data_kind} is not supported.')
            raise
        if df_kind == 'root':
            return out_df
        elif df_kind == 'pandas':
            out_df = self._RDF_to_DF(out_df)
            out_df = out_df.drop(columns=['B_const_mass_M', 'B_const_mass_psi2S_M'])
            return out_df
    #-----------------------------------------
