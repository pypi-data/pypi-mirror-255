#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import interpolate
import scipy.io
import radyn_xtools.globals as cnst
#import globals as cnst
from astropy.io import fits
from astropy import units as u
import glob as glob
from astropy.table import Table, Column, MaskedColumn
from astropy.io import ascii
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import cdflib
import matplotlib.font_manager as font_manager
import matplotlib as mpl


# all call examples are within a Jupyter Notebook.

def prep_pmesh(z):
    # z is an irregular grid and must be at cell boundaries for pcolormesh (therefore make an array that is ndep + 1 dimensions.)
    ndep = len(z)
    midz = (z[1:len(z)] + z[0:len(z)-1])/2.
    newz = np.insert(midz, 0, z[0] + (z[0]-midz[0]))
    ndep2=len(newz)
    z_bdry = np.append(newz, z[ndep-1] + (z[ndep-1]-midz[ndep-2]))
    return z_bdry

def findind(array,value):
    ''' closest_index = findind(array, value_of_interest);  finds index of array where array is closest to the given value.'''
    idx = (np.abs(array-value)).argmin()
    return idx


class modelclass:
    pass


def rcdf(fname, H_2 = False,dt_int=-99):
    ''' This automatically finds the largest time in the cdf even if it is 
not the last index.  
    dt_int = -99 reads in all entries in CDF
    dt_int = 0.2 reads in the _closest_ index at every 0.2s, which could have 
        a repeat among indices 

    call:   atmos_F11 = radyn_xtools.rcdf('radyn_out.cdf')
    '''
    run = cdflib.CDF(fname)
    timeS = np.array(run.varget("time"))
    tinds = np.linspace(0, len(timeS)-1, len(timeS), dtype='int')
    dtS = timeS[1:,] - timeS[0:-1]
    bad = np.all([dtS < 0], axis=0)
    nbad = np.count_nonzero(bad)
    if nbad > 0:
        tindS = tinds[1:,]
        badind = tindS[bad]
        tinds = tinds[0:badind[0]]
        timeS = timeS[tinds]

    if dt_int > 0:
        tsearch = np.arange(0.0, np.max(timeS), dt_int)
        tinds2 = []
        for i in range(len(tsearch)):
            found_ind = findind(timeS, tsearch[i])
            tinds2.append(found_ind)
    else:
        tinds2 = np.linspace(0, len(timeS)-1, len(timeS), dtype='int')

 #   radynvar = scipy.io.readsav(fname)  #+ 'radyn_sed.'+model_id+'.sav
    if dt_int < 0:
        print('Reading in all times from the CDF file ... ',fname)
    if dt_int > 0:
        print('Reading in select times from the CDF file ... ',fname)

    atmos = modelclass()
    test = run.varget("z1").transpose()
    atmos.z1t = test[:, tinds2]  # have to transpose all this stuff   atmos.z1t[ndep, ntime]

    test = run.varget("time")
    atmos.timet = test[tinds2]

    test = run.varget("vz1").transpose()
    atmos.vz1t = test[:,tinds2]

    test = run.varget("d1").transpose()
    atmos.d1t = test[:,tinds2]
    atmos.zmu = run.varget("zmu")
 #   try:
 #       test = run.varget("dz").transpose()
 #   except:
    ndep = len(atmos.z1t[:,0])
    atmos.dzt = np.zeros_like(atmos.z1t)
    atmos.dzt[1:ndep,:] = atmos.z1t[0:ndep-1,:]-atmos.z1t[1:ndep,:]

    test = run.varget("pg1").transpose()
    atmos.pg1t = test[:,tinds2]

    test= run.varget("ne1").transpose()
    atmos.ne1t = test[:,tinds2]

    test = run.varget("tau").transpose()
    atmos.taut = test[:,tinds2]

    test = run.varget("tg1").transpose()
    atmos.tg1t = test[:,tinds2]

    test =  run.varget("n1").transpose()
    atmos.n1t = test[:,:,:,tinds2]

    test = run.varget("totn").transpose()
    atmos.totnt = test[:,:,tinds2] #  run.varget("totn").transpose()
    
    try:
        test = run.varget("nstar").transpose() 
        atmos.nstart = test[:,:,:,tinds2]

    except:
        print('Could not read in LTE pops nstart.')

    try:
        test = run.varget("c").transpose()
        atmos.c1t =test[:,:,:,:,tinds2]  # collisional rates.

        test = run.varget("f20").transpose() 
        atmos.f20t = test[:,tinds2]
    except:
        print('Could not read in c1t or f20t')
    try:

        test = run.varget("rij").transpose() 
        atmos.rijt = test[:,:,tinds2] # radynvar.RIJT.transpose()
        test = run.varget("rji").transpose()
        atmos.rjit =test[:,:,tinds2] # radynvar.RJIT.transpose()
    except:
        print('Could not read in rjit, rijt.')

    test = run.varget("cmass1").transpose()
    atmos.cmass1t = test[:,tinds2]

    test = run.varget("bheat1").transpose()
    atmos.bheat1t = test[:,tinds2]
    atmos.cont = run.varget("cont")
    atmos.irad = run.varget("irad")
    atmos.jrad = run.varget("jrad")
    atmos.alamb = run.varget("alamb")
    atmos.ielrad = run.varget("ielrad")
    atmos.atomid = run.varget("atomid")
    atmos.label = run.varget("label")
    atmos.ion = run.varget("ion").transpose()
    atmos.g = run.varget("g").transpose()
    atmos.grph = run.varget("grph")

    if H_2:
        atmos.H_2 = (atmos.d1t / atmos.grph - atmos.totnt[:,0,:])*0.5 
        print('Read in H_2 population densities.')
    return atmos

def make_dataframe(timet, x1, y1):
    '''
   call:  df_F11 = radyn_xtools.make_dataframe(atmos_F11.timet, atmos_F11.z1t/1e5, np.log10(atmos_F11.tg1t))
    '''
    nt = len(timet)
    nx = len(x1[:,0])
    t1d = []
    typ1d = []
    x1d  = x1.transpose().flatten()
    y1d  = y1.transpose().flatten()
    for i in range(nt):
        for j in range(nx):
            t1d.append(timet[i])
            typ1d.append('flare')
    for i in range(nt):
        for j in range(nx):
            t1d.append(timet[i])
            typ1d.append('pre')
            x1d = np.append(x1d, x1[j,0])
            y1d = np.append(y1d, y1[j,0])

    d = {'time': t1d, 'x1': x1d, 'y1':y1d, 'typ':typ1d}
    datframe = pd.DataFrame(data=d)
    return datframe


def make_movie(df,xlim=(-100,500), ylim=(3000,2e4), save_movie=True,  ylabel='y-axis', xlabel = 'x-axis', movie_name="AtmosMovie.html"):
    '''
   call:  radyn_xtools.make_movie(df_F11, ylim=(3,7.5), save_movie=False, xlabel='Distance along loop from photosphere (km)', ylabel='Temperature (K)')
    '''
    fig = px.line(df, x="x1", y="y1",animation_frame="time",\
        color_discrete_sequence=px.colors.qualitative.Set1, \
                  range_x=xlim,range_y=ylim,markers=True,color="typ")
    fig.update_layout(yaxis=dict(title=ylabel), xaxis=dict(title=xlabel))
    fig.update_layout(width=800,height=600)
    fig["layout"].pop("updatemenus") # optional, drop animation buttons
    if save_movie:
        fig.write_html(movie_name)
        print('Saved ',movie_name)
    else:
        fig.show()





def load_atmos(model_id = 'mF13-85-3.dMe', model_dir='./', H_2 = False, load_by_id=True, file_type='FITS'):
    # this was load_atmos in radx_dm
    if file_type == 'IDL':  # probably won't work anymore
        if load_by_id:
            fname = glob.glob(model_dir+'radyn_out*'+model_id+'*.idl')
            if len(fname) > 1:
                print('Found more than 1 file with that ID!')
                return None
            radynvar = scipy.io.readsav(fname[0])  #+ 'radyn_sed.'+model_id+'.sav
            print('Read in ... ',fname[0])
        else:
            radynvar = scipy.io.readsav(model_id)
            print('Read in ... ',model_id)
    if file_type == 'FITS':
        if load_by_id:
            fname = glob.glob(model_dir+'radyn_out*'+model_id+'*.fits')
            if len(fname) > 1:
                print('Found more than 1 file with that ID in load_atmos!')
                print(fname)
                return None
            radynvar = fits.getdata(fname[0])  #+ 'radyn_sed.'+model_id+'.sav
            print('Read in ... ',fname[0])
        else:
            radynvar = fits.getdata(model_id)
            print('Read in ... ',model_id)

    atmos = modelclass()
    atmos.z1t = radynvar.z1t.squeeze().transpose()  # have to transpose all this stuff because scipy.io.readsav transposes.   atmos.z1t[ndep, ntime]
    atmos.timet = radynvar.timet.squeeze()
    atmos.vz1t = radynvar.vz1t.squeeze().transpose()
    atmos.d1t = radynvar.d1t.squeeze().transpose()
    atmos.zmu = radynvar.zmu.squeeze()
    atmos.dzt = radynvar.dzt.squeeze().transpose()
    atmos.pg1t = radynvar.pg1t.squeeze().transpose()
    atmos.ne1t = radynvar.ne1t.squeeze().transpose()
    atmos.taut = radynvar.taut.squeeze().transpose()
    atmos.z1t = radynvar.z1t.squeeze().transpose()
    atmos.tg1t = radynvar.tg1t.squeeze().transpose()
    atmos.n1t = radynvar.n1t.squeeze().transpose()
    atmos.trl1t = radynvar.trl1t.squeeze().transpose()
    atmos.totnt = radynvar.totnt.squeeze().transpose()
    atmos.hnt_ct = radynvar.hnt_ct.squeeze().transpose()
    atmos.coolt = radynvar.coolt.squeeze().transpose()
    atmos.coolt1t = radynvar.coolt1t.squeeze().transpose()
    atmos.cournt = radynvar.cournt.squeeze()
    atmos.dtnt = radynvar.dtnt.squeeze()
    atmos.fmjt = radynvar.fmjt.squeeze().transpose()
    atmos.gmlt = radynvar.gmlt.squeeze().transpose()
    atmos.en1t = radynvar.en1t.squeeze().transpose()
    atmos.wmu = radynvar.wmu.squeeze()
    try:
        atmos.nstart = radynvar.nstart.squeeze().transpose()
        atmos.c1t = radynvar.ct.squeeze().transpose()  # collisional rates.
        atmos.f20t = radynvar.f20t.squeeze().transpose()
    except:
        print('Could not read in nstart, c1t.')
    try:
        atmos.rijt = radynvar.rijt.transpose()
        atmos.rjit = radynvar.rjit.transpose()
    except:
        print('Could not read in rjit, rijt.')
    atmos.cmass1t = radynvar.cmass1t.squeeze().transpose() 
    atmos.bheat1t = radynvar.bheat1t.squeeze().transpose()
    atmos.tdheat1t = radynvar.tdheat1t.squeeze().transpose()
    atmos.heat1t = radynvar.heat1t.squeeze().transpose()
    atmos.xheat1t = radynvar.xheat1t.squeeze().transpose()
    atmos.cont = radynvar.cont.squeeze()
    atmos.irad = radynvar.irad.squeeze()
    atmos.jrad = radynvar.jrad.squeeze()
    atmos.alamb = radynvar.alamb.squeeze()
    atmos.ielrad = radynvar.ielrad.squeeze()
    atmos.atomid = radynvar.atomid.squeeze()
    atmos.label = radynvar.label.squeeze()
    atmos.ion = radynvar.ion.squeeze().transpose()
    atmos.g = radynvar.g.squeeze().transpose()
    atmos.ev = radynvar.ev.squeeze().transpose()
    atmos.eion1t = radynvar.eion1t.squeeze().transpose()
    atmos.grph = radynvar.grph.squeeze()
    atmos.model_id = radynvar.model_id.squeeze()
    if H_2:
        atmos.H_2 = (atmos.d1t / atmos.grph - atmos.totnt[:,0,:])*0.5 # if H_2 populations were included in LTE chemical equilibrium in radyn (m dwarf only)
        print('Read in H_2 population densities.')
    #isel = np.all([irad == 2],axis=0)
    #jsel = np.all([jrad == 2],axis=0)
    return atmos



