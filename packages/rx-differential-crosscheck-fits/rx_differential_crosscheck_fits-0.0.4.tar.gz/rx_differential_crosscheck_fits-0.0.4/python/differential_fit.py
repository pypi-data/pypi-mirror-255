from data_preprocess import data_preprocessor as dat_pcr

from zmodel import diff_MC_model   as mc_model
from zmodel import diff_DATA_model as dt_model

# zmodel from RK
from rk.model import zmodel as rkzmodel
from fitter import zfitter

import os
import gc
import matplotlib.pyplot as plt
import numpy as np
import zfit
import random
from hepstats.splot import compute_sweights

import utils_noroot as utnr

from zutils.plot import plot as zfp

log=utnr.getLogger(__name__)
log.setLevel('DEBUG')
#-------------------------------------------------
def ordinal(n):
    suffix = ["th", "st", "nd", "rd", ][n%10 if n%10<4 else 0]
    if 10<n<20:
        suffix = "th"
    return f"{n}{suffix}"
class differential_fit:
    def __init__(self, year, trig, proc, d_var_bin ) -> None:
        self.year   = year
        self.trig   = trig
        self.proc   = proc
        self.d_bound = d_var_bin
        self.partition = (0, 100) # scale number for testing, for real work flow, set it to (0, 1)

        self.MC_fit_plotting = True
        self.DT_fit_plotting = True
        self.save_ylds       = True 

        self.plt_dir   = None

        if self.trig in ['MTOS']:
            self.plt_range = (5180, 5600)
            self.fit_range = (5180, 5600)
        elif self.trig in ['ETOS', 'GTIS']:
            self.plt_range = (5080, 5680)
            self.fit_range = (5080, 5680)
        else:
            self.plt_range = (5080, 5680)
            self.fit_range = (5080, 5680)
        
        self.BDT_sel = 'nBDT'
        
        self._version   = 'v1.0' 
        
        self._obs = zfit.Space('mass', self.fit_range)
        self.mass_kind = 'mass_jpsi'
        
        d_mc_kind_mapping = { 'jpsi' : 'ctrl',
                              'psi2' : 'psi2' }
        self.q2bin = d_mc_kind_mapping[self.proc]

        self._weighted_data = None

    #-----------------------------------------
    @property
    def version(self):
        return self._version
    #-----------------------------------------
    @version.setter
    def version(self, version):
        log.info(f'Setting versoin to {version}')
        self._version = version
        self.out_dir  = f'output/dff_out/{self._version}/{self.year}/{self.trig}/{self.proc}'
    #-----------------------------------------
    def _get_splited_data(self, bound, kind='mc', sel_kind='yBDT'):
        if kind == 'data':
            kind = 'data'
        elif kind == 'mc':
            d_mc_kind_mapping = { 'jpsi' : 'ctrl',
                                  'psi2' : 'psi2' }
            kind = d_mc_kind_mapping[self.proc]
        
        obj = dat_pcr(self.year, self.trig, bound, kind, self.proc)
        obj.partition = self.partition
        obj.data_kind = sel_kind
        
        output_data = obj.get_splited_data()
        return output_data
    #-----------------------------------------
    def _get_integral_data(self, bound, kind='mc', sel_kind='yBDT'):
        if kind == 'mc':
            d_mc_kind_mapping = { 'jpsi' : 'ctrl',
                                  'psi2' : 'psi2' }
            kind = d_mc_kind_mapping[self.proc]
        if kind == 'mc_pi':
            kind = 'ctrl_pi'
        
        obj = dat_pcr(self.year, self.trig, bound, kind, self.proc)
        obj.partition = self.partition
        obj.data_kind = sel_kind
        
        output_data = obj.get_integral_data(df_kind='pandas')
        return output_data
    #-----------------------------------------
    def _mc_plotter(self, var, idx, i_df_mc, model, result, kind='splitted'):
        d_leg = { 'DoubleCB' : f'{self.proc}' }
        plotter = zfp(data=i_df_mc, model=model, result=result)
        plotter.plot(nbins=50, plot_range=self.plt_range, d_leg=d_leg)

        if kind == 'splitted':
            plt_dir = utnr.make_dir_path(f'{self.out_dir}/sim/{var}/plots/')
            plot_path = f'{plt_dir}/bin_{idx}.png'
        elif kind == 'integral':
            plt_dir = utnr.make_dir_path(f'{self.out_dir}/sim/')
            if var == None:
                plot_path = f'{plt_dir}/sim_integral.png'
            else:
                plot_path = f'{plt_dir}/sim_integral_{var}.png'
        else:
            log.error(f'Fitting kind of {kind} is not supportted now.')
            raise
        log.visible(f'Saving fitting plot to: {plot_path}')

        plt.savefig(plot_path, bbox_inches='tight')
        plt.close('all')

    #-----------------------------------------
    def _data_plotter(self, var, idx, i_df_dt, model, result, kind='splitted') -> list:
        d_leg = { 'DoubleCB'   : f'{self.proc}',
                  'Exponential': f'Combinatorials' }
        plotter = zfp(data=i_df_dt, model=model, result=result)
        plotter.plot(nbins=50, plot_range=self.plt_range, d_leg=d_leg)

        if kind == 'splitted':
            plt_dir = utnr.make_dir_path(f'{self.out_dir}/dat/{var}/plots/')
            lin_path = f'{plt_dir}/bin_{idx}_lin.png'
            log_path = f'{plt_dir}/bin_{idx}_log.png'
        elif kind == 'integral':
            plt_dir = utnr.make_dir_path(f'{self.out_dir}/dat/')
            lin_path = f'{plt_dir}/data_integral_lin.png'
            log_path = f'{plt_dir}/data_integral_log.png'
        else:
            log.error(f'Fitting kind of {kind} is not supportted now.')
            raise
        
        log.visible(f'Saving fitting plot to: {lin_path}')
        plt.savefig(lin_path, bbox_inches='tight')

        plotter.axs[0].set_yscale('log')
        plotter.axs[0].set_ylim(0.5, i_df_dt.maxy)

        log.visible(f'Saving fitting plot to: {log_path}')
        plt.savefig(log_path, bbox_inches='tight')

        plt.close('all')

    #-----------------------------------------
    def _get_fitted_params(self, model, params: list, sample, return_type='params'):
        status  = -999
        max_try = 10
        n_try   = 0
        
        while status != 0 and n_try < max_try:
            log.info(f'Try with the {ordinal(n_try+1)} fit...')
            if n_try != 0:
                params = [ (i + random.gauss(0, 0.02 * i)) for i in model.get_paramlist() ]
            
            model.update_params(params)
            try:
                result, hesse_status = model.fit_to(sample, binned=False)
                status = result.status if hesse_status == 0 else hesse_status
                n_try += 1
                
                if status != 0:
                    log.warning(f'Fit is not converged, try again.')
            except:
                log.error(f'Error, skip...')
                return 'fit fail', 'fit fail'
            
        if status == 0:
            log.info(f'Fit is converged.')
        else:
            log.warning(f'Fit is not converged with maximum tries.')

        if return_type == 'params':
            return (model.get_paramlist()[1:], result)
        elif return_type == 'par_and_err':
            params = [ (i['value'], i['hesse']['error'].real) for i in result.params.values() ]
            sw_yield = compute_sweights(model, sample)

            log.debug( model.get_params()[0] )
            log.debug( list(sw_yield.items()) )

            sw_yield = sw_yield[model.get_params()[0]]
            # sw_yield = np.sum(sw_yield)

            params.append(sw_yield)

            return (params, result)
    #-----------------------------------------
    def _fix_data_pars(self, pdf, d_sim_par):
        s_par = pdf.get_params(floating=True)

        d_par_val = { par.name                             : par for par       in             s_par}
        d_par_val = { name.replace(f'_dt', '') : par for name, par in d_par_val.items()}

        log.debug(f'parameters in data: {d_par_val}')
        log.debug(f'parameters in simulation: {d_sim_par}')

        log.info('-' * 20)
        log.info(f'Fixed fit parameters:')
        for par_name, [par_value, _] in d_sim_par.items():
            if par_name not in d_par_val:
                continue

            is_cabibo= '_pi_' in par_name
            is_mu_sg = par_name.startswith('mu_') or par_name.startswith('sg')
            if not is_cabibo and is_mu_sg:
                continue

            log.info(f'{par_name:<20}{"->":10}{par_value:>10.3e}')

            par = d_par_val[par_name]
            par.set_value(par_value)
            par.floating=False

        log.info('-' * 20)
        log.info('Floating fit parameters:')
        s_par = pdf.get_params(floating=True)
        [log.info(par.name) for par in s_par]

        return pdf
    #-----------------------------------------
    def _get_pars(self, res, no_errors=None):
        d_par_val = {}
        for par, d_val in res.params.items():
            val = d_val['value']
            if no_errors:
                err = 0
            else:
                err = d_val['hesse']['error'] 

            d_par_val[par.name] = [val, err]

        return d_par_val
    #-----------------------------------------
    def _fit_sim(self, data, chn='kp'):
        gc.collect()

        sim_dir   = utnr.make_dir_path(f'{self.out_dir}/sim')
        json_path = f'{sim_dir}/pars_{self.trig}_{chn}.json'
        
        mod = rkzmodel(proc=self.q2bin, trig=self.trig, q2bin=self.proc, year=self.year, obs=self._obs, mass=self.mass_kind)
        pdf = mod.get_signal(suffix=f'{self.trig}_{chn}') 

        tem_fitter=zfitter(pdf, data)
        res=tem_fitter.fit(ntries=10)

        if self.MC_fit_plotting == True:
            self._mc_plotter(chn, None, data, pdf, res, kind='integral')

        d_par = self._get_pars(res, no_errors=True)
        utnr.dump_json(d_par, json_path)

        log.debug(f'Fit to {chn} simulation sample got: {d_par}')
        log.debug(f'{len(data)} events are passed to the fitting.')

        res.freeze()

        return d_par
    #-----------------------------------------
    def _fit_data(self, data, d_sim_par, do_splot=False):
        gc.collect()

        mod = rkzmodel(proc=self.q2bin, trig=self.trig, q2bin=self.proc, year=self.year, obs=self._obs, mass=self.mass_kind)
        pdf = mod.get_model(suffix=f'dt_{self.trig}', prc_kind='ke_merged', use_br_wgt=1)
        pdf = self._fix_data_pars(pdf, d_sim_par)

        dat_dir   = utnr.make_dir_path(f'{self.out_dir}/dat')
        json_path = f'{dat_dir}/pars_{self.trig}.json'

        tem_fitter=zfitter(pdf, data)
        res=tem_fitter.fit(ntries=3)
        res.hesse()

        if self.DT_fit_plotting == True:
            self._data_plotter(None, None, data, pdf, res, kind='integral')

        d_par = self._get_pars(res, no_errors=False)
        utnr.dump_json(d_par, json_path)

        if do_splot == True:
            sw_wgt = compute_sweights(pdf, data)

            log.info(f'Getting sWeight for parameter {pdf.get_params()[0]}')
            sw_wgt = sw_wgt[pdf.get_params()[0]]

            d_par['sig_wgt'] = sw_wgt

        res.freeze()

        return d_par
    #-----------------------------------------
    
    def get_weighted_data(self):
        # preparing data

        if (self._weighted_data is None):
            var = list(self.d_bound.keys())[0]
            bound = { var : self.d_bound[var] }

            df_mc_full    = self._get_integral_data(bound, kind='mc'   , sel_kind=self.BDT_sel)
            df_mc_full    = df_mc_full.query   (f'mass>{self.fit_range[0]}&mass<{self.fit_range[1]}')

            df_mc_pi_full = self._get_integral_data(bound, kind='mc_pi', sel_kind=self.BDT_sel)
            df_mc_pi_full = df_mc_pi_full.query(f'mass>{self.fit_range[0]}&mass<{self.fit_range[1]}')

            df_dt_full    = self._get_integral_data(bound, kind='data' , sel_kind=self.BDT_sel)
            df_dt_full    = df_dt_full.query   (f'mass>{self.fit_range[0]}&mass<{self.fit_range[1]}')

            df_mc    = df_mc_full[['mass']]
            df_mc_pi = df_mc_pi_full[['mass']]
            df_dt    = df_dt_full[['mass']]

            kp_sim_pars = self._fit_sim(df_mc)
            pi_sim_pars = self._fit_sim(df_mc_pi, chn='pi')

            kp_sim_pars.update(pi_sim_pars)

            dat_pars = self._fit_data(df_dt, kp_sim_pars, do_splot=True)

            # 3. Add sWeight back to data.
            df_dt_full['sig_sw'] = dat_pars['sig_wgt']
            self._weighted_data = df_dt_full
        else:
            pass

        return self._weighted_data
    #-----------------------------------------
    def get_weighted_yields(self):
        log.info(f'======================================')
        log.info(f'==========Differential Check==========')
        log.info(f'=====Config version: {self.version}{ (17-len(self.version))*"=" }')
        log.info(f'===========Category: {self.year}_{self.trig}========')
        log.info(f'============Process: {self.proc}=============')
        log.info(f'======================================')

        df_dt_addwgt = self.get_weighted_data()
        # 4. Sperate data in different variable bins.
        # 5. Count the sum of the sWeights.
        from data_splitter import splitter as df_spliter
        d_out_yields = {}

        for k, v in self.d_bound.items():
            i_bound = { k : v }

            if k == 'nBrem' and self.trig == 'MTOS':
                continue

            obj  = df_spliter(df_dt_addwgt, i_bound, spectators=['mass', 'sig_sw'])
            i_d_df = obj.get_datasets(as_type='dict')
            
            out_i_d_df = {}
            
            for kk, v in i_d_df.items():
                if 'inf' not in str(kk):
                    out_i_d_df[str(kk[0])] = v['sig_sw'].sum()

            d_out_yields[k] = out_i_d_df

        utnr.dump_json(d_out_yields, f'{self.out_dir}/out_yields_int.json')
        return d_out_yields

    #-----------------------------------------
    def get_yields(self) -> dict[str, dict[str, list[list[float], int]]]:
        log.info(f'======================================')
        log.info(f'==========Differential Check==========')
        log.info(f'=====Config version: {self.version}{ (17-len(self.version))*"=" }')
        log.info(f'===========Category: {self.year}_{self.trig}========')
        log.info(f'============Process: {self.proc}=============')
        log.info(f'======================================')

        d_out_yields = {}

        mc_init_params = {'sig' : [5283   , 5180, 5380,
                                   25     , 1e-4, 300 ,
                                   0.5    , 0.01, 5   ,
                                   50     , 0.5 , 500 ,
                                   0.5    , 0.01, 5   ,
                                   50     , 0.5 , 500 ],
                          'yld' : [1000] }
        
        
        dt_init_params = { 'sig' : [5283   , 5180 , 5380,
                                    25     , 1e-4 , 300 ,
                                    0.5    , 0.01 , 10  ,
                                    50     , 0.01 , 500 ,
                                    0.5    , 0.01 , 10  ,
                                    50     , 0.01 , 500 ],
                           'bkg' : [-0.002 ,-2e-1 , 2e-1],
                           'yld' : [1000*0.6,
                                    1000*0.4] }
        
        mc_model_builder     = mc_model(f'{self.year}_{self.trig}_{self.proc}_MC_model', mc_init_params)
        mc_model_builder.obs = zfit.Space('mass', self.fit_range)
        mc_total_model       = mc_model_builder.build_model()
        mc_total_model.prefix= mc_model_builder.name
        
        dt_model_builder     = dt_model(f'{self.year}_{self.trig}_{self.proc}_DT_model', dt_init_params)
        dt_model_builder.obs = zfit.Space('mass', self.fit_range)
        dt_total_model       = dt_model_builder.build_model()
        dt_total_model.prefix= dt_model_builder.name
        
        for var in self.d_bound.keys():
            bound = { var : self.d_bound[var] }
            d_d_df_mc = self._get_splited_data(bound, kind='mc'  , sel_kind=self.BDT_sel)
            d_d_df_dt = self._get_splited_data(bound, kind='data', sel_kind=self.BDT_sel)
            
            d_df_mc = d_d_df_mc[var]
            d_df_dt = d_d_df_dt[var]
            
            d_out_yields[var] = {}

            for idx, (i_df_mc, i_df_dt) in enumerate(zip(d_df_mc.values(), d_df_dt.values())):
                i_df_mc = i_df_mc['mass'][(i_df_mc['mass'] > self.fit_range[0]) & (i_df_mc['mass'] < self.fit_range[1])]
                i_df_dt = i_df_dt['mass'][(i_df_dt['mass'] > self.fit_range[0]) & (i_df_dt['mass'] < self.fit_range[1])]
                # ==================================================================================
                # START: Getting init point from MC
                # ==================================================================================
                last_mc_params = [5283, 25, 0.5, 50, 0.5, 50]
                
                log.info(f'Getting model initial parameters from MC.')
                log.info(f'Now on {self.proc}, {var} bin of {idx}')
                
                mc_json_dir  = utnr.make_dir_path(f'{self.out_dir}/sim/{var}/json/')
                mc_json_name = f'bin_{idx}.json'
                mc_json_file = f'{mc_json_dir}/{mc_json_name}'
                
                if os.path.exists(mc_json_file):
                    log.info(f'MC fit result exists, loading...')
                    mc_params = utnr.load_json(mc_json_file)
                else:
                    if len(i_df_mc) == 0:
                        log.warning(f'No events.')
                        mc_params = last_mc_params
                    else:
                        init_mean = np.mean(i_df_mc)
                        init_std  = np.std(i_df_mc)
                        init_yld  = len(i_df_mc)
                        
                        mc_update_params = [init_yld, init_mean, init_std]
                        
                        mc_params, mc_result = self._get_fitted_params( mc_total_model, mc_update_params, i_df_mc )

                        if mc_params == 'fit fail':
                            continue
                        
                        if self.MC_fit_plotting == True:
                            self._mc_plotter(var, idx, i_df_mc, mc_total_model, mc_result)

                        utnr.dump_json(mc_params, mc_json_file)
                log.debug(f'Parameter from MC are: {mc_params}')
                last_mc_params = mc_params
                # ==================================================================================
                # END: Getting init point from MC
                # ==================================================================================
                
                # ==================================================================================
                # STRAT: Getting yields from fitting to real data
                # ==================================================================================
                log.info(f'Getting differential yields from data.')
                log.info(f'Now on {self.proc}, {var} bin of {idx}')
                
                dt_json_dir  = utnr.make_dir_path(f'{self.out_dir}/dat/{var}/jsons/')
                dt_json_name = f'bin_{idx}.json'
                dt_json_file = f'{dt_json_dir}/{dt_json_name}'
                
                if os.path.exists(dt_json_file):
                    log.info(f'Data fit result exists, loading...')
                    dt_params = utnr.load_json(dt_json_file)
                else:
                    if len(i_df_dt) == 0:
                        log.warning(f'No events. Skip.')
                        continue
                    else:
                        dt_init_yld  = len(i_df_dt)
                        dt_update_params = [ dt_init_yld*0.54, dt_init_yld*0.36 ] + mc_params

                        dt_params, dt_result = self._get_fitted_params( dt_total_model, dt_update_params, i_df_dt, return_type='par_and_err' )
                        dt_params[-1] = np.sum(dt_params[-1])

                        if dt_params == 'fit fail':
                            continue
                        if self.DT_fit_plotting == True:
                            self._data_plotter(var, idx, i_df_dt, dt_total_model, dt_result)
                    utnr.dump_json(dt_params, dt_json_file)
                log.debug(f'Parameter from DATA, and to be restored are: {dt_params}')
                # ==================================================================================
                # END: Getting yields from fitting to real data
                # ==================================================================================
                d_out_yields[var][str(list(d_df_mc.keys())[idx])] = (dt_params[0], dt_params[-1])

        if self.save_ylds == True:
            utnr.dump_json(d_out_yields, f'{self.out_dir}/out_yields{list(self.d_bound.keys())[0]}.json')
        return d_out_yields
    
    def clean_up(self):
        zfit.run.clear_graph_cache()
#-----------------------------------------

