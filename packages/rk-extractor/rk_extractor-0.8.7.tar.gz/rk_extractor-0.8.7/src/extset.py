
sig_name = 'Signal'

def get_bdt_bin_settings(bdt_bin = None):
    '''
    For a given BDT bin, will return corresponding settings
    Parameters
    ----------------
    bdt_bin (int): Index of bin

    Returns
    ----------------
    tuple with:

    d_bdt_wp (dict): Dictionary between BDT variable and bin boundaries, e.g. {'BDT_cmb' : [0.831, 0.900]}
    vra (str)      : Version used to scale rare PRec with respect to signal, it's BDT dependent through efficiencies
    vcc (str)      : Version used to pick up right charm PRec shape
    '''
    if   bdt_bin == 0:
        d_bdt_wp  = {'BDT_cmb' : [0.627, 0.697]}
        vra       = 'v5'
        vcc       = 'v0'
    elif bdt_bin == 1:
        d_bdt_wp  = {'BDT_cmb' : [0.697, 0.767]}
        vra       = 'v5'
        vcc       = 'v1'
    elif bdt_bin == 2:
        d_bdt_wp  = {'BDT_cmb' : [0.767, 0.837]}
        vra       = 'v5'
        vcc       = 'v2'
    elif bdt_bin == 3:
        d_bdt_wp  = {'BDT_cmb' : [0.837, 0.907]}
        vra       = 'v5'
        vcc       = 'v3'
    elif bdt_bin == 4:
        d_bdt_wp  = {'BDT_cmb' : [0.907, 0.977]}
        vra       = 'v4'
        vcc       = 'v4'
    elif bdt_bin == 5:
        d_bdt_wp  = {'BDT_cmb' : [0.977, 1.047]}
        vra       = 'v3'
        vcc       = 'v5'
    else:
        log.error(f'Invalid BDT bin: {bdt_bin}')
        raise ValueError

    d_bdt_wp['BDT_prc'] = [0.480751, 10]

    return d_bdt_wp, vra, vcc

