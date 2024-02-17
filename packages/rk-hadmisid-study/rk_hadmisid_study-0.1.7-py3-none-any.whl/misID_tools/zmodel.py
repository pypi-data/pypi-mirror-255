import zfit
import os
from zfit import z
import tensorflow as tf
import pandas as pd

from importlib.resources import files

from zmodel import diff_base_model
from zutils.pdf import SUJohnson
import utils_noroot as utnr


log = utnr.getLogger(__name__)
class Empirical(zfit.pdf.BasePDF):

    def __init__(self, m0, b1, b2, a, obs, extended=None, norm=None, name=None):
        params = { 
                   'm0' : m0,  
                   'b1' : b1,
                   'b2' : b2, 
                   'a'  : a ,
                 }
        super().__init__(obs=obs, params=params, extended=extended, norm=norm, name=name)

    def _unnormalized_pdf(self, x):
        x = z.unstack_x(x)
        # ma = self.params['ma']
        # mb = self.params['mb']
        m0 = self.params['m0']
        b1 = self.params['b1']
        b2 = self.params['b2']
        a  = self.params['a']

        dx = x - m0
        y = dx**a * z.exp( -dx*b1 + dx*dx*b2 )
        # n = ( ( x**2 - ma**2 - mb**2 )**2 - 4*ma**2*mb**2 )**0.5
        # dn= 2*x

        cond = tf.greater(x, m0)

        return tf.where(cond, y, 0)

class misID_base_model(diff_base_model):
    def __init__(self, name, params: dict, samples: dict, preffix=''):
        self.name     = name
        self._params  = params
        self._samples = samples
        self._preffix = preffix
        self._obs     = zfit.Space('B_M', limits=(4500, 6500))

        self._model_built = False
        self._bandwidth = 'adaptive_geom'

class My_SUJohnson(misID_base_model):
    def _initial_model(self):
        l_param_phsp = self.params['SU']

        if hasattr(self, 'fix') and self.fix == False:
            mu           = zfit.param.Parameter(f"{self.name}_mu",  l_param_phsp[0], 4000, 5000)
            lm           = zfit.param.Parameter(f"{self.name}_lm",  l_param_phsp[1], 0   , 100 )
            gm           = zfit.param.Parameter(f"{self.name}_gm",  l_param_phsp[2],-20  , 20  )
            dt           = zfit.param.Parameter(f"{self.name}_dt",  l_param_phsp[3], 0   , 10  )
        else:
            mu           = zfit.param.ConstantParameter(f"{self.name}_mu",  l_param_phsp[0])
            lm           = zfit.param.ConstantParameter(f"{self.name}_lm",  l_param_phsp[1])
            gm           = zfit.param.ConstantParameter(f"{self.name}_gm",  l_param_phsp[2])
            dt           = zfit.param.ConstantParameter(f"{self.name}_dt",  l_param_phsp[3])

        y_SUJs        = zfit.Parameter(f"{self.name}_NSUJs"    , self.params['yld'][0], 0, 1000)

        pdf_SUJohnson = SUJohnson(obs=self._obs, mu=mu, lm=lm, gamma=gm, delta=dt, name='SUJohnson')
        pdf_SUJohnson.set_yield(y_SUJs)

        self._total_model = pdf_SUJohnson
        self._model_built = True

