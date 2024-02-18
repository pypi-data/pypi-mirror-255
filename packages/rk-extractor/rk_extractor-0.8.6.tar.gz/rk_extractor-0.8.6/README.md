[[_TOC_]]

# Purpose

This project is used to calculate $R_K$ from:

1. The fitting model for the signal region.
1. The data in the signal region.
1. The $c_k^{r,t}$ vector and the corresponding covariance matrices.
1. Any constraint on the nuisance parameters

The tools used to do this are:

**Extractor** Which will build the likelihood and run the minimization   
**np_reader** Which is in charge of reading the nuisance parameters and provide them to the extractor   
**rk_ex_model** Which provides a toy model to run tests, while the actual model is been developed.   

These three tools come with unit tests.

# Installation 

# For use

This project has to be installed alongside other `rx` dependencies. It can be done by running:

```bash
pip install rx_extractor
```

or 

```bash
pip install -e .
```

in the directory with the code, after clonning it.

## For development

Use the `rx_setup` project to installing with the rest of the packages:

https://gitlab.cern.ch/r_k/setup#description

# Usage

Below is a description of how the project works:

```python
def test_real():
    rdr          = np_rdr(sys='v65', sta='v63', yld='v24')
    rdr.cache    = True
    cv_sys       = rdr.get_cov(kind='sys')
    cv_sta       = rdr.get_cov(kind='sta')
    d_eff        = rdr.get_eff()
    d_rjpsi      = rdr.get_rjpsi()
    d_byld       = rdr.get_byields()
    d_nent       = rkut.average_byields(d_byld, l_exclude=['TIS'])
    d_rare_yld   = rkut.reso_to_rare(d_nent, kind='jpsi')

    mod          = model(preffix='real', d_eff=d_eff)
    d_mod        = mod.get_model()
    d_dat        = mod.get_data(d_nent=d_rare_yld)

    obj          = ext()
    obj.rjpsi    = d_rjpsi
    obj.eff      = d_eff
    obj.cov      = cv_sys + cv_sta
    obj.data     = d_dat
    obj.model    = d_mod 
    obj.plt_dir  = 'tests/extractor/real'
    result       = obj.get_fit_result()

    log.info(f'Calculating errors')
    result.hesse()
    result.freeze()
    utnr.dump_pickle(result, 'tests/extractor/real/result.pkl')
```
which is taken from:

```
https://gitlab.cern.ch/r_k/rk_extractor/-/blob/master/tests/test_extractor.py?ref_type=heads#L128
```

## Loading of nuisance parameters and expected signal yields

This is done with `np_reader` will retrieve:

1. `$r_{J/\psi}$`
1. Efficiencies for the signal
1. Covariance matrix for the statistical and systematic uncertainties associated with $c_K$.
1. The expected yields of rare $B$ decays, calculated from the average over electron and muon TOS yields.

The inputs used are the versions of the efficiencies with the corresponding systematic and statistical variations (bootstrapping)
as well as the version of the resonant mode fits.

The nuisance parameters are obtained by reading files in the IHEP cluster. However these parameters can be `cached` with:

```python
def run():
    rdr           = np_rdr(sys='v65', sta='v63', yld='v24')
    rdr.cache     = True
    rdr.cache_dir = 'tests/np_reader/tarball'
    d_rjpsi       = rdr.get_rjpsi()
    d_eff         = rdr.get_eff()
    cov_sys       = rdr.get_cov(kind='sys')
    cov_sta       = rdr.get_cov(kind='sta')
    d_byld        = rdr.get_byields()
```
in a `tests/np_reader/tarball.tar.gz` file, see:

```bash
https://gitlab.cern.ch/r_k/rk_extractor/-/blob/master/tests/test_np_reader.py?ref_type=heads#L28
```

This file can be later reused (if `rdr.cache = True` is used) to speed up the processing.

## Model building

A class is used to build a toy model from the expected rare decays yield and the rare mode efficiencies. 
This class should be updated to use the correct model when available. 

## Extraction of results

The `extractor` class provides a `zfit` result object, which can be pickled.

# Toy tests

In order to verify that the model is not biased and has the right coverage, a set of scripts are available in

`scripts/jobs`

these are installed as part of the project, but should be ran outside the corresponding virtual environment.

## Software

The code is taken from an LCG view, given that this code will have to run on the GRID eventually.   
The code not available in the view: 

### Local tests

This code will, for now, go to:

```
/publicfs/lhcb/user/campoverde/SFT/RK_TOY
```
and will be re-used, to speed up tests. If any version is updated, remove the directory and re-run the local test as shown below.

### Grid

The code will be installed from zero in each grid node.

## Local tests

Before submitting one can test locally by running

```bash
./rxe_local 0 1 $JOBDIR/extractor "dset:2018_TOS,vars:none"
```
1. For all datasets use `all`, but that test would take too long.
1. The `vars` part specifies which variables should be fixed, in order to assess the impact on systematics. `none` will float them all.
1. This will create a sandbox `$JOBDIR/extractor/` that will look like the sandbox in the grid.
1. **This will only work in an environment with access to CVMFS, e.g. LXPLUS, IHEP, etc.**
1. No need of DIRAC or grid proxy is needed for these tests, but they have to be ran within a python environment with access to `logzero` and potentially other libraries.

## IHEP tests

For small tests that still require multiple fits but that can be done in the cluster:

```bash
./rxe_ihep_jobs -j 3 -f 1 -d 2018_TOS
```

where it would send one fit for each of three jobs, processing only one dataset.

## Grid submission
To use them do:

```bash
. /cvmfs/lhcb.cern.ch/lib/LbEnv
#make grid proxy for 100 hours
lhcb-proxy-init -v 100:00
lb-dirac bash

#you might need tqdm installed locally, in case it is not available in your system.
pip install --user tqdm

cd scripts/jobs

./rkex_jobs -j J -f F -m [local, wms] -n job_name
```
where:

1. `J` is the number of jobs
1. `F` is the number of fits per jobs
1. `local` or `wms` specify wether the jobs are ran locally (for tests) or in the grid.

these jobs can be monitored in the dirac website as any other job.

__IMPORTANT:__ 

1. Do not send more than 1000 fits per job. Otherwise (given the way `submit.py` is written) random seeds will overlap between jobs.
1. What the job actually does is in `scripts/jobs/rxe_run_toys`. As shown, the project used is already online and will be downloaded before starting
the job.
1. If a new version of the project is available, it has to be added to `pypi` first.
1. The inputs are the _cached_ parameters stored in a tarball, mentioned above. These parameters are to be found in the `v65_v63_v24` directory
created from the ` $EXTDIR/v65_v63_v24.tar.gz` tarball, where for now

```bash
EXTDIR=/publicfs/lhcb/user/campoverde/Data/rx_extractor
```

therefore, the jobs have to be sent from the IHEP cluster or this variable has to be modified.

## Retrieving outputs

1. Start with an environment where DIRAC (and a valid grid certificate) is available.
1. Go to the directory where the outputs (e.g. `sandbox_test_004`) are.
1. Run:

```bash
./rxe_download -n test_004
```

where the argument is the name of the job.

## Plotting

Run:

```bash
./rkex_plot
```

to 

1. Read all the `JSON` files in the retrieved sandboxes
1. Make a dataframe with the fit parameters.
3. Make plots and send them to the `plots` directory.

