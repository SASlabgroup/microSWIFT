def UVZAwaves(u, v, z, a, fs): 
    """
    UVZAwaves.py computes a scalar spectrum from an IMU heave estimate 'z' (made outside of this code)
    and estimates directional moments using GPS velocities 'u' and 'v' and raw IMU vertical acceleration 'a'.
    NOTE: UVZAwaves is similar to the SWIFT codes version of GPSandIMUwaves, but differs in that the 
    scalar spectrum is derived from the IMU-based heave estimate, rather than 'u' and 'v'.

    Parameters
    -----
    u  : 'x' direction velocity from GPS sensor [m/s] (+E)
    v  : 'y' direction velocity from GPS sensor [m/s] (+N)
    z  : IMU-based heave estimate (+up) [m]
    a  : raw vertical acceleration values from IMU [m/s^2] (+up)
    fs : sampling frequency [Hz]

    Returns
    ------
    Hs : Significant Wave height [m]
    Tp : Peak Wave Period [s]
    Dp : Peak Wave Direction [degrees from N]
    E  : energy density [m^2/Hz]
    f  : frequency bins [Hz]
    a1 : first normalized spectral moment [-]
    b1 : second " " 
    a2 : " "
    b2 : " "
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
    a = np.squeeze(a)

    # ---------------------- Tunable Parameters --------------
    # Standard deviations for despiking
    Nstd = 10

    # Time constant [s] for high-pass filter
    RC = 3.5

    # ----------------------- Fixed Parameters ---------------
    # wsecs = 256 # window length in seconds
    wsecs = 4 # window length in seconds #TODO: MODIFIED FOR TESTING delete
    # merge = 3   # Frequency bands to merge
    merge = 1   # Frequency bands to merge #TODO: MODIFIED FOR TESTING delete

    maxf = 0.5  # Frequency cutoff for telemetry, Hz

    # ---------- Variable input data, priority for GPS velocity -----------
    # if no vertical, assign a dummy but then void a1 and a2 results later
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
    bada = np.abs(demean(a)) >= Nstd * np.std(a)
    # Replace Spike values with average of non-spiked series
    u[badu] = np.mean( u[~badu] )
    v[badv] = np.mean( v[~badv] )
    z[badz] = np.mean( z[~badz] )
    a[bada] = np.mean( a[~bada] )

    # ----------------- Begin Processing ----------------------
    
    # num_points = u.shape[0] # number of points
    num_points = len(u)

    if ( (num_points >= fs*wsecs ) and (fs >= 1 ) and ( np.sum(badu) < 100 ) and (np.sum(badv) < 100) ):
        logger.info('Data is Sufficient for Processing - Processing Start')
        logger.info(f'num points: {num_points}')
        logger.info(f'fs*wsecs: {fs*wsecs}')
        logger.info(f'sum(badu): {np.sum(badu)}')
        logger.info(f'sum(badv): {np.sum(badv)}')
    else:
        logger.info('Data is NOT Sufficient for Processing - Program Exit')
        logger.info(f'num points: {num_points}')
        logger.info(f'fs*wsecs: {fs*wsecs}')
        logger.info(f'sum(badu): {np.sum(badu)}')
        logger.info(f'sum(badv): {np.sum(badv)}')
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
    u = demean(u)
    v = demean(v)
    z = demean(z)
    a = demean(a)
    
    #TODO: update filter: does NOT work for 48hz

    # New High-pass filter - from https://tomroelandts.com/articles/how-to-create-a-simple-high-pass-filter
    ## https://fiiir.com/

    # Configuration.
    fS = fs  # Sampling rate.
    fH = 0.05  # Cutoff frequency.
    N = 207 # Filter length, must be odd.

    # Compute sinc filter.
    h = np.sinc(2 * fH / fS * (np.arange(N) - (N - 1) / 2))

    # Apply window.
    h *= np.hamming(N)

    # Normalize to get unity gain.
    h /= np.sum(h)

    # Create a high-pass filter from the low-pass filter through spectral inversion.
    h = -h
    h[(N - 1) // 2] += 1

    # Filter Each signal
    u = np.convolve(u, h)
    v = np.convolve(v, h)
    z = np.convolve(z, h)
    a = np.convolve(a, h)

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
    awindow = np.zeros((win,windows))
    for n in np.arange(windows):
        ind_low = int((n)*(0.25*win))
        ind_high = int((n)*(0.25*win)+win)
        uwindow[:,n] = u[ind_low : ind_high]
        vwindow[:,n] = v[ind_low : ind_high]
        zwindow[:,n] = z[ind_low : ind_high]
        awindow[:,n] = a[ind_low : ind_high]

    # Detrend Individual Windows (full series is already detrended)
    for n in np.arange(windows):
        # uwindow[:,n] = signal.detrend(uwindow[:,n])
        # vwindow[:,n] = signal.detrend(vwindow[:,n])
        # zwindow[:,n] = signal.detrend(zwindow[:,n])
        uwindow[:,n] = demean(uwindow[:,n])
        vwindow[:,n] = demean(vwindow[:,n])
        zwindow[:,n] = demean(zwindow[:,n])
        awindow[:,n] = demean(awindow[:,n])

    # Taper and Resceale Data to Preserve Variance
    taper = np.repeat(np.reshape(np.sin(np.arange(1,win+1) * np.pi/(win+1)), (win, 1)), windows, axis=1)
    # taper each window
    uwindowtaper = uwindow * taper
    vwindowtaper = vwindow * taper
    zwindowtaper = zwindow * taper
    awindowtaper = awindow * taper

    # Compute Correction Factor (Compare old to new)
    factu = np.sqrt( np.var(uwindow, axis=0, ddof=1) / np.var(uwindowtaper, axis=0, ddof=1) )
    factv = np.sqrt( np.var(vwindow, axis=0, ddof=1) / np.var(vwindowtaper, axis=0, ddof=1) )
    factz = np.sqrt( np.var(zwindow, axis=0, ddof=1) / np.var(zwindowtaper, axis=0, ddof=1) )
    facta = np.sqrt( np.var(awindow, axis=0, ddof=1) / np.var(awindowtaper, axis=0, ddof=1) )

    # Correct for the change in variance (multiply each window by its varince factor)
    uwindowready = np.repeat(np.reshape(factu, (1, factu.shape[0])), win, axis=0) * uwindowtaper
    vwindowready = np.repeat(np.reshape(factv, (1, factv.shape[0])), win, axis=0) * vwindowtaper
    zwindowready = np.repeat(np.reshape(factz, (1, factz.shape[0])), win, axis=0) * zwindowtaper
    awindowready = np.repeat(np.reshape(factz, (1, facta.shape[0])), win, axis=0) * awindowtaper

    logger.info('FFT')
    # ---------------- FFT ------------------
    # Calculate Fourer Coefficients
    #**** Note: this FFT funcion is slightly different than the MATLAB version 
    # and results in deviations around the thousands decimal
    Uwindow_temp = fft.fft(uwindowready, axis=0)
    Vwindow_temp = fft.fft(vwindowready, axis=0)
    Zwindow_temp = fft.fft(zwindowready, axis=0)
    Awindow_temp = fft.fft(awindowready, axis=0)

    # Get only one-sided spectrum values
    Uwindow = np.delete(Uwindow_temp, np.arange((int(win/2) + 1), win), axis=0)
    Vwindow = np.delete(Vwindow_temp, np.arange((int(win/2) + 1), win), axis=0)
    Zwindow = np.delete(Zwindow_temp, np.arange((int(win/2) + 1), win), axis=0)
    Awindow = np.delete(Awindow_temp, np.arange((int(win/2) + 1), win), axis=0)

    # Throw out mean and add zero to the end
    Uwindow = np.delete(Uwindow, 0, axis=0)
    Vwindow = np.delete(Vwindow, 0, axis=0)
    Zwindow = np.delete(Zwindow, 0, axis=0)
    Awindow = np.delete(Awindow, 0, axis=0)
    # Uwindow[-1, :] = 0
    # Vwindow[-1, :] = 0
    # Zwindow[-1, :] = 0
    # Awindow[-1, :] = 0
    

    # Compute auto-spectra
    UUwindow = np.real(Uwindow * np.conj(Uwindow))
    VVwindow = np.real(Vwindow * np.conj(Vwindow))
    ZZwindow = np.real(Zwindow * np.conj(Zwindow))
    AAwindow = np.real(Awindow * np.conj(Awindow))

    # Compute cross-spectra
    UVwindow = (Uwindow * np.conj(Vwindow))
    UAwindow = (Uwindow * np.conj(Awindow))
    VAwindow = (Vwindow * np.conj(Awindow))
   
    logger.info('merging freq bands')
    # ----------- Merge Neighboring Frequency Bands -------- 
    UUwindowmerged = np.zeros((int(np.floor(win/(2*merge))), windows))
    VVwindowmerged = np.zeros((int(np.floor(win/(2*merge))), windows))
    ZZwindowmerged = np.zeros((int(np.floor(win/(2*merge))), windows))
    AAwindowmerged = np.zeros((int(np.floor(win/(2*merge))), windows))
    UVwindowmerged = np.zeros((int(np.floor(win/(2*merge))), windows), complex)
    UAwindowmerged = np.zeros((int(np.floor(win/(2*merge))), windows), complex)
    VAwindowmerged = np.zeros((int(np.floor(win/(2*merge))), windows), complex)
    
    # Compute average to merge
    # ** This results in zeros for all values - is that what we want? 
    for n in np.arange(merge, int(win/2)+1, merge): #TODO: added +1 to cover entire window... validate! This prevents divide by zero erros
        ind_low = (n-merge)
        ind_high = n
        UUwindowmerged[int(n/merge)-1, :] = np.mean( UUwindow[ind_low:ind_high, :], axis=0 )
        VVwindowmerged[int(n/merge)-1, :] = np.mean( VVwindow[ind_low:ind_high, :], axis=0 )
        ZZwindowmerged[int(n/merge)-1, :] = np.mean( ZZwindow[ind_low:ind_high, :], axis=0 )
        AAwindowmerged[int(n/merge)-1, :] = np.mean( AAwindow[ind_low:ind_high, :], axis=0 )
        UVwindowmerged[int(n/merge)-1, :] = np.mean( UVwindow[ind_low:ind_high, :], axis=0 )
        UAwindowmerged[int(n/merge)-1, :] = np.mean( UAwindow[ind_low:ind_high, :], axis=0 )
        VAwindowmerged[int(n/merge)-1, :] = np.mean( VAwindow[ind_low:ind_high, :], axis=0 )

    logger.info('merged')

    # Define Frequnecy range and bandwidth
    n = (win/2) / merge # number of frequnecy bands
    Nyquist = 0.5 * fs  # Highest spectral frequnecy
    bandwidth = Nyquist/n # Frequency (Hz) bandwidth

    # Find middle of each freq band
    #** ONLY for merging odd numbers of bands
    # f = (1/wsecs) + (bandwidth/2) + (bandwidth * np.arange(n-1))
    f = (1/wsecs) + (bandwidth/2) + (bandwidth * np.arange(n))
    #TODO: fix freq length
    # print(f[-1])

    logger.info('ensemble averaged')
    # --------- Ensemble Average Windows together ----------------
    # take average of all windows at each frequency band, divide by n*samplerate to get power 
    # spectral density. Use factor of 2 since we are using one-sided spectrum
    UU = np.mean( UUwindowmerged / (win/2 * fs), axis=1)
    VV = np.mean( VVwindowmerged / (win/2 * fs), axis=1)
    ZZ = np.mean( ZZwindowmerged / (win/2 * fs), axis=1)
    AA = np.mean( AAwindowmerged / (win/2 * fs), axis=1)
    UV = np.mean( UVwindowmerged / (win/2 * fs), axis=1)
    UA = np.mean( UAwindowmerged / (win/2 * fs), axis=1)
    VA = np.mean( VAwindowmerged / (win/2 * fs), axis=1)

    # ------------------ Spectral results -----------------------
    E  = ZZ.copy()                         # scalar spectral density [m^2/Hz]
    a1 = np.real(UA) / np.sqrt((UU+VV)*AA) # first normalized directional moment [-] (see Thomson et al. 2018)
    b1 = np.real(VA) / np.sqrt((UU+VV)*AA) # second normalized directional moment [-]
    a2 = (UU-VV)/(UU+VV)                   # [-]
    b2 = 2*np.real(UV)/(UU+VV)             # [-]
    #TODO: fix check
    check = 999 * np.ones(42)
    logger.info('spectral results')
    #-- From GPSandIMUwaves:

    # %% convert to displacement spectra (from velocity and acceleration)
    # % assumes perfectly circular deepwater orbits
    # % could be extended to finite depth by calling wavenumber.m 
    # Exx = ( UU )  ./ ( (2*pi*f).^2 );  %[m^2/Hz]
    # Eyy = ( VV )  ./ ( (2*pi*f).^2 );  %[m^2/Hz]
    # Ezz = ( AZAZ )  ./ ( (2*pi*f).^4 ) .* (9.8^2);  %[m^2/Hz]

    # Qxz = imag(UAZ) ./ ( (2*pi*f).^3 ) .* (9.8); %[m^2/Hz], quadspectrum of vertical acc and horizontal velocities
    # Cxz = real(UAZ) ./ ( (2*pi*f).^3 ) .* (9.8); %[m^2/Hz], cospectrum of vertical acc and horizontal velocities

    # Qyz = imag(VAZ) ./ ( (2*pi*f).^3 ) .* (9.8); %[m^2/Hz], quadspectrum of vertical acc and horizontal velocities
    # Cyz = real(VAZ) ./ ( (2*pi*f).^3 ) .* (9.8); %[m^2/Hz], cospectrum of vertical acc and horizontal velocities

    # Cxy = real(UV) ./ ( (2*pi*f).^2 );  %[m^2/Hz]
    #--
    #TODO: keep below?
    # Exx = UU / ( (2 * np.pi * f ) ** 2 )
    # Eyy = VV / ( (2 * np.pi * f ) ** 2 ) 
    # Ezz = AA / ( (2 * np.pi * f ) ** 4 )
    # Qxz = np.imag(UA) / ( (2 * np.pi * f) ** 3 ) * (9.8)  # [m^2/Hz], quadspectrum of vertical acc and horizontal velocities
    # Cxz = np.real(UA) / ( (2 * np.pi * f) ** 3 ) * (9.8)  # [m^2/Hz], cospectrum of vertical acc and horizontal velocities
    # Qyz = np.imag(VA) / ( (2 * np.pi * f) ** 3 ) * (9.8); # [m^2/Hz], quadspectrum of vertical acc and horizontal velocities
    # Cyz = np.real(VA) / ( (2 * np.pi * f) ** 3 ) * (9.8); # [m^2/Hz], cospectrum of vertical acc and horizontal velocities
    # Cxy = np.real(UV) / ( (2 * np.pi * f) ** 2 ) 

    # %% wave spectral moments 
    # % wave directions from Kuik et al, JPO, 1988 and Herbers et al, JTech, 2012
    # % NOTE THAT THIS USES COSPECTRA OF AZ AND U OR V, WHICH DIFFS FROM QUADSPECTRA OF Z AND X OR Y
    # a1 = Cxz / np.sqrt( (Exx+Eyy) * Ezz ) #[], would use Qxz for actual displacements
    # b1 = Cyz / np.sqrt( (Exx+Eyy) * Ezz )  #[], would use Qyz for actual displacements
    # a2 = (Exx - Eyy) / (Exx + Eyy)
    # b2 = 2 * Cxy / (Exx + Eyy)
    #TODO:

#################
    # # Convert to displacement spectra (from velocity and heave)
    # # Assume perfectly circular deepwater orbits - could be extended to finite depth by 
    # # calling wavenumber.m - need to change this to wavenumber.py which I have written
    # Exx = UU / ( (2 * np.pi * f ) ** 2 ) # Energy density, units are m^2/Hz
    # Eyy = VV / ( (2 * np.pi * f ) ** 2 ) # Energy density, units are m^2/Hz
    # Ezz = ZZ.copy() # Energy density, units are m^2/Hz

    # # Use orbit shape as check on qualityt, expect <1 since SWIFT wobbles
    # check = Ezz / (Eyy + Exx)

    # # Quadspectrum and Cospectrum computations
    # freq_rad = (2 * np.pi * f)
    # # XZ's
    # Qxz = np.imag(UZ) / freq_rad # Energy density, units are m^2/Hz, quadspectrum of vertical displacement and horizontal velocities
    # Cxz = np.real(UZ) / freq_rad # Energy density, units are m^2/Hz, cospectrum of vertical displacement and horizontal velocities

    # # YZ's
    # Qyz = np.imag(VZ) / freq_rad # Energy density, units are m^2/Hz, quadspectrum of vertical displacement and horizontal velocities
    # Cyz = np.real(VZ) / freq_rad # Energy density, units are m^2/Hz, cospectrum of vertical displacement and horizontal velocities

    # # XY's
    # Cxy = np.real(UV) / ( (2 * np.pi * f ) ** 2 )

    # # -------- Wave Specral Moments ------------------- 
    # # wave directions from Kuik et al, JPO, 1988 and Herbers et al, JTech, 2012
    # # Note that this uses COSPECTRA OF Z AND U OR V, WHICH DIFFS FROM QUADSPECTRA OF Z AND X OR Y
    # # note also that normalization is skewed by the bias of Exx + Eyy over Ezz
    # # (non-unity check factor)
    # a1 = Cxz / np.sqrt( (Exx + Eyy) * Ezz ) # would use Qxz for actual displacements
    # b1 = Cyz / np.sqrt( (Exx + Eyy) * Ezz )
    # a2 = (Exx - Eyy) / ( Exx + Eyy )
    # b2 = 2 * Cxy / (Exx + Eyy)

#################
    # %% convert to displacement spectra (from velocity and acceleration)
    # % assumes perfectly circular deepwater orbits
    # % could be extended to finite depth by calling wavenumber.m 
    # Exx = ( UU )  ./ ( (2*pi*f).^2 );  %[m^2/Hz]
    # Eyy = ( VV )  ./ ( (2*pi*f).^2 );  %[m^2/Hz]
    # Ezz = ( AZAZ )  ./ ( (2*pi*f).^4 ) .* (9.8^2);  %[m^2/Hz]

    # Qxz = imag(UAZ) ./ ( (2*pi*f).^3 ) .* (9.8); %[m^2/Hz], quadspectrum of vertical acc and horizontal velocities
    # Cxz = real(UAZ) ./ ( (2*pi*f).^3 ) .* (9.8); %[m^2/Hz], cospectrum of vertical acc and horizontal velocities

    # Qyz = imag(VAZ) ./ ( (2*pi*f).^3 ) .* (9.8); %[m^2/Hz], quadspectrum of vertical acc and horizontal velocities
    # Cyz = real(VAZ) ./ ( (2*pi*f).^3 ) .* (9.8); %[m^2/Hz], cospectrum of vertical acc and horizontal velocities

    # Cxy = real(UV) ./ ( (2*pi*f).^2 );  %[m^2/Hz]


    # %% wave spectral moments 
    # % wave directions from Kuik et al, JPO, 1988 and Herbers et al, JTech, 2012
    # % NOTE THAT THIS USES COSPECTRA OF AZ AND U OR V, WHICH DIFFS FROM QUADSPECTRA OF Z AND X OR Y
    # a1 = Cxz ./ sqrt( (Exx+Eyy) .* Ezz );  %[], would use Qxz for actual displacements
    # b1 = Cyz ./ sqrt( (Exx+Eyy) .* Ezz );  %[], would use Qyz for actual displacements
    # a2 = (Exx - Eyy) ./ (Exx + Eyy);
    # b2 = 2 .* Cxy ./ ( Exx + Eyy );

#################

    # ---------- Compute Wave Directions ---------------
    # note tha 0 deg is for waves headed towards positive x (EAST, right hand system)
    dir1 = np.arctan2(b1, a1) # [rad], 4 quadrant
    dir2 = np.arctan2(b2, a2) / 2 # [rad], only 2 quadrant
    # spread1 = np.sqrt( 2 * (1 - np.sqrt(np.abs((a1 ** 2) + (b2 ** 2))) ) ) # Getting a strange value - commenting out for now
    # spread2 = np.sqrt( np.abs( 0.5 - 0.5 * (a2 * np.cos(2 * dir2) + b2 * np.cos(2 * dir2) ) ) ) 

    # ----------- Screen for presence/absence of vertical data --------
    #TODO: fix this:

    # if zdummy == 1: 
    #     Ezz[:] = 0
    #     a1[:] = 9999
    #     b1[:] = 9999
    #     dir1[:] = 9999
    #     spread1[:] = 9999
    
    # # ------ Compute Scalar Energy Spectra -------------
    # E = Exx + Eyy

    # ------ Compute Wave Statistics -------------
    #TODO: adjust f limits?
    fwaves = np.logical_and(f > 0.05, f < 1)# Frequency cutoff for wave stats, 0.4 is specific to SWIFT hull
    # clean Scalar Energy spectra from frequencies above and below cutoff 
    #TODO: a1, b1?
    # E[np.logical_not(fwaves)] = 0 #TODO: J. Davis Jul 21 2022 modified to not set to zero, but to use fwaves for computing Hs,fe, etc.

    print(f'{len(E)}')
    print(f'{len(f)}')
    print(f'{len(fwaves)}')
    logger.info(f'{len(E)}')
    logger.info(f'{len(f)}')
    logger.info(f'{len(fwaves)}')
    logger.info(f'{fwaves}')
    logger.info(f'E: {E}')
    logger.info(f'E[fwaves]: {E[fwaves]}')
    logger.info(f'f: {f}')


    # Compute Significant Wave Height
    Hs = 4 * np.sqrt( np.sum(E[fwaves]) * bandwidth)

    # Compute Energy Period 
    fe = np.sum( f[fwaves] * E[fwaves] ) / np.sum( E[fwaves])
    feindex = np.argmin( np.abs(f - fe))
    Ta = 1 / fe

    # Compute Peak Period
    #TODO: use E?
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
    # Ezz = np.delete(Ezz, ind_to_delete)
    dir = np.delete(dir, ind_to_delete)
    # spread = np.delete( spread, ind_to_delete)
    a1 = np.delete(a1, ind_to_delete)
    b1 = np.delete(b1, ind_to_delete)
    a2 = np.delete(a2, ind_to_delete)
    b2 = np.delete(b2, ind_to_delete)
    #TODO: check = np.delete(check, ind_to_delete)
    f = np.delete(f, ind_to_delete)

    logger.info(f'len(E): {len(E)}; len(f): {len(f)}; len(a1): {len(a1)}; len(b1): {len(b1)}; len(a2): {len(a2)}; len(b2): {len(b2)}')
    
    
    # Return values
    return Hs, Tp, Dp, E, f, a1, b1, a2, b2, check
