from np_reader import np_reader as np_rdr
from log_store import log_store
import pprint
import os

log=log_store.add_logger('rk_extractor:test_npreader')
#-----------------------------
def test_simple():
    log.info('simple')
    rdr       = np_rdr(sys='v65', sta='v63', yld='v24')
    rdr.cache = True
    d_rjpsi   = rdr.get_rjpsi()
    d_eff     = rdr.get_eff()
    cov_sys   = rdr.get_cov(kind='sys')
    cov_sta   = rdr.get_cov(kind='sta')
    d_byld    = rdr.get_byields()
#-----------------------------
def main():
    test_simple()
#-----------------------------
if __name__ == '__main__':
    main()

