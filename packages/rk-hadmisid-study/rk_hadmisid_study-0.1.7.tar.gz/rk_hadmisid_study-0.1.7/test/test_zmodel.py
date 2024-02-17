from misID_tools.zmodel import misID_real_model_builder
from zutils.plot import plot as zfp

import zutils.utils as zut
import matplotlib.pyplot as plt
import zfit
import numpy
import tqdm 
import os
import pytest
from itertools import product

class data:
    ver = 'v4'              
    obs = zfit.Space('B_M', limits=(4500, 6500))
    out_dir = f'output/zmodel/{ver}'

    os.makedirs(out_dir, exist_ok=True) 

all_dset = [ '2011', '2012', '2015', '2016', '2017', '2018', 'all_int', 'r1', 'r2p1', 'all', 'all_int' ]
all_trig = [ 'ETOS', 'GTIS' ]

def test_model(pdf):
    arr_val = numpy.linspace(4000, 6000, 20)
    [pdf.pdf(val) for val in tqdm.tqdm(arr_val, ascii=' -')]

@pytest.mark.parametrize('dset, trig', product(all_dset, all_trig))
def test_real_model_load(dset, trig):
    misID_builder = misID_real_model_builder(f'misID_{dset}_{trig}', version=data.ver, obs=data.obs, preffix=f'{dset}_{trig}')

    try:
        misID_builder.load_model(dset, trig)
        model = misID_builder.build_model()
    except:
        assert False

    test_model(model)

    zut.print_pdf(model, txt_path=f'{data.out_dir}/{trig}_{dset}_pdf_IO.txt') 
    
def test_real_model_default():
    misID_builder = misID_real_model_builder('misID_def', version=data.ver, obs=data.obs)

    misID_builder.load_model(dset='2018', trig='ETOS')
    model = misID_builder.build_model()

    try:
        sampler = model.create_sampler(fixed_params=True)

        plotter = zfp(data=sampler, model=model)
        plotter.plot(nbins=50, plot_range=(4500, 6500), stacked=True)
        
        plt.savefig(f'{data.out_dir}/plot_misID_default.png', bbox_inches='tight')
        plt.close('all')
    except:
        assert False 

    zut.print_pdf(model, txt_path=f'{data.out_dir}/pdf_default.txt') 


@pytest.mark.parametrize('dset, trig', product(all_dset, all_trig))
def test_real_model_all(dset, trig):
    misID_builder = misID_real_model_builder('misID', version=data.ver, obs=data.obs, preffix=f'{dset}_{trig}')

    misID_builder.load_model(dset=dset, trig=trig)
    model = misID_builder.build_model()

    try:
        sampler = model.create_sampler(fixed_params=True)

        plotter = zfp(data=sampler, model=model)
        plotter.plot(nbins=50, plot_range=(4500, 6500), stacked=False)
        
        plt.savefig(f'{data.out_dir}/{trig}_{dset}_plot_misID.png', bbox_inches='tight')
        plt.close('all')
    except:
        assert False

    zut.print_pdf(model, txt_path=f'{data.out_dir}/{trig}_{dset}_pdf_misID.txt') 

def main():
    test_real_model_load('all'    , 'ETOS')
    test_real_model_load('all_int', 'ETOS')
    return
    test_real_model_all('all', 'ETOS')
    test_real_model_default()

if __name__ == '__main__':
    main()