def vactoair(wave_vac):
    sigma2 = (1e4/(wave_vac) )**2   
    fact = 1.0 +  5.792105E-2/(238.0185E0 - sigma2) + 1.67917E-3/( 57.362E0 - sigma2)
    wave_air = wave_vac/fact
    return wave_air

def airtovac(wave_air):
    # taken from IDL vactoair and airtovac.pro.
    sigma2 = (1e4/(wave_air) )**2
    fact = 1E0 +  5.792105E-2/(238.0185E0 - sigma2) + 1.67917E-3/( 57.362E0 - sigma2)
    # see also Neckel & Labs 1984
    wave_vac = wave_air*fact
    return wave_vac


def ci_cont(model_dir='./', model_id='mF13-85-3.dMe',dlogm=True, silent=False):
    ''' Loads in contribution function (ci) to the emergent mu=0.95 intensity at select 
        continuum wavelengths.  dlogm returns erg/s/cm2/dlog10colmass/sr/Ang 
        (otherwise returns in erg/s/cm2/cm/sr/Ang)
        Notes:
           One should use the height scale returned in the dictionary instead of atmos.z1t.
           Returned wavelength in vaccuum (Angstroms)
           Column mass returned in log10 units.
           ciprime is the cumulative contribution function;  ciprime[ndep-1] = 1.0 (bottom of atmosphere)
    '''
    ccont = fits.getdata(model_grid+'ccontribf/ccontribf'+'*'+model_id+'*fits')
    
    timesci = ccont['citime']
    if not dlogm:
        ci = np.transpose(ccont['ciz_t']) 
        zci = np.transpose(ccont['zci_t'])
        if not silent:
            print('Returning contribution function in units of per unit height (cm)')
    else:
        ci = np.transpose(ccont['cim_t']) 
        zci = np.transpose(ccont['mci_t'])
        if not silent:
            print('Returning contribution function in units of per unit log10 col mass/(g/cm2)')

    tauci = np.transpose(ccont['tau_ci_t'])
    ciprime = np.transpose(ccont['cip_t'])
    wlci = ccont['wl_ci']
    if not silent:
        print('returning a dictionary of contribution function (nw, ndep, ntime)')

    if not dlogm:
        ccontrib_dict = {'time':timesci, 'wl':wlci, 'z':zci, 'ci':ci, 'tauci':tauci, 'ciprime':ciprime}
    else:
        ccontrib_dict = {'time':timesci, 'wl':wlci, 'log10m_col':zci, 'ci':ci, 'tauci':tauci, 'ciprime':ciprime}

    if not silent:
        print(ccontrib_dict.keys())
        print('Shapes:')
        print('ci:  ',contrib_dict['ci'].shape)
        print('time:  ',contrib_dict['time'].shape)
        print('wl:  ',contrib_dict['wl'].shape)
        try:
            print('z:  ',contrib_dict['z'].shape)
        except:    
            print('log10m_col:  ',contrib_dict['log10m_col'].shape)
        print('ciprime:  ',contrib_dict['ciprime'].shape)
        print('tauci:  ',contrib_dict['tauci'].shape)

    return ccontrib_dict


def ci_image1(atmos,line='Hg',model_dir='./', model_id='mF13-85-3.dMe',mu=0.95,time=0.,xlim=[-20,20],ylim=[-100,1500],ci_log=False,vmax=0.5,vmin=0.5*1e-5,user_cmap='Greys_r', oplot_Ilam = True, Ilam_color='white', oplot_vel=True,vel_color='gray',oplot_legend2=True,oplot_legend1=True,savefig=False,plot_filename='contrib_fn_plot',user_figsize=(6,6),user_fontsize=14,ci_prime=[-99,-99],ci_zlim=[-200,-200],ciprime_color='white',oplot_tau1=False, tau_color='k',tau_2d = False,tlim0=0,tlim1=30,src_2d=False,source_ha=False,oplot_t0=True, oplot_annotate=False,flip_wl=True, oplot_nel=False, labcolor='white',nelim0=0, nelim1=5e15, ZFIND=100.0,leg_loc=(0.02,0.02)):
    '''  default values for the call are indicated here: 
    your_python_dictionary = adx.ci_image1(atmos,time=18,vmin=-2,vmax=1,xlim=[6560,6566],\
        user_cmap=rnbw_map,savefig=True,user_figsize=(6,6),ci_log=True,user_fontsize=14,\
                                  vel_color='#BBBBBB',oplot_tau1=1)  '''

    if line == 'Hg' or line == 'Ha' or line == 'Hb' or line == 'CaIIK' or line == 'CaIIH' or line == 'Pab' or line == 'Paa' or line == 'HeI10830' or line == 'CaII8542':
        contrib_file = glob.glob(model_dir+'lcontribf/lcontribf-'+line+'*'+model_id+'*fits')
    else:
        print('Line contribution function for ', line, ' not available.')
        print('Available lines in full grid download:  Hg (Balmer gamma), Hb (Balmer beta), Ha (Balmer alpha), Paa (Paschen alpha), Pab (Paschen beta), CaIIK, CaIIH, CaII8542, HeI10830')
        return None
    cfline = fits.getdata(contrib_file[0],1)
    
    col_rnbw = color_rainbow14()
    if mu < 0.80:
        print('Only mu=0.95 is available. Returning.')
        return None
    muind = findind(atmos.zmu, mu)
    user_mu = atmos.zmu[muind]
    if line == 'Ha' and mu==0.95: 
        plt_label = r'H$\alpha$'
    if line == 'Hg' and mu ==0.95:
        plt_label=r'H$\gamma$'
    if line == 'Hb' and mu ==0.95:
        plt_label=r'H$\beta$'
    if (line == 'Paa' or line == 'PaA') and mu == 0.95:
        plt_label = r'Pa $\alpha$'
    if (line == 'Pab' or line == 'PaB') and mu == 0.95:
        plt_label = r'Pa $\beta$'
    if (line == 'Ca II K' or line == 'CaIIK') and mu ==0.95:
        plt_label = 'Ca II K'
    if (line == 'Ca II H' or line == 'CaIIH') and mu ==0.95:
        plt_label = 'Ca II H'
    if (line == 'Ca II 8542' or line == 'CaII8542') and mu ==0.95:
        plt_label = 'Ca II 8542'
    if (line == 'He I 10830' or line == 'HeI10830') and mu ==0.95:
        plt_label = 'He I 10830'
    lam_rest = cfline['lam0_vac'].squeeze()

    print('Lambda Rest (Vac) is ',lam_rest, ' Ang')
        
    if lam_rest > 3000.:
        lam_rest = vactoair(lam_rest)
        
    print('Plotting contribution function (erg/s/cm3/sr/Ang) for ',plt_label,' at mu= {:0.3f}'.format(user_mu), 'at time = {:0.3f} '.format(time), 'sec for model',str(contrib_file),'.')
    # to do:  put in other lines that adam has stored.
    #print(cfha.dtype)   this prints the available arrays
    contribline = cfline['contribf'].squeeze()
 #   contribline = cfline['contribf']
    contriblinewl = cfline['lint95_lam'].squeeze()
    c_I_line = contribline.transpose()  # at mu = 0.95
    c_I_line_wl = contriblinewl.transpose()  # should be AIR wavelengths here.


   # contribline_ha = cfline_ha['contribf']
   # contriblinewl_ha = cfline_ha['lam']
    
    tind = findind(atmos.timet, time)
    if ylim[0] < 0:
        ylim[0] = np.min(atmos.z1t[:,tind]/1e5)
    zprep = prep_pmesh(atmos.z1t[:,tind]/1e5)
    zprep2 = atmos.z1t[:,tind]/1e5
    wlprep2 = c_I_line_wl[:,tind]
    wlprep = prep_pmesh(c_I_line_wl[:,tind])
    wl2d, z2d = np.meshgrid(wlprep,zprep)
    vz2d, z2dx = np.meshgrid((lam_rest-wlprep)/lam_rest*2.998e5,zprep)
    vzprep2 = (lam_rest-wlprep2)/lam_rest*2.998e5
    user_time = atmos.timet[tind]
    plt.rc('font',size=user_fontsize)
    f, (ax1,ax4) = plt.subplots(ncols=2,figsize=user_figsize, sharey='row',
                               gridspec_kw={'width_ratios': [4,1]})
