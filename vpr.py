#! /usr/bin/env python3

# ./vpr.py

import argparse

import numpy as np

from pause import pause
from gplot import gplot

def plot_RV(file):
    gplot.mxtics().mytics()
    gplot.xlabel("'BJD - 2 450 000'")
    gplot.ylabel("'RV [m/s]'")
    gplot.key("title '%s' noenhance" % file)
    gplot('"%s" us ($1-2450000):"RV":(sprintf("%%s\\nn: %%d\\nBJD: %%.6f\\nRV: %%f +/- %%f", strcol("filename"),$0+1,$1,$2,$3)) with labels  hypertext point pt 0 t"", "" us ($1-2450000):"RV":"e_RV" w e pt 7 lc 7' % file)
    pause()

def plot_rvo(rv=None, e_rv=None, file=None):
    #gplot('"%s" matrix every 2::1 us (($1-1)/2+18):3 w p pt 7' % file)
    if file:
        mat = np.genfromtxt(file)
        bjd, RV, e_RV = mat[:3]
        rv, e_rv = mat[3::2], mat[4::2]

    ii = np.isfinite(e_rv)
    RV = np.mean(rv[ii]) 
    e_RV = np.std(rv[ii])/(ii.sum()-1)**0.5

    gplot.xlabel('"Order index"')
    gplot.ylabel('"RV [m/s]"')
    gplot(rv, e_rv, 'us 0:1:2 w e pt 7 t "%s", RV=%s, e_RV=%s, RV lc 3 t "RV = %.5f +/- %.5f m/s", RV+e_RV lc 3 dt 2 t "", RV-e_RV lc 3 dt 2 t ""' % (file, RV,e_RV,RV,e_RV))
    pause()

def arg2slice(arg):
    """Convert string argument to a slice."""
    # We want four cases for indexing: None, int, list of ints, slices.
    # Use [] as default, so 'in' can be used.
    if isinstance(arg, str):
        arg = eval('np.s_['+arg+']')
    return [arg] if isinstance(arg, int) else arg

def plot_cmp(vpr, vprcmp):
        gplot.mxtics().mytics()
        gplot.xlabel("'BJD - 2 450 000'")
        gplot.ylabel("'RV [m/s]'")
        gplot-(vprcmp.BJD, vprcmp.RV, vprcmp.e_RV, vprcmp.A.filename, ' us ($1-2450000):2:(sprintf("%%s\\nn: %%d\\nBJD: %%.6f\\nRV: %%f +/- %%f", stringcolumn(4),$0+1,$1,$2,$3)) with labels  hypertext point pt 0 t"", "" us ($1-2450000):2:3 w e pt 7 lc 1 t "%s [o=%s] rms=%.2f m/s" noenh' % (vprcmp.tag, vprcmp.oset, vprcmp.rms))
        gplot+(vpr.BJD, vpr.RV, vpr.e_RV, vpr.A.filename, ' us ($1-2450000):2:(sprintf("%%s\\nn: %%d\\nBJD: %%.6f\\nRV: %%f +/- %%f", stringcolumn(4),$0+1,$1,$2,$3)) with labels  hypertext point pt 0 t "", "" us ($1-2450000):2:3 w e pt 7 lc 7 t "%s [o=%s] rms=%.2f m/s" noenh' % (vpr.tag, vpr.oset, vpr.rms))
        pause('RV time serie')

