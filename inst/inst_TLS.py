import numpy as np
from astropy.io import fits
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u

from .readmultispec import readmultispec
from .airtovac import airtovac

from .FTS_resample import resample, FTSfits

# see https://github.com/mzechmeister/serval/blob/master/src/inst_FIES.py

def Spectrum(filename='data/TLS/other/BETA_GEM.fits', o=None):
    hdu = fits.open(filename, ignore_blank=True)[0]
    hdr = hdu.header
    f = hdu.data
    gg = readmultispec(filename, reform=True, quiet=True)
    w = gg['wavelen']
    w = airtovac(w)
    if o is not None:
         w, f = w[o], f[o]

    b = 1 * np.isnan(f) # bad pixel map
    b[f>1.5] |= 2 # large flux
    b[(5300<w) & (w<5343)] |= 4  # only for HARPS s1d template (this order misses)
    dateobs = hdr['DATE-OBS']
    exptime = hdr['EXP_TIME']
    ra =  hdr['RA']
    de = hdr['DEC']
    #ra = 
    #de = '+22:42:39.071811263'
    #sys.path.insert(1, sys.path[0]+os.sep+'BarCor')            # bary now in src/BarCor
    #import sys
    #sys.path.insert(1, '/home/raid0/zechmeister/python/chamarthisireesha/VIPER/BarCor')            # bary now in src/BarCor
    #import bary
    #bjd, berv = bary.bary(dateobs, '20:00:43.7130382888', '+22:42:39.071811263', 'TLS', epoch=2000, exptime=exptime, pma=0, pmd=0)
    #print(bjd, berv)
    #from pause import pause; pause(bjd, berv)
    tls = EarthLocation.from_geodetic(lat=50.980111*u.deg, lon=11.711167*u.deg, height=342*u.m)
    sc = SkyCoord(ra=ra*u.hour, dec=de*u.deg)
    midtime = Time(dateobs, format='isot', scale='utc') + exptime * u.s
    berv = sc.radial_velocity_correction(obstime=midtime, location=tls)  
    berv = berv.to(u.km/u.s).value  
    bjd = midtime.tdb.jd
    print(bjd, berv)
    return w, f, b, bjd, berv

def Tpl(tplname, o=None):
    if tplname.endswith('.model'):
        # echelle template
        from inst.inst_TLS import Spectrum
        w, f, b = Spectrum(tplname)
        if o is not None:
            w, f = w[o], f[o]
    if tplname.endswith('_s1d_A.fits'):
        hdu = fits.open(tplname)[0]
        f = hdu.data
        h = hdu.header
        w = h['CRVAL1'] +  h['CDELT1'] * (1. + np.arange(f.size) - h['CRPIX1'])
        w = airtovac(w)
    else:
        # long 1d template
        hdu = fits.open(tplname)
        w = hdu[1].data.field('Arg')
        f = hdu[1].data.field('Fun')

    return w, f


def FTS(ftsname='lib/TLS/FTS/TLS_I2_FTS.fits', dv=100):

    return resample(*FTSfits(ftsname), dv=dv)



