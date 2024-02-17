import zfit
from zfit import z

import numpy as np
import utils_noroot as utnr
import pandas as pd

import types

log=utnr.getLogger(__name__)
# log.setLevel('DEBUG') # print debug massage

class my_fermi_pdf(zfit.pdf.BasePDF):
    def __init__(self, mu, s, obs, extended=None, norm=None, name='my_fermi_pdf'):
        params = { 'mu' : mu,
                   's'  : s  }
        
        super().__init__(obs=obs, params=params, extended=extended, norm=norm,
                         name=name)

    def _unnormalized_pdf(self, x):
        x  = z.unstack_x(x)  # returns a list with the columns: do x, y, z = z.unstack_x(x) for 3D
        mu = self.params['mu']
        s  = self.params['s']
        return 1 / ( z.exp( (x-mu)/(s) ) + 1)

def fit_to(self, data, binned=False):
    model = self
    if isinstance(data, np.ndarray):
        log.info(f'Input data is \'np.ndarray\', converting it to zfit.Data.')
        data = zfit.Data.from_numpy(obs=model.space, array=data)
    if isinstance(data, pd.Series):
        log.info(f'Input data is \'pd.Series\', converting it to zfit.Data.')
        data = zfit.Data.from_pandas(obs=model.space, df=pd.DataFrame(data))
    if isinstance(data, pd.DataFrame):
        log.info(f'Input data is \'pd.DataFrame\', converting it to zfit.Data.')
        data = zfit.Data.from_pandas(obs=model.space, df=data)

    log.debug(f'model.space     : {model.space}')
    log.debug(f'data.space      : {data.space}')
    log.debug(f'data type       : {type(data)}')
    log.debug(f'data n_obs      : {data.n_obs}')
    log.debug(f'data n_events   : {data.nevents}')
    log.debug(f'data            : {data}')

    log.info('Fitting...')
    
    if binned:
        binned_space = zfit.Space('mass', limits=(model.space.limits[0], model.space.limits[1]), binning=100)
        model = zfit.pdf.BinnedFromUnbinnedPDF(pdf=model, space=binned_space)
        data  = zfit.data.BinnedData.from_unbinned(data=data, space=binned_space)
        nll = zfit.loss.ExtendedBinnedNLL(model=model, data=data)
    else:
        nll = zfit.loss.ExtendedUnbinnedNLL(model=model, data=data)
    
    minimizer = zfit.minimize.Minuit()
    result = minimizer.minimize(nll)

    params = result.params.keys()
    floating_params = [param for param in params if not isinstance(param, zfit.param.ConstantParameter)]

    hesse_status = 0
    if len(floating_params) > 1:
        result.hesse(params=floating_params)
        log.debug(result)
        
        log.debug(result.params.values())
        
        for i in result.params.values():
            if i['hesse']['error'].imag != 0:
                log.warning(f"Imaginary error encountered.")
                log.warning(result.params)
                hesse_status = -999
    self.result = result
    return result, hesse_status
#-----------------------------------------
def update_params(self, params: list):
    log.debug('Updating parameters')
    for par, val in zip(self.get_params(), params):
        log.debug(f'{par.name}: {par.value().numpy()} ---> {val}')
        try:
            par.set_value(val)
        except ValueError:
            pass
#-----------------------------------------
def get_paramlist(self, err=False) -> list:
    out = []
    for par in self.result.params.values():
        if err:
            out.append((par['value'], par['hesse']['error'].real))
        else:
            out.append(par['value'])
    
    return out
#-----------------------------------------
def get_paramdict(self, err=False) -> dict:
    out = {}

    for par, par_info in self.result.params.items():
        if err:
            out[par.name] = (par_info['value'], par_info['hesse']['error'])
        else:
            out[par.name] = (par_info['value'])
    
    return out
