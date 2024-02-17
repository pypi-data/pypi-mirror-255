# Differential_check
This project is aim to extract diffefrential yield. 

# installation

Create a virtual environment and activate it:

```bash
mamba create -n diff_fit root=6.28 python=3.10
mamba activate diff_fit
```

## Variables binning file
Edit and run /script/save_var_bins.py

## Data preprocessing
Due to the conflicts between ROOT and zfit (maybe only for python 3.10?), data must be save locally before we import zfit. Edit and run /script/data_preprocceing.py to save data to .xslx files. (Xlsxwriter is required.)

## Get differential yields
/python/differential_fit.py contains code that can:
- Fit to the splited MC with a DSCB + exponential fit model.
- Do toy test for this fit model and parameters
- Fit to real data using mentioned parameters as initial value.
- Return fitted yields:

```python
d_yields = { var1 : [ yields_bin0, yields_bin1 ,... ],
             var2 : [ yields_bin0, yields_bin1 ,... ],
             ... }
```

(WIP)
