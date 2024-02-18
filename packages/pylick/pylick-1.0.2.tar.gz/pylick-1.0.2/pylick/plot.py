import matplotlib.pyplot as plt 
import matplotlib as mpl 
import numpy as np

from pylick.__config__ import __style__, __dirPlot__




def _default_settings(user_plParams):
    
    default_rcParams = {'lines.linewidth': 1.,
                        'axes.labelsize': 16.,
                        'xtick.top': True, 
                        'ytick.right': True,
                        'xtick.direction': 'in',
                        'ytick.direction': 'in',
                        'xtick.major.size': 5.,
                        'ytick.major.size': 5.,
                        'xtick.major.width': 1.,
                        'ytick.major.width': 1.,
                        'xtick.labelsize': 14.,
                        'ytick.labelsize': 14.,
                       }

    default_plParams = {'figsize': (8,4.8),
                        'xlab': r'Restframe wavelength [$\AA$]',
                        'ylab': r'Flux [unitless]',
                        # Colors of: flux, ferr, indices
                        'spec_colors': ['#000080', '#8E8EC2', (.4,.4,.4,1)],
                        # Style of the index patches (1: vband, 2: box)
                        'ind_style': 1,
                        # Fontsizes of: title, labels, indices 
                        'spec_fontsizes': [14, 14, 13],
                        'format': '.pdf',
                        # Debug
                        'inspect': False,
                        # Filename.ext of the plot to be saved
                        'filename': None,
                       }

    for k, v in default_rcParams.items():
        mpl.rcParams[k] = v

    for def_k, def_v in default_plParams.items():
        if not def_k in user_plParams:
            user_plParams[def_k] = def_v

    return user_plParams
        

def _rgba2rgb(rgba, background=(255,255,255)):  # Not used
    """Flattens transparent colors.

    Args:
        rgba (ndarray): 4D (RGBA) color array containing data with `float` type
        background (tuple, optional): White background color. Defaults to (255,255,255).

    Returns:
        ndarray: 3D (RGB) color array
    """
    row, col, ch    = rgba.shape
    rgb             = np.zeros((row, col, 3), dtype=float)
    r, g, b, a      = rgba[:,:,0], rgba[:,:,1], rgba[:,:,2], rgba[:,:,3]
    a               = np.asarray(a, dtype=float) / 255.0
    R, G, B         = background
    
    rgb[:,:,0], rgb[:,:,1], rgb[:,:,2] = r * a + (1.0 - a) * R, g * a + (1.0 - a) * G, b * a + (1.0 - a) * B

    return np.asarray(rgb, dtype='uint8')



def ax_addindex(ax, text, style, bbox_index, y_text, color, y_text_va="bottom", fontsize=13):
    """Plot and annotate an index region in data coordinates.

    Args:
        ax (axis): axis object
        text (str): name of the index to be displayed
        bbox_index (float, tuple): bounding box for the patch: (left, right, None, None) for vertical shadings, (left, right, down, up) for boxes
        y_text (float): y location of the text
        color (str, tuple): (r,g,b) color for the shadings. Must be in rgb format.
        fontsize (int): fontsize of the index to be displayed
    """ 

    if style==1:
        # Vertical shadings
        l, r = bbox_index[0], bbox_index[1]
        ax.axvspan(l, r, alpha=0.3, color=color, lw=1, zorder=4)
        text = ax.annotate(text, (0.5*(l+r), y_text), xycoords="data", 
                           rotation=90, ha='center',va=y_text_va, fontsize=fontsize, zorder=5)

    elif style==2:
        # Boxes
        l, r, d, u             = bbox_index
        alpha_face, alpha_edge = 0.2, 0.8
        col_face, col_edge     = [*color,alpha_face], [*color,alpha_edge] #darkdarkrblue
   
        rect = mpl.patches.Rectangle((l,d), width=(r-l), height=(u-d), 
                                     angle=0.0, facecolor=col_face, edgecolor=col_edge, lw=.7, ls='-')

        text = ax.annotate(text, (0.5*(l+r), y_text), xycoords="data", 
                           rotation=90, ha='center',va=y_text_va, fontsize=fontsize, zorder=5)
    else:            
        print("ERROR: Index style not suported: define bbox_index=(left, right, None, None) or (left, right, down, up)")

    return text