#fig.set_tight_layout({'rect': [0, 0, 1, 0.95], 'pad': 0, 'h_pad': 0})

    if user_cmap != 'Greys_r' and user_cmap != 'Greys' and user_cmap != 'bone' and user_cmap != 'bone_r':
        xmap = color_map(umap=user_cmap)
    else:
        xmap = user_cmap
    if ci_log == 0:
        ax1.pcolormesh(wl2d, z2d, c_I_line[:,:,tind],vmax=vmax,vmin=vmin,cmap = xmap,rasterized=True)
    else:
        c_I_line[:,:,tind] = np.where(c_I_line[:,:,tind] <= 0, 1e-30, c_I_line[:,:,tind]) # replace bad values so don't get warning
        ci0 = np.log10(c_I_line[:,:,tind])
        if tau_2d == True:
            tauall = cfline['tau'].squeeze()
            tauline = tauall.transpose()
         #   print(tauline.shape, wl2d.shape, z2d.shape)
            if flip_wl:
                ax1.pcolormesh(wl2d, z2d,np.log10(np.flip(tauline[:,:,tind]/mu,axis=1)),vmax=vmax,vmin=vmin,cmap = xmap,rasterized=True)
            else:
                ax1.pcolormesh(wl2d, z2d,np.log10(tauline[:,:,tind]),vmax=vmax,vmin=vmin,cmap = xmap,rasterized=True)
        elif src_2d == True:
            srcall = cfline['src'].squeeze()
            srcline = srcall.transpose()
            print(srcline.shape, wl2d.shape, z2d.shape)
            plvec = np.vectorize(planckfni)
            b1d = np.zeros((len(atmos.tg1t[:,tind]),1))
            b1d[:,0] = plvec(np.median(wlprep), atmos.tg1t[:,tind])
            if flip_wl:
                src_flipped = np.flip(srcline[:,:,tind],axis=1)
            else:
                src_flipped = srcline[:,:,tind]
            dnu2dlam = np.zeros_like(src_flipped) + cnst.CCANG / np.median(wl2d)**2
            src_flipped_dlam = src_flipped * dnu2dlam
            b2d = np.broadcast_to(b1d, src_flipped.shape)
            print(b1d)
            ax1.pcolormesh(wl2d, z2d,( src_flipped_dlam/ b2d),vmax=vmax,vmin=vmin,cmap =xmap,rasterized=True)
            src_ratio =  src_flipped_dlam/ b2d
        else:
            ax1.pcolormesh(wl2d, z2d,ci0,vmax=vmax,vmin=vmin,cmap = xmap,rasterized=True)
    ax1.set_ylim(ylim)
    xlim = xlim + lam_rest
    ax1.set_xlim(xlim)
    from matplotlib.ticker import MultipleLocator
    ax1.yaxis.set_minor_locator(MultipleLocator(25.0))
    ax1.xaxis.set_minor_locator(MultipleLocator(2))

    ax1.set_xlabel(r'Wavelength ($\rm{\AA}$)')
    ax1.set_ylabel('Distance (km) from Photosphere')

    if oplot_tau1:
        tauall = cfline['tau'].squeeze()
        tauline = tauall.transpose()
        shptau = tauline.shape
        tau2deq1 = np.zeros((shptau[1]))
        for tt in range(shptau[1]):
            tau2deq1[tt] = np.interp(1.0, tauline[:,tt,tind] / mu, atmos.z1t[:,tind]/1e5)
        if flip_wl:
            ax1.plot(c_I_line_wl[:,tind], np.flip(tau2deq1),color=tau_color,ls='dashed',label=r'$\tau=1$',lw=2,zorder=22)  # need to flip tau because contribf is flipped in contribfunc.pro
        else:
            ax1.plot(c_I_line_wl[:,tind], tau2deq1,color=tau_color,ls='dashed',label=r'$\tau=1$',lw=2,zorder=22)
        ax1.legend(loc='upper left',frameon=False,ncol=2,labelcolor=labcolor)

    if oplot_Ilam:
        contriblineint = cfline['lint95_t'].squeeze()
        emerg_intline = contriblineint.transpose()
        ax1.plot(c_I_line_wl[:,tind], emerg_intline[:,tind] * ylim[1] / np.max(emerg_intline[:,tind]) * 0.75 ,color=Ilam_color,label=r'I$_{\lambda}$',lw=2.0,marker='+',ms=6.)
        if oplot_legend1:
            ax1.legend(loc='upper left',frameon=False,labelcolor=labcolor)
        print('The maximum emergent I_lam (erg/s/cm2/sr/Ang) for this profile is {:0.3e}'.format(np.max(emerg_intline[:,tind])))

    if ci_prime[0] > 0 and ci_prime[1] > 0:
        nlam = len(c_I_line_wl[:,tind])
        ciinds = np.all([atmos.z1t[:,tind]/1e5 > ci_zlim[0], atmos.tg1t[:,tind] < 1e5],axis=0)
        nzci = np.count_nonzero(ciinds)
        CIPRIME = np.zeros((nlam,nzci) )
        CIPRIMEZ0 = np.zeros(nlam)
        for ww in range(nlam):
            dzt_sel = atmos.dzt[ciinds,tind]
            c_I_line_sel = c_I_line[ciinds, :, tind]
            z1t_sel = atmos.z1t[ciinds,tind]
            ZPRIME, CIPRIME[ww,:] = np.abs(akcdf_dz(dzt_sel, c_I_line_sel[:,ww],norm=True))
            CIPRIMEZ0[ww] = np.interp(ci_prime[0], CIPRIME[ww,:], z1t_sel)
        ax1.plot(c_I_line_wl[:,tind], CIPRIMEZ0/1e5, ls=(0,(5,1)),color=ciprime_color,lw=0.7)
        
        nlam = len(c_I_line_wl[:,tind])
        ciinds = np.all([atmos.z1t[:,tind]/1e5 > ci_zlim[1], atmos.tg1t[:,tind] < 1e5],axis=0)
        nzci = np.count_nonzero(ciinds)
        CIPRIME = np.zeros((nlam,nzci) )
        CIPRIMEZ1 = np.zeros(nlam)
        for ww in range(nlam):
            dzt_sel = atmos.dzt[ciinds,tind]
            c_I_line_sel = c_I_line[ciinds, :, tind]
            z1t_sel = atmos.z1t[ciinds,tind]
            ZPRIME, CIPRIME[ww,:] = np.abs(akcdf_dz(dzt_sel, c_I_line_sel[:,ww],norm=True))
            CIPRIMEZ1[ww] = np.interp(ci_prime[1], CIPRIME[ww,:], z1t_sel)
        ax1.plot(c_I_line_wl[:,tind], CIPRIMEZ1/1e5, ls=(0,(5,1)),color=ciprime_color,lw=0.7)
   # ax1.ticklabel_format(useMathText=True)
 #   ax1.formatter.use_mathtext=True
    global X 
    X= vzprep2
    global Y
    Y=zprep2
    global ZVALS

    if tau_2d == True:
        if flip_wl:
            ZVALS = np.flip(tauline[:,:,tind] / mu,axis=1)
        else:
            ZVALS = tauline[:,:,tind] / mu
    elif src_2d == True:
        ZVALS = src_ratio
    else:
        ZVALS = c_I_line[:,:,tind]
        
    ax2 = ax1.twiny()
    if oplot_vel:
        ax2.plot(atmos.vz1t[:,tind]/1e5 * mu, atmos.z1t[:,tind]/1e5,ls='solid',color=vel_color,label=r'$v$',lw=1.75)  # ls=(0,(3,1,1,1,1,1))

    dlammin = lam_rest - xlim[0]
    dlamplus = lam_rest - xlim[1]

    ax2.set_xlim(dlammin/lam_rest *2.998e5, dlamplus/lam_rest * 2.998e5)
    ax2.set_xlabel('L.o.S. Gas Velocity (km s$^{-1}$); negative = downward')

    if oplot_annotate:
        ax2.text(-325,100,'Backwarmed Upper',ha='center',va='center',fontsize=10)
        ax2.text(-325,50,'Photosphere',ha='center',va='center',fontsize=10)

        ax2.text(-325,830,'Stationary Chrom',ha='center',va='center',fontsize=10)
        ax2.text(-325,780,'Flare Layers',ha='center',va='center',fontsize=10)
        ax2.text(-325,890,'CC',ha='center',va='center',fontsize=10)
        ax2.text(-325,1000,'Evaporation',ha='center',va='center',fontsize=10)

    if oplot_legend2:
        ax2.legend(loc='upper right',frameon=False,labelcolor=vel_color)
    ax2.format_coord = format_coord
    ax4.plot(atmos.tg1t[:,tind]/1000.0, atmos.z1t[:,tind]/1e5,color='k')
    ax4.set_xlim(tlim0,tlim1)
    ax4.set_xticks(np.arange(tlim0, tlim1, step=20)) 
  #  from matplotlib.ticker import MultipleLocator

    ax4.xaxis.set_minor_locator(MultipleLocator(10))
    ax4.yaxis.set_minor_locator(MultipleLocator(25.0))
    ax4.grid(axis='both',alpha=0.35,which='both')  # axis='y'


    bright = color_bright()
   # tinc = np.arange(0, tlim1, 5)
   # for ti in range(len(tinc)):
   #     ax4.plot([tinc[ti],tinc[ti]],[-100,1500],color=bright[6],lw=0.7)

    ax4.plot(atmos.tg1t[:,tind]/1000.0, atmos.z1t[:,tind]/1e5,color=bright[0],label='Gas Temp')

    if oplot_t0:
        ax4.plot(atmos.tg1t[:,0]/1000.0, atmos.z1t[:,0]/1e5,color=bright[0],label='Gas Temp ($t=0$s)',ls='dotted')

  
    srcall = cfline['src'].squeeze()
    srcline = srcall.transpose()
            #print(srcline.shape, wl2d.shape, z2d.shape)
            #plvec = np.vectorize(planckfni)
            #b1d = np.zeros((len(atmos.tg1t[:,tind]),1))
            #b1d[:,0] = plvec(np.median(wlprep), atmos.tg1t[:,tind])
    if flip_wl:
        src_flipped = np.flip(srcline[:,:,tind],axis=1)
    else:
        src_flipped = srcline[:,:,tind]
    dnu2dlam = np.zeros_like(src_flipped) + cnst.CCANG / np.median(wl2d)**2
    src_flipped_dlam = src_flipped * dnu2dlam
    src_slice_dlam = src_flipped_dlam[:,15]
    src_trad = np.zeros(len(src_slice_dlam))
    for tt in range(len(src_slice_dlam)):
        src_trad[tt] = trad(lam_rest, src_slice_dlam[tt])
        
    ax4.plot(src_trad/1000, atmos.z1t[:,tind]/1e5,color=bright[4],ls='dashed',label='Source Fctn Temp')

    if source_ha == True:
        srcall_ha = cfline_ha['src']
        srcline_ha = srcall_ha[0].transpose()
        if flip_wl:
            src_flipped_ha = np.flip(srcline_ha[:,:,tind],axis=1)
        else:
            src_flipped_ha = srcline_ha[:,:,tind]
        dnu2dlam_ha = np.zeros_like(src_flipped_ha) + cnst.CCANG / np.median(6562.8)**2
        src_flipped_dlam_ha = src_flipped_ha * dnu2dlam_ha
        src_slice_dlam_ha = src_flipped_dlam_ha[:,25]
        src_trad_ha = np.zeros(len(src_slice_dlam_ha))
        for tt in range(len(src_slice_dlam_ha)):
            src_trad_ha[tt] = trad(6562.8, src_slice_dlam_ha[tt])
        
        ax4.plot(src_trad_ha/1000, atmos.z1t[:,tind]/1e5,color=bright[4],ls='dashed',label=r'H$\alpha$ Source Function')
    
    ax4.set_ylim(ylim)
    ax4.set_xlabel(r'Temp ($10^3$ K)')
    ax4.legend(fontsize=8,frameon=False,loc=leg_loc)

    if oplot_nel:
        ax5 = ax4.twiny()
        ax5.plot(atmos.ne1t[:,tind]/1e15, atmos.z1t[:,tind]/1e5, color=bright[1])
        zfind = findind(atmos.z1t[:,tind]/1e5, ZFIND)
        ax5.text(atmos.ne1t[zfind, tind]/1e15, atmos.z1t[zfind, tind]/1e5 - 25.0, r'$n_e$',fontsize=15,color=bright[1])
        ax5.set_xlabel(r'El dens ($10^{15}$ cm$^{-3}$)',fontsize=10)
        ax5.set_xlim(nelim0/1e15, nelim1/1e15)
        
    tval = user_time
    ax1.set_title('t = {0:.2f}'.format(user_time)+' s '+model_id)
    plt.tight_layout()
    if savefig:
        plt.savefig(plot_filename+'.pdf')
        print('created plot: ',plot_filename+'.pdf')
    print('The map value range is [',vmin,vmax,'] erg/s/cm3/sr/Ang.')
    print('Returned height (km), wl (Ang), and contribution function with dimensions:',zprep2.shape, wlprep2.shape, c_I_line.shape)
    tauall = cfline['tau'].squeeze()
    tauline = tauall.transpose()
         #   print(tauline.shape, wl2d.shape, z2d.shape)
            #ax1.pcolormesh(wl2d, z2d,np.log10(np.flip(tauline[:,:,tind]/mu,axis=1)),vmax=vmax,vmin=vmin,cmap = xmap,rasterized=True)
            
    ilam_ret = emerg_intline[:,tind]

    if flip_wl:
        tau_return = np.flip(tauline[:,:,tind]/mu,axis=1)
    else:
        tau_return = tauline[:,:,tind]/mu
    ci_dict = {'zpmesh':z2d, 'wlpmesh':wl2d, 'z1d':zprep2, 'wl1d':wlprep2, 'contrib2D':c_I_line[:,:,tind], 'lam0':lam_rest, 'Ilam':ilam_ret, 'tau2D':tau_return} 
    return ci_dict
    

