from scales import scales as scl
from scales import get_proc_labels 

import os
import mplhep
import pandas            as pnd
import utils_noroot      as utnr
import matplotlib.pyplot as plt
#-------------------------------
def plot_df(df, trig):
    df = df[df.trig == trig]
    ax = None
    d_proc_lab = get_proc_labels()
    for proc, df_p in df.groupby('kind'):
        ax=df_p.plot(x='year', y='val', yerr='err', ax=ax, label=d_proc_lab[proc], linestyle='none', marker='o')

    os.makedirs('tests/scales/', exist_ok=True)

    plt_path = f'tests/scales/{trig}.png'
    plt.grid()
    plt.ylabel('Scale')
    plt.ylim(0.0, 0.5)
    plt.xlabel('')
    plt.tight_layout()
    plt.savefig(plt_path)
    plt.close('all')
#-------------------------------
def test_all_datasets():
    df = pnd.DataFrame(columns=['year', 'trig', 'kind', 'val', 'err'])
    for year in ['2011', '2012', '2015', '2016', '2017', '2018']:
        for trig in ['ETOS', 'GTIS']:
            for kind in ['bpks', 'bdks', 'bsph', 'bpk1', 'bpk2']:
                obj      = scl(dset=year, trig=trig, kind=kind, vers='v3')
                val, err = obj.get_scale()

                df = utnr.add_row_to_df(df, [year, trig, kind, val, err])

    plot_df(df, 'ETOS')
    plot_df(df, 'GTIS')
#-------------------------------
def test_simple():
    obj      = scl(dset='2011', trig='ETOS', kind='bpks', vers='v5', d_sel={'BDT_cmb' : '(BDT_cmb > 0.831497) && (BDT_cmb < 0.9)'})
    val, err = obj.get_scale()

    #obj      = scl(dset='2011', trig='ETOS', kind='bpks', vers='v4', d_sel={'BDT_cmb' : '(BDT_cmb > 0.9) && (BDT_cmb < 0.977)'})
    #val, err = obj.get_scale()

    #obj      = scl(dset='2011', trig='ETOS', kind='bpks', vers='v3', d_sel={'BDT_cmb' : 'BDT_cmb > 0.977'})
    #val, err = obj.get_scale()
#-------------------------------
def main():
    plt.style.use(mplhep.style.LHCb2)
    test_simple()
    return
    test_all_datasets()
#-------------------------------
if __name__ == '__main__':
    main()