def spectrum_simple(wave, flux, ferr=None, mask=None, ax=None, settings={}):
    """
    Plots spetrum and associated errors (if given). A large error (9e9) is assigned to masked pixels, 
    making them appear as vertical lines. Additional settings may be passed as a dictionary using `settings`.

    Args:
        wave (np.ndarray): wavelength sampling of the spectrum
        flux (np.ndarray): spectral fluxes corresponding to `spec_wave`
        ferr (np.ndarray, optional): spectral fluxes' uncertainties.  Defaults to None.
        mask (np.ndarray, optional): boolean array flagging bad pixels to interpolate over. Defaults to None.
        ax (~matplotlib.axes.Axes, optional): overplot onto the provided ax object, otherwise create new figure. Defaults to None.
        settings (dict, optional): further instructions for the plot code. Defaults to {}.

    Returns:
        ~matplotlib.figure.Figure: Figure

    """

    # Load default configuration
    settings = _default_settings(settings)
    
    if ax is None:
        fig, ax = plt.subplots(figsize=settings["figsize"])

    if mask is not None:
        ferr[mask] = 9e9

    if ferr is not None:
        ax.fill_between(wave, flux-ferr, flux+ferr, step='mid', color=settings['spec_colors'][1], zorder=3)

    ax.step(wave, flux, where='mid', color=settings['spec_colors'][0], zorder=4)

    ax.set_xlabel(settings['xlab'], fontsize=settings['spec_fontsizes'][1])
    ax.set_ylabel(settings['ylab'], fontsize=settings['spec_fontsizes'][1])
    ax.set_ylim(np.nanmin(flux)*0.8, np.nanmax(flux)*1.05)

    return fig



def spectrum_with_indices(wave, flux, index_regions, index_names, index_units,
                          z=None, ferr=None, mask=None, ax=None, index_done=None, settings={}):

    """
    Plots :py:func:`spectrum_simple` with indices overlayed.

    Args:
        wave (np.ndarray): wavelength sampling of the spectrum
        flux (np.ndarray): spectral fluxes corresponding to `spec_wave`
        ferr (np.ndarray, optional): spectral fluxes' uncertainties.  Defaults to None.
        mask (np.ndarray, optional): boolean array flagging bad pixels to interpolate over. Defaults to None.
        ax (~matplotlib.axes.Axes, optional): overplot onto the provided ax object, otherwise create new figure. Defaults to None.
        settings (dict, optional): further instructions for the plot code. Defaults to {}.

    Returns:
        ~matplotlib.figure.Figure: Figure
        
    """

    # Load default configuration
    settings  = _default_settings(settings)

    if z is not None:
        wave = wave/(1+z)

    ferr = np.zeros_like(wave) if ferr is None else np.array(ferr)

    if mask is None:
        mask = np.zeros_like(wave, dtype=bool)

    if index_done is None:
        index_done = np.ones_like(index_names, dtype=bool)

    fig       = spectrum_simple(wave, flux, ferr, mask, ax, settings=settings)
    ax        = fig.gca()
    render    = fig.canvas.get_renderer()
    ax_heigth = np.diff(ax.get_ylim())[0]
    y_text    = ax.get_ylim()[0] + 0.05*ax_heigth
    spec_cols = [mpl.colors.to_rgb(col) for col in settings['spec_colors']]

    # Set xlim in advance to avoid problems with get_window_extent() leater
    xlim   = [min(wave[~mask][0], index_regions[0][1][0]),
              max(wave[~mask][-1], index_regions[-1][1][1])] if settings['inspect'] else \
             [min(wave[~mask][0], index_regions[index_done][0][1][0]),
              max(wave[~mask][-1], index_regions[index_done][-1][1][1]) ]  
    xspan  = xlim[1]-xlim[0]
    ax.set_xlim(xlim[0]-0.03*xspan, xlim[1]+0.03*xspan)

    # Avoid overlap between indices
    y_offset = np.zeros_like(index_names, dtype=float)
    
    for i in range(len(index_regions)):
        if (index_units[i] == 'A' or index_units[i] == 'mag'):

            # Extracting the central regions
            l, r = index_regions[i][1][0],index_regions[i][1][1]

            # Avoid overlap - to be further tested 
            if i>0:
                if 0.5*(l+r)<last_right_edge:
                    y_offset[i] += 1.2*last_texth
                
            if index_done[i]:
                t = ax_addindex(ax, text=r"$\mathrm{{{:s}}}$".format(index_names[i]), style=settings['ind_style'], 
                                bbox_index=(l,r,ax_heigth/2, ax_heigth/2), y_text=y_text+y_offset[i], 
                                color=spec_cols[2], y_text_va="bottom", fontsize=settings['spec_fontsizes'][2])
            elif settings['inspect']:
                t = ax_addindex(ax, text=r"$\mathrm{{{:s}}}$".format(index_names[i]), style=settings['ind_style'], 
                                bbox_index=(l,r,ax_heigth/2, ax_heigth/2), y_text=y_text+y_offset[i], 
                                color='darkred', y_text_va="bottom", fontsize=settings['spec_fontsizes'][2])

            _tbbox                 = t.get_window_extent(render).transformed(ax.transData.inverted()).get_points()
            last_textw, last_texth = _tbbox[1,0]-_tbbox[0,0], _tbbox[1,1]-_tbbox[0,1]
            last_right_edge        = 0.5*(l+r)+last_textw/3   # !!! empirical - to test
            
    # fig.subplots_adjust(left=0.125,bottom=0.135,right=0.95,top=0.92)

    if settings['filename']:
        fig.savefig(settings['filename'])
 
    return fig