#-----------------------------------------
class diff_base_model:
    """
    Base zfit model with additional functions to make it easier to use.
    
    How to use
    
    Define
    1. Define `_initial_model()` in the inherited class.
    2. In the end of `_initial_model()`, set `self._model_built == True`
    3. In the end of `_initial_model()`, set `self._total_model == <your-model>`

    Usage
    1. `obj_builder = <you-model-builder>( builder-name, initial-parameters )`
    2. `model = obj_builder.build_model()`
    
    - `model.fit_to(data)`: If you want fit model to data.
    - `model.update_params(new_params)`: Move to a new initial parameters.
    - `model.get_paramlist()`: Get all values of parameters as a list.
    """
    def __init__(self, name, params):
        self.name = name
        self._params = params
        self._model_built = False
        self._obs = zfit.Space('mass', limits=(5100, 5600))
    
    @property
    def params(self):
        return self._params
    
    @params.setter
    def params(self, params):
        self._params = params
    
    @property
    def obs(self):
        return self._obs
    
    @obs.setter
    def obs(self, obs):
        if not isinstance(obs, zfit.Space):
            log.error(f'\'obs\' must be a zfit.Space instence')

        log.debug(f'Fit space is set to be: ')
        log.debug(f'Observable: {obs.obs}')
        log.debug(f'Limits    : {obs.limits}')
        self._obs = obs
        
    def _add_method(self, obj):
        obj.fit_to        = types.MethodType(fit_to       , obj)
        obj.update_params = types.MethodType(update_params, obj)
        obj.get_paramlist = types.MethodType(get_paramlist, obj)
        obj.get_paramdict = types.MethodType(get_paramdict, obj)

    def build_model(self):
        if not self._model_built:
            self._initial_model()
        self._add_method(self._total_model)
        return self._total_model
#-----------------------------------------
class diff_MC_model(diff_base_model):
    
    def _initial_model(self):
        l_param  = self.params['sig']
        
        # l_param = [ mean_mu    , low_limit_mu    , upp_limit_mu    ,
        #             mean_sigma , low_limit_sigma , upp_limit_sigma ,
        #             mean_alphaL, low_limit_alphaL, upp_limit_alphaL,
        #             mean_nL    , low_limit_nL    , upp_limit_nL    ,
        #             mean_alphaR, low_limit_alphaR, upp_limit_alphaR,
        #             mean_nR    , low_limit_nR    , upp_limit_nR     
        #           ]
        
        mu    = zfit.Parameter(f"{self.name}_mu"   ,  l_param[0], l_param[1], l_param[2])
        sigma = zfit.Parameter(f"{self.name}_sigma",  l_param[3], l_param[4], l_param[5])

        al    = zfit.Parameter(f"{self.name}_alphaL", l_param[6] , l_param[7] , l_param[8]  )
        nl    = zfit.Parameter(f"{self.name}_nL"    , l_param[9] , l_param[10], l_param[11] )
        ar    = zfit.Parameter(f"{self.name}_alphaR", l_param[12], l_param[13], l_param[14] )
        nr    = zfit.Parameter(f"{self.name}_nR"    , l_param[15], l_param[16], l_param[17] )

        yields= zfit.Parameter(f"{self.name}_sig_yields" , self.params['yld'][0], 0, 1e8)
        
        pdf_DSCB  = zfit.pdf.DoubleCB(mu, sigma, al, nl, ar, nr, obs=self.obs)
        pdf_DSCB.set_yield(yields)

        self._total_model = pdf_DSCB
        self._model_built = True
    
    def build_model(self):
        if not self._model_built:
            self._initial_model()
        self._add_method(self._total_model)
        return self._total_model

class diff_DATA_model(diff_base_model):
    def _initial_model(self):
        
        l_param_sig = self.params['sig']
        l_param_bkg = self.params['bkg']
        
        # l_param = [ mean_mu    , low_limit_mu    , upp_limit_mu    ,
        #             mean_sigma , low_limit_sigma , upp_limit_sigma ,
        #             mean_alphaL, low_limit_alphaL, upp_limit_alphaL,
        #             mean_nL    , low_limit_nL    , upp_limit_nL    ,
        #             mean_alphaR, low_limit_alphaR, upp_limit_alphaR,
        #             mean_nR    , low_limit_nR    , upp_limit_nR     
        #           ]
        
        mu    = zfit.Parameter(f"{self.name}_mu"   ,  l_param_sig[0], l_param_sig[1], l_param_sig[2])
        sigma = zfit.Parameter(f"{self.name}_sigma",  l_param_sig[3], l_param_sig[4], l_param_sig[5])

        # al    = zfit.Parameter(f"{self.name}_alphaL", l_param_sig[6], l_param_sig[7] , l_param_sig[8] )
        # nl    = zfit.Parameter(f"{self.name}_nL"    , l_param_sig[9], l_param_sig[10], l_param_sig[11])

        # ar    = zfit.Parameter(f"{self.name}_alphaR", l_param_sig[12], l_param_sig[13], l_param_sig[14])
        # nr    = zfit.Parameter(f"{self.name}_nR"    , l_param_sig[15], l_param_sig[16], l_param_sig[17])

        al    = zfit.param.ConstantParameter(f"{self.name}_alphaL", l_param_sig[6] )
        nl    = zfit.param.ConstantParameter(f"{self.name}_nL"    , l_param_sig[9] )

        ar    = zfit.param.ConstantParameter(f"{self.name}_alphaR", l_param_sig[12] )
        nr    = zfit.param.ConstantParameter(f"{self.name}_nR"    , l_param_sig[15] )

        sig_yields = zfit.Parameter(f"{self.name}_sig_yields" , self.params['yld'][0], 0, 1e8)

        pdf_DSCB  = zfit.pdf.DoubleCB(mu, sigma, al, nl, ar, nr, obs=self.obs)
        pdf_DSCB.set_yield(sig_yields)
        
        # l_param = [ mean_lambda, low_limit_lambda, upp_limit_lambda ]

        # lam = zfit.Parameter(f'{self.name}_lambda', l_param_bkg[0], l_param_bkg[1], l_param_bkg[2])
        lam = zfit.param.ConstantParameter(f'{self.name}_lambda', l_param_bkg[0])
        
        bkg_yields = zfit.Parameter(f"{self.name}_bkg_yields" , self.params['yld'][1], 0, 1e8)
        
        comb_bkg = zfit.pdf.Exponential(lam, obs=self.obs)
        comb_bkg.set_yield(bkg_yields)

        self._total_model = zfit.pdf.SumPDF( [pdf_DSCB, comb_bkg] )

        self._model_built = True

    def build_model(self):
        if not self._model_built:
            self._initial_model()
        self._add_method(self._total_model)
        return self._total_model

