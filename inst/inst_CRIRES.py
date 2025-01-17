import numpy as np
import os.path
import sys
from datetime import datetime
from astropy.io import fits
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
from astropy.constants import c

from .readmultispec import readmultispec
from .airtovac import airtovac

from .FTS_resample import resample, FTSfits

import matplotlib.pyplot as plt


# see https://github.com/mzechmeister/serval/blob/master/src/inst_FIES.py

path = sys.path[0] + '/lib/CRIRES/'

location = crires = EarthLocation.from_geodetic(lat=-24.6268*u.deg,
                                                lon=-70.4045*u.deg,
                                                height=2648*u.m)

oset = '1:19'

ip_guess = {'s': 1.5}

atmall = {'H2O': 'lib/CRIRES/atmos/stdAtmos_crires_H2O.fits', 'CH4': 'lib/CRIRES/atmos/stdAtmos_crires_CH4.fits', 'N2O': 'lib/CRIRES/atmos/stdAtmos_crires_N2O.fits', 'CO2': 'lib/CRIRES/atmos/stdAtmos_crires_CO2.fits', 'CO': 'lib/CRIRES/atmos/stdAtmos_crires_CO.fits'}

def Spectrum(filename='', order=None, targ=None):
    hdu = fits.open(filename, ignore_blank=True)
    hdr = hdu[0].header

    dateobs = hdr['DATE-OBS']
    ra = hdr.get('RA', np.nan)
    de = hdr.get('DEC', np.nan)

    hdr = hdu[1].header
    exptime = hdr.get('EXPTIME', 0)

    targdrs = SkyCoord(ra=ra*u.deg, dec=de*u.deg)
    if not targ: targ = targdrs
    midtime = Time(dateobs, format='isot', scale='utc') + exptime * u.s
    berv = targ.radial_velocity_correction(obstime=midtime, location=crires)
    berv = berv.to(u.km/u.s).value
    bjd = midtime.tdb

    order_drs, detector = divmod(order-1, 3)
    order_drs = 5 - order_drs		# order number (CRIRES+ definition)
    detector += 1			# detector number (1,2,3)

    err = hdu[detector].data.field(3*order_drs+1)
    spec = hdu[detector].data.field(3*order_drs)
    pixel = np.arange(spec.size)

    setting = (hdu[0]).header['ESO INS WLEN ID']
    
    if str(setting) in ('K2148', 'K2166', 'K2192'):
	# using an own wavelength solution instead of the one created by DRS
        file_wls = np.genfromtxt(path+'wavesolution_own/wave_solution_'+str(setting)+'.dat', dtype=None, names=True).view(np.recarray)
        coeff_wls = [file_wls.b1[order-1], file_wls.b2[order-1], file_wls.b3[order-1]]
        wave = np.poly1d(coeff_wls[::-1])(pixel)

        # using blaze function
        blaze = np.load(path+str(setting)+'_blaze_own.npy')[order]
        spec /= blaze

    else:
        wave = (hdu[detector].data.field(3*order_drs+2))*10

    flag_pixel = 1 * np.isnan(spec)		# bad pixel map

    return pixel, wave, spec, err, flag_pixel, bjd, berv


def Tpl(tplname, order=None, targ=None):
    '''Tpl should return barycentric corrected wavelengths'''

    if tplname.endswith('_tpl.fits'):
        # tpl created with viper
        hdu = fits.open(tplname, ignore_blank=True)
        hdr = hdu[0].header

        order_drs, detector = divmod(order-1, 3)
        order_drs = 5 - order_drs		# order number (CRIRES+ definition)
        detector += 1			# detector number (1,2,3)

        err = hdu[detector].data.field(3*order_drs+1)
        spec = hdu[detector].data.field(3*order_drs)
        pixel = np.arange(spec.size)
        wave = (hdu[detector].data.field(3*order_drs+2))
    else:
        pixel, wave, spec, err, flag_pixel, bjd, berv = Spectrum(tplname, order=order, targ=targ)
        wave *= 1 + (berv*u.km/u.s/c).to_value('')

    return wave, spec


def FTS(ftsname='lib/CRIRES/FTS/CRp_SGC2_FTStmpl-HR0p007-WN3000-5000_Kband.dat', dv=100):

    return resample(*FTSfits(ftsname), dv=dv)


def write_fits(wtpl_all, tpl_all, e_all, list_files, file_out):

    file_in = list_files[0]

    # copy header from first fits file
    hdu = fits.open(file_in, ignore_blank=True)
    hdr = hdu[0].header

    if len(list_files) > 1:
        # delete parts that vary for all observations
        del hdr['DATE-OBS']
        del hdr['UTC']
        del hdr['LST']
        del hdr['ARCFILE']
        del hdr['ESO INS SENS*']
        del hdr['ESO INS TEMP*']
        del hdr['ESO INS1*']
        del hdr['ESO DET*']
        del hdr['ESO OBS*']
        del hdr['ESO TPL*']
        del hdr['ESO TEL*']
        del hdr['ESO OCS MTRLGY*']
        del hdr['ESO ADA*']
        del hdr['ESO AOS*']
        del hdr['ESO SEQ*']
        del hdr['ESO PRO DATANCOM']
        del hdr['ESO PRO REC1 PARAM*']
        del hdr['ESO PRO REC1 RAW*']

        for hdri in hdu:
            hdri.header['EXPTIME'] = 0

    # file creation date
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
    hdr['DATE'] = dt_string

    # save raw file informations in FITS header
    hdr.set('ESO PRO REC2 ID', 'viper_create_tpl', 'Pipeline recipe', after='ESO PRO REC1 PIPE ID')

    for i in range(0, len(list_files), 1):
        pathi, filei = os.path.split(list_files[len(list_files)-i-1])
        hdr.set('ESO PRO REC2 RAW'+str(len(list_files)-i)+' NAME', filei, 'File name', after='ESO PRO REC2 ID')

    hdr.set('ESO PRO DATANCOM', len(list_files), 'Number of combined frames', after='ESO PRO REC2 RAW'+str(len(list_files))+' NAME')

    # write the template data to the file
    for o in range(1, 19, 1):
        # data spread over 3 detectors, each having 6 orders
        order_drs, detector = divmod(o-1, 3)
        order_drs = 5 - order_drs		# order number (CRIRES+ definition)
        detector += 1			# detector number (1,2,3)

        data = hdu[detector].data
        cols = hdu[detector].columns

        if o in list(tpl_all.keys()):
            data[str(cols.names[3*order_drs])] = tpl_all[o]		# data
            data[str(cols.names[3*order_drs+1])] = e_all[o]		# errors
            data[str(cols.names[3*order_drs+2])] = wtpl_all[o]		# wavelength
        else:
            # writing zeros for non processed orders
            data[str(cols.names[3*order_drs])] = np.ones(2048)
            data[str(cols.names[3*order_drs+1])] = np.nan * np.ones(2048)
            data[str(cols.names[3*order_drs+2])] = (data.field(3*order_drs+2))*10	 # [Angstrom]

    hdu.writeto(file_out+'_tpl.fits', overwrite=True)
    hdu.close()