def color_rainbow14(printc = 'no'):
    ''' This is rainbow14 plus grey as last entry, Figure 18 top panel of Paul Tol's website.  color_rainbow(printc = no or yes)'''
    rainbow = [(209,187,215), (174,118,163), (136,46,114), (25,101,176), (82,137,199), (123,175,222), (77,178,101), (144,201,135), (202, 224, 171), (247, 240, 86), (246,193, 65), (241,147,45), (232, 96,28), (220, 5,12), (119, 119, 119)]
    labels=['ltpurple0', 'medpurple1','darkpurple2', 'darkblue3','medblue4', 'lightblue5', 'darkgreen6','medgreen7', 'ltgreen8','yellow9','ltorange10','medorange11', 'dkorange12', 'red13', 'grey14']
    for i in range(len(rainbow)):    
        r, g, b = rainbow[i]    
        rainbow[i] = (r / 255., g / 255., b / 255.)
        if printc == 'yes' or printc =='y':
            print(i, labels[i])
    return rainbow

# Good color schemes to use from https://www.sron.nl/~pault/
def color_map(umap = 'rnbw'):
#    ''' user_cmap = mf.color_map(umap='rnbw') where umap can be burd, burd_flip, or bryl'''
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib import cm
    if umap == 'sun' or umap == 'solar' or umap =='whitelight' or umap == 'solarwl' or umap == 'Sun' or umap == 'Solar' or umap == 'WL' or umap == 'wl':
        scale_f = 0.5
        nn = 255.0
        rgb0 = (255/nn, 242.8/nn, 236.23/nn)
        rgb01 = (255. * 0.75 /nn, 242.8 * 0.75 /nn, 236.23 * 0.75/nn)
        rgb1 = (255. * scale_f /nn, 242.8 * scale_f /nn, 236.23 * scale_f/nn)
        rgb2 = (255. * 0.25 /nn, 242.8 * 0.25 /nn, 236.23 * 0.25/nn)
        rgb3 = (255. * 0.0 /nn, 242.8 * 0.0 /nn, 236.23 * 0.0/nn)

        clrs_sun = [rgb3, rgb2, rgb1,rgb01, rgb0]
        cmap_name = 'clrs_sun'
        usermap  = LinearSegmentedColormap.from_list(cmap_name, clrs_sun, N=500)

    
    if umap == 'cube_purple':
        test = ascii.read('/home/adamkowalski/Dropbox/0-Final_Products/mypy/cubehelix_pur_hex.dat')
        test = ascii.read('/home/adamkowalski/Dropbox/0-Final_Products/mypy/cubehelix3.dat')
        r = test['r']
        g = test['g']
        b = test['b']
        cols  = []
        for i in range(len(r)):
            cols.append('#'+r[i]+g[i]+b[i])
        cmap_name = 'cubehelix_purple'
        usermap = LinearSegmentedColormap.from_list(cmap_name,cols, N=500)
    #    print(cols)
    #return usermap

    
    if umap == 'rnbw':  # this is rainbow34 aka rainbow_WhBr from Figure 20 of Paul Tol's website for interpolating.
        print('Brown to White rainbow.')
        clrs = ['#E8ECFB', '#DDD8EF', '#D1C1E1', '#C3A8D1', '#B58FC2','#A778B4','#9B62A7', '#8C4E99', '#6F4C9B', '#6059A9',  '#5568B8', '#4E79C5', '#4D8AC6', '#4E96BC', '#549EB3', '#59A5A9', '#60AB9E', '#69B190', '#77B77D', '#8CBC68',  '#A6BE54', '#BEBC48', '#D1B541', '#DDAA3C', '#E49C39', '#E78C35', '#E67932', '#E4632D', '#DF4828', '#DA2222', '#B8221E', '#95211B', '#721E17', '#521A13']
        cmap_name = 'rainbow_brwh'
        usermap = LinearSegmentedColormap.from_list(cmap_name, np.flip(clrs), N=500)
      #  usermap.set_bad('#666666')
        usermap.set_bad('#521A13')
    if umap == 'rnbw_flip':  # this is rainbow34 aka rainbow_WhBr from Figure 20 of Paul Tol's website for interpolating.
        print('Brown to White rainbow.')
        clrs = ['#E8ECFB', '#DDD8EF', '#D1C1E1', '#C3A8D1', '#B58FC2','#A778B4','#9B62A7', '#8C4E99', '#6F4C9B', '#6059A9',  '#5568B8', '#4E79C5', '#4D8AC6', '#4E96BC', '#549EB3', '#59A5A9', '#60AB9E', '#69B190', '#77B77D', '#8CBC68',  '#A6BE54', '#BEBC48', '#D1B541', '#DDAA3C', '#E49C39', '#E78C35', '#E67932', '#E4632D', '#DF4828', '#DA2222', '#B8221E', '#95211B', '#721E17', '#521A13']
        cmap_name = 'rainbow_brwh'
        usermap = LinearSegmentedColormap.from_list(cmap_name, clrs, N=500)
    elif umap == 'burd':
        BuRd = ["#2166AC", "#4393C3", "#92C5DE", "#D1E5F0","#F7F7F7", "#FDDBC7","#F4A582", "#D6604D", "#B2182B"]  # bad = 255,238,153 = FFEE99
        cmap_name = 'BuRd' 
        usermap = LinearSegmentedColormap.from_list(cmap_name, np.flip(BuRd), N=100)
    elif umap == 'burd_flip':
        BuRd = ["#2166AC", "#4393C3", "#92C5DE", "#D1E5F0","#F7F7F7", "#FDDBC7","#F4A582", "#D6604D", "#B2182B"]  # bad = 255,238,153 = FFEE99
        cmap_name = 'BuRd_Flipped' 
        usermap = LinearSegmentedColormap.from_list(cmap_name, BuRd, N=100)
    elif umap == 'bryl':
        clrs_ylbr = ['#FFFFE5', '#FFF7BC','#FEE391','#FEC44F','#FB9A29','#EC7014','#CC4C02', '#993404','#662506']
        cmap_name = 'ylbr'
        usermap = LinearSegmentedColormap.from_list(cmap_name, np.flip(clrs_ylbr), N=500)
        usermap.set_bad('#662506')
    else:
        print( ' umap can be rnbw, burd, burd_flip, or bryl')
   
    if umap == 'BWB':  # this is rainbow34 aka rainbow_WhBr from Figure 20 of Paul Tol's website for interpolating.
        print('Brown to White rainbow.')
        clrs = ['#000000','#FFFFFF']
        cmap_name = 'BWB'
        usermap = LinearSegmentedColormap.from_list(cmap_name, clrs, N=500)
      #  usermap.set_bad('#666666')
        usermap.set_bad('#000000')
    return usermap


def trad(wl, ilam):
    # can solve for T_rad on your own using the blackbody formula:
    # ilam in erg/s/cm2/sr/ang,  wl in ang.
    inuv_percm = ilam * 1e8
    hh, cc, kb = 6.626e-27, 2.998e10, 1.38e-16
    Trad = (1./(np.log( (2.0 * hh * cc**2) / (inuv_percm * (wl/1e8)**5) + 1.0))) * \
        hh * cc / (kb * wl/1e8)
    return Trad
    

def akcdf_dz(dz,y,norm=False):
    ciprime = np.zeros_like(y)
    zprime = np.zeros_like(y)
    for j in range(len(dz)):
        ciprime[j] = np.sum(y[0:j]*dz[0:j])
        zprime[j] = np.sum(dz[0:j])
    if norm == True:
        ciprime = ciprime / np.sum(y*dz)
    return zprime, ciprime




def format_coord(x, y):
    global X, Y, ZVALS
    xarr=X
    yarr=Y
    colx = findind(xarr,x)
    rowy = findind(yarr,y)
    zval = ZVALS[rowy, colx]
    return 'x=%1.4f, y=%1.4f, indx = %1i, indy=%4i, val=%1.4e' % (x, y, colx, rowy, zval)

