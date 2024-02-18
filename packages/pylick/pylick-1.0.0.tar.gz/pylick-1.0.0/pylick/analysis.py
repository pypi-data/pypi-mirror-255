import time
import warnings
# warnings.filterwarnings("ignore")
import numpy as np

from astropy.table import Table, MaskedColumn

from pylick.plot import spectrum_with_indices
from pylick.indices import IndexLibrary
from pylick.measurement import MeasSpectrum
from pylick.__config__ import __table__, __dirRes__


__all__ = ['Catalog', 'Galaxy']


def printConsole(text, color):
    if color == 'w':
        print("\x1b[0;49;97m"+text+"\x1b[0m")
    if color == 'c':
        print("\x1b[36m"+text+"\x1b[0m")
    if color == 'r':
        print("\x1b[91m"+text+"\x1b[0m")
    if color == 'y':
        print("\x1b[1;33m"+text+"\x1b[0m")

def helloMsg():
    printConsole("################################################################", 'r')
    printConsole("#### pyLick: A Python program to measure spectral indices.  ####", 'r')
    printConsole("####                                                        ####", 'r')
    printConsole("####        Authors: M. Moresco, N. Borghi, S. Quai         ####", 'r')
    printConsole("################################################################\n", 'r')

def progressBar(iteration, total, prefix = 'Progress:', suffix = '', length = 40, fill = '█'):
    prefix =  ("{:8s}").format(prefix)
    percent = ("{:d}").format(int(100 * (iteration / float(total))))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    # print('\rID {:s}: {:s}\t'.format(prefix, bar), end = "")
    print(f'  ID {prefix}: |{bar}| {percent}% {suffix}', end = "\r")

def printSingleRes(ID, names, vals, errs, BPR=None):
    printConsole("\n < Galaxy ID {:s} >".format(ID),'y')
    ind_table                   = Table(masked=True)
    ind_table["Index"]          = names
    ind_table["Value"]          = MaskedColumn(data=vals, mask=np.isnan(vals))
    ind_table["Error"]          = MaskedColumn(data=errs, mask=np.logical_or(np.isnan(vals), errs==0) )
    ind_table["BPR (%)"]        = BPR*100
    ind_table["Value"].format   = "{:.4f}"
    ind_table["Error"].format   = "{:.4f}"
    ind_table["BPR (%)"].format = "{:.1f}"
    ind_table.remove_rows(np.where(np.isnan(vals))[-1]) # Remove if index is not measured
    ind_table.pprint_all()

