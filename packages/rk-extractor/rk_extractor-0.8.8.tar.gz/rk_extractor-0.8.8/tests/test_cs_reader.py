from cs_reader import cs_reader as cs_rdr

import pprint

#----------------------------------------
def test_cache():
    rdr           = cs_rdr(version='v4')
    rdr.cache     = True
    rdr.cache_dir = 'tests/cs_reader/v4_csrdr'
    x, y = rdr.get_constraints()
#----------------------------------------
def test_simple():
    rdr          = cs_rdr(version='v4')
    d_val, d_var = rdr.get_constraints()

    pprint.pprint(d_val)
    pprint.pprint(d_var)
#----------------------------------------
def main():
    test_cache()
    test_simple()
#----------------------------------------
if __name__ == '__main__':
    main()

