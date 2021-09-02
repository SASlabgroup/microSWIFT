def GPSwaves(u, v, z, fs): 
    """
    GPSwaves takes a 

    Parameters
    -----
    u : 'x' direction velocity from GPS sensor
    v : 'y' direction velocity from GPS sensor
    z : Vertical elevation values from 
    fs : frequency


    Returns
    ------
    Hs : Significant Wave height, meters
    Tp : Peak Wave Period, seconds
    Dp : Peak Wave Direction, degrees from north
    E : Energy Spectrum, units are m^2/Hz
    f : frequency bins, Hz
    a1 : first spectral moment 
    b1 : 
    a2 : 
    b2 : 
    
    Filtering Technique: 


    """

    # Packages
    import numpy as np
    # import scipy.signal as signal
    import numpy.fft as fft
    from logging import getLogger

    # Set up module level logger
    logger = getLogger('microSWIFT.'+__name__) 

    # Define demean function
    def demean(x):
        x_demean = x - np.mean(x)
        return x_demean

    # ------------------- Convert Inputs to Numpy Arrays ------
    u = np.squeeze(u)
    v = np.squeeze(v)
    z = np.squeeze(z)

    # ---------------------- Tunable Parameters --------------
    # Standard deviations for despiking
    Nstd = 10

    # Time constant [s] for high-pass filter
    RC = 3.5

    # ----------------------- Fixed Parameters ---------------
    wsecs = 256 # window length in seconds
    merge = 3   # Frequency bands to merge
    maxf = 0.5  # Frequency cutoff for telemetry, Hz

    # ---------- Variable input data, priority for GPS velocity -----------
    # if no vertical, assign a dummy but tthen void a1 and a2 results later
    if not z.any(): 
        z = np.zeros(u.shape)
        zdummy = 1
    else:
        zdummy = 0


    # ----------------- Quality Control and Despiking --------
    # Find Spike values
    # badu = np.abs(signal.detrend(u)) >= Nstd * np.std(u)
    # badv = np.abs(signal.detrend(v)) >= Nstd * np.std(v)
    # badz = np.abs(signal.detrend(z)) >= Nstd * np.std(z)
    badu = np.abs(demean(u)) >= Nstd * np.std(u)
    badv = np.abs(demean(v)) >= Nstd * np.std(v)
    badz = np.abs(demean(z)) >= Nstd * np.std(z)
    # Replace Spike values with average of non-spiked series
    u[badu] = np.mean( u[~badu] )
    v[badv] = np.mean( v[~badv] )
    z[badz] = np.mean( z[~badz] )

    # ----------------- Begin Processing ----------------------
    num_points = u.shape[0] # number of points
    if ( (num_points >= fs*wsecs ) and (fs >= 1 ) and ( np.sum(badu) < 100 ) and (np.sum(badv) < 100) ):
        logger.info('Data is Sufficient for Processing - Processing Start')
    else:
        logger.info('Data is NOT Sufficient for Processing - Program Exit')
        Hs = 999
        Tp = 999
        Dp = 999
        E = 999 * np.ones(42)
        f = 999 * np.ones(42)
        a1 = 999 * np.ones(42)
        b1 = 999 * np.ones(42)
        a2 = 999 * np.ones(42)
        b2 = 999 * np.ones(42)
        check = 999 * np.ones(42)
        # Return values and exit
        return Hs, Tp, Dp, E, f, a1, b1, a2, b2, check

    # --------------- Detrend and High Pass Filter -------------
    # u = signal.detrend(u)
    # v = signal.detrend(v)
    # z = signal.detrend(z)
    u = demean(u)
    v = demean(v)
    z = demean(z)

    # Define alpha for filter
    alpha = RC / (RC + 1/fs)

    # Filter each signal
    ufiltered = u.copy()
    vfiltered = v.copy()
    zfiltered = z.copy()
    for i in np.arange(1, len(u)):
        ufiltered[i] = alpha * ufiltered[i-1] + alpha * ( u[i] - u[i-1] )
        vfiltered[i] = alpha * vfiltered[i-1] + alpha * ( v[i] - v[i-1] )
        zfiltered[i] = alpha * zfiltered[i-1] + alpha * ( z[i] - z[i-1] )

    # Redefine the values as the filtered values
    u = ufiltered.copy()
    v = vfiltered.copy()
    z = zfiltered.copy()

    # ---------------- Break Data into Windows ------------------
    # Windows have 75% Overlap 
    win = int(np.round(fs * wsecs))  # Window length in points
    if (np.mod(win, 2) != 0):
        win = int(win - 1) # make the window an even number
    windows = int(np.floor( 4*(num_points/win - 1 ) + 1)) # number of windows, 4 is from 75% overlap
    dof = 2 * windows * merge   # Degrees of Freedom
    # Create matrix where each column is a window
    uwindow = np.zeros((win,windows))
    vwindow = np.zeros((win,windows))
    zwindow = np.zeros((win,windows))
    for n in np.arange(windows):
        ind_low = int((n)*(0.25*win))
        ind_high = int((n)*(0.25*win)+win)
        uwindow[:,n] = u[ind_low : ind_high]
        vwindow[:,n] = v[ind_low : ind_high]
        zwindow[:,n] = z[ind_low : ind_high]

    # Detrend Individual Windows (full series is already detrended)
    for n in np.arange(windows):
        # uwindow[:,n] = signal.detrend(uwindow[:,n])
        # vwindow[:,n] = signal.detrend(vwindow[:,n])
        # zwindow[:,n] = signal.detrend(zwindow[:,n])
        uwindow[:,n] = demean(uwindow[:,n])
        vwindow[:,n] = demean(vwindow[:,n])
        zwindow[:,n] = demean(zwindow[:,n])

    # Taper and Resceale Data to Preserve Variance
    taper = np.repeat(np.reshape(np.sin(np.arange(1,win+1) * np.pi/(win+1)), (win, 1)), windows, axis=1)
    # taper each window
    uwindowtaper = uwindow * taper
    vwindowtaper = vwindow * taper
    zwindowtaper = zwindow * taper
    # Compute Correction Factor (Compare old to new)
    factu = np.sqrt( np.var(uwindow, axis=0, ddof=1) / np.var(uwindowtaper, axis=0, ddof=1) )
    factv = np.sqrt( np.var(vwindow, axis=0, ddof=1) / np.var(vwindowtaper, axis=0, ddof=1) )
    factz = np.sqrt( np.var(zwindow, axis=0, ddof=1) / np.var(zwindowtaper, axis=0, ddof=1) )
    # Correct for the change in variance (multiply each window by its varince factor)
    uwindowready = np.repeat(np.reshape(factu, (1, factu.shape[0])), win, axis=0) * uwindowtaper
    vwindowready = np.repeat(np.reshape(factv, (1, factv.shape[0])), win, axis=0) * vwindowtaper
    zwindowready = np.repeat(np.reshape(factz, (1, factz.shape[0])), win, axis=0) * zwindowtaper
    
    # ---------------- FFT ------------------
    # Calculate Fourer Coefficients
    #**** Note: this FFT funcion is slightly different than the MATLAB version 
    # and results in deviations around the thousands decimal
    Uwindow_temp = fft.fft(uwindowready, axis=0)
    Vwindow_temp = fft.fft(vwindowready, axis=0)
    Zwindow_temp = fft.fft(zwindowready, axis=0)
   
    # Get only one-sided spectrum values
    Uwindow = np.delete(Uwindow_temp, np.arange((int(win/2) + 1), win), axis=0)
    Vwindow = np.delete(Vwindow_temp, np.arange((int(win/2) + 1), win), axis=0)
    Zwindow = np.delete(Zwindow_temp, np.arange((int(win/2) + 1), win), axis=0)

    # Throw out mean and add zero to the end
    Uwindow = np.delete(Uwindow, 0, axis=0)
    Vwindow = np.delete(Vwindow, 0, axis=0)
    Zwindow = np.delete(Zwindow, 0, axis=0)
    Uwindow[-1, :] = 0
    Vwindow[-1, :] = 0
    Zwindow[-1, :] = 0
   
    # Compute Power Spectrum (auto-spectra)
    # **** Similar values but slightly different since the fft is different
    UUwindow = np.real(Uwindow * np.conj(Uwindow))
    VVwindow = np.real(Vwindow * np.conj(Vwindow))
    ZZwindow = np.real(Zwindow * np.conj(Zwindow))

    # Compute Cross-Spectra
    # ** Again pretty close but not quite the same - differentiation around thousands place again
    UVwindow = (Uwindow * np.conj(Vwindow))
    UZwindow = (Uwindow * np.conj(Zwindow))
    VZwindow = (Vwindow * np.conj(Zwindow))
   
    # ----------- Merge Neighboring Frequency Bands -------- 
    UUwindowmerged = np.zeros((int(np.floor(win/(2*merge))), windows))
    VVwindowmerged = np.zeros((int(np.floor(win/(2*merge))), windows))
    ZZwindowmerged = np.zeros((int(np.floor(win/(2*merge))), windows))
    UVwindowmerged = np.zeros((int(np.floor(win/(2*merge))), windows), complex)
    UZwindowmerged = np.zeros((int(np.floor(win/(2*merge))), windows), complex)
    VZwindowmerged = np.zeros((int(np.floor(win/(2*merge))), windows), complex)
    
    # Compute average to merge
    # ** This results in zeros for all values - is that what we want? 
    for n in np.arange(merge, int(win/2), merge):
        ind_low = (n-merge)
        ind_high = n
        UUwindowmerged[int(n/merge)-1, :] = np.mean( UUwindow[ind_low:ind_high, :], axis=0 )
        VVwindowmerged[int(n/merge)-1, :] = np.mean( VVwindow[ind_low:ind_high, :], axis=0 )
        ZZwindowmerged[int(n/merge)-1, :] = np.mean( ZZwindow[ind_low:ind_high, :], axis=0 )
        UVwindowmerged[int(n/merge)-1, :] = np.mean( UVwindow[ind_low:ind_high, :], axis=0 )
        UZwindowmerged[int(n/merge)-1, :] = np.mean( UZwindow[ind_low:ind_high, :], axis=0 )
        VZwindowmerged[int(n/merge)-1, :] = np.mean( VZwindow[ind_low:ind_high, :], axis=0 )
    
    # Define Frequnecy range and bandwidth
    n = (win/2) / merge # number of frequnecy bands
    Nyquist = 0.5 * fs  # Highest spectral frequnecy
    bandwidth = Nyquist/n # Frequency (Hz) bandwidth
    # Find middle of each freq band
    #** ONLY for merging odd numbers of bands
    f = (1/wsecs) + (bandwidth/2) + (bandwidth * np.arange(n-1))

    # --------- Ensemble Average Windows together ----------------
    # take average of all windows at each frequency band, divide by n*samplerate to get power 
    # spectral density. Use factor of 2 since we are using one-sided spectrum
    UU = np.mean( UUwindowmerged / (win/2 * fs), axis=1)
    VV = np.mean( VVwindowmerged / (win/2 * fs), axis=1)
    ZZ = np.mean( ZZwindowmerged / (win/2 * fs), axis=1)
    UV = np.mean( UVwindowmerged / (win/2 * fs), axis=1)
    UZ = np.mean( UZwindowmerged / (win/2 * fs), axis=1)
    VZ = np.mean( VZwindowmerged / (win/2 * fs), axis=1)

    # Convert to displacement spectra (from velocity and heave)
    # Assume perfectly circular deepwater orbits - could be extended to finite depth by 
    # calling wavenumber.m - need to change this to wavenumber.py which I have written
    Exx = UU / ( (2 * np.pi * f ) ** 2 ) # Energy density, units are m^2/Hz
    Eyy = VV / ( (2 * np.pi * f ) ** 2 ) # Energy density, units are m^2/Hz
    Ezz = ZZ.copy() # Energy density, units are m^2/Hz

    # Use orbit shape as check on qualityt, expect <1 since SWIFT wobbles
    check = Ezz / (Eyy + Exx)

    # Quadspectrum and Cospectrum computations
    freq_rad = (2 * np.pi * f)
    # XZ's
    Qxz = np.imag(UZ) / freq_rad # Energy density, units are m^2/Hz, quadspectrum of vertical displacement and horizontal velocities
    Cxz = np.real(UZ) / freq_rad # Energy density, units are m^2/Hz, cospectrum of vertical displacement and horizontal velocities

    # YZ's
    Qyz = np.imag(VZ) / freq_rad # Energy density, units are m^2/Hz, quadspectrum of vertical displacement and horizontal velocities
    Cyz = np.real(VZ) / freq_rad # Energy density, units are m^2/Hz, cospectrum of vertical displacement and horizontal velocities

    # XY's
    Cxy = np.real(UV) / ( (2 * np.pi * f ) ** 2 )

    # -------- Wave Specral Moments ------------------- 
    # wave directions from Kuik et al, JPO, 1988 and Herbers et al, JTech, 2012
    # Note that this uses COSPECTRA OF Z AND U OR V, WHICH DIFFS FROM QUADSPECTRA OF Z AND X OR Y
    # note also that normalization is skewed by the bias of Exx + Eyy over Ezz
    # (non-unity check factor)
    a1 = Cxz / np.sqrt( (Exx + Eyy) * Ezz ) # would use Qxz for actual displacements
    b1 = Cyz / np.sqrt( (Exx + Eyy) * Ezz )
    a2 = (Exx - Eyy) / ( Exx + Eyy )
    b2 = 2 * Cxy / (Exx + Eyy)

    # ---------- Compute Wave Directions ---------------
    # note tha 0 deg is for waves headed towards positive x (EAST, right hand system)
    dir1 = np.arctan2(b1, a1) # [rad], 4 quadrant
    dir2 = np.arctan2(b2, a2) / 2 # [rad], only 2 quadrant
    # spread1 = np.sqrt( 2 * (1 - np.sqrt(np.abs((a1 ** 2) + (b2 ** 2))) ) ) # Getting a strange value - commenting out for now
    # spread2 = np.sqrt( np.abs( 0.5 - 0.5 * (a2 * np.cos(2 * dir2) + b2 * np.cos(2 * dir2) ) ) ) 

    # ----------- Screen for presence/absence of vertical data --------
    if zdummy == 1: 
        Ezz[:] = 0
        a1[:] = 9999
        b1[:] = 9999
        dir1[:] = 9999
        spread1[:] = 9999
    
    # ------ Compute Scalar Energy Spectra -------------
    E = Exx + Eyy

    # ------ Compute Wave Statistics -------------
    fwaves = np.logical_and(f > 0.05, f < 1)# Frequency cutoff for wave stats, 0.4 is specific to SWIFT hull
    # clean Scalar Energy spectra from frequencies above and below cutoff 
    E[np.logical_not(fwaves)] = 0

    # Compute Significant Wave Height
    Hs = 4 * np.sqrt( np.sum(E) * bandwidth)

    # Compute Energy Period 
    fe = np.sum( f[fwaves] * E[fwaves] ) / np.sum( E[fwaves])
    feindex = np.argmin( np.abs(f - fe))
    Ta = 1 / fe

    # Compute Peak Period
    fpindex = np.argmax(UU + VV) # can use velocity and it picks out more distinct peak
    Tp = 1/f[fpindex]
    if Tp > 20: # if peak is not found, use centroid
        Tp = Ta
        fpindex = feindex

    # --------- Spectral Directions ---------------
    dir = -180 / np.pi * dir1 # switch from rad to deg, and CCz to Cz (negate)
    dir = dir + 90 # rotate from eastward = 0 to northward  = 0 
    dir[ dir < 0 ] = dir[ dir < 0 ] + 360 
    westdirs = dir > 180
    eastdirs = dir < 180
    dir[ westdirs ] = dir[ westdirs ] - 180 # take reciprocal such wave direction is FROM, not TOWARDS
    dir[ eastdirs ] = dir[ eastdirs ] + 180 # take reciprocal such wave direction is FROM, not TOWARDS

    # Directional Spread
    # spread = 180 / np.pi * spread1

    # Compute Dominant Direction 
    Dp = dir[fpindex] 

    # Quality control
    if zdummy == 1:
        Dp = 999

    if Tp > 20: 
        Hs = 999
        Tp = 999
        Dp = 999

    # ----------- Clean High frequency results ------------
    ind_to_delete = np.squeeze(np.argwhere(f > maxf))
    E = np.delete(E, ind_to_delete)
    Ezz = np.delete(Ezz, ind_to_delete)
    dir = np.delete(dir, ind_to_delete)
    # spread = np.delete( spread, ind_to_delete)
    a1 = np.delete(a1, ind_to_delete)
    b1 = np.delete(b1, ind_to_delete)
    a2 = np.delete(a2, ind_to_delete)
    b2 = np.delete(b2, ind_to_delete)
    check = np.delete(check, ind_to_delete)
    f = np.delete(f, ind_to_delete)

    logger.info('Hs = {}, Tp ={}, Dp = {}, E {}, f = {}, a1 = {}, b1 = {}, a2 = {}, b2 = {}, check = {}'. format( Hs, Tp, Dp, E, f, a1, b1, a2, b2, check))

    # Return values
    return Hs, Tp, Dp, E, f, a1, b1, a2, b2, check