class VPR():
    def __init__(self, tag, gp='', oset=None, ocen=None, sort='', cen=False):
        '''
        oset: slice,list
        '''
        self.tag = tag.replace('.rvo.dat', '')
        self.file = file = self.tag + '.rvo.dat'
        self.oset = oset
        print(self.tag)

        if gp:
           gplot.put(gp)

        try:
            self.Afull = np.genfromtxt(file, dtype=None, names=True, encoding=None).view(np.recarray)
        except:
            self.Afull = np.genfromtxt(file, dtype=None, names=True).view(np.recarray)

        if sort:
            self.Afull.sort(order=sort)
        colnames = self.Afull.dtype.names

        if oset is not None:
            self.orders = np.r_[oset]
            onames = tuple(f"rv{o}" for o in self.orders)
        else:
            onames = tuple(col for col in colnames if col.startswith('rv'))
            self.orders = np.array([int(o[2:]) for o in onames])

        # remove columns not in oset
        self.A = self.Afull[[col for col in colnames if not col.startswith(('e_rv', 'rv')) or col.endswith(onames)]]

        mat = np.genfromtxt(file, skip_header=1)
        self.full_rv, self.full_e_rv = mat.T[4:-1:2], mat.T[5::2]

        self.rv = np.array(self.A[list(onames)].tolist()).T
        self.e_rv = np.array(self.A[list("e_"+o for o in onames)].tolist()).T

        # recompute mean RV
        self.BJD = self.A.BJD
        self.RV = np.mean(self.rv, axis=0)
        self.e_RV = np.std(self.rv, axis=0) / (len(onames)-1)**0.5

        if cen:
            off = np.nanmedian(self.RV)
            print('Subtracting', off, 'm/s from all RVs.')
            self.RV -= off
            self.rv -= off

        self.info()

        if ocen:
            RVo = np.mean(self.rv-self.RV, axis=1)
            print('Subtracting mean order offsets from all RVs.')
            # This should not change the RV mean values.
            # The idea is to reduce RV uncertainty overestimation coming from large order offsets.
            # Offsets are hints for systematics in wavelength solutions (template or fts-iod)
            self.rv -= RVo[:,None]
            self.RV = np.mean(self.rv, axis=0)
            self.e_RV = np.std(self.rv, axis=0) / (len(onames)-1)**0.5
            self.info()

    def info(self):
        self.rms = np.std(self.RV)
        print('rms(RV) [m/s]:     ', self.rms)
        print('median(e_RV) [m/s]:', np.median(self.e_RV))

    def plot_RV(self):
        gplot.mxtics().mytics()
        gplot.xlabel("'BJD - 2 450 000'")
        gplot.ylabel("'RV [m/s]'")
        gplot.key("title '%s' noenhance" % (self.tag))
        gplot(self.BJD, self.RV, self.e_RV, self.A.filename, ' us ($1-2450000):2:(sprintf("%%s\\nn: %%d\\nBJD: %%.6f\\nRV: %%f +/- %%f", stringcolumn(4),$0+1,$1,$2,$3)) with labels  hypertext point pt 0 t"", "" us ($1-2450000):2:3 w e pt 7 lc 7 t "orders = %s"' % self.oset)
        pause('RV time serie')

    def plot_rv(self, o=None, n=1):
        A = self
        gplot.var(n=n, N=len(self.rv.T))
        gplot.key('title "%s" noenhance'%self.tag)
        gplot.bind('")" "n = n>=N? N : n+1; repl"')
        gplot.bind('"(" "n = n<=1? 1 : n-1; repl"')
        gplot.bind('"]" "n = n+10>N? N : n+10; repl"')
        gplot.bind('"[" "n = n-10<1? 1 : n-10; repl"')
        gplot.bind('"^" "n = 1; repl"')
        gplot.bind('"$" "n = N; repl"')
        gplot.xlabel("'order o'")
        gplot.ylabel("'RV_{n,o} -- RV_{n}  [m/s]'")
        gplot.mxtics().mytics()
        stat_o = np.percentile(A.rv-A.RV, [17,50,83], axis=1)
        med_e_rvo = np.median(A.e_rv, axis=1)

        gplot('for [n=1:N]', self.orders, (A.rv-A.RV).T, self.e_rv.T,
            'us ($1-0.25+0.5*n/N):(column(1+n)):(column(1+n+N)) w e pt 6 lc "light-grey" t "", ' +
            '"" us ($1-0.25+0.5*n/N):(column(1+n)):(column(1+n+N)) w e pt 6 lc 1 t "RV_{".n.",o} -- RV_{".n."}",',
            '"" us ($1-0.25+0.5*n/N):(column(1+n)):(sprintf("RV_{n=%d,o=%d} = %.2f +/- %.2f m/s", n,$1, column(1+n), column(1+n+N))) w labels hypertext enh point pt 0 lc 1 t "",',
            A.BJD, A.RV+400, A.e_RV, A.A.filename, ' us 1:2:(sprintf("%s\\nn: %d\\nBJD: %.6f\\nRV: %f +/- %f",strcol(4),$0+1,$1,$2,$3)) w labels hypertext point pt 0 axis x2y1 t "",' +
            '"" us 1:2:3 w e lc 7 pt 7 axis x2y1 t "RV_n",' +
            '"" us 1:2:3 every ::n-1::n-1 w e lc 1 pt 7 axis x2y1 t "RV_{".n."}",',             self.orders, stat_o, med_e_rvo, 'us 1:3:2:4 w e lc 3 pt 4 t "order stat",' +
            ' "" us 1:3:(sprintf("o = %d\\noffset median: %.2f m/s\\nspread: %.2f m/s\\nmedian error: %.2f m/s", $1, $3, ($4-$2)/2, $5)) w labels hypertext rotate left point pt 0 lc 3 t "",' +
            '"" us 1:4:(sprintf(" %.2f",($4-$2)/2)) w labels rotate left tc "blue" t ""')
        print("Use '()[]^$' in gnuplot window to go through epochs n.")
        pause('rv order dispersion')