def format_coordxy(x, y):
    global XX, YY, ZZ
    xarr=XX
    yarr=YY
    zarr=ZZ
    colx = findind(xarr,x)
    #rowy = findind(yarr,y)
    #rowy2 = findind(zarr,
    zval = zarr[colx]
    yval = yarr[colx]
    xval = xarr[colx]
    return 'x=%1.4f, y1=%1.2e, y2=%1.2e, indx = %1i' % (xval, zval, yval, colx)


def color_bright(printc='no'):
    ''' color_bright(printc = no or yes) '''
    bright = [(68,119,170), (102,204,238), (34, 136, 51), (204,187,68), (238,102,119), (170,51,119), (187,187,187)]   
    labels=['blue' ,'cyan', 'green', 'yellow','red','purple', 'light grey']
    for i in range(len(bright)):    
        r, g, b = bright[i]    
        bright[i] = (r / 255., g / 255., b / 255.)
        if printc == 'yes' or printc =='y':
            print(i, labels[i])
    return bright


def load_VCSHG(model_id ='mF13-85.dMe', model_dir='./', time=-99.0, retdict=True, SnuDep=False):
    # this was load_atmos in radx_dm
    if not SnuDep:
        fname = glob.glob(model_dir+'spectra/VCSHG/HgammaFluxSpec*NoSnu*'+model_id+'.idl')
    else:
        fname = glob.glob(model_dir+'spectra/VCSHG/HgammaFluxSpec*.Snu*'+model_id+'.idl')
    if len(fname) > 1:
        print('Found more than 1 file with that ID in load_VCSHG!')
        print(fname)
        return None
    vcs = scipy.io.readsav(fname[0])  #+ 'radyn_sed.'+model_id+'.sav
    print('Read in ... ',fname[0])
    vac2air = np.vectorize(vactoair)
    line_flux_t_vcs = vcs.line_flux_vcs_t
    line_flux_t0_vcs = vcs.line_flux_vcs_t0
    line_lam_vcs = vcs.line_vcs_lam
    line_lam_air_vcs = vac2air(line_lam_vcs)
    timet = vcs.timet_spec
    line_flux_ave_vcs = vcs.line_flux_vcs_ave
    ave_cont_wl = vcs.ave_cont_wl
    ave_cont_flux = vcs.ave_cont_flux
    cont_flux_t = vcs.cont_flux_t
    ave_cont_flux_prime = vcs.ave_cont_flux
    if time < 0:
        line_select = line_flux_ave_vcs
        print('Returning time-averaged spectrum')
    else:
        tind = findind(timet, time)
        print('Returning spectrum at time = ',timet[tind])
        line_select = line_flux_t_vcs[tind,:]
        #print(line_flux_t_vcs.shape)
    print('returned lam(air) in Ang, flux (erg/s/cm2/Ang)')
    print('preflare not subtracted, flare continuum not subtracted')
    print('One should subtract off the slope in the continuum unless fitting to only region very close to emission line (e.g., line to continuum ratio)!')
    print('lam0(air) = ',vactoair(vcs.lam0))
    if retdict:
          hgamma_dict = {'wl_Ang_air':line_lam_air_vcs, 'flux':line_select,'lam0':vactoair(vcs.lam0),'notes':'flux in erg/s/cm2/Ang; preflare not subtracted, flare continuum not subtracted'}
          return hgamma_dict
    else:
          return line_lam_air_vcs, line_select

# this will take an input dictionary from load_VCSHG and use SpecLabFunctions
def calc_line_flux(indict):
    import SpecLabFunctions311 as SpecLab
    ldict = SpecLab.lflux(indict['wl_Ang_air'], indict['flux'], adj_wave=8,\
                lwindow_file='linewindows.Hg_wide.ecsv',cont_order=1,plot_check=False)
    return ldict

      
def findind_lower(arr, val):
     tmp = val - arr
     good = (tmp > 0.0)
     ngood = np.count_nonzero(good)
     index = ngood-1
     return index

def bilinear_ry(x0, y0, z, x, y):
    # follows bilinear.f in RADYN source code.  x should be electron density grid (17), y should be temperature grid (7)
    ind1 = findind_lower(x, x0)
    ind2 = findind_lower(y, y0)
    t = (x0 - x[ind1])/(x[ind1+1] - x[ind1])
    u = (y0 - y[ind2])/(y[ind2+1] - y[ind2])

    bilinear = (1-t)*(1-u)*z[ind1,ind2] + t*(1-u)*z[ind1+1,ind2] + t*u*z[ind1+1,ind2+1] + (1-t)*u*z[ind1,ind2+1]
    return bilinear


def load_modelvals(model_id = 'mF13-85-3.dMe', field='C3615p', aveval=-9, model_dir = '/home/adamkowalski/Dropbox/0-Final_Products/ModelOutput/tx_archive/dm/K21_Grid/',print_vals=False):
    '''
    aveval > 0 reads in average value of the field (also in modelvals.tave.fits)
    To get a list of possible fields, just call load_modelvals() with field='??'  '''

    fname = glob.glob(model_dir+'modelvals/modelvals*'+model_id+'*.dat')
    if len(fname) > 1:
        print('Found more than 1 file with that ID in reading modelvals!')
        print(fname)
        return None
    tevol_meta = ascii.read(fname[0],header_start=0, data_start=1,data_end=2)
    tevol_all = ascii.read(fname[0],header_start=2, data_start=3)

    if aveval > 0:
        print(field, tevol_all[field][-1])
        return float(tevol_all[field][-1])
     
    else:
        times = np.array(tevol_all["time_s"][0:-2])
        try:
            print('Calculated spectral quantities from ', fname[0])
            lc = np.array(tevol_all[field][0:-2])
            if print_vals:
                for tt in range(len(lc)):
                    print(times[tt], lc[tt])
            if not silent:
                print('Returning times, lc')
            return times, lc
        except:
            print(tevol_all.keys())
    

def load_contlc(wave = 3615.0, model_id='mF13-85-3.dMe', stype = 'flux', silent=True,model_dir = '/home/adamkowalski/Dropbox/0-Final_Products/ModelOutput/tx_archive/dm/K21_Grid/grid/'):
    fname = glob.glob(model_dir+'spectra/spec.*'+model_id+'*idl')

    if len(fname) > 1:
        print('Error:  Found more than one with that model ID in load_contlc.  Make sure periods are in the model_id')
        return None
    
    radyn = scipy.io.readsav(fname[0])

    if stype == 'flux': # radiative surface flux; gaussian quadrature sum of 5 mu-values
      #  t0_ret = radyn.flam_evol[0].cont_flux_pre
        wl_ret = radyn.flam_evol[0].cont_wl[0,:]

        indwl = findind(wl_ret, wave)
        time_ret = radyn.flam_evol[0].time_s
        cont_ret = radyn.flam_evol[0].cont_flux[:, indwl]

        print('Returning time (s), radiative surface flux (erg/s/cm2/Ang) light curve at closest wavelength, which is ', wl_ret[indwl],' --   Not preflare subtracted.')

    if stype == 'i95': 
        wl_ret = radyn.flam_evol[0].cont_wl[0,:]

        indwl = findind(wl_ret, wave)
        time_ret = radyn.flam_evol[0].time_s
        cont_ret = radyn.flam_evol[0].icont95[0].int[:, indwl]

        print('Returning time (s), emergent intensity at mu=0.95 (erg/s/cm2/Ang/sr) light curve at closest wavelength, which is ', wl_ret[indwl],' --   Not preflare subtracted.')

    if stype == 'i77': 
        wl_ret = radyn.flam_evol[0].cont_wl[0,:]

        indwl = findind(wl_ret, wave)
        time_ret = radyn.flam_evol[0].time_s
        cont_ret = radyn.flam_evol[0].icont77[0].int[:, indwl]

        print('Returning time (s), emergent intensity at mu=0.77 (erg/s/cm2/Ang/sr) light curve at closest wavelength, which is ', wl_ret[indwl],' --   Not preflare subtracted.')
        
    if stype == 'Trad': 
        wl_ret = radyn.flam_evol[0].cont_wl[0,:]

        indwl = findind(wl_ret, wave)
        time_ret = radyn.flam_evol[0].time_s
        cont_retI = radyn.flam_evol[0].icont95[0].int[:, indwl]

        cont_ret = np.zeros_like(cont_retI)
        for tt in range(0, len(time_ret)):
            cont_ret[tt] = trad(wl_ret[indwl], cont_retI[tt])
        print('Returning time (s), radiation temperature (K) from intensity at 0.95 light curve at closest wavelength, which is ', wl_ret[indwl],' --   Not preflare subtracted.')

    return time_ret, cont_ret


def load_spec_from_contribf(model_id='mF13-85-3.dMe', time = -9.0, line='CaIIK', norm_wl = -99.0, silent=False,model_dir = '/home/adamkowalski/Dropbox/0-Final_Products/ModelOutput/tx_archive/dm/K21_Grid/grid/'):

    if line == 'Hg' or line == 'Ha' or line == 'Hb' or line == 'CaIIK' or line == 'CaIIH' or line == 'Pab' or line == 'Paa' or line == 'HeI10830' or line == 'CaII8542':
        contrib_file = glob.glob(model_dir+'lcontribf/lcontribf-'+line+'*'+model_id+'*fits')
    else:
        print('Spectrum for ', line, ' not available.')
        print('Available lines in full grid download:  Paa (Paschen alpha), Pab (Paschen beta), CaIIK, CaIIH, CaII8542, HeI10830')
        return None
    cfline = fits.getdata(contrib_file[0],1)
    lam = cfline['lint95_lam'].squeeze()
    flx_t = cfline['lflux_t'].squeeze()
    flx_ave = cfline['lflux_ave'].squeeze()
    flx_t0 = cfline['lflux_t0'].squeeze()
    lam0_v = cfline['lam0_vac'].squeeze()
    times = cfline['time_s'].squeeze()
    return lam, lam0_v, flx_t, flx_ave, flx_t0, times
    

