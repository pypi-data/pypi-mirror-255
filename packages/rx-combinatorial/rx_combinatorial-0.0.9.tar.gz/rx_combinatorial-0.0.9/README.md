# Purpose

The package is used to get estimates of the combinatorial shape in the signal region of the
RX analyses.

# Installation

1. Make a virtual environment with `ROOT` and `python` like:

```bash
mamba install -c conda-forge root>=6.26 python==3.9
```

2. Do:

   ```bash
   git clone ssh://git@gitlab.cern.ch:7999/r_k/cb_calculator.git
   cd cb_calculator
   pip install -e .
   ```

# Making small JSON files with data to be fitted from ntuples

Run:

```bash
cb_job -n 20 -d 2018 -t TOS -q mid -v v10.18dc -r 1
```

to submit `20` jobs for `2018`, `TOS` (can also do `TIS`) SS and OS data using the `mid` queue (run for up to 10 hours), test jobs run with `-r 0`, real ones with `-r 1`. The output will go to the place where `$CASDIR` points.

# Calculate scales through fits
Run:

```bash
get_scales -d 2018 -t ETOS -v v1 [-c]
```

which will place the scale factors in the `$CALDIR` directory and the fitting parameters alongside the plots in `$CASDIR`.

# Plotting nominal PDF and fluctuated ones

For a given dataset and version of scales do:

```bash
plot_uncertainties -d 2018 -t ETOS -q jpsi -v v1 [-c]
```

# Plotting other variables

For dumping other kind of plots do for instance:

```bash
plot_data -d 2018 -t ETOS -k OS -v v
```

and do:

```bash
plot_data -h
```

to know what arguments can be passed

# Accessing PDFs

## Nominal PDF
Do:

```python
from builder import builder

obj = builder(dset='2018', trigger='ETOS', vers='v1', q2bin='jpsi', const=False)
pdf = obj.get_pdf(obs=obs) 
```

to get the PDF for a given year, trigger and using a given version of the `SS-OS` correction. The user has to provide the observable.
The `const` parameter determines if the B mass used was obtained by constraining the respective charm meson, for high q2 `const=False` always.

The relevant parameters are:

| Setting | Value                |
|---------|----------------------|
| dset    | r1, r2p1, 2017, 2018 |
| trig    | ETOS, GTIS           |

## Uncertainties

To _fluctuate_ the PDF parameters according to the uncertainties instead do:

```python
pdf = obj.get_pdf(obs=obs, mu_unc=x, lm_unc=y)
```

where:


| Setting | Description                                                                                                                            |
|---------|----------------------------------------------------------------------------------------------------------------------------------------|
| -1      | Use OS PDF from the signal region fit                                                                                                  |
| 0       | Use SS PDF from the signal region fit                                                                                                  |
| None    | Use SS PDF with corrections to go to OS region                                                                                         |
| dict    | Dictionary with `{par:val}` where `par` is the PDF parameter and `val` is the number of sigmas to shift it. Used to assess systematics |

See usage examples here:

```
https://gitlab.cern.ch/r_k/cb_calculator/-/blob/master/tests/cb_maker.py
```