class Catalog:
    """Class optimized to handle the analysis of an entire catalog of galaxies. 

    >>> from pylick.analysis import Catalog
    >>> meas_table = Catalog(...)
    >>> print(meas_table)

    Args:
        IDs (str): galaxy unique identifier(s)
        load_spectrum (funct): takes one `ID` as argument and returns the corresponding spectral [wave, flux, err, mask].
        index_keys (list): keys of the indices to measure (see :class:`pylick.indices.IndexLibrary`).
        meas_method (str, optional): method to measure the indices ("int", "wei", "exact"). Defaults to "int".
        z (list, optional): if given, `wave`s are assumed to be in the obs. frame and shifted to rest-frame. Defaults to None.
        bpr_thres (float, optional): bad-to-total pixel ratio above which the measurement is not performed. Defaults to 1.
        file_table (str, optional): path to the file containing the indices definitions. Must be formatted as the default one located at `data/file_table.dat`.
        plot (bool, optional): produce plot file. Defaults to False.
        plot_settings (dict, optional): instruction for the plot code. Defaults to {}.
        verbose (bool, optional): prints warnings and execution time in the console. Defaults to False.
    """        


    def __init__(self, IDs, load_spectrum, index_keys, 
                 z=None, meas_method='int', bpr_thres=1., file_table=None, 
                 plot=False, plot_settings={}, verbose=False):    

        self.IDs            = np.array(IDs, dtype=str)
        self.index_keys     = index_keys
        self.meas_method    = meas_method
        self.bpr_thres      = bpr_thres
        self.file_table     = file_table 
        self.Nobj           = len(IDs)
        self.Nidx           = len(index_keys)
        self.file_table     = __table__ if self.file_table is None else file_table
        lib                 = IndexLibrary(file_table=file_table, index_keys=index_keys)

        data_names          = ['']*self.Nidx*2
        data_names[::2]     = lib.names
        data_names[1::2]    = [name+'_err' for name in lib.names]
        data_indices        = np.empty((self.Nobj, 2*self.Nidx), dtype=float)

        # GO
        t0 = time.time()
        helloMsg()

        # if not verbose: progressBar(0, self.Nobj)
        for i, ID in enumerate(self.IDs):

            if not verbose: progressBar(i, self.Nobj, ID)

            spectrum   = np.array(load_spectrum(ID))
            wave       = spectrum[0] if z is None else spectrum[0]/(1+z[i])
            flux       = spectrum[1]
            ferr       = spectrum[2]
            mask       = spectrum[3].astype(bool)
            ferr[mask] = 9.9*10**99

            assert wave.size == flux.size == ferr.size, \
                    "pyLick: wave, flux, (ferr) must have the same size"
            
            meas   = MeasSpectrum(wave=wave, flux=flux, ferr=ferr, todo=~mask,
                                  regions=lib.regions, units=lib.units, names=lib.names, 
                                  meas_method=self.meas_method, BPR_thres=self.bpr_thres, 
                                  nans=np.nan, verbose=False)

            names  = lib.names
            vals   = meas.vals 
            errs   = meas.errs

            # Fill results array ind1, ind1_err, ind2, ind2_err, ...
            data_indices[i][::2]  = vals
            data_indices[i][1::2] = errs

            if plot:
                spectrum_with_indices(ID, wave, flux, ferr, mask,
                                      lib.regions, lib.tex_names, lib.units, meas.finite,
                                      plot_settings)

            if verbose: printSingleRes(ID, names, vals, errs, meas.BPR)

        tf = time.time() - t0

        self.data_names   = data_names
        self.data_indices = data_indices

        if not verbose: 
            progressBar(i+1, self.Nobj, ID, suffix=" in {:.1f}s ({:.2f}/s)".format(tf, tf/self.Nobj))
            print()                
        else:
            print()
            printConsole("Elapsed time: {:.2f} s".format(tf), 'r')
            print()


    @property
    def results(self):
        """Retrieve the results table."""
        t =  Table(self.data_indices, names=self.data_names)
        t.add_column(self.IDs, name="ID", index=0)
        return t

    def __repr__(self):
        return "Catalog Class - use `.data_res` attributes to retrieve the measurements astropy.Table, alternatively print()"

    def __str__(self):
        return self.results

    def save(self, filename, filefmt="ascii.ecsv", prepend_colnames="", prepend_table=None):
        """Save the results table.

        Args:
            filename (str): filename.
            filefmt (str, optional): format of the :class:`astropy.Table` to save. Defaults to "ascii.ecsv".
            prepend_colnames (str, optional): string to which append index names to be used as catalog columns. Defaults to empty string.
            prepend_table (:class:`astropy.Table`, optional): catalog to which append the results. Defaults to None.
        """

        out_colnames = [prepend_colnames+x for x in self.data_names]

        if prepend_table is None:
            res_table       = Table(masked=True)
            res_table["ID"] = self.IDs
        else:
            res_table = Table(prepend_table, masked=True)

        for i, colname in enumerate(out_colnames):
            res_table.add_column(self.data_indices[:,i], name=colname)
        
        res_table.write(filename, overwrite=True)

    # end Catalog class



