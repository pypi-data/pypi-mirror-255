import numpy
import pprint
import rk.utilities as rkut

from np_reader import np_reader as np_rdr
from cmb_ck    import combiner  as cmb_ck
#---------------------------------------------
def test_simple():
    rdr          = np_rdr(sys='v65', sta='v63', yld='v24')
    rdr.cache    = True
    d_eff        = rdr.get_eff()
    d_byld       = rdr.get_byields()
    d_nent       = rkut.average_byields(d_byld, l_exclude=['TIS'])
    d_rare_yld   = rkut.reso_to_rare(d_nent, kind='jpsi')

    cmb                 = cmb_ck(rk=1, eff=d_eff, yld=d_rare_yld) 
    cmb.out_dir         = 'tests/cmb_eff/simple'
    t_comb              = cmb.get_combination()
    d_rjpsi, d_eff, cov = t_comb
#---------------------------------------------
if __name__ == '__main__':
    test_simple()
