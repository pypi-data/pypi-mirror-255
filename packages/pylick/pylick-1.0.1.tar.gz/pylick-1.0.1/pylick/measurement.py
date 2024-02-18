import numpy as np
from scipy import interpolate, integrate


__all__ = [
    'MeasSpectrum'
    ]


def _direct_integration(y,x):
    res=0
    for i in range(len(x)-1):
        res+=y[i]*(x[i+1]-x[i])
    return res



def _wider_slice(todo, width=1):
    ''' Enlarge a slice of \pm width

    e.g. width=1,  0 0 0 1 1 0 0 -> 0 0 1 1 1 1 0

    '''
    tmptodo  = np.array(todo, dtype=bool)

    for i in range(width, np.size(tmptodo)-width+1):
        if todo[i] == True:
            tmptodo[i-width:i+width+1] = True

    return tmptodo



class MeasSpectrum:
    """Measurement of multiple indices on a single spectrum. 

    Args:
        IDs (str): galaxy unique identifier(s)
        index_list (list): list of indices to measure
        wave (np.ndarray): wavelength sampling of the spectrum
        flux (np.ndarray): spectral fluxes corresponding to `wave`
        ferr (np.ndarray, optional): spectral fluxes uncertainties.  Defaults to None.
        todo (np.ndarray, optional): boolean array flagging pixels to interpolate over. Defaults to None.
        z (float, optional): if given, `wave` are computed rest-frame. Defaults to None.
        bpr_thres (float, optional): bad-to-total pixel ratio above which the measurement is not performed. Defaults to None.
        meas_method (str, optional): method to measure the indices. Defaults to 'int'.
        index_table (str, optional): path to the user-defined table of indices. Defaults to None.
        plot (bool, optional): produce plot file. Defaults to False.
        plot_settings (dict, optional): instruction for the plot code. Defaults to {}.
    """

    def _slice_spec(self, wave, flux, ferr, todo, l, r, enlarge=None):
        """Creates slices of spectra given left and right margins

        Args:
            l (float): left margin
            r (float): right margin
            enlarge (int, optional): number of pixel to enlarge the region. Defaults to None.

        Returns:
            list: wave, flux, ferr arrays, number of total and bad pixels
        """
        clip = (wave > l) & (wave < r)

        if enlarge is not None:
            clip = _wider_slice(clip, width=enlarge)

        slice_wave  = wave[clip]
        slice_flux  = flux[clip]
        slice_ferr  = ferr[clip]
        n_pix_total = np.sum(clip)
        n_pix_bad   = np.sum(~todo[clip])
        
        # if 0:
        #     print("Slices of wave, flux, ferr")
        #     print(slice_wave)
        #     print(slice_flux)
        #     print(slice_ferr)
            # print("Total pixels: {}, of which bad {}".format(n_pix_total, n_pix_bad))

        return slice_wave, slice_flux, slice_ferr, n_pix_total, n_pix_bad


    def _flux_interp_np(self, l, r, binsize):
        """Interpolates the spetrum around the region [l,r] -/+ binsize

        Args:
            l (float): left margin
            r (float): right margin
            binsize ([type]): pixel size of the new interpolated array
        """        
        self.wave_intp = np.arange(l-binsize, r+binsize, binsize)
        self.flux_intp = np.interp(self.wave_intp, self.wave[self.todo],
                                        self.flux[self.todo])
        self.ferr_intp  = np.sqrt( np.interp(self.wave_intp, self.wave[self.todo], 
                                                np.square(self.ferr[self.todo])) )
        self.todo_intp = np.ceil( np.interp(self.wave_intp, self.wave, self.todo) ).astype(bool)


    def _flux_interp_exact(self, l, r, binsize):
        """Generates the interpolation function around the region [l,r] -/+ binsize

        Args:
            l (float): left margin
            r (float): right margin
            binsize ([type]): pixel size of the new interpolated array
        """    

        todo_intp = self.todo[self.todo]

        self.wave_intp = np.arange(l-binsize, r+binsize, binsize)
        self.flux_intp = interpolate.interp1d(self.wave[self.todo],self.flux[self.todo], kind=self.intp_kind)
        self.ferr_intp = interpolate.interp1d(self.wave[self.todo],self.ferr[self.todo], kind=self.intp_kind)

        # self.ferr_intp  = np.sqrt( np.interp(self.wave_intp, self.wave[self.todo], 
        #                                         np.square(self.ferr[self.todo])) )


    def _check_ind_def(self, regions, unit):
        msg = "PyLick: index regions are not properly defined"

        bb, br, cb, cr, rb, rr = regions.flatten()    

        if (unit == 'A') or (unit == 'mag'):
            assert bb < br and cb < cr and rb < rr, msg

    # ---------------------------------------------------------
    def _measure_multi_exact(self, regions, unit):
        """

        Parameters
        __________
        
        x : np.array
            spectrum wavelenghts

        y: np.array
            spectrum flux

        yerr : np.array

        
        regions : [np.float]*6
            index definition: blue pseudocont. [bb,br], central [cb, cr], red pseudocont. [rb, rr] 

        """



        bb, br, cb, cr, rb, rr = regions.flatten()              # Index definition bands
        bc, cc, rc = 0.5*(bb+br), 0.5*(cb+cr), 0.5*(rb+rr)		# Mean points
        db, dc, dr = (br - bb), (cr - cb), (rr - rb)			# Widths



        ind_value = self.nan
        ind_error = self.nan
        ind_BPR   = -1

        min_spec = np.min(self.wave[self.todo])
        max_spec = np.max(self.wave[self.todo])

        if (bb>min_spec) and (rr<max_spec): 

            # Interpolate the spectrum around the index region
            # self._flux_interp_exact(bb,rr,binsize=self.int_binsize)

            w_blu, f_blu, n_blu, Nblu, Nbad_blu = self._slice_spec(wave=self.wave,
                                                                   flux=self.flux,
                                                                   ferr=self.ferr,
                                                                   todo=self.todo,
                                                                   l=bb, r=br)
            w_cen, f_cen, n_cen, Ncen, Nbad_cen = self._slice_spec(wave=self.wave,
                                                                   flux=self.flux,
                                                                   ferr=self.ferr,
                                                                   todo=self.todo,
                                                                   l=cb, r=cr)
            w_red, f_red, n_red, Nred, Nbad_red = self._slice_spec(wave=self.wave,
                                                                   flux=self.flux,
                                                                   ferr=self.ferr,
                                                                   todo=self.todo,
                                                                   l=rb, r=rr)
            
            # flux_blu_mean = self.flux_intp.integral(bb, br)/(br-bb)
            # flux_red_mean = self.flux_intp.integral(rb, rr)/(rr-rb)
            flux_blu_mean = integrate.quad(self.flux_intp, bb, br, points=w_blu, limit=Nblu+2)[0] / (br-bb)
            flux_red_mean = integrate.quad(self.flux_intp, rb, rr, points=w_red, limit=Nred+2)[0] / (rr-rb)
            
            if (unit == 'A') or (unit == 'mag'):
                
                assert bb < br and cb < cr and rb < rr, "PyLick: index regions are not properly defined"

                # Pseudocontinuum estimated by linearly interpolating mean fluxes of lateral regions
                flux_pseudoc  = lambda x : ( flux_blu_mean * (rc - x) + flux_red_mean * (x - bc) ) / (rc - bc)

                ##### Errors from Cardiel et al. 1998
                # Number of pixels in the three bandpass
                Ntot	= Nblu + Ncen + Nred
                # OCIO!!!! To avoid errors from noise=0
                FNR     = np.sum(np.divide(f_blu,n_blu)) + np.sum(np.divide(f_cen,n_cen)) + np.sum(np.divide(f_red,n_red))
                SNR     = ( 1./(Ntot*np.sqrt(self.disp)) ) * FNR	# SN[AA]

                c2 = np.sqrt((1./dc)+
                                (((rc-cc)/(rc-bc))**2)*(1./db) +
                                (((cc-bc)/(rc-bc))**2)*(1./dr))
                c1 = dc*c2				
                c3 = 2.5*c2*np.log10(np.e)

                # Bad Pixels Ratio
                ind_BPR = (Nbad_blu+Nbad_cen+Nbad_red)/Ntot

                if unit == 'A':
                    fcn 		= lambda x : (1 - self.flux_intp(x) / flux_pseudoc(x))
                    ind_value	= integrate.quad(fcn, cb, cr, points=w_cen,  limit=Ncen+2)
                    # print(ind_value)
                    ind_value = ind_value[0]
                    ind_error 	= (c1-(c2*ind_value)) / SNR

                if unit == 'mag':
                    fcn 		= lambda x : (self.flux_intp(x) / flux_pseudoc(x))
                    ind_value	= -2.5 * np.log10( integrate.quad(fcn, cb, cr, points=w_cen, limit=Ncen+2)[0] / (cr - cb) )
                    ind_error 	= c3 / SNR

            elif unit == 'break_nu':
                flux_nu		  = lambda x : x**2 * self.flux_intp(x)
                noise_nu   	  = lambda x : x**2 * self.ferr_intp(x)
                flux_blu_mean = integrate.quad(flux_nu, bb, br, points=w_blu, limit=Nblu+2)[0] / (br-bb)
                flux_red_mean = integrate.quad(flux_nu, rb, rr, points=w_red, limit=Nred+2)[0] / (rr-rb)
                ind_value	  = flux_red_mean/flux_blu_mean

                #ERROR
                SNR_red		= (1./(Nred*np.sqrt(self.disp))) * (np.sum( flux_nu(w_red)/noise_nu(w_red) ))
                SNR_blue	= (1./(Nblu*np.sqrt(self.disp))) * (np.sum( flux_nu(w_blu)/noise_nu(w_blu) ))
                ind_error 	= ind_value * np.sqrt((1./np.square(SNR_blue)) + (1./np.square(SNR_red))) / np.sqrt(dr)
                
            
                # Bad Pixels Ratio
                ind_BPR = (Nbad_blu+Nbad_red) / (Nblu+Nred) 

            elif unit == 'break_lb':
                ind_value	= flux_red_mean/flux_blu_mean

                #ERROR
                SNR_red		= (1./(Nred*np.sqrt(self.disp))) * (np.sum(np.divide(f_red,n_red)))
                SNR_blue	= (1./(Nblu*np.sqrt(self.disp))) * (np.sum(np.divide(f_red,n_red)))
                ind_error 	= ind_value * np.sqrt((1./np.square(SNR_blue)) + (1./np.square(SNR_red))) / np.sqrt(dr) #ocio

                # Bad Pixels Ratio
                ind_BPR = (Nbad_blu+Nbad_red) / (Nblu+Nred) 

            else:
                print(unit)

        return ind_value, ind_error, ind_BPR


    def _measure_multi_interp(self, regions, unit):
        """ Interpolation method

        Args:
            regions (float): [[bb,br], [cb,cr], [rb, rr]] i.e. [blue pseudocont., central, red pseudocont.] 
            unit (str): unit type (A, mag, break_nu, break_lb), this defines the index

        Returns:
            ndarray: ind_value, ind_error, ind_BPR
        """

        bb, br, cb, cr, rb, rr = regions.flatten()              # Index definition bands

        ind_value = self.nan
        ind_error = self.nan
        ind_BPR   = -1

        min_spec = np.min(self.wave[self.todo])
        max_spec = np.max(self.wave[self.todo])

        
        if (bb>min_spec) and (rr<max_spec): 
            
            # Interpolate the spectrum around the index region
            self._flux_interp_np(bb,rr,binsize=self.int_binsize)


            bc, cc, rc = 0.5*(bb+br), 0.5*(cb+cr), 0.5*(rb+rr)		# Mean points
            db, dc, dr = (br - bb), (cr - cb), (rr - rb)			# Widths

            
            w_blu, f_blu, n_blu, Nblu, Nbad_blu = self._slice_spec(wave=self.wave_intp, 
                                                                   flux=self.flux_intp,
                                                                   ferr=self.ferr_intp,
                                                                   todo=self.todo_intp,
                                                                   l=bb,r=br)
            w_cen, f_cen, n_cen, Ncen, Nbad_cen = self._slice_spec(self.wave_intp, 
                                                                   self.flux_intp,
                                                                   self.ferr_intp,
                                                                   self.todo_intp,
                                                                   l=cb, r=cr)
            w_red, f_red, n_red, Nred, Nbad_red = self._slice_spec(self.wave_intp, 
                                                                   self.flux_intp,
                                                                   self.ferr_intp,
                                                                   self.todo_intp,
                                                                   l=rb, r=rr)
            
            flux_blu_mean = f_blu.mean()
            flux_red_mean = f_red.mean()
            wave_blu_mean = w_blu.mean()
            wave_red_mean = w_red.mean()

            if (unit == 'A') or (unit == 'mag'):
                
                assert bb < br and cb < cr and rb < rr, "PyLick: index regions are not properly defined"

                # Estimate pseudo-continuum
                m           = (flux_red_mean-flux_blu_mean)/(wave_red_mean-wave_blu_mean)
                q           = flux_blu_mean - m*wave_blu_mean
                f_pseudo    = m * (w_cen) + q

                ##### ERROR (Cardiel+1998)
                # Number of pixels in the three bandpass
                Ntot	= Nblu + Ncen + Nred
                # Flux to noise ratio
                FNR     = np.sum(np.divide(f_blu,n_blu)) + np.sum(np.divide(f_cen,n_cen)) + np.sum(np.divide(f_red,n_red))
                SNR     = ( 1./(Ntot*np.sqrt(self.disp)) ) * FNR	# SN[AA]
                c2 = np.sqrt((1./dc)+
                                (((rc-cc)/(rc-bc))**2)*(1./db) +
                                (((cc-bc)/(rc-bc))**2)*(1./dr))
                c1 = dc*c2				
                c3 = 2.5*c2*np.log10(np.e)

                # Bad Pixels Ratio
                ind_BPR = (Nbad_blu+Nbad_cen+Nbad_red) / Ntot 

                if unit == 'A':
                    ind_value = integrate.simps(1-(f_cen/f_pseudo),w_cen,even='avg')
                    ind_error = (c1-(c2*ind_value)) / SNR

                elif unit == 'mag':
                    ind_value = -2.5*np.log10(integrate.simps(f_cen/f_pseudo,w_cen,even='avg')/dc)
                    ind_error = c3 / SNR


            elif unit == 'break_nu':
                flux_nu_red  = np.multiply(np.square(w_red),f_red)
                flux_nu_blu  = np.multiply(np.square(w_blu),f_blu)
                noise_nu_red = np.multiply(np.square(w_red),n_red)
                noise_nu_blu = np.multiply(np.square(w_blu),n_blu)
                SNR_red		= (1./(Nred*np.sqrt(self.disp))) * (np.sum(np.divide(flux_nu_red,noise_nu_red)))
                SNR_blue	= (1./(Nblu*np.sqrt(self.disp))) * (np.sum(np.divide(flux_nu_blu,noise_nu_blu)))

                ind_value   = flux_nu_red.mean()/flux_nu_blu.mean()
                ind_error 	= ind_value * np.sqrt((1./np.square(SNR_blue)) + (1./np.square(SNR_red))) / np.sqrt(dr)

                # Bad Pixels Ratio
                ind_BPR = (Nbad_blu+Nbad_red) / (Nblu+Nred) 

            elif unit == 'break_lb':
                SNR_red		= (1./(Nred*np.sqrt(self.disp))) * (np.sum(np.divide(f_red,n_red)))
                SNR_blue	= (1./(Nblu*np.sqrt(self.disp))) * (np.sum(np.divide(f_blu,n_blu)))
                
                ind_value	= flux_red_mean/flux_blu_mean
                ind_error 	= ind_value * np.sqrt((1./np.square(SNR_blue)) + (1./np.square(SNR_red))) / np.sqrt(dr) #ocio

                # Bad Pixels Ratio
                ind_BPR = (Nbad_blu+Nbad_red) / (Nblu+Nred) 

            else:
                print(unit)

        else:
            if self.debug:
                print("pylick: Index outside of the spectrum ({:.2f} < lambda < {:.2f})".format(min_spec, max_spec))


        return ind_value, ind_error, ind_BPR


    def _measure_multi_wei(self, regions, unit):
        
        # Index definition bands = [bb, br], [cb, cr], [rb, rr]
        bb, br, cb, cr, rb, rr = regions.flatten()              

        ind_value = self.nan
        ind_error = self.nan
        ind_BPR   = -1

        if (bb>self.wave.min()) and (rr<self.wave.max()):

            bc, cc, rc = 0.5*(bb+br), 0.5*(cb+cr), 0.5*(rb+rr)		# Mean points
            db, dc, dr = (br - bb), (cr - cb), (rr - rb)			# Widths

            w_blu, f_blu, n_blu, Nblu, Nbad_blu = self._slice_spec(bb, br, enlarge=1)
            w_cen, f_cen, n_cen, Ncen, Nbad_cen = self._slice_spec(cb, cr, enlarge=1)
            w_red, f_red, n_red, Nred, Nbad_red = self._slice_spec(rb, rr, enlarge=1)
            
            weight_b              = np.ones(Nblu, dtype=float)
            weight_r              = np.ones(Nred, dtype=float)
            weight_b[0]           = (w_blu[1] - bb) / (w_blu[1] - w_blu[0])
            weight_r[0]           = (w_red[1] - rb) / (w_red[1] - w_red[0])
            weight_b[-1]          = (br - w_blu[-2]) / (w_blu[-1] - w_blu[-2])
            weight_r[-1]          = (rr - w_red[-2]) / (w_red[-1] - w_red[-2])
            weight_b[weight_b>1.] = 1.
            weight_r[weight_r>1.] = 1.

            flux_blu_mean = np.average(f_blu, weights=weight_b)
            flux_red_mean = np.average(f_red, weights=weight_r)
            
            if (unit == 'A') or (unit == 'mag'):
                weight_c              = np.ones(Ncen, dtype=float)
                weight_c[0]           = (w_cen[1] - cb) / (w_cen[1] - w_cen[0])
                weight_c[-1]          = (cr - w_cen[-2]) / (w_cen[-1] - w_cen[-2])
                weight_c[weight_c>1.] = 1.
                
                # Estimate pseudo-continuum
                bc            = np.average(w_blu, weights=weight_b)
                rc            = np.average(w_red, weights=weight_r)
                m             = (flux_red_mean-flux_blu_mean)/(rc-bc)
                q             = flux_blu_mean - m*bc
                f_pseudo      = m * (w_cen) + q

                ##### ERROR
                # Number of pixels in the three bandpass
                Ntot	= Nblu + Ncen + Nred
                # Flux to noise ratio
                FNR     = np.sum(np.divide(f_blu*weight_b,n_blu)) + \
                        np.sum(np.divide(f_cen*weight_c,n_cen)) + \
                        np.sum(np.divide(f_red,n_red))

                SNR     = ( 1./(Ntot*np.sqrt(self.disp)) ) * FNR

                c2 = np.sqrt((1./dc)+
                            (((rc-cc)/(rc-bc))**2)*(1./db) +
                            (((cc-bc)/(rc-bc))**2)*(1./dr))
                c1 = dc*c2				
                c3 = 2.5*c2*np.log10(np.e)

                # Bad Pixels Ratio
                ind_BPR = (Nbad_blu+Nbad_cen +Nbad_red) / Ntot
                # ind_BPR = (Nbad_cen) / Ncen


                if (unit=='A') :
                    #ind_value=simps((1-(flux_ind/pc_ind))*weight_ind,lambda_ind,even='avg')	
                    #ind_value=trapz(1-(flux_ind/pc_ind),lambda_ind)	
                    ind_value=_direct_integration((1-(f_cen/f_pseudo))*weight_c,w_cen)
                    ind_error = (c1-(c2*ind_value)) / SNR

                elif (unit=='mag') :
                    #ind_value=-2.5*log10(simps(flux_ind/pc_ind*weight_ind,lambda_ind,even='avg')/(cr-cb))	
                    #ind_value=-2.5*log10(trapz(flux_ind/pc_ind,lambda_ind)/(cr[i]-cb[i]))	
                    ind_value=-2.5*np.log10(_direct_integration(f_cen/f_pseudo*weight_c,w_cen)/dc)
                    ind_error = c3 / SNR


            elif unit == 'break_nu':
                flux_nu_red  = np.multiply(np.square(w_red),f_red)
                flux_nu_blu  = np.multiply(np.square(w_blu),f_blu)
                noise_nu_red = np.multiply(np.square(w_red),n_red)
                noise_nu_blu = np.multiply(np.square(w_blu),n_blu)
                disp_r       = np.mean(np.diff(w_red))
                disp_b       = np.mean(np.diff(w_blu))
                SNR_red		 = (1./(Nred*np.sqrt(disp_r))) * (np.sum(np.divide(flux_nu_red*weight_r,noise_nu_red)))
                SNR_blue	 = (1./(Nblu*np.sqrt(disp_b))) * (np.sum(np.divide(flux_nu_blu*weight_b,noise_nu_blu)))

                ind_value    = np.average(flux_nu_red, weights=weight_r) / np.average(flux_nu_blu, weights=weight_b)
                ind_error 	 = ind_value * np.sqrt((1./np.square(SNR_blue)) + (1./np.square(SNR_red))) / np.sqrt(dr)
                
                # Bad Pixels Ratio
                ind_BPR = (Nbad_blu+Nbad_red) / (Nblu+Nred) 

            elif unit == 'break_lb':
                disp_r       = np.mean(np.diff(w_red))
                disp_b       = np.mean(np.diff(w_blu))
                SNR_red		 = (1./(Nred*np.sqrt(disp_r))) * (np.sum(np.divide(f_red*weight_r,n_red)))
                SNR_blue	 = (1./(Nblu*np.sqrt(disp_b))) * (np.sum(np.divide(f_blu*weight_b,n_blu)))
                
                ind_value	 = flux_red_mean/flux_blu_mean
                ind_error 	 = ind_value * np.sqrt((1./np.square(SNR_blue)) + (1./np.square(SNR_red))) / np.sqrt(dr)

                # Bad Pixels Ratio
                ind_BPR = (Nbad_blu+Nbad_red) / (Nblu+Nred) 

        return ind_value, ind_error, ind_BPR


    # ------------------------------------------- To Be Done...
    def _measure_ind_general_int(self,x,y,erry,disp):
        # bb,br = blue 
        # cb,cr = central
        # rb,rr = red
        print(" This feature is not available yet.")
        if False:
            # Ref. Cenarro et al. (2001)
            # pseudocontinuum:
            flux_generic_pc=y[(x>=8474.)*(x<=8484.)+(x>=8563.)*(x<=8577.)+(x>=8619.)*(x<=8642.)+(x>=8700.)*(x<=8725.)+(x>=8776.)*(x<=8792.)]
            noise_generic_pc=erry[(x>=8474.)*(x<=8484.)+(x>=8563.)*(x<=8577.)+(x>=8619.)*(x<=8642.)+(x>=8700.)*(x<=8725.)+(x>=8776.)*(x<=8792.)]		
            lambda_generic_pc=x[(x>=8474.)*(x<=8484.)+(x>=8563.)*(x<=8577.)+(x>=8619.)*(x<=8642.)+(x>=8700.)*(x<=8725.)+(x>=8776.)*(x<=8792.)]
            pc = np.polyfit(lambda_generic_pc, flux_generic_pc, 1, rcond=None, full= False, w = np.divide(1., noise_generic_pc))								
            # CaT: Ca1 + Ca2 + Ca3
            # Ca1 central bandpass = [8484.0, 8513.0]
            flux_Ca1=y[np.logical_and(x>=8484.,x<=8513.)]
            lambda_Ca1=x[np.logical_and(x>=8484.,x<=8513.)]
            pc_Ca1=pc[0]*lambda_Ca1+pc[1]
            #	Ca1 = simps( 1. - ( flux_Ca1 / pc_Ca1 ), lambda_Ca1, even='avg' )
            Ca1=disp*np.sum(1.-(flux_Ca1/pc_Ca1))
            # Ca2 central bandpass = [8522.0, 8562.0]
            flux_Ca2=y[np.logical_and(x>=8522.,x<=8562.)]
            lambda_Ca2=x[np.logical_and(x>=8522.,x<=8562.)]
            pc_Ca2=pc[0]*lambda_Ca2+pc[1]
            #	Ca2 = simps( 1. - ( flux_Ca2 / pc_Ca2 ), lambda_Ca2, even='avg' )
            Ca2=disp*np.sum(1.-(flux_Ca2/pc_Ca2))
            # Ca3 central bandpass = [8642.0, 8682.0]
            flux_Ca3=y[np.logical_and(x>=8642.,x<=8682.)]
            lambda_Ca3=x[np.logical_and(x>=8642.,x<=8682.)]
            pc_Ca3=pc[0]*lambda_Ca3+pc[1]
            #	Ca3 = simps( 1. - ( flux_Ca3 / pc_Ca3 ), lambda_Ca3, even='avg' )
            Ca3=disp*np.sum(1.-(flux_Ca3/pc_Ca3))
            #print 'Ca', Ca1, Ca2, Ca3
            CaT=Ca1+Ca2+Ca3
            #print 'CaT', CaT
            # PaT: Pa1 + Pa2 + Pa3
            # Pa1 central bandpass = [8461.0, 8474.0]
            flux_Pa1=y[np.logical_and(x>=8461.,x<=8474.)]
            lambda_Pa1=x[np.logical_and(x>=8461.,x<=8474.)]
            pc_Pa1=pc[0]*lambda_Pa1+pc[1]
            #	Pa1 = simps( 1. - ( flux_Pa1 / pc_Pa1 ), lambda_Pa1, even='avg' )
            Pa1=disp*np.sum(1.-(flux_Pa1/pc_Pa1))
            # Pa2 central bandpass = [8577.0, 8619.0]
            flux_Pa2=y[np.logical_and(x>=8577.,x<=8619.)]
            lambda_Pa2=x[np.logical_and(x>=8577.,x<=8619.)]
            pc_Pa2=pc[0]*lambda_Pa2+pc[1]
            #	Pa2 = simps( 1. - ( flux_Pa2 / pc_Pa2 ), lambda_Pa2, even='avg' )
            Pa2=disp*np.sum(1.-(flux_Pa2/pc_Pa2))
            # Pa3 central bandpass = [8730.0, 8772.0]
            flux_Pa3=y[np.logical_and(x>=8730.,x<=8772.)]
            lambda_Pa3=x[np.logical_and(x>=8730.,x<=8772.)]
            pc_Pa3=pc[0]*lambda_Pa3+pc[1]
            #	Pa3 = simps( 1. - ( flux_Pa3 / pc_Pa3 ), lambda_Pa3, even='avg' )
            Pa3=disp*np.sum(1.-(flux_Pa3/pc_Pa3))
            PaT=Pa1+Pa2+Pa3
            #print 'PaT', PaT
            # CaT^* = CaT - 0.93 PaT (Cenarro et al. (2001)) 
            lick_value=CaT-(0.93*PaT) 
            # Error CaT^*:
            flux_SN_CaT=y[(x>=8484.)*(x<=8513.)+(x>=8522.)*(x<=8562.)+(x>=8642.)*(x<=8682.)+(x>=8461.)*(x<=8474.)+(x>=8577.)*(x<=8619.)+(x>=8730.)*(x<=8772.)+(x>=8474.)*(x<=8484.)+(x>=8562.)*(x<=8577.)+(x>=8619.)*(x<=8642.)+(x>=8700.)*(x<=8725.)+(x>=8776.)*(x<=8792.)]
            noise_SN_CaT=erry[(x>=8484.)*(x<=8513.)+(x>=8522.)*(x<=8562.)+(x>=8642.)*(x<=8682.)+(x>=8461.)*(x<=8474.)+(x>=8577.)*(x<=8619.)+(x>=8730.)*(x<=8772.)+(x>=8474.)*(x<=8484.)+(x>=8562.)*(x<=8577.)+(x>=8619.)*(x<=8642.)+(x>=8700.)*(x<=8725.)+(x>=8776.)*(x<=8792.)]
            rapp_SN_CaT=np.sum(np.divide(flux_SN_CaT,noise_SN_CaT))
            N_SN_CaT=len(flux_SN_CaT)
            SN_CaT=(1./(N_SN_CaT*np.sqrt(disp)))*rapp_SN_CaT
            lick_error=(16.43-(0.1052*lick_value))/SN_CaT	
            #	#xp = np.linspace(8400, 8800, 1200)
            #	_ = plt.plot(lambda_Pa1, flux_Pa1, '.-', lambda_Pa1, pc_Pa1, '--',lambda_Pa2, flux_Pa2, '.-', lambda_Pa2, pc_Pa2, '--',lambda_Pa3, flux_Pa3, '.-', lambda_Pa3, pc_Pa3, '--')
            #	plt.xlim(8350, 8900)
            #	#plt.ylim(0.0001, 0.0003)
            #	plt.show()
        else:
            lick_value=self.nan
            lick_error=self.nan
        return lick_value, lick_error

    def _measure_ind_general_wei(self,x,y,erry,disp):
        """
        .. warning:
        To be implemented
        """
        print(" This feature is not available yet.")

        if (x.min()<bb and x.max()>rr):
            # Ref. Cenarro et al. (2001)
            # pseudocontinuum:
            flux_generic_pc=y[(x>=8474.)*(x<=8484.)+(x>=8563.)*(x<=8577.)+(x>=8619.)*(x<=8642.)+(x>=8700.)*(x<=8725.)+(x>=8776.)*(x<=8792.)]
            noise_generic_pc=erry[(x>=8474.)*(x<=8484.)+(x>=8563.)*(x<=8577.)+(x>=8619.)*(x<=8642.)+(x>=8700.)*(x<=8725.)+(x>=8776.)*(x<=8792.)]		
            lambda_generic_pc=x[(x>=8474.)*(x<=8484.)+(x>=8563.)*(x<=8577.)+(x>=8619.)*(x<=8642.)+(x>=8700.)*(x<=8725.)+(x>=8776.)*(x<=8792.)]
            pc = np.polyfit(lambda_generic_pc, flux_generic_pc, 1, rcond=None, full= False, w = np.divide(1., noise_generic_pc))								
            # CaT: Ca1 + Ca2 + Ca3
            # Ca1 central bandpass = [8484.0, 8513.0]
            flux_Ca1=y[np.logical_and(x>=8484.,x<=8513.)]
            lambda_Ca1=x[np.logical_and(x>=8484.,x<=8513.)]
            pc_Ca1=pc[0]*lambda_Ca1+pc[1]
            #	Ca1 = simps( 1. - ( flux_Ca1 / pc_Ca1 ), lambda_Ca1, even='avg' )
            Ca1=disp*np.sum(1.-(flux_Ca1/pc_Ca1))
            # Ca2 central bandpass = [8522.0, 8562.0]
            flux_Ca2=y[np.logical_and(x>=8522.,x<=8562.)]
            lambda_Ca2=x[np.logical_and(x>=8522.,x<=8562.)]
            pc_Ca2=pc[0]*lambda_Ca2+pc[1]
            #	Ca2 = simps( 1. - ( flux_Ca2 / pc_Ca2 ), lambda_Ca2, even='avg' )
            Ca2=disp*np.sum(1.-(flux_Ca2/pc_Ca2))
            # Ca3 central bandpass = [8642.0, 8682.0]
            flux_Ca3=y[np.logical_and(x>=8642.,x<=8682.)]
            lambda_Ca3=x[np.logical_and(x>=8642.,x<=8682.)]
            pc_Ca3=pc[0]*lambda_Ca3+pc[1]
            #	Ca3 = simps( 1. - ( flux_Ca3 / pc_Ca3 ), lambda_Ca3, even='avg' )
            Ca3=disp*np.sum(1.-(flux_Ca3/pc_Ca3))
            #print 'Ca', Ca1, Ca2, Ca3
            CaT=Ca1+Ca2+Ca3
            #print 'CaT', CaT
            # PaT: Pa1 + Pa2 + Pa3
            # Pa1 central bandpass = [8461.0, 8474.0]
            flux_Pa1=y[np.logical_and(x>=8461.,x<=8474.)]
            lambda_Pa1=x[np.logical_and(x>=8461.,x<=8474.)]
            pc_Pa1=pc[0]*lambda_Pa1+pc[1]
            #	Pa1 = simps( 1. - ( flux_Pa1 / pc_Pa1 ), lambda_Pa1, even='avg' )
            Pa1=disp*np.sum(1.-(flux_Pa1/pc_Pa1))
            # Pa2 central bandpass = [8577.0, 8619.0]
            flux_Pa2=y[np.logical_and(x>=8577.,x<=8619.)]
            lambda_Pa2=x[np.logical_and(x>=8577.,x<=8619.)]
            pc_Pa2=pc[0]*lambda_Pa2+pc[1]
            #	Pa2 = simps( 1. - ( flux_Pa2 / pc_Pa2 ), lambda_Pa2, even='avg' )
            Pa2=disp*np.sum(1.-(flux_Pa2/pc_Pa2))
            # Pa3 central bandpass = [8730.0, 8772.0]
            flux_Pa3=y[np.logical_and(x>=8730.,x<=8772.)]
            lambda_Pa3=x[np.logical_and(x>=8730.,x<=8772.)]
            pc_Pa3=pc[0]*lambda_Pa3+pc[1]
            #	Pa3 = simps( 1. - ( flux_Pa3 / pc_Pa3 ), lambda_Pa3, even='avg' )
            Pa3=disp*np.sum(1.-(flux_Pa3/pc_Pa3))
            PaT=Pa1+Pa2+Pa3
            #print 'PaT', PaT
            # CaT^* = CaT - 0.93 PaT (Cenarro et al. (2001)) 
            lick_value=CaT-(0.93*PaT) 
            # Error CaT^*:
            flux_SN_CaT=y[(x>=8484.)*(x<=8513.)+(x>=8522.)*(x<=8562.)+(x>=8642.)*(x<=8682.)+(x>=8461.)*(x<=8474.)+(x>=8577.)*(x<=8619.)+(x>=8730.)*(x<=8772.)+(x>=8474.)*(x<=8484.)+(x>=8562.)*(x<=8577.)+(x>=8619.)*(x<=8642.)+(x>=8700.)*(x<=8725.)+(x>=8776.)*(x<=8792.)]
            noise_SN_CaT=erry[(x>=8484.)*(x<=8513.)+(x>=8522.)*(x<=8562.)+(x>=8642.)*(x<=8682.)+(x>=8461.)*(x<=8474.)+(x>=8577.)*(x<=8619.)+(x>=8730.)*(x<=8772.)+(x>=8474.)*(x<=8484.)+(x>=8562.)*(x<=8577.)+(x>=8619.)*(x<=8642.)+(x>=8700.)*(x<=8725.)+(x>=8776.)*(x<=8792.)]
            rapp_SN_CaT=np.sum(np.divide(flux_SN_CaT,noise_SN_CaT))
            N_SN_CaT=len(flux_SN_CaT)
            SN_CaT=(1./(N_SN_CaT*np.sqrt(disp)))*rapp_SN_CaT
            lick_error=(16.43-(0.1052*lick_value))/SN_CaT	
            #	#xp = np.linspace(8400, 8800, 1200)
            #	_ = plt.plot(lambda_Pa1, flux_Pa1, '.-', lambda_Pa1, pc_Pa1, '--',lambda_Pa2, flux_Pa2, '.-', lambda_Pa2, pc_Pa2, '--',lambda_Pa3, flux_Pa3, '.-', lambda_Pa3, pc_Pa3, '--')
            #	plt.xlim(8350, 8900)
            #	#plt.ylim(0.0001, 0.0003)
            #	plt.show()
        else:
            lick_value=self.nan
            lick_error=self.nan
        return lick_value, lick_error

        #-------------------------------------------------------------


    # ---------------------------------------------------------
    def __init__(self, wave, flux, ferr, todo, regions, units, names, meas_method, BPR_thres, nans, verbose):

        Nindices         = len(regions)
        self.wave        = wave
        self.flux        = flux
        self.ferr        = ferr 
        self.todo        = todo
        self.regions     = regions
        self.units       = units
        self.nan         = nans
        self.int_binsize = 0.0625
        self.intp_kind   = 'linear'
        self.debug       = verbose

        # Average dispersion of the spectrum
        # SPECTRA SHOULD BE LINEARLY SAMPLED, so disp=pixel dimension
        dispv     = np.diff(self.wave)
        self.disp = dispv.mean()

        self.vals = np.full(Nindices, np.nan, dtype=float)
        self.errs = np.full(Nindices, np.nan, dtype=float)
        self.BPR  = np.full(Nindices, np.nan, dtype=float)

        # if meas_method == 'int':
        #     # Interpolate spectrum (0.0625 AA)
        #     self._flux_interp(bin=0.0625)
        
        if wave[todo].sum() > 10:    # To avoid errors due to very bad spactra while running the catalog

            for k in range(Nindices):

                self._check_ind_def(self.regions[k],self.units[k])   # To move into the indices module


                if meas_method == 'exact':	
                    # self.flux_intp = interpolate.interp1d(wave[todo],flux[todo], kind='zero')
                    # self.ferr_intp  = interpolate.interp1d(wave[todo],ferr[todo], kind='zero')
                    # # self.flux_intp = lambda x: np.interp(x, wave, flux)
                    # # self.ferr_intp  = lambda x: np.interp(x, wave, ferr)
                    bb, rr = np.nanmin(wave[todo]), np.nanmax(wave[todo])
                    self._flux_interp_exact(bb,rr,binsize=self.int_binsize)

                    self.vals[k], self.errs[k], self.BPR[k] = self._measure_multi_exact(self.regions[k],self.units[k])


                elif meas_method == 'int':
                    self.vals[k], self.errs[k], self.BPR[k] = self._measure_multi_interp(self.regions[k],self.units[k])


                elif meas_method == 'wei':
                    self.vals[k], self.errs[k], self.BPR[k] = self._measure_multi_wei(self.regions[k],self.units[k])
                    

                else:
                    raise ValueError("PyLick: meas_method not understood.")
        
        bad             = self.BPR > BPR_thres
        self.vals[bad]  = self.nan
        self.errs[bad]  = self.nan

        self.finite = np.logical_and(np.isfinite(self.vals), np.isfinite(self.errs))