def load_spec(model_id='mF13-85-3.dMe', time = -9.0, stype = 'cont_flx', norm_wl = -99.0, silent=False,model_dir = '/home/adamkowalski/Dropbox/0-Final_Products/ModelOutput/tx_archive/dm/K21_Grid/grid/'):
    
    '''
    defaults:       load_spec(model_id='mF13-85-3.dMe', time = -9.0, stype = 'cont_flx', norm_wl = -99.0, silent=False, model_dir='...)
      time = -9.0:  returns time-averaged spectrum
      time = -99.0: returns spectra at all times
      time >=0:     returns spectrum at time = t
      stype options:  'cont_flx', 
                      'cont_i95', 
                      'cont_i77', 
                      'cont_i50', 
                      'cont_i23', 
                      'cont_i05', 
                      'Hg_flx', 
                      'Ha_flx', 
                      'Hb_flx', 
                      'merged_flx', 
                      'Hg_flx_VCS', 
                      'Paa_flx' (H Paschen alpha flux), 
                      'Pab_flx' (H Paschen beta flux), 
                      'CaIIK_flx', 
                      'CaIIH_flx', 
                      'CaII8542_flx', 
                      'HeI10830_flx' 
                    Note:  The intensity spectra at mu=0.95 for the emission lines, instead of radiative flux spectra, 
                           can be directly obtained by the user from the .fits files.
    returns a dict: {'wl':wl_ret, 'Slam_t0':t0_ret, 'Slam':spec_ret, 'Slam_prime':prime_spectrum, 'time':t_spec, 'wl0':lam0_air}
                    Note:  Wavelengths for emission lines in air, for continuum in vaccuum
    '''

    if stype == 'CaIIK_flx' or stype == 'HeI10830_flx' or stype == 'CaIIH_flx' or stype == 'CaII8542_flx' or stype == 'Paa_flx' or stype == 'Pab_flx': # left off here. Just need to trigger other lines.
        if stype == 'CaIIK_flx':
            line = 'CaIIK'
        if stype == 'HeI10830_flx':
            line = 'HeI10830'
        if stype == 'CaIIH_flx':
            line = 'CaIIH'
        if stype == 'CaII8542_flx':
            line = 'CaII8542'
        if stype == 'Paa_flx':
            line = 'Paa'
        if stype == 'Pab_flx':
            line = 'Pab'
        
        wl_ret, wl_ret0, spec_ret, ave_ret, spec_ret_t0, times_ret = load_spec_from_contribf(model_id=model_id, model_dir=model_dir, time=time,line=line)
        lam0_air = vactoair(wl_ret0)
        if not silent:
            print('lam0 in air is ', lam0_air, ' Ang')
        
        if time >= 0:
            tind = findind(times_ret, time)
            t_spec = times_ret[tind]
            t0_ret = spec_ret_t0[0,:]
            wl_ret = wl_ret[0,:]
            spec_ret = spec_ret[tind,:]
            prime_spectrum = spec_ret - t0_ret
            if not silent:
                print('Returning spectrum at time = ',t_spec, ' s')

        if time > -10 and time < 0:
            t_spec= 'average'
            t0_ret= spec_ret_t0[0,:]
            wl_ret = wl_ret[0,:]
            spec_ret = ave_ret
            prime_spectrum = spec_ret - t0_ret
            if not silent:
                print('Returning time-averaged spectrum.')

        if time < -10:
            t_spec= times_ret
            t0_ret = spec_ret_t0
            prime_spectrum = spec_ret - t0_ret
            if not silent:
                print('Returning all spectra at all times with shapes for (Slam(t0), Slam(t), wl):', t0_ret.shape, spec_ret.shape, wl_ret.shape, ' -> (ntime, nwl)')

        spec_dict = {'wl':wl_ret, 'Slam_t0':t0_ret, 'Slam':spec_ret, 'Slam_prime':prime_spectrum, 'time':t_spec, 'wl0':lam0_air}
        if not silent:
            print('  ')
            print('Returned a dictionary with: wl [Ang], Slam_t0 [erg/s/cm2/Ang], Slam [erg/s/cm2/Ang], Slam_prime [= Slam - Slam_t0],  time [s], wl0 [Ang]')
            print('Spectra in units of erg/s/cm2/Ang/steradian if requested continuum intensity:  icont95, icont77, icont50, icont23, icont05')
            print('Rest wavelength [Ang] = ',lam0_air)
            print('Air wavelengths? Yes for emission lines.  No for continuum.')
            print('  ')
        return spec_dict


    lam0 = -999
    fname = glob.glob(model_dir+'spectra/spec.*'+model_id+'*.fits')

    if len(fname) > 1:
        print('Error:  Invalid ID or more than one model with that ID.  Returning.')
        return None
    
#    radyn = scipy.io.readsav(fname[0])
#    radyn = fits.getdata(

    if not silent:
        print('Reading in spectra from ',fname[0])
        
    if time < 0 and time > -10:
        t_spec = 'average'
        if not silent:
            print('Returning time-averaged spectrum.')

    if time >=  0: 
        if stype == 'Hg_flx_VCS':
            radyn = fits.getdata(fname[0], 3)
        else:    
            radyn = fits.getdata(fname[0], 1) # first extension has spectra as a function of time.

        alltimes = radyn['time_s'].squeeze()
        tind = findind(alltimes, time)
        t_spec = alltimes[tind]
        if not silent:
            print('Returning spectrum at time = ',t_spec, ' s')

        if stype == 'Hg_flx_VCS':
            spec_ret = radyn['Hg_flux_t_VCS'].squeeze()[tind,:] 
            wl_ret = radyn['Hg_lam_air_VCS'].squeeze() 
            t0_ret = radyn['Hg_flux_t0_VCS'].squeeze()
            lam0 = radyn['Hg_lam0'].squeeze() # vacuum, convert to air later
            
        if stype == 'cont_flx': # non-equilibrium b-f and f-f spectrum (continuum) only, no b-b.  Hyd, Helium, Ca II continua in detail, background continua from other elements in LTE are listed in opctab.dat file (see Allred et al. 2015).
            spec_ret = radyn['cont_flux'].squeeze()[tind,:] 
            wl_ret = radyn['cont_wl'].squeeze()[tind,:] # vacuum
            t0_ret = radyn['cont_flux_pre'].squeeze()[tind,:] 
            # with the IDL tool rmovie.pro. radyn.flam_evol[0].cont_flux_pre[tind] is the same as radyn.flam_evol[0].cont_flux[0]
        if stype == 'cont_i95':
            spec_ret = radyn['icont95'].squeeze()[tind,:] 
            wl_ret = radyn['cont_wl'].squeeze()[tind,:] 
            t0_ret = radyn['icont95_pre'].squeeze()[tind,:]
        if stype == 'cont_i77':
            spec_ret = radyn['icont77'].squeeze()[tind,:] 
            wl_ret = radyn['cont_wl'].squeeze()[tind,:] 
            t0_ret = radyn['icont77_pre'].squeeze()[tind,:]
        if stype == 'cont_i50':
            spec_ret = radyn['icont50'].squeeze()[tind,:] 
            wl_ret = radyn['cont_wl'].squeeze()[tind,:] 
            t0_ret = radyn['icont50_pre'].squeeze()[tind,:]
        if stype == 'cont_i23':
            spec_ret = radyn['icont23'].squeeze()[tind,:] 
            wl_ret = radyn['cont_wl'].squeeze()[tind,:] 
            t0_ret = radyn['icont23_pre'].squeeze()[tind,:]
        if stype == 'cont_i05':
            spec_ret = radyn['icont05'].squeeze()[tind,:] 
            wl_ret = radyn['cont_wl'].squeeze()[tind,:] 
            t0_ret = radyn['icont05_pre'].squeeze()[tind,:]
        if stype == 'merged_flx':   # non-equilibrium b-f and f-f spectrum (continuum) + hyd Balmer non-equi. b-b with new Stark broadening (H alpha, H beta, H gamma)
            spec_ret = radyn['merged_flux'].squeeze()[tind,:] 
            wl_ret = radyn['merged_wl'].squeeze()[tind,:] 
            t0_ret = radyn['merged_pre'].squeeze()[tind,:]
        if stype == 'Ha_flx': # just H alpha at 51 wavelength points (continuum over wavelength range included)
            spec_ret = radyn['Ha_flux'].squeeze()[tind,:] 
            wl_ret = radyn['Ha_wl'].squeeze()[tind,:] 
            t0_ret = radyn['Ha_flux_pre'].squeeze()[tind,:]
            lam0= radyn['Ha_lam0'].squeeze()
        if stype == 'Hb_flx':
            spec_ret = radyn['Hb_flux'].squeeze()[tind,:] 
            wl_ret = radyn['Hb_wl'].squeeze()[tind,:] 
            t0_ret = radyn['Hb_flux_pre'].squeeze()[tind,:]
            lam0= radyn['Hb_lam0'].squeeze()
        if stype == 'Hg_flx': # just H gmma at 31 wavelength points (continuum over wavelength range included)
            spec_ret = radyn['Hg_flux'].squeeze()[tind,:] 
            wl_ret = radyn['Hg_wl'].squeeze()[tind,:]  # air, converted Ha, Hb, and Hg from RADYN vacuum wavelengths to air before
            t0_ret = radyn['Hg_flux_pre'].squeeze()[tind,:]
            lam0= radyn['Hg_lam0'].squeeze() # vacuum (by hand)


    if time < -10:
        if stype == 'Hg_flx_VCS':
            radyn = fits.getdata(fname[0],3)
        else:
            radyn = fits.getdata(fname[0], 1) # first extension has spectra as a function of time.
        t_spec = radyn['time_s'].squeeze()
        
        if stype == 'Hg_flx_VCS':
            spec_ret = radyn['Hg_flux_t_VCS'].squeeze()
            wl_ret = radyn['Hg_lam_air_VCS'].squeeze()
            t0_ret = radyn['Hg_flux_t0_VCS'].squeeze()
            lam0 = radyn['Hg_lam0'].squeeze() # convert to air later.
            
        if stype == 'cont_flx':
            spec_ret = radyn['cont_flux'].squeeze()
            wl_ret = radyn['cont_wl'].squeeze()
            t0_ret = radyn['cont_flux_pre'].squeeze()
        if stype == 'cont_i95':
            spec_ret = radyn['icont95'].squeeze() 
            wl_ret = radyn['cont_wl'].squeeze() 
            t0_ret = radyn['icont95_pre'].squeeze()
        if stype == 'cont_i77':
            spec_ret = radyn['icont77'].squeeze() 
            wl_ret = radyn['cont_wl'].squeeze() 
            t0_ret = radyn['icont77_pre'].squeeze()
        if stype == 'cont_i50':
            spec_ret = radyn['icont50'].squeeze() 
            wl_ret = radyn['cont_wl'].squeeze() 
            t0_ret = radyn['icont50_pre'].squeeze()
        if stype == 'cont_i23':
            spec_ret = radyn['icont23'].squeeze() 
            wl_ret = radyn['cont_wl'].squeeze() 
            t0_ret = radyn['icont23_pre'].squeeze()
        if stype == 'cont_i05':
            spec_ret = radyn['icont05'].squeeze() 
            wl_ret = radyn['cont_wl'].squeeze() 
            t0_ret = radyn['icont05_pre'].squeeze()
        if stype == 'merged_flx':   # non-equilibrium b-f and f-f spectrum (continuum) + hyd Balmer non-equi. b-b with new Stark broadening (H alpha, H beta, H gamma)
            spec_ret = radyn['merged_flux'].squeeze() 
            wl_ret = radyn['merged_wl'].squeeze() 
            t0_ret = radyn['merged_pre'].squeeze()
        if stype == 'Ha_flx': # just H alpha at 51 wavelength points (continuum over wavelength range included)
            spec_ret = radyn['Ha_flux'].squeeze() 
            wl_ret = radyn['Ha_wl'].squeeze() 
            t0_ret = radyn['Ha_flux_pre'].squeeze()
            lam0= radyn['Ha_lam0'].squeeze()
        if stype == 'Hb_flx':
            spec_ret = radyn['Hb_flux'].squeeze() 
            wl_ret = radyn['Hb_wl'].squeeze() 
            t0_ret = radyn['Hb_flux_pre'].squeeze()
            lam0= radyn['Hb_lam0'].squeeze()
        if stype == 'Hg_flx': # just H gmma at 31 wavelength points (continuum over wavelength range included)
            spec_ret = radyn['Hg_flux'].squeeze() 
            wl_ret = radyn['Hg_wl'].squeeze() 
            t0_ret = radyn['Hg_flux_pre'].squeeze()
            lam0= radyn['Hg_lam0'].squeeze()
        if not silent:
            print('Returning all spectra at all times with shapes for (Slam(t0), Slam(t), wl):', t0_ret.shape, spec_ret.shape, wl_ret.shape, ' -> (ntime, nwl)')

    if time  < 0 and time > -10: # The flam_ave structures give a single averaged over t1 to t2 (usually 0.2-9.8s).
        if stype == 'Hg_flx_VCS':
            radyn = fits.getdata(fname[0],3)
        else:
            radyn = fits.getdata(fname[0],2)

        if stype == 'Hg_flx_VCS':
            spec_ret = radyn['Hg_flux_ave_VCS'].squeeze()
            wl_ret = radyn['Hg_lam_air_VCS'].squeeze() 
            t0_ret = radyn['Hg_flux_t0_VCS'].squeeze()
            lam0 = radyn['Hg_lam0'].squeeze() 
            
        if stype == 'cont_flx':
            spec_ret = radyn['cont_flux'].squeeze()
            wl_ret = radyn['cont_wl'].squeeze()
            t0_ret = radyn['cont_flux_pre'].squeeze()
        if stype == 'merged_flx':   # non-equilibrium b-f and f-f spectrum (continuum) + hyd Balmer non-equi. b-b with new Stark broadening (H alpha, H beta, H gamma)
            spec_ret = radyn['merged_flux'].squeeze()
            wl_ret = radyn['merged_wl'].squeeze()
            t0_ret = radyn['merged_pre'].squeeze()
        if stype == 'Ha_flx': # just H alpha at 51 wavelength points (continuum over wavelength range included)
            spec_ret = radyn['Ha_flux'].squeeze()
            wl_ret = radyn['Ha_wl'].squeeze()
            t0_ret = radyn['Ha_flux_pre'].squeeze()
            lam0= radyn['Ha_lam0'].squeeze()
        if stype == 'Hb_flx':
            spec_ret = radyn['Hb_flux'].squeeze()
            wl_ret = radyn['Hb_wl'].squeeze()
            t0_ret = radyn['Hb_flux_pre'].squeeze()
            lam0= radyn['Hb_lam0'].squeeze()
        if stype == 'Hg_flx': # just H gmma at 31 wavelength points (continuum over wavelength range included)
            spec_ret = radyn['Hg_flux'].squeeze()
            wl_ret = radyn['Hg_wl'].squeeze()
            t0_ret = radyn['Hg_flux_pre'].squeeze()
            lam0= radyn['Hg_lam0'].squeeze()
        if stype == 'icont95' or stype == 'icont77' or stype == 'icont50' or stype == 'icont23' or stype == 'icont05':
            print('Time averages not provided in FITS files for the continuum intensities. Returning.')
            return None
        if not silent and stype != 'Hg_flx_VCS':
            t1 = radyn['t1'].squeeze()
            t2 = radyn['t2'].squeeze()
            dt = radyn['dt'].squeeze()
            print('Time average from {0:.3f}-{1:.3f} s to {2:.3f}+{3:.3f} s with dt = {4:.3f} s'.format( t1,dt/2.0,t2,dt/2.0,dt))
        
    prime_spectrum = spec_ret - t0_ret # prime means preflare subtracted 

    if norm_wl > 0:
        wl_ind = findind(wl_ret, norm_wl)
        prime_spectrum = prime_spectrum / prime_spectrum[wl_ind]
        if not silent:
            print('Normalized prime spectrum to wl = ',wl_ret[wl_ind])

    if lam0 > 0:
        lam0 = vactoair(lam0)  # lam0 stored by hand are alamb[2,4,7]
    if not silent:
        print('  ')
        print('Returned a dictionary with: wl [Ang], Slam_t0 [erg/s/cm2/Ang], Slam [erg/s/cm2/Ang], Slam_prime [= Slam - Slam_t0],  time [s], wl0 [Ang]')
        print('Spectra in units of erg/s/cm2/Ang/steradian if requested continuum intensity:  icont95, icont77, icont50, icont23, icont05')
        print('Rest wavelength [Ang] = ',lam0)
        print('Air wavelengths? Yes for emission lines.  No for continuum.')
        print('  ')
        
    spec_dict = {'wl':wl_ret, 'Slam_t0':t0_ret, 'Slam':spec_ret, 'Slam_prime':prime_spectrum, 'time':t_spec, 'wl0':lam0}
    return spec_dict