class misID_pp_model_builder(misID_base_model):
    """
    For mimic pass-pass sample fit,  components needed:
    - Combinatorial background. Described by as nominal model, SU johnson.
    - B0/+ -> K*0/+ e+ e-. Described by GridKDE from simulation sample.
    - B+ -> K+ e+ e-. Marker as signal, described by GridKDE from simulation sample.
    - B+ -> K+ K+ K-/K+ pi+ pi-. Described by GridKDE from simulation sample.
    - Other mis-ID components. Described by phase-space model.
    """
    def _initial_model(self):

        def key_to_zfit_data(label, wgt=True): 
            data_df   = self._samples[label]
            if wgt == True:
                data_zfit = zfit.Data.from_pandas(data_df['B_M'], obs=self._obs, weights=data_df['w'])
            else:
                data_zfit = zfit.Data.from_pandas(data_df['B_M'], obs=self._obs)
            return data_zfit
        
        total_pdf = []

        # Define singal pdf
        data_sig     = key_to_zfit_data('sign', wgt=False)
        y_sig        = zfit.param.Parameter(f"{self.name}_Nsign"     , self.params['yld'][0], 0, 1e3)
        pdf_sig      = zfit.pdf.KDE1DimGrid(data_sig, name='sign', obs=self._obs)
        pdf_sig.set_yield(y_sig)
        total_pdf.append(pdf_sig)

        # Define B0 -> K*0 e+ e-
        data_prec_bd = key_to_zfit_data('bdks', wgt=False)
        y_prec_bd    = zfit.Parameter(f"{self.name}_Nbdks" , self.params['yld'][1], 0, 1e2)
        pdf_prec_bd  = zfit.pdf.KDE1DimGrid(data_prec_bd, name='bdks', obs=self._obs)
        pdf_prec_bd.set_yield(y_prec_bd)
        total_pdf.append(pdf_prec_bd)

        # Define B+ -> K*+ e+ e-
        data_prec_bp = key_to_zfit_data('bpks', wgt=False)
        y_prec_bp    = zfit.Parameter(f"{self.name}_Nbpks" , self.params['yld'][2], 0, 1e2)
        pdf_prec_bp  = zfit.pdf.KDE1DimGrid(data_prec_bp, name='bpks', obs=self._obs)
        pdf_prec_bp.set_yield(y_prec_bp)
        total_pdf.append(pdf_prec_bp)

        # # Define B+ -> K+ K+ K-
        data_bpkkk   = key_to_zfit_data('bpkkk', wgt=False)
        y_bpkkk      = zfit.param.ConstantParameter(f"{self.name}_Nbpkkk"    , self.params['yld'][3])
        pdf_bpkkk    = zfit.pdf.KDE1DimGrid(data_bpkkk, name='bpkkk', obs=self._obs, bandwidth=self._bandwidth)
        pdf_bpkkk.set_yield(y_bpkkk)
        total_pdf.append(pdf_bpkkk)

        # Define B+ -> K+ pi+ pi-
        data_bpkpipi = key_to_zfit_data('bpkpipi', wgt=False)
        y_bpkpipi    = zfit.param.ConstantParameter(f"{self.name}_Nbpkpipi"  , self.params['yld'][4])
        pdf_bpkpipi  = zfit.pdf.KDE1DimGrid(data_bpkpipi, name='bpkpipi', obs=self._obs, bandwidth=self._bandwidth)
        pdf_bpkpipi.set_yield(y_bpkpipi)
        total_pdf.append(pdf_bpkpipi)

        # Define comb. and others
        l_param_phsp = self.params['phsp']
        m0           = zfit.param.ConstantParameter(f"{self.name}_m0" ,  l_param_phsp[0])

        b1           = zfit.param.Parameter(f"{self.name}_b1" ,  l_param_phsp[1], 0, 1)
        b2           = zfit.param.ConstantParameter(f"{self.name}_b2" ,  l_param_phsp[2])

        a            = zfit.param.ConstantParameter(f"{self.name}_a"  ,  l_param_phsp[3])

        y_phsp       = zfit.Parameter(f"{self.name}_Nphsp"      , self.params['yld'][5], 0, 3e2)
        pdf_phsp     = Empirical(m0, b1, b2, a, name='other mis-ID', obs=self._obs)
        pdf_phsp.set_yield(y_phsp)
        total_pdf.append(pdf_phsp)

        l_param_SU = self.params['SU']
        mu           = zfit.param.ConstantParameter(f"{self.name}_mu",  l_param_SU[0])
        lm           = zfit.param.ConstantParameter(f"{self.name}_lm",  l_param_SU[1])
        gm           = zfit.param.ConstantParameter(f"{self.name}_gm",  l_param_SU[2])
        dt           = zfit.param.ConstantParameter(f"{self.name}_dt",  l_param_SU[3])

        y_SUJs        = zfit.param.ConstantParameter(f"{self.name}_NSUJs", int(self.params['yld'][6]))

        pdf_SUJohnson = SUJohnson(obs=self._obs, mu=mu, lm=lm, gamma=gm, delta=dt, name='Combinatorial')
        pdf_SUJohnson.set_yield(y_SUJs)
        total_pdf.append(pdf_SUJohnson)

        # self._total_model = pdf_phsp
        self._total_model = zfit.pdf.SumPDF( total_pdf, name=self.name )
        self._model_built = True

