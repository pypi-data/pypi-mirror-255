from bdt_scale import scale_maker as scl_mkr 

#------------------------------------------------
def test_simple():
    d_wp             = {}
    d_wp['BDT_prc']  = 0.4, 0.80
    d_wp['BDT_cmb']  = 0.8, 1.03

    obj= scl_mkr(wp=d_wp, step_size=1e-2, dset='r1', trig='ETOS')
    obj.out_dir = f'tests/scl_mkr/simple'
    df = obj.save_efficiencies(version='v1')
#------------------------------------------------
def main():
    test_simple()
#------------------------------------------------
if __name__ == '__main__':
    main()

