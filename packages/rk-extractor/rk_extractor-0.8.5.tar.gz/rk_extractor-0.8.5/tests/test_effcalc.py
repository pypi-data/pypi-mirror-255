from scales import eff_calc

import pprint

#-------------------------------------------------
def test_new_wp():
    obj   = eff_calc(proc=['bpkp'], year=['2011'], trig=['ETOS'])
    d_eff = obj.get_efficiencies(d_sel={'BDT_cmb' : 'BDT_cmb > 0.977'})

    pprint.pprint(d_eff)
#-------------------------------------------------
def test_simple():
    obj   = eff_calc(proc=['bpkp'], year=['2011'], trig=['ETOS'])
    d_eff = obj.get_efficiencies()

    pprint.pprint(d_eff)
#-------------------------------------------------
def main():
    test_new_wp()
    return
    test_simple()
#-------------------------------------------------
if __name__ == '__main__':
    main()