class diff_Jpsi_model(diff_base_model):
    def _initial_model(self):
        
        l_param_sig = self.params['sig']
        l_param_bkg = self.params['bkg']
        
        # l_param = [ mean_mu    , low_limit_mu    , upp_limit_mu    ,
        #             mean_sigma , low_limit_sigma , upp_limit_sigma ,
        #             mean_alphaL, low_limit_alphaL(no use), upp_limit_alphaL(no use),
        #             mean_nL    , low_limit_nL(no use)    , upp_limit_nL(no use)    ,
        #             mean_alphaR, low_limit_alphaR(no use), upp_limit_alphaR(no use),
        #             mean_nR    , low_limit_nR(no use)    , upp_limit_nR(no use)     
        #           ]
        
        mu    = zfit.Parameter(f"{self.name}_mu"   ,  l_param_sig[0], l_param_sig[1], l_param_sig[2])
        sigma = zfit.Parameter(f"{self.name}_sigma",  l_param_sig[3], l_param_sig[4], l_param_sig[5])

        al    = zfit.param.ConstantParameter(f"{self.name}_alphaL", l_param_sig[6])
        nl    = zfit.param.ConstantParameter(f"{self.name}_nL"    , l_param_sig[9])

        ar    = zfit.param.ConstantParameter(f"{self.name}_alphaR", l_param_sig[12])
        nr    = zfit.param.ConstantParameter(f"{self.name}_nR"    , l_param_sig[15])

        sig_yields = zfit.Parameter(f"{self.name}_sig_yields" , self.params['yld'][0], 0, 1e8)

        pdf_DSCB  = zfit.pdf.DoubleCB(mu, sigma, al, nl, ar, nr, obs=self.obs)
        pdf_DSCB.set_yield(sig_yields)
        
        # l_param = [ mean_lambda, low_limit_lambda, upp_limit_lambda ]

        lam = zfit.Parameter(f'{self.name}_lambda', l_param_bkg[0], l_param_bkg[1], l_param_bkg[2])
        
        bkg_yields = zfit.Parameter(f"{self.name}_bkg_yields" , self.params['yld'][1], 0, 1e8)
        
        comb_bkg = zfit.pdf.Exponential(lam, obs=self.obs)
        comb_bkg.set_yield(bkg_yields)

        # l_param = [ mean_mu, low_limit_mu, upp_limit_mu,
        #             mean_s , low_limit_s , upp_limit_s  ]

        prec_mu = zfit.Parameter(f'{self.name}_prec_mu', l_param_bkg[3], l_param_bkg[4], l_param_bkg[5])
        prec_s  = zfit.Parameter(f'{self.name}_prec_s' , l_param_bkg[6], l_param_bkg[7], l_param_bkg[8])
        # prec_s  = zfit.param.ConstantParameter(f'{self.name}_prec_s' , l_param_bkg[6])

        prec_bkg = my_fermi_pdf(prec_mu, prec_s, self.obs)

        prec_yields = zfit.Parameter(f"{self.name}_prec_yields" , self.params['yld'][2], 0, 1e8)
        prec_bkg.set_yield(prec_yields)

        self._total_model = zfit.pdf.SumPDF( [pdf_DSCB, comb_bkg, prec_bkg] )
        # self._total_model = zfit.pdf.SumPDF( [pdf_DSCB, comb_bkg] )

        self._model_built = True
