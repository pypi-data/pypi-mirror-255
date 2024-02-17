# Hadron mis-ID

## Description

This project contents tools and scripts to study hadron mis-ID background. 

Mis-ID components will be studied and generated using pass-fail method. Importing or using of the final mis-ID pdf only reply on the cached data in `\storage`.

## Fail-to-pass method

TBD

## Installation

Set environment:

```shell
conda create -n RK python
conda actiate RK
```

Clone and install this project:

```shell
git clone ssh://git@gitlab.cern.ch:7999/r_k/hadron-mis-id.git
cd hadron-mis-id
pip install -e .
```

## Usage

### Study and generate mis-ID components

TBD, reply on the `dev_zhihao` branch of project [High Q2 Yield Study](https://gitlab.cern.ch/r_k/high_q2_yield_study/-/tree/dev_zhihao?ref_type=heads)

### Get mis-ID pdf

It is recommanded to check `/test/test_zmodel.py` first.

```python
from misID_tools.zmodel import misID_real_model_builder

misID_builder = misID_real_model_builder('misID', 'v3', obs=zfit.Space('B_M', limits=(4500, 6500)), preffix='all_ETOS')
misID_builder.load_model(dset='all', trig='ETOS')
model = misID_builder.build_model() # A zfit.pdf.SumPdf object, shape and yield are fixed

# model.fit_to(data)
```

More information about different version of model, find [model_version](./misID_data/model/README.md).

## Test

Testo for mis-ID builder:

```shell
cd hadron-mis-id/test
pytest test_zmodel
```
