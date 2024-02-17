from misID_tools.samples import get_weighted_sample

import matplotlib.pyplot as plt
import numpy as np
import mplhep

def plot_data(df, name):
    bins = 80

    limits = (4000, 6500)

    counts, bin_edges = np.histogram(df['B_M'], bins, range=limits)

    # Substitute plt.hist()
    mplhep.histplot((counts, bin_edges), yerr=True, color='black', histtype='errorbar')

    plt.xlabel('B_M')

    plt.savefig(f'./output/{name}.png')
    plt.close('all')

    return 1

def test_samples():
    _, (_, _, Ka_ff) = get_weighted_sample(kind='K' , year='2018', trig='ETOS', channel='data')
    _, (_, _, Pi_ff) = get_weighted_sample(kind='Pi', year='2018', trig='ETOS', channel='data')
    Ha_pp, _ = get_weighted_sample(kind='H' , year='2018', trig='ETOS', channel='data')

    assert plot_data(Ka_ff, 'Kaon_failfail')
    assert plot_data(Pi_ff, 'Pion_failfail')
    assert plot_data(Ha_pp, 'All_passpass')

     