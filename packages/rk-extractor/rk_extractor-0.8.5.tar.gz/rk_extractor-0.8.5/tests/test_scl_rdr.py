from bdt_scale import scale_reader as scl_rdr

#------------------------------------------------
def test_zero():
    prcno            = 0.480751
    cmbno            = 0.831497

    d_wp             = {}
    d_wp['BDT_prc']  = prcno, 100 
    d_wp['BDT_cmb']  = 0.730, cmbno 

    obj = scl_rdr(wp=d_wp, version='v1', dset='r1', trig='ETOS')
    scl = obj.get_scale()

    print(scl)
#------------------------------------------------
def test_simple():
    prcno            = 0.480751
    cmbno            = 0.831497

    d_wp             = {}
    d_wp['BDT_prc']  = prcno, 100 
    d_wp['BDT_cmb']  = cmbno, 0.900 
    d_wp['BDT_cmb']  = 0.900, 0.977 
    d_wp['BDT_cmb']  = 0.977, 100 
    #d_wp['BDT_cmb']  = 0.800, None 

    obj = scl_rdr(wp=d_wp, version='v1', dset='r1', trig='ETOS')
    scl = obj.get_scale()

    print(scl)
#------------------------------------------------
def main():
    test_simple()
    test_zero()
#------------------------------------------------
if __name__ == '__main__':
    main()