class misID_ff_model_builder(misID_base_model):
    """
    input: name, params: {'phsp':[2], 'yld':[6] }, samples: {<key> : <sample> }[5]

    For fail-fail sample fit,  components needed:
    - B0/+ -> K*0/+ e+ e-. Described by GridKDE from simulation sample.
    - B+ -> K+ e+ e-. Marker as signal, described by GridKDE from simulation sample.
    - B+ -> K+ K+ K-/K+ pi+ pi-. Described by GridKDE from simulation sample.
    - Other mis-ID components and Combinatorial background. Described by phase-space model.
    """
    def _initial_model(self):

        def key_to_zfit_data(label, wgt=True): 
            data_df   = self._samples[label]
            if wgt == True:
                data_zfit = zfit.Data.from_pandas(data_df['B_M'], obs=self._obs, weights=data_df['w'])
            else:
                data_zfit = zfit.Data.from_pandas(data_df['B_M'], obs=self._obs)
            return data_zfit
        
        total_pdf = []

        # Define singal pdf
        data_sig     = key_to_zfit_data('sign', wgt=False)
        y_sig        = zfit.Parameter(f"{self.name}_Nsign"     , self.params['yld'][0], 0, 1e4)
        pdf_sig      = zfit.pdf.KDE1DimGrid(data_sig, name='sign', obs=self._obs)
        pdf_sig.set_yield(y_sig)
        total_pdf.append(pdf_sig)

        # Define B0 -> K*0 e+ e-
        data_prec_bd = key_to_zfit_data('bdks', wgt=False)
        y_prec_bd    = zfit.Parameter(f"{self.name}_Nbdks" , self.params['yld'][1], 0, 1e4)
        pdf_prec_bd  = zfit.pdf.KDE1DimGrid(data_prec_bd, name='bdks', obs=self._obs)
        pdf_prec_bd.set_yield(y_prec_bd)
        total_pdf.append(pdf_prec_bd)

        # Define B+ -> K*+ e+ e-
        data_prec_bp = key_to_zfit_data('bpks', wgt=False)
        y_prec_bp    = zfit.Parameter(f"{self.name}_Nbpks" , self.params['yld'][2], 0, 1e4)
        pdf_prec_bp  = zfit.pdf.KDE1DimGrid(data_prec_bp, name='bpks', obs=self._obs)
        pdf_prec_bp.set_yield(y_prec_bp)
        total_pdf.append(pdf_prec_bp)

        # # Define B+ -> K+ K+ K-
        data_bpkkk   = key_to_zfit_data('bpkkk', wgt=False)
        y_bpkkk      = zfit.Parameter(f"{self.name}_Nbpkkk"    , self.params['yld'][3], 0, 1e4)
        pdf_bpkkk    = zfit.pdf.KDE1DimGrid(data_bpkkk, name='bpkkk', obs=self._obs, bandwidth=self._bandwidth)
        pdf_bpkkk.set_yield(y_bpkkk)
        total_pdf.append(pdf_bpkkk)

        # Define B+ -> K+ pi+ pi-
        data_bpkpipi = key_to_zfit_data('bpkpipi', wgt=False)
        y_bpkpipi    = zfit.Parameter(f"{self.name}_Nbpkpipi"  , self.params['yld'][4], 0, 1e4)
        pdf_bpkpipi  = zfit.pdf.KDE1DimGrid(data_bpkpipi, name='bpkpipi', obs=self._obs, bandwidth=self._bandwidth)
        pdf_bpkpipi.set_yield(y_bpkpipi)
        total_pdf.append(pdf_bpkpipi)

        # Define comb. and others
        l_param_phsp = self.params['phsp']
        m0           = zfit.param.Parameter(f"{self.name}_m0" ,  l_param_phsp[0], l_param_phsp[0] - 0.05*l_param_phsp[0], l_param_phsp[0] + 0.05*l_param_phsp[0])

        b1           = zfit.param.Parameter(f"{self.name}_b1" ,  l_param_phsp[1], 0, 1   )
        b2           = zfit.param.ConstantParameter(f"{self.name}_b2" ,  l_param_phsp[2] )
        a            = zfit.param.ConstantParameter(f"{self.name}_a"  ,  l_param_phsp[3] )

        y_phsp       = zfit.Parameter(f"{self.name}_Nphsp"      , self.params['yld'][5], 0, 1e4)
        pdf_phsp     = Empirical(m0, b1, b2, a, name='other mis-ID & cmb', obs=self._obs)
        pdf_phsp.set_yield(y_phsp)
        total_pdf.append(pdf_phsp)

        # self._total_model = pdf_phsp
        self._total_model = zfit.pdf.SumPDF( total_pdf, name=self.name )
        self._model_built = True