class Galaxy:
    """Class optimized to handle the analysis of a single galaxy. 

    >>> from pylick.analysis import Galaxy
    >>> ind_meas = Galaxy(...)
    >>> print(ind_meas)

    Args:
        ID (str): galaxy unique identifier
        index_keys (list): keys of the indices to measure (see :class:`pylick.indices.IndexLibrary`).
        wave (np.ndarray): wavelength sampling of the spectrum.
        flux (np.ndarray): spectral fluxes corresponding to `wave`.
        ferr (np.ndarray, optional): spectral fluxes uncertainties. Defaults to None.
        mask (np.ndarray, optional): boolean array flagging bad (True) and good (False) pixels. Defaults to None.
        z (float, optional): if given, `wave` is assumed to be in the obs. frame and shifted to rest-frame. Defaults to None.
        meas_method (str, optional): method to measure the indices ("int", "wei", "exact"). Defaults to "int".
        bpr_thres (float, optional): bad-to-total pixel ratio above which the measurement is not performed. Defaults to 1.
        file_table (str, optional): path to the file containing the indices definitions. Must be formatted as the default one located at `data/file_table.dat`.
        verbose (bool, optional): prints warnings and execution time in the console. Defaults to True.
    """        

    def __init__(self, ID, index_keys, wave, flux,
                 ferr=None, mask=None, z=None,
                 meas_method='int', bpr_thres=1., file_table=None,
                 plot=False, plot_settings={}, verbose=True):

        self.IDs           = ID
        self.index_keys    = index_keys
        self.wave          = np.array(wave)
        self.flux          = np.array(flux)
        self.meas_method   = meas_method
        self.bpr_thres     = bpr_thres
        self.file_table    = file_table 
        self.Nidx          = len(index_keys)

        self.file_table = __table__ if self.file_table is None else file_table

        self.wave = self.wave if z is None \
                    else self.wave/(1+z)

        self.ferr = np.zeros_like(self.wave) if ferr is None \
                    else np.array(ferr)
        
        self.mask = np.zeros_like(self.wave, dtype=bool) if mask is None \
                    else np.array(mask, dtype=bool) 

        assert self.wave.size == self.flux.size == self.ferr.size, \
                "pyLick: wave, flux, (ferr) must have the same size"

        # GO
        if verbose: t0 = time.time()

        self.qual             = (~self.mask)   # pixels to keep
        self.ferr[~self.qual] = 9.9*10**99.

        self.lib              = IndexLibrary(file_table=self.file_table, index_keys=self.index_keys)

        self.meas             = MeasSpectrum(self.wave, self.flux, self.ferr, self.qual,
                                             self.lib.regions, self.lib.units, self.lib.names, self.meas_method,
                                             BPR_thres=self.bpr_thres, nans=np.nan, verbose=verbose)


        if verbose: printConsole("Elapsed time: {:.2f} s\n".format(time.time() - t0), 'r')


    @property
    def names(self):
        """Retrieve indices names."""
        return self.lib.names

    @property
    def vals(self):
        """Retrieve indices values."""
        return self.meas.vals

    @property
    def errs(self):
        """Retrieve indices uncertainties."""
        return self.meas.errs

    def __repr__(self):
        return "Galaxy Class - use `.names`, `.vals`, `.errs` attributes to retrieve the measurements, alternatively print()"

    def __str__(self):
        msg = "{:10s}      {:5s}      {:5s}\n".format("names", "vals", "errs")
        msg = msg + '-'*len(msg) + '\n'

        for i in range(self.Nidx):
            if np.isnan(self.vals[i]) & np.isnan(self.errs[i]):
                continue
            else:
                msg = msg + "{:10s} {:10.4f} {:10.4f}\n".format(self.names[i], self.vals[i], self.errs[i])
        return msg  

    def plot(self, filename=None, settings={}):
        """ Produce the plot with annotated indices 
            (see :py:func:`pylick.plot.spectrum_with_indices`).

            Args:
                plot (bool, optional): produce plot file. Defaults to False.
                plot_settings (dict, optional): instructions for the plot code. Defaults to {}.
            
            Returns:
                ~matplotlib.figure.Figure: Figure
        """

        fig = spectrum_with_indices(self.wave, self.flux, self.ferr, mask=self.mask,
                                    index_regions=self.lib.regions, index_names=self.lib.tex_names, 
                                    index_units=self.lib.units, index_done=self.meas.finite,
                                    ax=None, settings=settings)

        if filename is None:
            fig.show()
        else:
            fig.savefig(filename)
        

    # end Galaxy class