def rad2plot_help():
    names = ['Height','Col Mass', 'Temp', 'Density', 'Nel', 'Beam Heating', 'Pressure', 'Velocity']
    info = ['z1t/1e5 [km]', 'log10 cmass1t [g/cm2]', 'tg1t [K]', 'd1t [g/cm3]', 'ne1t [electrons/cm3]', 'bheat1t [erg/s/cm3]', 'pg1t [dyn/cm2]','vz1t/1e5 [km/s], positive=up']
    print('The options for rad2plot are the following: ')
    for nn in range(len(names)):
        print(names[nn],':', info[nn])
    return None

def rad2plot(atmos,x1in, y1in, y2in, time = 0.0, xlim=[-100,1500], y1lim=[3,6], y2lim=[3,6], user_figsize=(8,6), user_fontsize=16, oplot_t0=False,psym=False, y1log = False, y2log = False,savefig=False,plot_filename='rad2plot',y2_other=0):
    if x1in == 'Height':
        x1 = atmos.z1t/1e5
        x1in = x1in + ' (km)'
    if x1in == 'Col Mass':
        x1 = np.log10(atmos.cmass1t)
        x1in = x1in + r' (g cm$^{-2}$)'
        x1in = r'log$_{10}$ '+x1in
        
    if y1in == 'Temp':
        y1 = atmos.tg1t
        y1in = y1in +' (K)'
    if y1in == 'Density':
        y1 = atmos.d1t
        y1in = y1in+r' (g cm$^{-3}$)'
    if y1in == 'Nel':
        y1 = atmos.ne1t
        y1in = r'N$_e$ (cm$^{-3}$)'
    if y1in == 'Beam Heating':
        y1 = atmos.bheat1t
        y1in = y1in + r' (erg s$^{-1}$ cm$^{-3}$)'
    if y1in == 'Pressure':
        y1 = atmos.pg1t
        y1in = y1in + r' (dyn cm$^{-2}$)'
    if y1in == 'Velocity':
        y1 = atmos.vz1t/1e5
        y1in = y1in+r' (km s$^{-1}$)'

    if y2in == 'Temp':
        y2 = atmos.tg1t
        y2in = y2in +' (K)'
    if y2in == 'Density':
        y2 = atmos.d1t
        y2in = y2in+r' (g cm$^{-3}$)'
    if y2in == 'Nel':
        y2 = atmos.ne1t
        y2in = r'N$_e$ (cm$^{-3}$)'
    if y2in == 'Beam Heating':
        y2 = atmos.bheat1t
        y2in = y2in + r' (erg s$^{-1}$ cm$^{-3}$)'
    if y2in == 'Pressure':
        y2 = atmos.pg1t
        y2in = y2in + r' (dyn cm$^{-2}$)'
    if y2in == 'Velocity':
        y2 = atmos.vz1t/1e5
        y2in = y2in+r' (km s$^{-1}$)'
    if y2in == 'user':
        y2 = y2_other
        
    if y1log:
        y1 = np.log10(y1)
        y1in = r'log$_{10}$ '+y1in
    if y2log:
        y2 = np.log10(y2)
        y2in= r'log$_{10}$ '+y2in
    
    timet = atmos.timet
    brightcol = color_bright()
    rnbw_col = color_rainbow14()
    plt.rc('font',size=user_fontsize)
    f, ax1 = plt.subplots(figsize=user_figsize)
    indt1 = findind(timet, time)
    utime = timet[indt1]
    print('time = ',timet[indt1])
    print('min max of y1:',np.min(y1[:,indt1]), np.max(y1[:,indt1]))
    print('min max of y2:',np.min(y2[:,indt1]), np.max(y2[:,indt1]))

    if psym:
        ax1.plot(x1[:,indt1], y1[:,indt1], ls='solid',color='k',lw=2,marker='+')
    else:
        ax1.plot(x1[:,indt1], y1[:,indt1], ls='solid',color='k',lw=2)
    if oplot_t0 == True:
        ax1.plot(x1[:,0], y1[:,0], ls='dotted',color='k')
        print('Dotted linestyles are the t=0s atmospheric parameters.')
    ax1.set_ylim(y1lim)
    ax1.set_xlim(xlim)
    ax1.set_xlabel(x1in)
    ax1.set_ylabel(y1in)
    ax2 = ax1.twinx()
    if psym:
        ax2.plot(x1[:,indt1], y2[:,indt1],ls='dashed',color=rnbw_col[13],lw=2,marker='+')
    else:
        ax2.plot(x1[:,indt1], y2[:,indt1],ls='dashed',color=rnbw_col[13],lw=2)
    if oplot_t0 == True:
        ax2.plot(x1[:,0], y2[:,0],ls='dashdot',color=rnbw_col[13])
    ax2.set_ylabel(y2in,color=rnbw_col[13])
    ax2.set_ylim(y2lim)
    
    ax2.tick_params(axis='y', colors=rnbw_col[13])
    ax2.spines['right'].set_color(rnbw_col[13])
    ax2.set_title('t = '+str('{0:.2f}'.format(utime))+' s')
    global XX
    global YY
    global ZZ
    XX = x1[:,indt1]
    YY = y2[:,indt1]
    ZZ = y1[:,indt1]
    ax2.format_coord = format_coordxy
    plt.tight_layout()
    if savefig:
        plt.savefig(plot_filename+'.pdf')
        print('created plot: ',plot_filename+'.pdf')
    return None


