import os
import numpy as np
from astropy.io import fits



def _dir_build(path, dir_name, force=False):
    r""" Checks and builds `dir_name`

    Args:
        path (str): path of the folder to build
        dir_name (char): name of the folder to build
        force (bool): remove folder if already existing. Defaults to False.
    """

    full_path = path+'/'+dir_name+'/'

    if (not os.path.exists(full_path)):
        print("\nFolder {:s} created\n".format(dir_name))
        os.mkdir(full_path)

    elif force:
        print("\nFolder {:s} & its content are removed\n".format(dir_name))
        os.system('rm -r ' + full_path)
        os.mkdir(full_path)   

    else:
        print("\nWARNING: The folder {} already exists, set 'force=True' to remove it\n".format(full_path))



def _detect_spectrum_window(flux):
    r"""Finds the spectrum window excluding non-positive side regions

    Args:
        flux (np.ndarray): spectral fluxes

    Returns:
        np.ndarray: Boolean mask to remove side regions where flux is non-posivive
    """
    il   = 0
    ir   = -1
    while True:
        if (flux[il] > 0):
            break
        il += 1
    while True:
        if (flux[ir] > 0):
            break
        ir -= 1        
    flag_window = np.ones_like(flux, dtype=bool)
    flag_window[:il] = 0
    flag_window[ir:] = 0

    return flag_window



def load_spec_fits(dir_spec, filename, colnames=['wave', 'flux', 'ferr', 'mask'], reduce_window=False, hdul=1):
    r""" Function to load a .fits spectrum

    Args:
        dir_spec (str): directory where the spectrum is located
        filename (str): filename including the .fits extension
        colnames (list, optional): Names of the fits columns. Defaults to ['wave', 'flux', 'ferr', 'mask'].
        reduce_window (bool, optional): Whether to restrict the spectrum excluding non-positive side regions. Defaults to False.
        hdul (int, optional): N of the extension of the .fits Header Data Unit where the spectrum is located. Defaults to 1.

    Returns:
        list: spectrum imported according to the given colnames
    """
    spectrum = [[]]*len(colnames)

    hdulist  = fits.open(dir_spec+filename)

    if reduce_window:
        window      = _detect_spectrum_window(hdulist[hdul].data[colnames[hdul]][0])

        try:
            spectrum    = [hdulist[hdul].data[colnames[i]][0][window] for i in range(len(colnames))]
        except KeyError as e:
            print("> PyLick: {:s} - These are the available keys: {:s}".format(e, hdulist[hdul].columns))
    
    else:
        try:
            spectrum    = [hdulist[hdul].data[colnames[i]][0] for i in range(len(colnames))]
        except KeyError as e:
            print("> PyLick: {:s} - These are the available keys: {:s}".format(e, hdulist[hdul].columns))
    
    hdulist.close()

    return np.array(spectrum)



def spec_stats(wave, flux, ferr=None):
    r""" Prints statistics of the spectrum

    Args:
        wave (np.ndarray): wavelength sampling of the spectrum
        flux (np.ndarray): spectral fluxes corresponding to `spec_wave`
        ferr (np.ndarray, optional): spectral fluxes' uncertainties.  Defaults to None.
    """

    pars = ["wave", "flux"] if ferr is None else ["wave", "flux", "ferr", " SNR"]
    vals = [wave, flux] if ferr is None else [wave, flux, ferr]
    
    for p, v in zip(pars, vals):
        print(" {:s})\t range: {}--{}\t mean: {}\t median: {}" \
              .format(p, *np.around([v.min(), v.max(), np.mean(v), np.median(v)], decimals=2),)
             )

    print(" delta_wave_mean: {:.2f}".format(np.mean(np.diff(wave))))