def plot_res(folder, o=[1], n=[1]):
    '''
    Plot stacked residuals.

    Examples:
    vpr -res -oset [20] -nset [`seq -s, 1 50`]
    vpr -res -oset [`seq -s, 19 29`] -nset [17]
    '''
    gplot.var(No=len(o), o=1, obeg=1, oend=len(o))
    gplot.var(Nn=len(n), n=1, nbeg=1, nend=len(n))
    gplot.bind("'('  'o=obeg=oend = o>1?o-1:1;   nbeg=1; nend=Nn; set key tit \"(o=\".A[o].\")\"; repl'")
    gplot.bind("')'  'o=obeg=oend = o<No?o+1:No; nbeg=1; nend=Nn; set key tit \"(o=\".A[o].\")\"; repl'")
    gplot.bind("'['  'n=nbeg=nend = n>1?n-1:1;   obeg=1; oend=No; set key tit \"[n=\".Sp[n].\"]\"; repl'")
    gplot.bind("']'  'n=nbeg=nend = n<Nn?n+1:Nn; obeg=1; oend=No; set key tit \"[n=\".Sp[n].\"]\"; repl'")
    gplot.key_invert()
    gplot.term_qt_size('600,1300')
    gplot.xlabel("'pixel x'").ylabel("'residuals'")
    gplot.array(A=o, Sp=n)
    gplot.array(d3color=[0x1F77B4, 0xFF7F0E, 0x2CA02C, 0xD62728, 0x9467BD, 0x8C564B])
    print("type '(' and ')' to go through the orders o or '[' and ']' to go through epochs n")
    gplot(f'for [n=nbeg:nend] for [o=obeg:oend] sprintf("{folder}/%03d_%03d.dat", Sp[int(n)], A[int(o)]) us 1:($2+int(nbeg==nend?o:n)/3.) lc rgb d3color[1+ int(nbeg==nend?o:n)%5] pt 7 ps 0.5 t "".Sp[n]."-".A[o]')
    # colored y2ticlabel are not really possible :(
    # gplot+('A us (1700):(int(nbeg==nend?$1:0)/3.):2:(d3color[1+ int(nbeg==nend?$1:n)%5]) with labels tc rgb var')
    # gplot+('A us (NaN):(int(nbeg==nend?$1:0)/3.):yticlabel(2) t ""')
    pause('residuals stacked: o=%s' % o)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Analyse viper RVs', add_help=False, formatter_class=argparse.RawTextHelpFormatter)
    argopt = parser.add_argument   # function short cut
    argopt('tag', nargs='?', help='tag', default='tmp', type=str)
    argopt('-gp', help='gnuplot commands', default='', type=str)
    argopt('-cen', help='center RVs to zero median', action='store_true')
    argopt('-cmp', help='compare two time series (default: cmp=None or, if cmposet is passed, cmp=tag)', type=str)
    argopt('-cmpocen', help='center orders (subtract order offset) of comparison', action='store_true')
    argopt('-cmposet', help='index for order subset of comparison', type=arg2slice)
    argopt('-nset', help='index for spectrum subset (e.g. 1:10, ::5)', default=None, type=arg2slice)
    argopt('-ocen', help='center orders (subtract order offset)', action='store_true')
    argopt('-oset', help='index for order subset (e.g. 1:10, ::5)', default=None, type=arg2slice)
    argopt('-sort', nargs='?', help='sort by column name', const='BJD')
    argopt('-res', help='Plot residuals stacked (folder name)', nargs='?',  const='res', type=str)

    args = vars(parser.parse_args())

    resopt = args.pop('res')
    if resopt is not None:
        plot_res(resopt, o=args['oset'], n=args['nset'])
        exit()

    args.pop('nset')
    tagcmp = args.pop('cmp')
    cmposet = args.pop('cmposet')
    cmpocen = args.pop('cmpocen')

    vpr = VPR(**args)

    if tagcmp or cmposet or cmpocen:
        if tagcmp: args['tag'] = tagcmp
        if cmposet: args['oset'] = cmposet
        if cmpocen: args['ocen'] = cmpocen
        vprcmp = VPR(**args)
        plot_cmp(vpr, vprcmp)
    elif args['oset'] is None and not args['cen']:
        plot_RV(vpr.file)
    else:
        vpr.plot_RV()
    vpr.plot_rv(n=1)