def make_movie_2panels(model_id = 'mF13-85-3.dMe', model_dir = './', xtype = 'z',xrange=[-100,600], tstrt=0.0, tend=10.0, tinc = 0.2, yrange_ul = [2e3,30e6], yrange_ur = [1e2,1e6], yrange_lr = [-50,50], yrange_ll = [1e-11, 1e-6], Esel_1 = 150.0, Esel_2 = 350.0 ): 
    movie_name = "mov."+model_id+".mp4"  # "c5F11-25-4.2_Solar_10s_TB09_new_arrows.mp4"
    plot_title =  model_id  #r'$5\times 10^{11}$ erg cm$^{-2}$ s$^{-1}$, $\delta=4.2$, $E_c=25$ keV (log$_{10}$ $g=4.44$)'

    mpl.rcParams['font.family']='serif'
    cmfont = font_manager.FontProperties(fname=mpl.get_data_path() + '/fonts/ttf/cmr10.ttf')
    mpl.rcParams['font.serif']=cmfont.get_name()
    mpl.rcParams['mathtext.fontset']='cm'
    mpl.rcParams['axes.unicode_minus']=False

    bright = color_bright()

    model_1 = load_atmos(model_id = model_id, model_dir = model_dir)
    
    tmov_sel = np.arange(tstrt, tend, tinc)
    x = model_1.z1t / 1e5
    xlabel = '$z$: Distance (km) from Photosphere along Loop'
    timet = model_1.timet

    # upper left yaxis
    y_ul = model_1.tg1t
    yscale_ul = 'log'
    ylabel_ul = r'Temperature (K)'
    label_ul = 'Temp.' # if you want to plot a legend with ax1.legend()
    color_ul = 'black'
    oplot_ul = 1  # this controls if you want to plot t=0 values as dashed lines.

    # upper right yaxis
    y_ur = model_1.bheat1t
    yscale_ur = 'log'
    ylabel_ur = r'Q$_{\rm{beam}}$: $e$- Beam Heating (erg cm$^{-3}$ s$^{-1}$)'
    label_ur = r'Q$_{\rm{beam}}$'
    color_ur = bright[4]
    oplot_ur = 0

    # lower left yaxis
    y_lr = model_1.vz1t / 1e5
    yscale_lr = 'linear'
    ylabel_lr = r'Gas Velocity (km s$^{-1}$) neg: downward'
    label_lr = r'Vel. (neg: downflows)'
    color_lr = 'k'
    oplot_lr = 0

    y_ll = model_1.d1t

    yscale_ll = 'log'
    ylabel_ll = r'$\rho$: Mass Density (g cm$^{-3}$)'
    label_ll = r'$\rho$'
    color_ll = bright[2]
    oplot_ll = 1
    
    z0 = model_1.z1t[:,0]
    
    inds_movie = [0] * len(tmov_sel)
    ii=0
    while ii < len(tmov_sel):
        inds_movie[ii] = findind(timet, tmov_sel[ii])
        ii+=1
    import matplotlib.animation as ani

    outfname = movie_name
   
    plt.rc('font', family='serif',size=16)

    fig, (ax1, ax2) = plt.subplots(nrows=2,tight_layout=True,figsize=(9,9),sharex=True,sharey=False)


    writer = ani.writers['ffmpeg'](fps=10)
    with writer.saving(fig, outfname, 100):  # 100 dpi, larger gives larger movie
        for j in range(len(inds_movie)):

            i = inds_movie[j]
            print(timet[inds_movie[j]], model_1.timet[inds_movie[j]])
            ax1.plot(x[:,i], y_ul[:,i],label=label_ul,color=color_ul)
            ax1.set_ylabel(ylabel_ul,color=color_ul)
            ax1.set_ylim(yrange_ul)
            ax1.set_yscale(yscale_ul)
            ax1.set_xlim(xrange)
            ax1.text(-20,7e3,'T')
            ax1.grid(axis='both',alpha=0.35,which='both')  # axis='y'

            if yscale_ul == 'linear':
                ax1.ticklabel_format(style='sci',useMathText=True,axis='y',scilimits=(0,0)) 
               # ax1.text(0.1, 0.9, 'Time = '+"{:.2f}".format(timet[i])+' s', \
              #           horizontalalignment='left',verticalalignment='center',transform=ax1.transAxes, \
               #          fontsize=14,color='black')
            if oplot_ul == 1:
                ax1.plot(x[:,0], y_ul[:,0],ls='dashed',color=color_ul)
            ax1.set_title(plot_title+" time={:.2f}".format(timet[i])+' s',fontsize=14)

            if i > 0:
                ax1b.get_yaxis().set_visible(False)

            ax1b = ax1.twinx()
            ax1b.plot(x[:,i], y_ur[:,i],label=label_ur,color=color_ur,lw=2)

           # make_patch_spines_invisible(ax1b)
            ax1b.set_ylim(yrange_ur)
            ax1b.set_yscale(yscale_ur)
            ax1b.set_xlim(xrange)
            ax1b.set_ylabel(ylabel_ur,color=color_ur,alpha=1.0)
            ax1b.set_ylabel(ylabel_ur,color=color_ur,alpha=1.0)
            ax1b.set_ylabel(ylabel_ur,color=color_ur,alpha=1.0)

            #if yscale_ur == 'linear':
             #   ax1b.ticklabel_format(style='sci',useMathText=True,axis='y',scilimits=(0,0))
            #if oplot_ur == 1:
            #    ax1b.plot(x[:,0], y_ur[:,0],ls='dashed',color=color_ur)
        
       # ee1, gg, mm,lil,dz_tot1 = bstop.thicktarg_save_m(atmos_1, timet[inds_movie[j]], Esel_1, \
       #                                          1.0, -10, 0.511,\
      #                                 plot_it=False,helium=True,h2=False)
        #ax1bb = ax1.twinx()
      #  ax1bb.set_yscale('linear')
      #  ax1bb.set_ylim(0,1)
      #  ee2, gg, mm,lil, dz_tot2 = bstop.thicktarg_save_m(atmos_1, timet[inds_movie[j]], Esel_2, \
      #                  1.0, -10, 0.511,\
       #                                plot_it=False,helium=True,h2=False)
      #  ax1bb.plot(x[i,:], ee1 / np.max(ee1),color=bright[6],lw=1.5,ls='dashdot')
     #   ax1bb.plot(x[i,:], ee2 / np.max(ee2),color=bright[6],lw=1.5,ls='dashdot')

      #  make_patch_spines_invisible(ax1bb)
      #  ax1bb.get_xaxis().set_visible(False)
     #   ax1bb.get_yaxis().set_visible(False)

            ax2.plot(x[:,i], y_ll[:,i], color=color_ll,lw=2)
            ax2.text(50,2e-7,label_ll,ha='center',va='center',color=color_ll)
            ax2.set_ylim(yrange_ll)
            ax2.set_yscale(yscale_ll)
            ax2.set_xlim(xrange)
            ax2.set_xlabel(xlabel)
            ax2.set_ylabel(ylabel_ll,color=color_ll)
            ax2.grid(axis='both',alpha=0.35,which='both')  # axis='y'

            if yscale_ll == 'linear':
                ax2.ticklabel_format(style='sci',useMathText=True,axis='y',scilimits=(0,0))
            if oplot_ll == 1:
                ax2.plot(x[:,0], y_ll[:,0],ls='dashed',color=color_ll,zorder=50)
            if i > 0:
                ax2b.get_yaxis().set_visible(False)  # This is HORRIBLE BUG in recent versions of python.

            ax2b = ax2.twinx()
            ax2b.set_ylim(yrange_lr)
            ax2b.plot(x[:,0], np.zeros_like(x[:,0]), color='k',ls='dotted')
            ax2b.set_yscale(yscale_lr)
            ax2b.set_xlim(xrange)

            ax2b.set_ylabel(ylabel_lr,color='k')
            ax2b.plot(x[:,i], y_lr[:,i], color=color_lr,lw=2)
            #plt.tight_layout(pad=-0.8, w_pad=0.5, h_pad=1.)
            writer.grab_frame()
            ax1.cla()
            ax1b.cla()
            ax2.cla()
            ax2b.cla()
            

def read_rh(ifile,model_dir=''):
    input_atmos_file = model_dir+'RH_input/'+ifile
    n_dep_rh = ascii.read(input_atmos_file,format='no_header',data_start=8, data_end=9)
    n_dep_RH = n_dep_rh[0][0]
    user_atmos = ascii.read(input_atmos_file,format='no_header',data_start=11, data_end=11+n_dep_RH)
    temp_model = np.array(user_atmos['col2'][:])
    cmass_model = np.array(10**user_atmos['col1'][:])
    nel_model = np.array(user_atmos['col3'][:])
    vkms_model = np.array(user_atmos['col4'][:])
    vturbkms_model = np.array(user_atmos['col5'][:])

    user_nh = ascii.read(input_atmos_file,format='no_header',data_start=11 + n_dep_RH + 2, data_end=11+n_dep_RH + 2 + n_dep_RH)
    ndep = len(temp_model)
    n_HI_set =  (user_nh['col1'][:]+ user_nh['col2'][:]+user_nh['col3'][:]+user_nh['col4'][:]+user_nh['col5'][:]) 
    nH_n1_nlte = np.array(user_nh['col1'][:])
    nH_n2_nlte = np.array(user_nh['col2'][:])
    nH_n3_nlte = np.array(user_nh['col3'][:])
    nH_n4_nlte = np.array(user_nh['col4'][:])
    nH_n5_nlte = np.array(user_nh['col5'][:])
    nH_np_nlte = np.array(user_nh['col6'][:])

    lgmass = np.log10(cmass_model)
    rh_atmos = {'lgmass':lgmass, 'T':temp_model, 'n_el':nel_model, 'vkms':vkms_model, 'vturbkms':vturbkms_model,'n1_H':nH_n1_nlte, 'n2_H':nH_n2_nlte, 'n3_H':nH_n3_nlte, 'n4_H':nH_n4_nlte, 'n5_H':nH_n5_nlte, 'n_p':nH_np_nlte}
    return rh_atmos
    
def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
