from mc_reader import mc_reader as mc_rdr
import pprint
import pytest
import os

#-----------------------------
def skip_test():
    try:
        uname = os.environ['USER']
    except:
        pytest.skip()

    if uname in ['angelc', 'campoverde']:
        return

    pytest.skip()
#-----------------------------
def test_simple():
    skip_test()
    rdr        = mc_rdr(version='v4')
    rdr.cache  = False 
    d_mcsg     = rdr.get_parameter(name='sg')
    d_mcmu     = rdr.get_parameter(name='mu')
#-----------------------------
def test_data():
    skip_test()
    rdr        = mc_rdr(version='v4', real_data=True)
    rdr.cache  = False 
    d_mcsg     = rdr.get_parameter(name='sg')
    d_mcmu     = rdr.get_parameter(name='mu')
#-----------------------------
def test_cache():
    skip_test()
    rdr        = mc_rdr(version='v4')
    rdr.cache  = True 
    rdr.cache_dir = 'tests/mc_reader/v4_mcrdr'
    d_mcsg     = rdr.get_parameter(name='sg')
    d_mcmu     = rdr.get_parameter(name='mu')
#-----------------------------
def main():
    test_data()
    test_simple()
    test_cache()
#-----------------------------
if __name__ == '__main__':
    main()