class misID_real_model_builder(misID_base_model):
    """
    The pdf builder for the total mis-ID pdf.
    
    Usage:
    ```
    misID_builder = misID_real_model_builder(name)
    misID_builder.load_model(path)
    
    model = misID_builder.build_model() # you got a zfit.pdf.SumPDF as model.

    ```
    """

    def __init__(self, name: str=None, version: str=None, obs: zfit.Space=None, preffix=''):
        self.name     = name
        self._vers    = version
        self._obs     = obs 
        self._preffix = preffix

        self._params  = []
        self._samples = []

        self._pars_dir    = None
        self._model_built = False
        self._initialized = False
        self._bandwidth = 'adaptive_geom'

    def _initialize(self):
        if self._initialized:
            return

        if self._obs is None:
            log.error(f'Observable is missing')
            raise

        self._pars_dir=files('misID_data').joinpath(f'model/{self._vers}')
        if not os.path.isdir(self._pars_dir):
            log.error(f'Missing directory with data: {self._pars_dir}')
            raise FileNotFoundError

        self._initialized = True

    def _initial_base_models(self):
        out_models = []

        def select_data(label, samples, wgt=True): 
            data_df   = samples[label]
            if wgt == True:
                data_zfit = zfit.Data.from_pandas(data_df['B_M'], obs=self._obs, weights=data_df['w'])
            else:
                data_zfit = zfit.Data.from_pandas(data_df['B_M'], obs=self._obs)
            return data_zfit

        if len(self._samples) > 1:
            log.info(f'{len(self._samples)} base models detected, loading them and adding up...')

        for idx in range(len(self._samples)):
            curr_samples = self._samples[idx]
            curr_params  = self._params[idx]

            curr_pdfs    = []

            # Define B+ -> K+ K+ K-
            data_bpkkk   = select_data('bpkkk', curr_samples  , wgt=False)
            pdf_bpkkk    = zfit.pdf.KDE1DimGrid(data_bpkkk, name=f'bpkkk_{idx}', obs=self._obs, bandwidth=self._bandwidth)

            # Define B+ -> K+ pi+ pi-
            data_bpkpipi = select_data('bpkpipi', curr_samples, wgt=False)
            pdf_bpkpipi  = zfit.pdf.KDE1DimGrid(data_bpkpipi, name=f'bpkpipi_{idx}', obs=self._obs, bandwidth=self._bandwidth)

            # Define others
            l_param_phsp = curr_params['phsp']
            m0           = zfit.param.ConstantParameter(f"{self._preffix}_{self.name}_{idx}_m0" ,  l_param_phsp[0])
            b1           = zfit.param.ConstantParameter(f"{self._preffix}_{self.name}_{idx}_b1" ,  l_param_phsp[1])
            b2           = zfit.param.ConstantParameter(f"{self._preffix}_{self.name}_{idx}_b2" ,  l_param_phsp[2])
            a            = zfit.param.ConstantParameter(f"{self._preffix}_{self.name}_{idx}_a"  ,  l_param_phsp[3])

            pdf_phsp     = Empirical(m0, b1, b2, a, name=f'other mis-ID_{idx}', obs=self._obs)
            
            # Yields
            y_bpkkk   = zfit.param.ConstantParameter(f"{self._preffix}_{self.name}_{idx}_Nbpkkk"    , curr_params['yld'][0])
            y_bpkpipi = zfit.param.ConstantParameter(f"{self._preffix}_{self.name}_{idx}_Nbpkpipi"  , curr_params['yld'][1])
            y_phsp    = zfit.param.ConstantParameter(f"{self._preffix}_{self.name}_{idx}_Nphsp"     , curr_params['yld'][2])

            pdf_bpkkk.set_yield(y_bpkkk)
            pdf_bpkpipi.set_yield(y_bpkpipi)
            pdf_phsp.set_yield(y_phsp)

            # Add up
            curr_pdfs.append(pdf_bpkkk)
            curr_pdfs.append(pdf_bpkpipi)
            curr_pdfs.append(pdf_phsp)

            out_models.append( zfit.pdf.SumPDF(curr_pdfs, name=self.name) )

        return out_models

    def _initial_model(self):

        if hasattr(self, 'fix_mode'):
            log.warning(f'fix_mode is temporarily removed, due to the complecated data set tag.')
        
        total_pdfs = self._initial_base_models()

        if len(total_pdfs) > 1:
            self._total_model = zfit.pdf.SumPDF( total_pdfs, name=self.name )
        else:
            self._total_model = total_pdfs[0]

        self._model_built = True

    def set_model(self, params: dict, samples: dict):
        self._initialize()
        self._params  = [ params ] 
        self._samples = [ samples ] 

    def save_model(self, year, trig):
        self._initialize()

        if year not in ['2011', '2012', '2015', '2016', '2017', '2018', 'all_int']:
            raise ValueError(f'{year} is not a base model tag, use a single year when saving model.')
        
        utnr.dump_json(self._params[0], f'{self._pars_dir}/{trig}/{year}/pars_misID.json')

        for key, df in self._samples[0].items():
            df.to_csv(f'{self._pars_dir}/{trig}/{year}/{key}.csv', index=False)

    def load_model(self, dset=None, trig=None):
        self._initialize()

        mapping = {
            'all'  : ['2011', '2012', '2015', '2016', '2017', '2018'],
            'r1'   : ['2011', '2012'],
            'r2p1' : ['2015', '2016'],
        }

        log.info(f'Model for data set {dset} will be load.')

        if dset in ['2011', '2012', '2015', '2016', '2017', '2018', 'all_int']:
            self._load_par_and_samples(dset, trig)
        elif dset in list(mapping.keys()):
            for a_year in mapping[dset]:
                self._load_par_and_samples(a_year, trig)
        else:
            raise ValueError(f'Data set of {dset} is not supported for now.')

    def _load_par_and_samples(self, year, trig):
        pars_path = f'{self._pars_dir}/{trig}/{year}'
        df_dict = {}

        for key in [ 'bpkkk', 'bpkpipi' ]:
            df_dict[key] = pd.read_csv(f'{pars_path}/{key}.csv')

        self._params.append(utnr.load_json(f'{pars_path}/pars_misID.json'))
        self._samples.append(df_dict)


