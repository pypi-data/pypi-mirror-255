import ROOT
import math

import array
import os
import sys
import collections
import re
import random
import pickle
import datetime
import sympy
import bisect

import utils_noroot as utnr
import numpy        as np
import operator     as op
import pandas       as pnd
import awkward      as ak

import warnings
import logging

from atr_mgr         import mgr        as amgr

warnings.filterwarnings( action='ignore', category=RuntimeWarning, message='creating converter.*' )
warnings.filterwarnings( action='ignore', category=FutureWarning , message='buffer.SetSize(N) is deprecated.*' )
ROOT.gErrorIgnoreLevel=ROOT.kWarning

lvl=logging.INFO
log=utnr.getLogger(__name__, lvl)
#-------------------------
#Settings
#-------------------------
CME="#sqrt{s}=13TeV"
MAX_RAT=-1
MIN_RAT=-1
MAX_GRP=-1
MIN_GRP=-1

tp_yrange=None

l_color=[]
l_marker=[]
l_line=[]

ROOT.gROOT.SetBatch(True)
#-------------------------
#Legends
#-------------------------
leg_xmin=0.60
leg_xmax=0.95
leg_ymin=0.50
leg_ymax=0.90
#-------------------------
#Pads
#-------------------------
logy=True
#-------------------------
#Fit plots
#-------------------------
PLOT_BINS=100

DEBUG=0

import sympy
from sympy.parsing.sympy_parser import parse_expr as sympy_parse_expr

#-------------------------------------------------------
def rdf_report_to_df(rep):
    '''
    Takes the output of rdf.Report(), i.e. an RDataFrame cutflow report.

    Produces a pandas dataframe with 
    '''
    d_data = {'cut' : [], 'All' : [], 'Passed' : []}
    for cut in rep:
        name=cut.GetName()
        pas =cut.GetPass()
        tot =cut.GetAll()

        d_data['cut'   ].append(name)
        d_data['All'   ].append(tot)
        d_data['Passed'].append(pas)

    df = pnd.DataFrame(d_data)
    df['Efficiency' ] = df['Passed'] / df['All']
    df['Cummulative'] = df['Efficiency'].cumprod() 

    return df
#-------------------------------------------------------
def chain_to_tree(chain):
    file_path  = get_random_filename()
    chain_name = chain.GetName()

    chain.Merge(file_path)

    ifile=ROOT.TFile(file_path)
    itree=ifile.Get(chain_name)

    return (itree, ifile)
#-------------------------------------------------------
def get_hist_compatibility(h_1, h_2, kind='chi2_ndof'):
    h_1 = h_1.Clone()
    h_2 = h_2.Clone()

    h_1.Scale(1/h_1.Integral())
    h_2.Scale(1/h_2.Integral())

    if kind == 'kolmogorov':
        return h_1.KolmogorovTest(h_2)

    nbins_1 = h_1.GetNbinsX()
    nbins_2 = h_2.GetNbinsX()

    if nbins_1 != nbins_2:
        log.error(f'Binning of histograms differ: {nbins_1}/{nbins_2}')
        raise

    chi2      = 0.
    diff_quad = 0.
    for i_bin in range(1, nbins_1 + 1):
        bc_1 = h_1.GetBinContent(i_bin)
        be_1 = h_1.GetBinError(i_bin)

        bc_2 = h_2.GetBinContent(i_bin)
        be_2 = h_2.GetBinError(i_bin)

        error      = math.sqrt(be_1 ** 2 + be_2 ** 2)
        diff       = (bc_1 - bc_2) ** 2 
        diff_quad += diff

        if error == 0:
            log.debug(f'Zero error for bin: {i_bin}/{nbins_1}')
            term = 1
        else:
            term = diff / error ** 2
            log.debug(f'Bin/kind: {i_bin:3d}/{kind}  --> {term:>10.3f} = ({bc_1:>4.3f} - {bc_2:>4.3f}) ** 2 / {error:>10.3e} ** 2')

        chi2 += term

    if   kind == 'chi2_pvalue':
        val = ROOT.Math.chisquared_cdf_c(chi2, nbins_1)
    elif kind == 'chi2_ndof':
        val = chi2      / nbins_1
    elif kind == 'diff_quad':
        val = diff_quad / nbins_1
    else:
        log.error(f'Compatibily type {kind} not allowed')
        raise

    return val 
#-------------------------------------------------------
def reformat_2D_hist(hist):
    ROOT.gPad.Update()

    l_fun = hist.GetListOfFunctions()
    pal   = l_fun.FindObject("palette")
    if not pal:
        log.error(f'Palette not found in 2D histogram, not reformating it.')
        raise

    pal.SetY1NDC(0.25)
    pal.SetY2NDC(0.85)
#-------------------------------------------------------
def get_arr_eff_err(arr_tot=None, arr_pas=None):
    utnr.check_type(arr_tot, np.ndarray)
    utnr.check_type(arr_pas, np.ndarray)

    if arr_tot.shape != arr_pas.shape:
        log.error('Yield arrays have different shapes:')
        print(arr_tot.shape)
        print(arr_pas.shape)
        raise

    l_err = []
    for tot, pas in zip(arr_tot, arr_pas):
        (eff_cn, err_up, err_dn) = get_eff_err(pas, tot)
        err = (err_up + err_dn) / 2.
        l_err.append(err)

    return np.array(l_err)
#-------------------------------------------------------
#From https://github.com/HDembinski/essays/blob/master/error_propagation_with_sympy.ipynb
#value_and_covariance("s / (s + b)", s=(5, 0.5), b=(10, 0.1))

def value_and_covariance_gen(expr, variables):
    expr = sympy_parse_expr(expr)

    symbols = sympy.symbols(variables)
    cov_symbols = sympy.symbols(tuple("C_" + k for k in variables))
    expr2 = sum( (expr.diff(s) * c) ** 2 for s, c in zip(symbols, cov_symbols))
    expr2 = expr2.simplify()

    fval = sympy.lambdify(symbols, expr)
    fcov = sympy.lambdify(symbols + cov_symbols, expr2)

    def fn(**kwargs):
        x = tuple(v[0] for v in kwargs.values())
        c = tuple(v[1] for v in kwargs.values())
        return fval(*x), fcov(*x, *c)

    return fn
#-------------------------------------------------------
def value_and_covariance(expr, **kwargs):
    val, err2 = value_and_covariance_gen(expr, tuple(kwargs))(**kwargs)

    err = math.sqrt(err2)

    return (val, err)
#-------------------------------------------------------
if True:
    l_color.append(1)
    l_color.append(2)
    l_color.append(4)
    l_color.append(3)
    l_color.append(6)
    l_color.append(8)
    l_color.append(39)
    l_color.append(49)
    l_color.append(38)
    l_color.append(46)

    l_marker.append(20)
    l_marker.append(21)
    l_marker.append(22)
    l_marker.append(23)
    l_marker.append(33)
    l_marker.append(47)
    l_marker.append(34)
    l_marker.append(39)
    l_marker.append(47)
    l_marker.append(49)

    l_line.append(1)
    l_line.append(1)
    l_line.append(1)
    l_line.append(1)
    l_line.append(1)
    l_line.append(1)
    l_line.append(1)
    l_line.append(1)
    l_line.append(1)
    l_line.append(1)
#------------------------------
def divide_dics(d_num, d_den, label=""):
    tmp=d_num.keys()
    l_key_num=list(tmp)
    n_num = len(l_key_num)

    tmp=d_den.keys()
    l_key_den=list(tmp)
    n_den = len(l_key_den)

    if l_key_num != l_key_den:
        s_key_den=set(l_key_den)
        s_key_num=set(l_key_num)

        s_key_common = s_key_den.intersection(s_key_num)
        n_com = len(s_key_common)

        ROOT.Warning("divide_dics", "Dictionaries have different keys for {}, dropping non-shared keys".format(label) )
        ROOT.Warning("divide_dics", "nNum, nDen -> nCommon: {}, {} -> {}".format(n_num, n_den, n_com) )

        l_key_num = list(s_key_common)

    d_rat={}
    l_key_num=sorted(l_key_num)
    for key in l_key_num:
        num=d_num[key]
        den=d_den[key]

        try:
            d_rat[key] = num/den
        except:
            ROOT.Error("divide_dics", col("Dividing {}/{} for key {}, assigning ---> 0".format(num, den, key), 'yellow'))
            d_rat[key] = 0 

    return d_rat
#------------------------------
def cantorPairing(a, b):
    #https://en.wikipedia.org/wiki/Pairing_function#Cantor_pairing_function
    seed=(a + b) * (a + b + 1) + 2 * b 

    return seed
#----------------------------------
def makeWeights(evt, index):
    seed=cantorPairing(evt, index)
    random.seed(seed)

    #From http://www.columbia.edu/~ks20/4404-Sigman/4404-Notes-ITM.pdf
    c=math.exp(-1)
    p=1 
    x=0 
    while True:
        p*=random.uniform(0, 1)
        if p < c:
            break
        x+=1
    
    return x
#----------------------------------
vMakeWeights=np.vectorize(makeWeights)
#----------------------------------
def weightData(arr_dat, arr_evt, index):
    if len(arr_dat) != len(arr_evt):
        ROOT.Error("weightData", "Different array sizes for data and event number")
        ROOT.Error("weightData", "    Data : {}".format(len(arr_dat)))
        ROOT.Error("weightData", "    Event: {}".format(len(arr_evt)))
        exit(1)

    if index < 0:
        log.error("The index needs to be positive, using {}".format(index))
        raise

    if index == 0:
        log.debug("Not weighting dataset, index = " + str(index))
        return arr_dat

    arr_wgt_pois=vMakeWeights(arr_evt, index)
    arr_wgt_dat = arr_dat * arr_wgt_pois 

    return arr_wgt_dat
#------------------------------
def effTandP(p, e_p, f, e_f):
    tot=p + f

    t1=(p * e_f) / tot**2
    t2=(f * e_p) / tot**2

    err=math.sqrt(t1**2 + t2**2)
    eff=p/tot

    return (eff, err)
#------------------------------
def get_eff_err(pased, total):
    '''
    Given passed and total yields returns, (efficiency, error_up, error_down)
    '''
    level = 0.68

    if total == 0:
        log.error(f'Total yield is zero')
        raise

    eff_cn = pased / total
    if total < pased:
        log.warning(f'Total > passed: {total:.0f} > {pased:.0f}, assigning eff error = 0')
        return (eff_cn, 0, 0) 

    eff_up = ROOT.TEfficiency.ClopperPearson(total, pased, level,  True)
    eff_dn = ROOT.TEfficiency.ClopperPearson(total, pased, level, False)

    del_up = eff_up - eff_cn
    del_dn = eff_cn - eff_dn

    return (eff_cn, del_up, del_dn)
#------------------------------
def toy_eff_TandP(mu_p, sg_p, mu_f, sg_f):
    ran=ROOT.TRandom3(0)
    p = -1
    f = -1

    while p < 0:
        p=ran.Gaus(mu_p, sg_p)

    while f < 0:
        f=ran.Gaus(mu_f, sg_f)

    e=p/(p + f)

    return e
#-------------------------------------------------------
def CheckAxisLimits(a1, a2):
    firstBin = a1.GetBinWidth(1)
    lastBin  = a1.GetBinWidth(a1.GetNbins())

    eq_1=ROOT.TMath.AreEqualAbs(a1.GetXmin(), a2.GetXmin(), firstBin * 1.e-10) 
    eq_2=ROOT.TMath.AreEqualAbs(a1.GetXmax(), a2.GetXmax(), lastBin  * 1.e-10)

    if not eq_1 or not eq_2:
        return False

    return True
#-------------------------------------------------------
def CheckBinLimits(a1, a2):
    h1Array = a1.GetXbins()
    h2Array = a2.GetXbins()

    fN = h1Array.fN
    if fN != 0:
        if h2Array.fN != fN:
            ROOT.Warning("CheckBinLimits", "fN_1/fN_2:{}/{}".format(fN, h2Array.fN))
            return False 
    else: 
        for i in range(0, fN):
            binWidth = a1.GetBinWidth(i)
            if not ROOT.TMath.AreEqualAbs( h1Array.GetAt(i), h2Array.GetAt(i), binWidth*1e-10 ): 
                return False 

    return True 
#-------------------------------------------------------
def CheckBinLabels(a1, a2):
    l1 = a1.GetLabels()
    l2 = a2.GetLabels()
                   
    if l1 is None and l2 is None:
        return True 

    if l1 is None or  l2 is None: 
        return False

    if l1.GetSize() != l2.GetSize():
        return False

    for i in range(1, a1.GetNbins() + 1):
        label1 = a1.GetBinLabel(i)
        label2 = a2.GetBinLabel(i)
        if label1 != label2:
            return False
                                              
    return True 
#-------------------------------------------------------
def CheckConsistency(h1, h2, deep=True):
    if h1 == h2: 
        return True 
                
    if h1.GetDimension() != h2.GetDimension(): 
        ROOT.Warning("CheckConsistency", "Different dimension")
        return False 

    dim    = h1.GetDimension()

    nbinsx = h1.GetNbinsX()
    nbinsy = h1.GetNbinsY()
    nbinsz = h1.GetNbinsZ()
                                        
    if nbinsx != h2.GetNbinsX() or (dim > 1 and nbinsy != h2.GetNbinsY() ) or (dim > 2 and nbinsz != h2.GetNbinsZ()):
        ROOT.Warning("CheckConsistency", "Different number of bins")
        return False
                                                                    
    ret = True 
                                                                        
    ret = ret and CheckAxisLimits(h1.GetXaxis(), h2.GetXaxis())
    if dim > 1: 
        ret = ret and CheckAxisLimits(h1.GetYaxis(), h2.GetYaxis())
    if dim > 2: 
        ret = ret and CheckAxisLimits(h1.GetZaxis(), h2.GetZaxis())
                                                                                        
    if not ret:
        ROOT.Warning("CheckConsistency", "Different axes limits")

    if not deep:
        return ret
                                                                                                                
    ret = ret and CheckBinLimits(h1.GetXaxis(), h2.GetXaxis())
    if dim > 1: 
        ret = ret and CheckBinLimits(h1.GetYaxis(), h2.GetYaxis())
    if dim > 2: 
        ret = ret and CheckBinLimits(h1.GetZaxis(), h2.GetZaxis())

    if not ret:
        ROOT.Warning("CheckConsistency", "Different bin limits")
                                                                                                                                                                                                                       
    #if not h1.IsEmpty() and not h2.IsEmpty(): 
    #    ret = ret and CheckBinLabels(h1.GetXaxis(), h2.GetXaxis())
    #    if dim > 1:
    #        ret = ret and CheckBinLabels(h1.GetYaxis(), h2.GetYaxis())
    #    if dim > 2: 
    #        ret = ret and CheckBinLabels(h1.GetZaxis(), h2.GetZaxis())


    return ret
#-------------------------------------------------------
def copyContents(h_org, h_cop):
    if not CheckConsistency(h_org, h_cop, deep=False):
        ROOT.Warning("copyContents", "Histograms are not compatible")
        raise

    nbins=h_org.GetNbinsX()
    for i_bin in range(1, nbins + 1):
        val=h_org.GetBinContent(i_bin)
        err=h_org.GetBinError(i_bin)

        h_cop.SetBinContent(i_bin, val)
        h_cop.SetBinError(i_bin, err)
#------------------------------
#------------------------------
def getFileObject(ifile, name):
    try:
        obj=getattr(ifile, name)
        return obj
    except AttributeError:
        ROOT.Info("getFileObject", "Cannot get %s from file %s" % (name, ifile.GetName()) )
        ifile.ls()
        raise
    except:
        ROOT.Info("getFileObject", "Unknown exception caught")
        raise
#------------------------------
def getWeight(tree, w_c, w_v, e_v, wgt_tol, ntoy=100):
    f_w_c=ROOT.TTreeFormula(w_c, w_c, tree)
    f_w_v=ROOT.TTreeFormula(w_v, w_v, tree)
    f_e_v=ROOT.TTreeFormula(e_v, e_v, tree)

    tree.SetBranchStatus("*", 0)
    setBranchStatusTTF(tree, "{} && {} && {}".format(w_c, w_v, e_v))

    d_wi_w = {}
    l_wf=[]
    for entry in tree:
        w_c_f=f_w_c.EvalInstance()
        w_v_f=f_w_v.EvalInstance()

        w_i=int(w_c_f * w_v_f * wgt_tol)
        
        if w_i not in d_wi_w:
            e_v_f=f_e_v.EvalInstance()
            d_wi_w[w_i] = (w_c_f , w_v_f , e_v_f)
            l_wf.append(w_c_f * w_v_f)

    l_wf=l_wf.sort()
    l_wi=sorted(d_wi_w)

    d_wi_j={}
    for j, w_i in enumerate(l_wi):
        d_wi_j[w_i]=j

    nwgt=len(l_wi)
    print("Found {} weights".format(nwgt))
    w_jk=np.matrix([[0.] * ntoy] * nwgt)
    ran=ROOT.TRandom3(0)
    for wi, (w_c_f, w_v_f, e_v_f) in d_wi_w.items():
        j = d_wi_j[wi]
        for k in range(0, ntoy):
            w_f_k=w_c_f * ran.Gaus(w_v_f, e_v_f)
            w_jk[j,k] = w_f_k

    return (w_jk, d_wi_j)
#------------------------------
def addSyst(tree, h, x, w, w_jk, d_wi_j, wgt_tol):
    nwgt=len(d_wi_j)
    nbin=h.GetNbinsX()

    n_ij=np.matrix([[0] * nwgt] * nbin)

    tree.SetBranchStatus("*", 0)
    setBranchStatusTTF(tree, "{} && {}".format(x, w))

    f_x=ROOT.TTreeFormula(x, x, tree)
    f_w=ROOT.TTreeFormula(w, w, tree)
    for entry in tree:
        x_f=f_x.EvalInstance()
        w_f=f_w.EvalInstance()

        i=h.FindBin(x_f) - 1
        if i < 0 or i >= nbin:
            continue

        w_i=int(w_f * wgt_tol)
        if w_i not in d_wi_j:
            print("Cound not find {} weight in {}".format(w_i, d_wi_j))
            exit(1)

        j=d_wi_j[w_i]

        n_ij[i,j]+=1
    
    b_ik=n_ij * w_jk
    for i in range(0, nbin):
        bc = np.mean(b_ik[i])
        be = np.std(b_ik[i], ddof=1)

        h.SetBinContent(i + 1, bc)
        h.SetBinError(i + 1, be)
#------------------------------
def combineSyst(name, h_mean, l_hist):
    if len(l_hist) <= 0:
        print("List of histograms is empty")
        exit(1)

    h_ref = l_hist[0]
    nbins = h_mean.GetNbinsX()

    d_ibin_be={}
    for hist in l_hist:
        if nbins != hist.GetNbinsX():
            print("Histograms with different binning")
            exit(1)

        for ibin in range(1, nbins + 1):
            be=hist.GetBinError(ibin)
            if ibin not in d_ibin_be:
                d_ibin_be[ibin] = [be]
            else:
                d_ibin_be[ibin].append(be)

    h_cmb=h_mean.Clone(name)

    for ibin in range(1, nbins + 1):
        cmb_bc=h_mean.GetBinContent(ibin)

        l_be=d_ibin_be[ibin]
        cmb_be=0
        for be in l_be:
            cmb_be+=be ** 2

        cmb_be = math.sqrt(cmb_be)

        h_cmb.SetBinContent(ibin, cmb_bc)
        h_cmb.SetBinError(ibin, cmb_be)

    return h_cmb
#-----------------------------------------
#-----------------------------------------
def get_derivative(fun, arr_var, l_deg, epsilon=1e-5):
    ndim=fun.GetNdim()
    if ndim != len(l_deg):
        print("Wrong dimensionality:") 
        print("degree: {}".format(len(l_deg))) 
        print("Func  : {}".format(fun.GetNdim()))
        exit(1)

    if ndim != len(arr_var):
        print("Wrong dimensionality:") 
        print("Point: {}".format(len(arr_var))) 
        print("Func : {}".format(fun.GetNdim()))
        exit(1)

    if l_deg == [0] * ndim:
        return fun.EvalPar(arr_var)

    dim=0
    for deg in l_deg:
        if deg != 0:
            break
        else:
            dim+=1

    arr_var_up=array.array('d', arr_var)
    l_next_deg=list(l_deg)
    try:
        arr_var_up[dim]+=epsilon
        l_next_deg[dim]-=1
    except IndexError:
        print("IndexError: Trying to access index {} in:".format(dim))
        print(arr_var_up)
        print(l_next_deg)
        exit(1)
    except:
        print("OtherError: Trying to access index {} in:".format(dim))
        print(sys.exc_info()[0])
        print(arr_var_up)
        print(l_next_deg)
        exit(1)

    dfun = get_derivative(fun, arr_var_up, l_next_deg) - get_derivative(fun, arr_var, l_next_deg)
    dfun /= epsilon

    return dfun
#-----------------------------------------
def get_mean_1d(fun, tp_x):
    if fun.GetNdim() != 1: 
        print("Func : {}".format(fun.GetNdim()))
        exit(1)

    mu_x=tp_x[0]

    arr_p=array.array('d', [mu_x])

    d_fun_0=get_derivative(fun, arr_p, [0])
    d_fun_2=get_derivative(fun, arr_p, [2])

    sg_x=tp_x[1]

    mu_fun = d_fun_0 + 0.5 * (d_fun_2 * sg_x ** 2)

    print(d_fun_0/mu_fun)

    return mu_fun 
#-----------------------------------------
def get_mean_2d(fun, tp_x, tp_y):
    if fun.GetNdim() != 2: 
        print("Func : {}".format(fun.GetNdim()))
        exit(1)

    mu_x=tp_x[0]
    mu_y=tp_y[0]

    arr_p=array.array('d', [mu_x, mu_y])

    d_fun_00=get_derivative(fun, arr_p, [0, 0])
    d_fun_20=get_derivative(fun, arr_p, [2, 0])
    d_fun_02=get_derivative(fun, arr_p, [0, 2])

    sg_x=tp_x[1]
    sg_y=tp_y[1]

    mu_fun = d_fun_00 + 0.5 * (d_fun_20 * sg_x ** 2 + d_fun_02 * sg_y ** 2)

    return mu_fun 
#-----------------------------------------
def get_error_1d(fun, tp_x):
    if fun.GetNdim() != 1: 
        print("Func : {}".format(fun.GetNdim()))
        exit(1)

    mu_x=tp_x[0]

    arr_p=array.array('d', [mu_x])

    d_fun_1=get_derivative(fun, arr_p, [1])
    d_fun_2=get_derivative(fun, arr_p, [2])

    sg_x=tp_x[1]

    var_fun = (d_fun_1 * sg_x) ** 2 - 0.25 * (d_fun_2 * sg_x ** 2) ** 2

    print( (d_fun_1 * sg_x) ** 2 / var_fun )

    return math.sqrt(var_fun)
#-----------------------------------------
def get_error_2d(fun, tp_x, tp_y):
    if fun.GetNdim() != 2: 
        print("Func : {}".format(fun.GetNdim()))
        exit(1)

    mu_x=tp_x[0]
    mu_y=tp_y[0]

    arr_p=array.array('d', [mu_x, mu_y])

    d_fun_10=get_derivative(fun, arr_p, [1, 0])
    d_fun_01=get_derivative(fun, arr_p, [0, 1])

    d_fun_11=get_derivative(fun, arr_p, [1, 1])

    d_fun_20=get_derivative(fun, arr_p, [2, 0])
    d_fun_02=get_derivative(fun, arr_p, [0, 2])

    sg_x=tp_x[1]
    sg_y=tp_y[1]

    term_1 = (d_fun_10 * sg_x) ** 2    +    (d_fun_01 * sg_y) ** 2 
    term_2 = (d_fun_11 * sg_x * sg_y) ** 2
    term_3 = sg_x ** 4 * d_fun_20 ** 2 + sg_y ** 4 * d_fun_02 ** 2
    term_4 = d_fun_02 * d_fun_20 * sg_x ** 2 * sg_y ** 2

    var_fun = term_1 + term_2 + 0.75 * term_3 + 0.5 * term_4
    #print(math.sqrt(term_2 - 0.25 * term_3))

    return math.sqrt(var_fun)
#-------------------------------------------------------
#-------------------------------------------------------
def exists(obj):
    try:
        obj.GetName()
    except ReferenceError:
        return False
    except:
        print("Cannot retrieve name from object")
        return True

    return True
#-------------------------------------------------------
def get_from_file(obj_name, file_path, kind=None):
    utnr.check_file(file_path)

    ifile=ROOT.TFile(file_path)
    obj = ifile.Get(obj_name)

    if not obj:
        log.error('Object \"{}\" not found in \"{}\"'.format(obj_name, file_path))
        ifile.ls()
        ifile.Close()
        raise

    if kind is not None and not obj.InheritsFrom(kind):
        log.error('Object \"{}\" is not of type \"{}\"'.format(obj_name, kind))
        obj.Print()
        ifile.Close()
        raise

    return (obj, ifile)
#-------------------------------------------------------
#-------------------------------------------------------
def getBins(hist):
    nbins=hist.GetNbinsX()

    l_x=[]
    l_y=[]
    for i_bin in range(1, nbins + 1):
        x=hist.GetBinCenter (i_bin)
        y=hist.GetBinContent(i_bin)

        l_x.append(x)
        l_y.append(y)

    return (l_x, l_y)
#-------------------------------------------------------
#Plotting
#-------------------------------------------------------
def getHistRange(l_hist):
    low_index =1e10
    high_index=0
    threshold =1e10
    arr_x=None
    for hist in l_hist:
        arr_x, arr_y = getBins(hist)

        thr_tmp=max(arr_y) / 1e4
        if thr_tmp < threshold:
            threshold = thr_tmp

        low_tmp=0
        for y in arr_y:
            if y > thr_tmp:
                break
            low_tmp+=1

        high_tmp=len(arr_y) - 1
        for y in reversed(arr_y):
            if y > thr_tmp:
                break
            high_tmp-=1

        if low_tmp < low_index:
            low_index = low_tmp

        if high_tmp > high_index:
            high_index = high_tmp

    #print((low_index, high_index))

    min_x=arr_x[ low_index - 1]
    max_x=arr_x[high_index]

    return (min_x, max_x, threshold)
#-------------------------------------------------------
def getPlotRange(plot, l_component):
    l_hist=[]
    for component in l_component:
        hist=plot.getHist(component)
        try:
            hist.GetName()
        except ReferenceError:
            print("Cannot retrieve {} histogram".format(component))
            plot.Print()
            exit(1)

        l_hist.append(hist)

    low_index =1e10
    high_index=0
    threshold =1e10
    arr_x=None
    for hist in l_hist:
        arr_x=hist.GetX()
        arr_y=hist.GetY()

        thr_tmp=max(arr_y) / 1e4
        if thr_tmp < threshold:
            threshold = thr_tmp

        low_tmp=0
        for y in arr_y:
            if y > thr_tmp:
                break
            low_tmp+=1

        high_tmp=len(arr_y) - 1
        for y in reversed(arr_y):
            if y > thr_tmp:
                break
            high_tmp-=1

        if low_tmp < low_index:
            low_index = low_tmp

        if high_tmp > high_index:
            high_index = high_tmp

    #print((low_index, high_index))

    min_x=arr_x[ low_index]
    max_x=arr_x[high_index]

    return (min_x, max_x, threshold)
#-------------------------------------------------------
#Hypothesis testing
#-------------------------------------------------------
def getPvalue(plot, hist_1, hist_2, threshold=0.1):
    h_1=plot.getHist(hist_1)
    h_2=plot.getHist(hist_2)

    try:
        h_1.GetName()
        h_2.GetName()
    except ReferenceError:
        print("Either histogram could not be found")
        plot.Print()
        exit(1)

    n1=h_1.GetN()
    n2=h_2.GetN()

    if n1 != n2 or n1 <= 0 or n2 <= 0:
        print("Wrong bin numbers n1={}, n2={}".format(n1, n2))
        exit(1)

    arr_vy1=h_1.GetY()
    arr_hy1=h_1.GetEYhigh()
    arr_ly1=h_1.GetEYlow()

    arr_vy2=h_2.GetY()
    arr_hy2=h_2.GetEYhigh()
    arr_ly2=h_2.GetEYlow()

    chi2=0
    ndof=0
    for vy1, hy1, ly1, vy2, hy2, ly2 in zip(arr_vy1, arr_hy1, arr_ly1, arr_vy2, arr_hy2, arr_ly2):
        if vy1 == 0 or vy2 == 0:
            continue
        elif vy1 == vy2:
            ey1 = 1
            ey2 = 1
        else:
            ey1 = ly1 if vy1 > vy2 else hy1
            ey2 = ly2 if vy2 > vy1 else hy2

        sigma=(ey1**2 + ey2**2)
        resd2=(vy1    -    vy2)**2

        if ey1/vy1 > threshold or ey2/vy2 > threshold:
            continue

        chi2+=resd2/sigma
        ndof+=1
        
    pvalue=ROOT.Math.chisquared_cdf_c(chi2, ndof)

    #print((chi2, ndof, pvalue))

    return pvalue

def getPvalue(l_hist, threshold=0.1):
    try:
        h_1=l_hist[0]
        h_2=l_hist[1]
    except ReferenceError:
        print("Either histogram could not be found")
        print(l_hist)
        exit(1)

    n1=h_1.GetNbinsX()
    n2=h_2.GetNbinsX()

    if n1 != n2 or n1 <= 0 or n2 <= 0:
        print("Wrong bin numbers n1={}, n2={}".format(n1, n2))
        exit(1)

    chi2=0
    ndof=0
    for i_bin in range(1, n1 + 1):
        vy1 = h_1.GetBinContent(i_bin)
        vy2 = h_2.GetBinContent(i_bin)

        ey1 = h_1.GetBinError(i_bin)
        ey2 = h_2.GetBinError(i_bin)

        if vy1 == 0 or vy2 == 0:
            continue

        sigma=(ey1**2 + ey2**2)
        resd2=(vy1    -    vy2)**2

        if ey1/vy1 > threshold or ey2/vy2 > threshold:
            continue

        chi2+=resd2/sigma
        ndof+=1
        
    pvalue=ROOT.Math.chisquared_cdf_c(chi2, ndof)

    #print((chi2, ndof, pvalue))

    return pvalue

def getPull(h_ref, h_mes):
    nref=h_ref.GetNbinsX()
    nmes=h_mes.GetNbinsX()

    if nref != nmes:
        print("Histograms differen in bin number {} vs {}".format(nref, nmes))
        exit(1)

    axis_x=h_ref.GetXaxis()
    min_x=axis_x.GetXmin()
    max_x=axis_x.GetXmax()

    h_pull=ROOT.TH1F("h_pull_{}_{}".format(h_ref.GetName(), h_mes.GetName()), "", nref, min_x, max_x)

    for i_bin in range(1, nref + 1):
        y_ref=h_ref.GetBinContent(i_bin)
        y_mes=h_mes.GetBinContent(i_bin)

        e_ref=h_ref.GetBinError(i_bin)
        e_mes=h_mes.GetBinError(i_bin)

        sigma=math.sqrt(e_ref**2 + e_mes**2)

        resid=y_ref-y_mes

        if sigma == 0:
            h_pull.SetBinContent(i_bin, 0)
            h_pull.SetBinError  (i_bin, 0)
        else:
            h_pull.SetBinContent(i_bin, resid/sigma)
            h_pull.SetBinError  (i_bin, 1)

    axis_y=h_pull.GetYaxis()
    axis_y.SetRangeUser(-5, 5)

    return h_pull
#-------------------------------------------------------
#For fits
#-------------------------------------------------------
def get_fit_res_par(res_path, fix_list):
    d_obj, rfile = get_objects(res_path, clas='RooFitResult')

    tfile = open(fix_list)
    l_par_name = tfile.read().splitlines()

    d_res_par = {}
    for _, res in sorted(d_obj.items()):
        l_par = res.floatParsFinal()
        for par_name in l_par_name:
            par = l_par.find(par_name)
            if not par:
                log.error('Cannot find {} in results file'.format(par_name))
                l_par.Print()
                raise

            val = par.getVal()
            utnr.add_to_dic_lst(d_res_par, par_name, val)

    tfile.close()
    rfile.Close()

    return d_res_par
#-------------------------------------------------------
def plotFit(resultspath, l_save_scale=['log'], d_opt={}):
    utnr.check_file(resultspath)
    #---------------------
    resultsdir=resultspath.replace(".root", "")
    utnr.make_dir_path(resultsdir)
    #---------------------
    ifile=ROOT.TFile(resultspath)
    wks=ifile.Get("wks")

    d_result={}
    regex="result_([A-Za-z]+)(_\d{2})?"
    for key in ifile.GetListOfKeys():
        obj=key.ReadObj()

        if not obj.InheritsFrom("RooFitResult"):
            continue

        resultname=obj.GetName()
        treename=utnr.get_regex_group(resultname, regex, i_group=1)
        utnr.add_to_dic_lst(d_result, treename, obj)


    if len(d_result) != 1:
        log.error("Cannot find results for one and only one tree in: " + resultspath)
        ifile.ls()
        print(d_result.keys())
        ifile.Close()
        raise

    [(treename, l_result)] = list(d_result.items())

    utnr.check_nonempty(l_result)

        
    d_par_val={}
    d_par_err={}
    for i_res, res in enumerate(l_result):
        res_name=res.GetName()
        dat_name=res_name.replace("result", "data")
        suf_name=res_name.replace("result_", "")

        mod = check_wks_obj(wks,  'model',  'pdf', retrieve=True)
        dat = check_wks_obj(wks, dat_name, 'data', retrieve=True)

        s_obs=mod.getObservables(dat)
        nobs=s_obs.size()

        mod.SetTitle("Model")
        dat.SetTitle("Data")


        slice_text = get_slice_text(i_res, d_opt, l_result)
        if slice_text is not None:
            d_opt['text'] = slice_text


        wks.loadSnapshot(suf_name)
        pval=res.GetTitle()
        if nobs != 1:
            log.error(f"Model contains {nobs} observables")
            raise

        for scale in l_save_scale:
            doPlotFit1D(pval, mod, dat, resultsdir, suf_name, scale, d_opt=d_opt)

    ifile.Close()
#-------------------------------------------------------
def get_slice_text(i_slice, d_opt, l_result):
    if 'slice_text' not in d_opt:
        return None

    l_text = d_opt['slice_text']
    if len(l_text) != len(l_result):
        log.error('Results and texts associated are different in size')
        print(l_text)
        print(l_result)
        raise

    return l_text[i_slice]
#-------------------------------------------------------
def plotParameters(d_par_val, d_par_err, tp_slice, resultsdir):
    varname=tp_slice[0]
    l_slice=tp_slice[1]
    nslice=len(l_slice) - 1

    arr_bin=np.array(l_slice)

    ofilename="{}/parameters.root".format(resultsdir)
    ofile=ROOT.TFile(ofilename, "recreate")

    for tree_par in d_par_val:
        try:
            treename = tree_par.split("|")[0]
            parname  = tree_par.split("|")[1]
        except:
            ROOT.Error("plotParameters", "Cannot access parameter name in " + tree_par)
            raise

        arr_yval=d_par_val[tree_par]
        arr_yerr=d_par_err[tree_par]

        h=ROOT.TH1F("h_" + tree_par, "{}({})".format(parname, varname), nslice, arr_bin)
        h.GetYaxis().SetTitle(parname)
        h.GetXaxis().SetTitle(varname)

        for i_bin in range(1, nslice + 1):
            val=arr_yval[i_bin - 1]
            err=arr_yerr[i_bin - 1]

            h.SetBinContent(i_bin, val)
            h.SetBinError(i_bin, err)

        h.Write()

        can=ROOT.TCanvas("can_" + tree_par, "", 1000, 600)
        h.Draw()

        can.SaveAs("{}/par_{}_{}.pdf".format(resultsdir, treename, parname))
        can.SaveAs("{}/par_{}_{}.png".format(resultsdir, treename, parname))

    ofile.Close()
#-------------------------------------------------------
def addEntry(d_par_val, d_par_err, treename, res):
    s_par = res.floatParsFinal()

    for par in s_par:
        parname=par.GetName()
        key=treename + "|" + parname
        parval=par.getVal()
        parerr=par.getError()

        if key not in d_par_val:
            d_par_val[key] = np.array([parval])
            d_par_err[key] = np.array([parerr])
        else:
            d_par_val[key]=np.append(d_par_val[key], parval)
            d_par_err[key]=np.append(d_par_err[key], parerr)
#-------------------------------------------------------
def doPlotFit1D(pvalue, model, data, resultsdir, suffix, scale='log', d_opt={}):
    if scale not in ['lin', 'log']:
        log.error('Invalid scale ' + str(scale))
        raise
    #--------------------------
    s_obs = model.getObservables(data)
    var_obs = s_obs.first()
    #--------------------------
    d_pdfname={"model" : "Model"}
    if  model.InheritsFrom('RooProdPdf'):
        log.info('Found RooProdPdf, taking only first component, assuming others are constraints')
        l_pdf = model.pdfList()
        model = l_pdf.at(0)
        model.SetName('model')

    if model.InheritsFrom("RooAddPdf"):
        l_pdf=model.pdfList()
    else:
        l_pdf=[model]

    for pdf in l_pdf:
        name =pdf.GetName()
        title=pdf.GetTitle()
        d_pdfname[name]=title
    #--------------------------
    if data.InheritsFrom("RooDataHist"):
        data=rebinDataHist(data, var_obs)
        plot=var_obs.frame()
    else:
        plot=var_obs.frame(PLOT_BINS)

    data.plotOn(plot, ROOT.RooFit.Name("data"))
    #--------------------------
    index_style=2

    for pdfname in d_pdfname:
        color=l_color[index_style]
        line =l_line [index_style]

        log.debug(f'Plotting component: {pdfname}')

        model.plotOn(plot, ROOT.RooFit.Components(pdfname), ROOT.RooFit.LineColor(color), ROOT.RooFit.MarkerColor(color), ROOT.RooFit.LineStyle(line), ROOT.RooFit.Name(pdfname) )
        index_style+=1

    can=ROOT.TCanvas("can", "", 600, 600)
    DrawFit(plot, var_obs, can, scale)

    fit_pad=can.cd(1)
    d_objname=dict({"data" : "Data"}, **d_pdfname)

    leg=getLegend(plot, d_objname)
    leg.Draw()

    txt_pval=get_pval_box(pvalue)
    txt_pval.Draw()

    if 'text' in d_opt:
        text   =d_opt['text']
        txt_ext=get_txt_box(text)
        txt_ext.Draw()

    if scale == 'log':
        fit_pad.SetLogy(logy)

    plotpath=f"{resultsdir}/fit_{suffix}_{scale}.png"
    log.visible(f'Saving to: {plotpath}')
    can.SaveAs(plotpath)
#-------------------------------------------------------
def get_pval_box(pvalue):
    txt_pval=ROOT.TPaveText(0.6, 0.83, 0.85, 0.93, "NDC")

    fpvalue=float(pvalue)
    txt_pval.AddText("p-value={:.2e}".format(fpvalue) )
    reformatTextBox(txt_pval)

    return txt_pval
#-------------------------------------------------------
def get_txt_box(text):
    txt_box=ROOT.TPaveText(0.18, 0.83, 0.60, 0.93, "NDC")

    txt_box.AddText(text)
    reformatTextBox(txt_box)

    return txt_box
#-------------------------------------------------------
def rebinDataHist(data, obs):
    name=data.GetName()
    obs.setBins(data.numEntries())
    h_data=data.createHistogram("h_data_" + name, obs)
    nbin=h_data.GetNbinsX()

    l_divisor=sympy.divisors(nbin)

    fgroup_size = nbin/float(PLOT_BINS)

    loc = bisect.bisect_right(l_divisor, fgroup_size)
    group_size = l_divisor[loc]
    if group_size < 2:
        return data 

    data.SetName("orig_" + name)

    ROOT.Info("rebinDataHist", "Rebinning {} bins into {} groups of {} bins".format(nbin, nbin/group_size, group_size) )

    h_data.Rebin(group_size)
    nbin =h_data.GetNbinsX()
    x_min=h_data.GetXaxis().GetXmin()
    x_max=h_data.GetXaxis().GetXmax()

    obs_h=ROOT.RooRealVar(obs)
    obs_h.setBins(nbin)
    obs_h.setRange(x_min, x_max)

    data=ROOT.RooDataHist(name, "", ROOT.RooArgList(obs_h), h_data)

    return data
#-------------------------------------------------------
def getNRanges(var):
    rng_def = var.getBinningPtr("fake_range")

    counter = 0
    while True:
        counter += 1
        name = "r_{}".format(counter)
        rng = var.getBinningPtr(name)
        #print(name)
        #rng.Print()
        if rng == rng_def:
            break

    print("Found {} ranges".format(counter - 1))

    return counter - 1
#-------------------------------------------------------
def doPlotFit2D(pvalue, model, data, resultsdir, suffix):
    s_obs = model.getObservables(data)
    it=s_obs.createIterator()
    obs_1 = it.Next() 
    obs_2 = it.Next()
    #--------------------------
    d_pdfname={"model" : "Model"}
    if model.InheritsFrom("RooAddPdf"):
        l_pdf=model.pdfList()
    else:
        l_pdf=[model]

    for pdf in l_pdf:
        name =pdf.GetName()
        title=pdf.GetTitle()
        d_pdfname[name]=title
    #--------------------------
    nrange = getNRanges(obs_2)
    for i_rng in range(1, nrange + 1):
        plotSlice(i_rng, obs_1, obs_2, data, model, d_pdfname, resultsdir, suffix)
#-------------------------------------------------------
def plotSlice(i_rng, obs_1, obs_2, data, model, d_pdfname, resultsdir, suffix):
    plot=obs_1.frame()
    rng_cut =ROOT.RooFit.CutRange("r_{}".format(i_rng))

    data.plotOn(plot, ROOT.RooFit.Name("data"), rng_cut)
    #--------------------------
    index_style=2
    for pdfname in d_pdfname:
        color=l_color[index_style]
        line =l_line [index_style]

        line_col=ROOT.RooFit.LineColor(color)
        mark_col=ROOT.RooFit.MarkerColor(color)
        line_sty=ROOT.RooFit.LineStyle(line)
        name    =ROOT.RooFit.Name(pdfname)
        comp    =ROOT.RooFit.Components(pdfname)
        proj    =ROOT.RooFit.ProjectionRange("r_{}".format(i_rng))

        model.plotOn(plot, line_col, mark_col, line_sty, name, comp, proj) 
        index_style+=1

    txt_pval=ROOT.TPaveText(0.6, 0.83, 0.85, 0.93, "NDC")
    txt_pval.AddText("p-value=?")
    reformatTextBox(txt_pval)

    can=ROOT.TCanvas("can", "", 600, 600)
    plot.Draw()
    DrawFit(plot, obs_1, can)

    fit_pad=can.cd(1)
    d_objname=dict({"data" : "Data"}, **d_pdfname)
    leg=getLegend(plot, d_objname)
    leg.Draw()
    txt_pval.Draw()

    max_y = plot.GetMaximum()
    plot.SetMaximum(10 * max_y)
    plot.SetMinimum(0.1)

    fit_pad.SetLogy(logy)
    plotpath = "{}/fit_{}_{:02d}.png".format(resultsdir, suffix, i_rng)
    log.visible('Saving ' +  plotpath)
    can.SaveAs(plotpath)
#-------------------------------------------------------
def DrawFit(frame_ffit, obs, canvas, scale = 'log'):
    pull = frame_ffit.pullHist("data", "model", True)

    frame_pull=obs.frame()

    frame_pull.addPlotable(pull, "P")
    #------------------------------------------
    canvas.SetBit(ROOT.kMustCleanup)
    canvas.Divide(1, 2, 0.01, 0.01, 0)
    #------------------------------------------
    fit_pad=canvas.cd(1)
    fit_pad.SetPad(0, 0.22, 1, 1)

    frame_ffit.Draw()
    reformat_frame_fit(frame_ffit, obs, scale)
    #------------------------------------------
    pull_pad=canvas.cd(2)
    pull_pad.SetPad(0, 0.00, 1, 0.33)
    pull_pad.SetRightMargin(0.1)
    pull_pad.SetBottomMargin(0.35)

    frame_pull.Draw()
    reformat_frame_pull(frame_pull, obs)
    #------------------------------------------
    m1_sig, p1_sig, m2_sig, p2_sig = get_sigma_lines(obs)

    m1_sig.Draw()
    p1_sig.Draw()
    m2_sig.Draw()
    p2_sig.Draw()
#-------------------------------------------------------
def reformat_frame_fit(frame, obs, scale):
    min_x=obs.getMin()
    max_x=obs.getMax()

    xaxis=frame.GetXaxis()
    xaxis.SetLabelOffset(1.2)
    xaxis.SetRangeUser(min_x, max_x)

    max_y=frame.GetMaximum()
    if scale == 'log':
        frame.SetMinimum(0.1)
        frame.SetMaximum(100 * max_y)
    else:
        frame.SetMaximum(1.3 * max_y)
#-------------------------------------------------------
def reformat_frame_pull(frame, obs):
    min_x=obs.getMin()
    max_x=obs.getMax()
    xname=obs.GetTitle()

    xaxis_pull=frame.GetXaxis()
    yaxis_pull=frame.GetYaxis()

    yaxis_pull.SetTitle("Pull")
    yaxis_pull.SetLabelSize(0.1)
    yaxis_pull.SetTitleSize(0.1)
    yaxis_pull.SetTitleOffset(0.7)

    xaxis_pull.SetRangeUser(min_x, max_x)
    xaxis_pull.SetLabelSize(0.12)
    xaxis_pull.SetTitle(xname)
    xaxis_pull.SetTitleSize(0.12)
    xaxis_pull.SetTitleOffset(1.1)
#-------------------------------------------------------
def get_sigma_lines(obs):
    min_x=obs.getMin()
    max_x=obs.getMax()

    p2sigma = ROOT.TLine(min_x, 2, max_x, 2)
    ROOT.SetOwnership(p2sigma, False)
    p2sigma.SetLineStyle(4)
    p2sigma.SetLineColor(4)

    m2sigma = ROOT.TLine(min_x, -2, max_x, -2)
    ROOT.SetOwnership(m2sigma, False)
    m2sigma.SetLineStyle(4)
    m2sigma.SetLineColor(4)

    p1sigma = ROOT.TLine(min_x, 1, max_x, 1)
    ROOT.SetOwnership(p1sigma, False)
    p1sigma.SetLineStyle(2)
    p1sigma.SetLineColor(2)

    m1sigma = ROOT.TLine(min_x, -1, max_x, -1)
    ROOT.SetOwnership(m1sigma, False)
    m1sigma.SetLineStyle(2)
    m1sigma.SetLineColor(2)

    return (m1sigma, p1sigma, m2sigma, p2sigma)
#-------------------------------------------------------
def setValues(s_par, results):
    l_par_res = results.floatParsFinal()
    it_res    = l_par_res.createIterator()
    var_res   = it_res.Next()

    while var_res:
        name=var_res.GetName()

        var_mod=s_par.find(name)
        old_val=var_mod.getVal()
        new_val=var_res.getVal()
        var_mod.setVal(new_val)
        print("{0:20}{1:20}{2:10}{3:20}".format(name, old_val, "--->", new_val))
        var_res=it_res.Next()
#-------------------------------------------------------
def ReformatRooPlot(frame, pdf_names=["pdf"], data_names=["data"]):
    print( "utils.py::Reformating frame.")
    frame.Print("v")

    l_hist=list()
    l_pdf =list()
    l_text=list()

    for pdf_name in pdf_names:
        l_pdf.append( frame.findObject(pdf_name) )
        l_text.append( frame.findObject(pdf_name + "_paramBox") )

    for data_name in data_names:
        l_hist.append( frame.findObject(data_name) )

    for hist in l_hist:
        try:
            max_y = hist.GetHistogram().GetMaximum()
            frame.SetMaximum(1.3*max_y)
        except Exception as e:
            print("Histogram not found, maxy unchanged.")

    for text in l_text:
        try:
            text.Paint("NDC")
            text.SetLineColor(0)
            text.SetFillStyle(0)
            text.SetX1NDC(0.55)
            text.SetX2NDC(0.90)
            text.SetY1NDC(0.80)
            text.SetY2NDC(0.92)
        except Exception as e:
            print("Parameters Box not found")

    return l_text
#-------------------------------------------------------
#-------------------------------------------------------
def read_link(link, verbose=False):
    if os.path.islink(link):
        orig=link
        path=os.readlink(link)
        if not os.path.isdir(path) and not os.path.isfile(path):
            part=path
            dirpath = os.path.dirname(orig)
            path="{}/{}".format(dirpath, path)
            if verbose:
                print("{} ---> {}".format(part, path))
    else:
        return link

    if not os.path.isdir(path) and not os.path.isfile(path):
        print("Candidate {} does not exist".format(path))
        exit(1)

    return path
#-------------------------------------------------------
def reformatTextBox(text):
    text.SetLineColor(0)
    text.SetFillStyle(0)
    text.SetBorderSize(1)
#-------------------------------------------------------
def getFandCError(ntot, etot, npas, epas):
    effi = float(npas) / float(ntot)

    err2 = effi * (etot/float(ntot)) ** 2 + (1-2*effi) * (epas/float(ntot)) ** 2

    return math.sqrt(err2)
#-------------------------------------------------------
#Tree branch manipulation
#-------------------------------------------------------
def tree_has_branch(tree, pattern):
    l_branch = tree.GetListOfBranches()
    for branch in l_branch:
        branchname=branch.GetName()
        found = re.match(pattern, branchname)
        if found:
            log.info('Branch {} matched {}'.format(branchname, pattern))
            return True

    log.info('No match for {} was found'.format(pattern))
    return False
#-------------------------------------------------------
def turnOffBranches(tree, pattern):
    l_branch = tree.GetListOfBranches()
    for branch in l_branch:
        branchname = branch.GetName()
        mtch = re.match(pattern, branchname)
        if not mtch:
            continue

        log.info('Turning off ' + branchname)
        tree.SetBranchStatus(branchname, 0)
#-------------------------------------------------------
def setBranchStatusTTF(tree, cuts):
    l_branch = tree.GetListOfBranches()
    for branch in l_branch: 
        branchname = branch.GetName()
        if branchname in cuts:
            tree.SetBranchStatus(branchname, 1)
#-------------------------------------------------------
def check_tree_var(tree, variable):
    branch = tree.GetBranch(variable)
    if branch == None:
        treename = tree.GetName()
        log.error('Could not find branch {} in tree {}'.format(variable, treename))
        raise
#-------------------------------------------------------
#-------------------------------------------------------
class MergePlots(object):
    def __init__(self, l_graphs):
        super(MergePlots, self).__init__()
        self.l_graphs    = l_graphs
        self.l_pads      = list()
        self.num_xlabels = 5 if len(l_graphs) > 5 else len(l_graphs)

        self.max_y = 0
        self.min_y = 0
    #******************************************
    def Print(self):
        for graph in self.l_graphs:
            graph.Print()
    #******************************************
    def SetRange(self, max_y, min_y):
        self.max_y = max_y
        self.min_y = min_y
    #******************************************
    def GetRange(self):

        if self.max_y != 0 and self.min_y != 0:
            return [self.min_y, self.max_y]

        maximum = 0
        minimum = 0

        for graph in self.l_graphs:
            xmax = ROOT.Double()
            xmin = ROOT.Double()

            ymax = ROOT.Double()
            ymin = ROOT.Double()

            graph.ComputeRange(xmin, ymin, xmax, ymax)

            if ymax > maximum:
                maximum = ymax

            if ymin < minimum:
                minimum = ymin

        return [minimum, maximum]
    #******************************************
    def GetyAxis(self):
        Range=self.GetRange()
        yaxis = ROOT.TGaxis(0.1, 0.192, 0.1, 0.906, Range[0], Range[1], 510)
        yaxis.SetLineColor(4)

        return yaxis
    #******************************************
    def FormatGraphs(self):
        n_graphs = len(self.l_graphs)
        for i_graph in range(0, n_graphs):
            graph = self.l_graphs[i_graph]

            x_axis = graph.GetXaxis()
            y_axis = graph.GetYaxis()

            x_axis.SetTickLength(0.00)
            nbins = x_axis.GetNbins()
            x_axis.SetBinLabel(nbins/2, graph.GetTitle() )
            x_axis.LabelsOption("v")
            graph.SetTitle("")

            graph.GetXaxis().SetLabelSize(0.026 * math.pow(n_graphs, 1) )

            if i_graph != 0:
                graph.GetYaxis().SetLabelColor(0)
                graph.GetYaxis().SetAxisColor(0)
            else:
                graph.GetYaxis().SetLabelColor(0)
                graph.GetYaxis().SetAxisColor(4)

            graph.GetYaxis().SetTitle("")
    #******************************************
    def GetPads(self):
        if len(self.l_pads) > 0:
            return

        pad_width = 0.8/len(self.l_graphs)
        xmin = 0.1

        npads = len(self.l_graphs)
        for i_pad in range(0, npads):
            xlo = xmin + (i_pad + 0.) * pad_width
            xhi = xmin + (i_pad + 1.) * pad_width
            ylo = 0.05
            yhi = 1

            pad = ROOT.TPad("pad_%d" % i_pad, "", xlo, ylo, xhi, yhi)
            pad.SetNumber(i_pad)
            pad.SetFrameLineColor(0)
            pad.SetBottomMargin(0.15)

            self.l_pads.append(pad)
    #******************************************
    def SetYaxisTitle(self, title):
        self.YTitle = title
    #******************************************
    def Plot(self, file_name):
        can_mrg = ROOT.TCanvas("can_mrg", "", 800, 600)
        can_mrg.SetLeftMargin(0)
        self.GetPads()

        n_graphs = len(self.l_graphs)

        l_range = self.GetRange()

        if len(self.l_pads) != len(self.l_graphs):
            print( "Number of pads %d and graphs %s, are different." % ( len(self.l_pads), len(self.l_graphs) ) )
            exit(1)

        self.FormatGraphs()
        for i_graph, graph in enumerate(self.l_graphs):
            # graph.GetYaxis().SetAxisMinimum(l_range[0])
            # graph.GetYaxis().SetAxisMaximum(l_range[1])
            graph.GetYaxis().SetLimits( l_range[0], l_range[1] )

            pad = self.l_pads[i_graph]
            can_mrg.cd()

            pad.Draw()
            pad.cd()
            graph.Draw("AC")

            if i_graph != 0:
                pad.SetLeftMargin(0)

            if i_graph != n_graphs -1:
                pad.SetRightMargin(0)

        can_mrg.cd()

        yaxis = self.GetyAxis()
        yaxis.SetTitle(self.YTitle)
        yaxis.SetTitleOffset(1)
        yaxis.Draw()

        can_mrg.SaveAs("%s.pdf" % file_name)

        ofile=ROOT.TFile("%s.root" % file_name,"recreate")
        can_mrg.Write()
        ofile.Close()
#-------------------------------------------------------
def IsHist(hist):
    is_TH1F = hist.InheritsFrom(ROOT.TH1F.Class())
    is_TH1D = hist.InheritsFrom(ROOT.TH1D.Class())

    return is_TH1F or is_TH1D
#-------------------------------------------------------
def getRatio(l_hist):
    if len(l_hist) < 2:
        log.error('Ratios cannot use fewer than 2 histograms.')
        print(l_hist)
        raise

    h_den=l_hist[0]
    l_h_num=l_hist[1:]
    l_h_rat=[]

    denname=h_den.GetName()
    for h_num in l_h_num:
        numname=h_num.GetName()
        ratname='{}_over{}'.format(numname, denname)
        h_rat=h_num.Clone(ratname)
        h_rat.Reset('ICES')
        h_rat.Divide(h_num, h_den)

        l_h_rat.append(h_rat)

    if len(l_h_num) == 1:
        yname = '{}/{}'.format(l_h_num[0].GetTitle(), h_den.GetTitle())
    else:
        yname = '{}/{}'.format(                  'X', h_den.GetTitle())

    return (l_h_rat, yname)
#--------------------------------------------------
#Plotting
#--------------------------------------------------
def fill_hist(hist, arr_val = None, arr_wgt = None, instance=0):
    utnr.check_none(arr_val)
    utnr.check_none(arr_wgt)
    utnr.check_numeric(instance)

    utnr.check_array_shape(arr_val, arr_wgt)
    utnr.check_array_dim(arr_val, 1)
    utnr.check_array_dim(arr_wgt, 1)

    for val, wgt in zip(arr_val, arr_wgt):
        val = utnr.get_instance(val, instance)
        wgt = utnr.get_instance(wgt, instance)

        utnr.check_numeric(val)
        utnr.check_numeric(wgt)

        hist.Fill(val, wgt)

    return hist
#--------------------------------------------------
def plotHistPads(l_hist, tup, path, d_opt={}):
    if   tup== (2, 1):
        xsize=1500
        ysize= 600
    elif tup== (3, 1):
        xsize=1800
        ysize= 600
    elif tup== (2, 2):
        xsize=1000
        ysize=1000
    elif tup== (3, 2):
        xsize=1500
        ysize=1000
    else:
        log.error('Unsupported pad splitting')
        raise

    can=ROOT.TCanvas('can', '', xsize, ysize)
    can.Divide(tup[0], tup[1])
    npad = tup[0] * tup[1]

    for ipad in range(1, npad + 1):
        try:
            hist=l_hist[ipad - 1]
        except:
            log.info('Drew {} histograms'.format(ipad - 1))
            break

        can.cd(ipad)

        try:
            hist.Draw(d_opt['sty'])
        except:
            hist.Draw()

    log.visible('Saving to ' + path)
    can.SaveAs(path)
#--------------------------------------------------
def plot_arrays(d_array, plotpath, nbins, min_x = 0, max_x = 0, d_opt={}):
    l_hist=[]
    for key, arr_val in d_array.items():
        hist=arr_to_hist('h_' + key, key, nbins, min_x, max_x, arr_val)
        l_hist.append(hist)

    plotHistograms(l_hist, plotpath, d_opt=d_opt)
#--------------------------------------------------
def plot_histograms(l_hist, outpath, d_opt = {}):
    log.visible(f'Saving to: {outpath}')
    plotHistograms(l_hist, outpath, d_opt = d_opt)
#--------------------------------------------------
def plotHistograms(l_hist, outpath, d_opt = {}):
    for hist in l_hist:
        if not hist.InheritsFrom('TH1'):
            log.error('Object is introduced is not a histogram')
            print(hist)
            raise

    if 'obj' in d_opt:
        l_obj=d_opt['obj']
        if len(l_obj) != len(l_hist):
            log.error('Objects introduced do not match histograms')
            raise

    for i_hist, hist in enumerate(l_hist):
        color=utnr.get_elm(l_color , i_hist)
        smark=utnr.get_elm(l_marker, i_hist)

        hist.SetMarkerColor(color)
        hist.SetLineColor(color)
        hist.SetMarkerStyle(smark)
        hist.SetMarkerSize(2.5)

        if (i_hist == len(l_hist) - 1) and ('last_color' in d_opt):
            color=d_opt['last_color']
            hist.SetMarkerColor(color)
            hist.SetLineColor(color)

        if 'normalize'  in d_opt and d_opt['normalize']:
            area = hist.Integral()
            if not math.isclose(area, 0.):
                hist.Scale(1./area)

        if 'zeroerrors' in d_opt and d_opt['zeroerrors']:
            zeroErrors(hist, clone=False)

        if 'leg_stats'  in d_opt and d_opt['leg_stats']:
            title = hist.GetTitle()
            area  = get_hist_area(hist) 
            title = '{}, {:.5e}'.format(title, area)
            hist.SetTitle(title)

    
    if "xrange" in d_opt:
        xmin, xmax = d_opt["xrange"]
    else:
        xaxis= l_hist[0].GetXaxis()
        xmin = xaxis.GetXmin()
        xmax = xaxis.GetXmax()

    if 'yrange' in d_opt:
        ymin, ymax = d_opt['yrange']
    else:
        ymax = -sys.float_info.max
        ymin = +sys.float_info.max
        for hist in l_hist:
            yymax = hist.GetYaxis().GetXmax()
            yymin = hist.GetYaxis().GetXmin()

            ymax = yymax if yymax > ymax else ymax
            ymin = yymin if yymin < ymin else ymin

        ymax = 1.05 * ymax
        ymin = 0.95 * ymin if 'miny' not in d_opt else d_opt['miny']

    for hist in l_hist:
        hist.GetYaxis().SetRangeUser(ymin, ymax)

    xname=''
    if "xname" in d_opt:
        xname = d_opt["xname"]

    yname=''
    if "yname" in d_opt:
        yname = d_opt["yname"]

    if 'normalize' in d_opt and d_opt['normalize']:
        yname = 'Normalized'

    if 'width' in d_opt:
        width=d_opt['width']
    else:
        width=600

    if 'height' in d_opt:
        height=d_opt['height']
    else:
        height=600

    ran=ROOT.TRandom3(0)
    ranval=ran.Integer(100000000)
    c_hist = ROOT.TCanvas(f'c_hist_{ranval}', '', width, height)

    l_sty=['ET0'] * len(l_hist)
    if 'sty' in d_opt and d_opt['sty'] is not None:
        l_sty = d_opt['sty']
        if  not isinstance(l_sty, list): 
            log.error('Unsupported value for sty:')
            print(l_sty)
            raise
        elif len(l_sty) != len(l_hist):
            log.error('Wrong size of list of styles:')
            log.error('{0:<20}{1:<20}'.format('Needed'  , len(l_hist)))
            log.error('{0:<20}{1:<20}'.format('Provided',  len(l_sty)))
            raise

    if   'ratio' in d_opt and d_opt['ratio']:
        c_hist.Divide(1, 2, 0.01, 0.01, 0)

        pad_1=c_hist.cd(1)
        pad_1.SetPad(0, 0.22, 1, 1)

        pad_2=c_hist.cd(2)
        pad_2.SetPad(0, 0.00, 1, 0.33)
        pad_2.SetRightMargin(0.08)
        pad_2.SetBottomMargin(0.3)

        l_h_rat, yname_r = getRatio(l_hist)

        if 'ymaxr' in d_opt and 'yminr' in d_opt:
            yminr=d_opt['yminr']
            ymaxr=d_opt['ymaxr']
            for h_rat in l_h_rat:
                h_rat.GetYaxis().SetRangeUser(yminr, ymaxr)

        xaxis_r = l_h_rat[0].GetXaxis()
        yaxis_r = l_h_rat[0].GetYaxis()

        xaxis_r.SetLabelSize(0.12)
        xaxis_r.SetTitle(xname)
        xaxis_r.SetTitleSize(0.12)
        xaxis_r.SetTitleOffset(1.1)

        yaxis_r.SetLabelSize(0.08)
        yaxis_r.SetTitle(yname_r)
        yaxis_r.SetTitleSize(0.10)
        yaxis_r.SetTitleOffset(0.6)

        min_x = xaxis_r.GetXmin()
        max_x = xaxis_r.GetXmax()

        line=ROOT.TLine(min_x, 1, max_x, 1)
        line.SetLineColor(1)
        line.SetLineWidth(2)
        line.SetLineStyle(6)

        hasline=False
        for h_rat in l_h_rat:
            if 'ymax_r' in d_opt:
                ymax_r = d_opt['ymax_r']
                h_rat.SetMaximum(ymax_r)

            if 'ymin_r' in d_opt:
                ymin_r = d_opt['ymin_r']
                h_rat.SetMinimum(ymin_r)

            h_rat.Draw('same')
            if not hasline:
                line.Draw()
                hasline=True
    elif 'extra_pad' in d_opt:
        obj=d_opt['extra_pad']
        c_hist.Divide(2, 1)
        pad_1=c_hist.cd(1)
        pad_2=c_hist.cd(2)
        obj.Draw()
    else:
        pad_1=c_hist

    pad_1.cd()

    for hist, sty in zip(l_hist, l_sty):
        hist.GetXaxis().SetTitle(xname)
        hist.GetYaxis().SetTitle(yname)

        if 'draw_all'   in d_opt and d_opt['draw_all']:
            nbins = hist.GetNbinsX()
            hist.GetXaxis().SetRangeUser(-1, nbins + 1)
        else:
            hist.GetXaxis().SetRangeUser(xmin, xmax)

        hist.Draw(f'same {sty}')

    if 'band' in d_opt:
        yval, yerr, label = d_opt['band']
        ymin = yval - yerr
        ymax = yval + yerr

        band=get_band(xmin, xmax, ymin, ymax)
        band.SetTitle(label)
        band.Draw('same F')

    axisobj=l_hist[0]
    if   'ratio'     in d_opt and d_opt['ratio']:
        xaxis=axisobj.GetXaxis()
        xaxis.SetRangeUser(xmin, xmax)
        xaxis.SetLabelOffset(1.2)
        yaxis=axisobj.GetYaxis()

    pad_1.cd()

    l_text=[]
    if 'text' in d_opt:
        text, loc=d_opt['text']
        l_text = [text]

    if 'l_text' in d_opt:
        l_text, loc=d_opt['l_text']

    for i_text, text in enumerate(l_text):
        txt = get_text(loc, i_text)

        txt.AddText(text)
        reformatTextBox(txt)
        ROOT.SetOwnership(txt, False)
        txt.SetBit(ROOT.kCanDelete)
        txt.Draw()

    leg=None
    #xmin, ymin, xmax, ymax
    if True:
        if   'legend' not in d_opt or d_opt['legend'] is None:
            pass
        #Automatic
        elif d_opt['legend'] == 'auto':
            leg=pad_1.BuildLegend()
        #Upper right
        elif d_opt['legend'] == +1:
            leg=pad_1.BuildLegend(0.6, 0.65, 0.9, 0.93)
        elif d_opt['legend'] == +0.1:
            leg=pad_1.BuildLegend(0.6, 0.80, 0.9, 0.93)
        elif d_opt['legend'] == +10:
            leg=pad_1.BuildLegend(0.4, 0.65, 0.9, 0.93)
        #Lower right
        elif d_opt['legend'] == -1:
            leg=pad_1.BuildLegend(0.6, 0.20, 0.9, 0.50)
        elif d_opt['legend'] == -10:
            leg=pad_1.BuildLegend(0.4, 0.20, 0.9, 0.50)
        #Upper left
        elif d_opt['legend'] == +2:
            leg=pad_1.BuildLegend(0.2, 0.50, 0.5, 0.90)
        elif d_opt['legend'] == +0.2:
            leg=pad_1.BuildLegend(0.2, 0.70, 0.5, 0.90)
        elif d_opt['legend'] == +20:
            leg=pad_1.BuildLegend(0.2, 0.50, 0.8, 0.90)
        elif d_opt['legend'] == +30:
            leg=pad_1.BuildLegend(0.2, 0.50, 0.6, 0.90)
        elif d_opt['legend'] == -2:
            leg=pad_1.BuildLegend(0.2, 0.20, 0.5, 0.50)
        else:
            log.error('Invalid legend entry: {}'.format(d_opt['legend']))
            raise

    if 'leg_ncol' in d_opt:
        ncol=d_opt['leg_ncol']
        leg.SetNColumns(ncol)

    if 'leg_head' in d_opt and leg is not None:
        leg.SetHeader(d_opt['leg_head'])

    if leg is not None:
        leg.Draw()

    if 'hline' in d_opt and d_opt['hline'] is not None:
        try:
            yval, color = d_opt['hline']
        except TypeError:
            yval        = d_opt['hline']
            color       = 1
        except:
            log.error('Cannot extract line position and color')
            raise

        line = ROOT.TLine(xmin, yval, xmax, yval)
        line.SetLineStyle(2)
        line.SetLineWidth(2)
        line.SetLineColor(color)
        line.Draw()

    if 'vline' in d_opt:
        xval, color = d_opt['vline']
        line = ROOT.TLine(xval, ymin, xval, ymax)
        line.SetLineColor(color)
        line.SetLineStyle(2)
        line.SetLineWidth(2)
        line.Draw()

    if 'logy'  in d_opt and d_opt['logy']:
        pad_1.SetLogy()

    if 'ygrid' in d_opt and d_opt['ygrid']:
        pad_1.SetGridy()

    if 'xgrid' in d_opt and d_opt['xgrid']:
        pad_1.SetGridx()

    ReformatCanvas(pad_1) 

    dirname=os.path.dirname(outpath)
    if not os.path.isdir(dirname):
        log.visible('Directory {} not found, making it.'.format(dirname))
        os.makedirs(dirname, exist_ok=True)

    c_hist.SaveAs(outpath)
    if 'save_root' in d_opt and d_opt['save_root']:
        root_out = outpath.split('.')[0] + '.root'
        c_hist.SaveAs(root_out)
#--------------------------------------------------
def get_text(loc, i_dy = 0):
    dy = 0.05
    #Upper left
    if   loc == 0.1:
        txt=ROOT.TPaveText(0.20, 0.87 - i_dy * dy, 0.40, 0.93 - i_dy * dy, "NDC")
    elif loc == 1:
        txt=ROOT.TPaveText(0.15, 0.87 - i_dy * dy, 0.50, 0.93 - i_dy * dy, "NDC")
    elif loc == 10:
        txt=ROOT.TPaveText(0.15, 0.87 - i_dy * dy, 0.70, 0.93 - i_dy * dy, "NDC")
    elif loc == 100:
        txt=ROOT.TPaveText(0.16, 0.85 - i_dy * dy, 0.95, 0.94 - i_dy * dy, "NDC")
    #Upper right
    elif loc == 2:
        txt=ROOT.TPaveText(0.60, 0.87 - i_dy * dy, 0.85, 0.93 - i_dy * dy, "NDC")
    elif loc == 20:
        txt=ROOT.TPaveText(0.50, 0.87 - i_dy * dy, 0.85, 0.93 - i_dy * dy, "NDC")
    elif loc == 30:
        txt=ROOT.TPaveText(0.17, 0.17 - i_dy * dy, 0.72, 0.23 - i_dy * dy, "NDC")
    #Lower left 
    elif loc == -1:
        txt=ROOT.TPaveText(0.17, 0.19 + i_dy * dy, 0.52, 0.25 + i_dy * dy, "NDC")
    elif loc == -10:
        txt=ROOT.TPaveText(0.17, 0.19 + i_dy * dy, 0.70, 0.30 + i_dy * dy, "NDC")
    else:
        log.error('Unsupported location {}'.format(loc))
        raise

    return txt
#-------------------------------------------------------
def ReformatCanvas(Pad, left_margin=-1):
    l_rngobj  = []
    l_hist    = []
    l_roohist = [] 
    l_legd    = []
    multigraph = ROOT.TMultiGraph()

    primitives=Pad.GetListOfPrimitives()
    for primitive in primitives:
        if primitive.InheritsFrom('RooHist'):
            l_roohist.append(primitive)
            l_rngobj.append(primitive)

        if primitive.InheritsFrom('TGraph'):
            l_rngobj.append(primitive)

        if primitive.InheritsFrom('TH1'):
            primitive.SetStats(False);
            l_hist.append(primitive)
            l_rngobj.append(primitive)

        if primitive.InheritsFrom('TLegend'):
            l_legd.append(primitive)

        if primitive.InheritsFrom('TMultigraph'):
            multigraph=primitive
            l_rngobj.append(primitive)

    max_y=0
    min_y=1e20
    for hist in l_hist:
        tmp=hist.GetMaximum()
        if max_y < tmp:
            max_y = tmp 

        tmp=hist.GetMinimum(0)
        if min_y > tmp: 
            min_y = tmp 

    for hist in l_roohist:
        if max_y < hist.GetMaximum():
            max_y = hist.GetMaximum()

        if min_y > hist.GetMinimum() and hist.GetMinimum() > 0:
            min_y = hist.GetMinimum()

    if multigraph.GetListOfGraphs():
        for graph in multigraph.GetListOfGraphs():
            ymax = graph.GetYaxis().GetXmax()
            if max_y < ymax:
                max_y = ymax

            ymin = graph.GetYaxis().GetXmin()
            if min_y > ymin and ymin > 0:
                min_y = ymin

    is_log = Pad.GetLogy()
    if is_log:
        scale_max = 10**1.9 * max_y
        scale_min = 10**0.5 * min_y
        log.debug('Using optimized log range ({:.2e},{:.2e})'.format(scale_min, scale_max))
    else:
        scale_max = 1.5 * max_y
        scale_min = 0 
        log.debug('Using optimized linear range ({:.2e},{:.2e})'.format(scale_min, scale_max))

    log.debug("New scale {:.3e} for maximum {:.3e}".format(scale_max, max_y) )
    log.debug("New scale {:.3e} for minimum {:.3e}".format(scale_min, min_y) )

    for legend in l_legd:
        legend.SetLineWidth(0)
        legend.SetFillStyle(0)

    Pad.SetTopMargin(0.05)
    Pad.SetRightMargin(0.08)
    Pad.SetBottomMargin(0.16)
    if left_margin != -1:
        Pad.SetLeftMargin(left_margin)

    Pad.Update()
#-------------------------------------------------------
def Reformat2D(canvas):
    canvas.SetRightMargin(0.15)
    canvas.SetTopMargin(0.05)

    canvas.SetLeftMargin(0.20)
    canvas.SetBottomMargin(0.20)

    #canvas.SetLeftMargin(0.23)
    #canvas.SetBottomMargin(0.23)

    v_hist=ROOT.std.vector("TH2F*")()
    primitives = canvas.GetListOfPrimitives()
    for primitive in primitives:
        if primitive.InheritsFrom(ROOT.TH2.Class()) and primitive.GetEntries() > 0:
            v_hist.push_back(primitive)

    canvas.Update()
    for hist in v_hist:
        palette = hist.GetListOfFunctions().FindObject("palette")
        palette.SetX1NDC(0.86)
        palette.SetX2NDC(0.90)
        palette.SetY1NDC(0.25)
        palette.SetY2NDC(0.95)
#-------------------------------------------------------
def ATLASLabel(x, y, text, color, canvas, extra_txt=""):
    l=ROOT.TLatex()
    l.SetNDC()
    l.SetTextFont(72)
    l.SetTextColor(color)

    delx = 0.115*696*canvas.GetWh()/( 472*canvas.GetWw() )
    dely = 0.0001 * canvas.GetWh()

    l.DrawLatex(x,y,"ATLAS")

    p=ROOT.TLatex()
    p.SetNDC()
    p.SetTextFont(42)
    p.SetTextColor(color)
    p.DrawLatex(x+delx,y,text)
    p.DrawLatex(x,y-1.*dely, extra_txt)
    p.DrawLatex(x,y-2.*dely, CME)
#-------------------------------------------------------
def LHCbLabel(x, y, text, color, canvas, extra_txt=""):
    l=ROOT.TLatex()
    l.SetNDC()
    l.SetTextFont(72)
    l.SetTextColor(color)

    delx = 0.1*700*canvas.GetWh()/( 472*canvas.GetWw() )
    dely = 0.0001 * canvas.GetWh()

    l.DrawLatex(x,y,"LHCb")

    p=ROOT.TLatex()
    p.SetNDC()
    p.SetTextFont(42)
    p.SetTextColor(color)
    p.DrawLatex(x+delx,y,text)
    p.DrawLatex(x,y-1.*dely, CME)
    p.DrawLatex(x,y-2.*dely, extra_txt)
#-------------------------------------------------------
def get_band(xmin, xmax, ymin, ymax):
    npt=10
    arr_x=np.linspace(xmin, xmax, npt)
    
    g=ROOT.TGraph(2 * npt);
    for i_pt in range(0, npt):
        g.SetPoint( i_pt        , arr_x[i_pt], ymax)
        g.SetPoint( 2*npt-1-i_pt, arr_x[i_pt], ymin) 
    
    g.SetFillColor(ROOT.kGreen)
    g.SetMarkerSize(0)
    g.SetLineColor(ROOT.kGray)
    g.SetFillStyle(3013)

    return g
#-------------------------------------------------------
def getLegend(frame, d_objname):
    nobjs=int(frame.numItems())

    l_obj=[]
    l_lab=[]
    l_opt=[]

    for iobj in range(0, nobjs):
        obj=frame.getObject(iobj)
        name=obj.GetName()
        is_dat=obj.InheritsFrom( "RooHist") 
        is_pdf=obj.InheritsFrom("RooCurve")
        is_txt=obj.InheritsFrom("TPaveText")
        if is_dat or is_pdf: 
            try:
                label=d_objname[name]
            except:
                log.error("Cannot find object {} in dictionary".format(name))
                print(d_objname)
                raise

            l_lab.append(label)
            l_obj.append(obj)
            if is_dat:
                l_opt.append("P")
            else:
                l_opt.append("l")
        elif is_txt:
            reformat_params(obj)
            params = obj
            pass
        else:
            log.warning("Found object of type {} in frame, skipping".format(type(obj)) )
            continue

    legend=createLegend(leg_xmin, leg_xmax, leg_ymin, leg_ymax, l_lab, l_obj, l_opt)

    return legend 
#-------------------------------------------------------
def reformat_params(txt):
    txt.SetLineColor(0)

    d_var = {}

    d_var['ncmb'] = 'N_{comb}'
    d_var['nsig'] = 'N_{sign}' 
    d_var['pdf_reso_comb_lb_mm'] = '#lambda'
    d_var['pdf_reso_sign_mass_fb_mm'] = 'f_{b}' 
    d_var['pdf_reso_sign_mass_lb_mm'] = '#lambda' 
    d_var['pdf_reso_sign_mass_mu_mm'] = '#mu' 
    d_var['pdf_reso_sign_mass_sg_mm'] = '#sigma' 

    l_line = txt.GetListOfLines()
    for line in l_line:
        title = line.GetTitle()
        var = title.split('=') [0].replace(' ', '')
        val = title.split('=') [1]

        var = d_var[var]

        title = '{} = {:>}'.format(var, val)
        line.SetTitle(title)
#-------------------------------------------------------
def createLegend(x1, x2, y1, y2, l_label, l_object, l_opt, header = ""):
    legend = ROOT.TLegend(x1, y1, x2, y2)
    legend.SetHeader(header)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    for label, objct, opt in zip(l_label, l_object, l_opt):
        try:
            legend.AddEntry( objct, label, opt)
        except Exception as e:
            print("Cannot add legend for %d" % label)

    return legend
#-------------------------------------------------------
def histCategories(l_category, name, title, color, title_y = ""):
    nbins=1
    minx=0
    maxx=0
    miny=0
    tup =max(l_category, key = lambda tup : tup[1])
    maxy=1.3 * tup[1]

    hist=GetHistogram(name, title, color, nbins, minx, maxx, miny, maxy, 20, "", title_y)

    for name, value in l_category:
        hist.Fill(name, value)

    nbins=len(l_category)
    hist.GetXaxis().SetRangeUser(0, nbins)

    for ibin in range(1, nbins + 1):
        hist.SetBinError(ibin, 0)

    return hist
#-------------------------------------------------------
def GetHistogram(name, title, color, nbins, minx, maxx, miny=0, maxy=0, style = 20, title_x="", title_y = ""):
    bin_width = float( (maxx-minx)/nbins )

    hist = ROOT.TH1F(name, title, nbins, minx, maxx)
    hist.SetLineColor(color)
    hist.SetMarkerColor(color)
    hist.SetMarkerStyle(style)
    hist.GetXaxis().SetTitle(title_x)
    hist.GetYaxis().SetTitle(title_y)
    hist.Sumw2(True)

    if maxy != 0:
        hist.GetYaxis().SetRangeUser(miny, maxy)

    return hist
#-------------------------------------------------------
def cloneHistogram(name, title, color, h_org, miny=0, maxy=0, style = 20, title_x="", title_y = ""):
    hist=h_org.Clone(name)
    hist.Reset("ICES")

    hist.SetTitle(title)
    hist.SetLineColor(color)
    hist.SetMarkerColor(color)
    hist.SetMarkerStyle(style)

    hist.GetXaxis().SetTitle(title_x)
    hist.GetYaxis().SetTitle(title_y)
    hist.Sumw2(True)

    if maxy != 0:
        hist.GetYaxis().SetRangeUser(miny, maxy)

    return hist
#-------------------------------------------------------
def GetHistogram2D(name, title, nbins_x, min_x, max_x, nbins_y, min_y, max_y, title_x, title_y):
    hist = ROOT.TH2F(name, title, nbins_x, min_x, max_x, nbins_y, min_y, max_y)
    hist.GetXaxis().SetTitle(title_x)
    hist.GetYaxis().SetTitle(title_y)

    return hist
#-------------------------------------------------------
def SaveHistograms(l_histograms, name, kind="", process="", l_opts=[], normalize=False, log=False, legend=0, ratio=False, d_obj={}, root=False, pdf=False, d_opt={}):
    nhist=len(l_histograms) 
    if nhist == 0:
        log.info("No histograms were found")
        raise
    
    if len(l_opts) == 0:
        l_opts = [""] + (nhist - 1) * ["same"]

    if not ratio:
        can=ROOT.TCanvas("can_%s" % name , "", 600, 600)
    else:
        can=ROOT.TCanvas("can_%s" % name , "", 600, 800)

    counter=0
    h_stack=ROOT.THStack("stack_" + name, "")
    for histogram, opt in zip(l_histograms, l_opts):
        color=l_color[counter]

        histogram.SetMarkerColor(color)
        histogram.SetLineColor(color)
        if normalize:
            histogram.Scale(1./histogram.Integral())

        h_stack.Add(histogram)

        counter+=1


    h_stack.Draw("nostack")

    xaxis=h_stack.GetXaxis()
    yaxis=h_stack.GetYaxis()

    if "xrange" in d_opt:
        xmin, xmax = d_opt["xrange"]
        xaxis.SetRangeUser(xmin, xmax)

    if "xname" in d_opt:
        xname = d_opt["xname"]
        xaxis.SetTitle(xname)

    if "yname" in d_opt:
        yname = d_opt["yname"]
        yaxis.SetTitle(yname)

    can.Modified()

    if log:
        can.SetLogy()

    if legend == 1:
        leg=can.BuildLegend(0.6, 0.65, 0.95, 0.93)
    elif legend == -1:
        leg=can.BuildLegend(0.6, 0.20, 0.95, 0.50)

    counter=0
    maxy=h_stack.GetMaximum()
    miny=h_stack.GetMinimum()
    l_tmp=[]
    for key in d_obj:
        color=l_color[counter]
        style=l_line [counter]
        if "line" in key: 
            val=d_obj[key]

            line=ROOT.TLine(val, miny, val, maxy)
            line.SetLineStyle(2)
            line.SetLineColor(color)
            line.SetLineStyle(style)
            line.Draw()
            l_tmp.append(line)

        counter+=1

    if ratio:
        reference_name = l_histograms[0].GetName()
        ROOT.Info("SaveHistograms", "Using reference histogram: %s" % reference_name)
        can = GetRatios(can, reference_name)

        upper_pad=can.cd(1)

        if log:
            upper_pad.SetLogy()

        if   legend == +1:
            leg=upper_pad.BuildLegend(0.6, 0.65, 0.9, 0.93)
        elif legend == -1:
            leg=upper_pad.BuildLegend(0.6, 0.20, 0.9, 0.50)

        ReformatCanvas(upper_pad)
        LHCbLabel(0.20, 0.86, kind, 1, upper_pad, process)

        if 'ygrid' in d_opt and d_opt['ygrid']:
            upper_pad.SetGridy()

        if 'xgrid' in d_opt and d_opt['xgrid']:
            upper_pad.SetGridx()


        lower_pad=can.cd(2)
    else:
        ReformatCanvas(can)
        LHCbLabel(0.20, 0.86, kind, 1, can, process)

        if 'ygrid' in d_opt and d_opt['ygrid']:
            can.SetGridy()

        if 'xgrid' in d_opt and d_opt['xgrid']:
            can.SetGridx()

    if 'leg_head' in d_opt:
        header = d_opt['leg_head']
        leg.SetHeader(header, '')

    can.SaveAs("%s.png" % name)
    if pdf:
        can.SaveAs("%s.pdf" % name)

    if root:
        ofile=ROOT.TFile("%s.root" % name , "recreate")
        for hist in l_histograms:
            hist.Write()
        ofile.Close()
#-------------------------------------------------------
def GetRatios(canvas, reference_hist, numerator_hist = "", logy=False, can_width=800, can_height=600):
    l_primitive = canvas.GetListOfPrimitives()
    h_ref=None

    l_h_orig=[]
    for primitive in l_primitive:
        if primitive.InheritsFrom("TH1"): 
            l_h_orig.append(primitive)
            if primitive.GetName() == reference_hist:
                h_ref = primitive

        if primitive.InheritsFrom("THStack"):
            l_h_orig=primitive.GetHists()
            if l_h_orig.Contains(reference_hist):
                h_ref=l_h_orig.FindObject(reference_hist)
                break

    if h_ref is None:
        ROOT.Info("GetRatios", "Reference histogram {} not found in ".format(reference_hist))
        l_primitive.Print()
        exit(1)

    MIN_X=h_ref.GetXaxis().GetXmin()
    MAX_X=h_ref.GetXaxis().GetXmax()

    try:
        ROOT.Info("GetRatios", "Using reference %s " % h_ref.GetName())
    except ReferenceError:
        ROOT.Error("GetRatios", "Could not retrieve reference histogram %s" % h_ref.GetName())
        exit(1)

    l_h_ratio = [] 
    l_h_nume  = [] 
    l_h_main  = []
    for h_orig in l_h_orig:
        #--------------------------------
        h_main = h_orig.Clone( "ratio_%s" % h_orig.GetName() )
        ROOT.SetOwnership(h_main, False)
        l_h_main.append(h_main)
        #--------------------------------
        hist_name = h_orig.GetName()
        if reference_hist == hist_name:
            continue

        l_h_nume.append(h_main)

        if numerator_hist != "" and numerator_hist != hist_name:
            continue
        #--------------------------------
        h_ratio = h_main.Clone()
        ROOT.SetOwnership(h_ratio, False)
        h_ratio.SetName( reference_hist + "_" + h_main.GetName() )

        if not CheckConsistency(h_main, h_ref):
            ROOT.Info("GetRatios", "Histograms with different binning")
            h_main.Print("all")
            h_ref.Print("all")
            continue

        h_ratio.Divide(h_main, h_ref)

        ROOT.Info("GetRatios", "Getting {}/{} = {}".format(h_main.GetName(), h_ref.GetName(), h_ratio.GetName()))
        #--------------------------------
        h_ratio.SetStats(False)
        h_ratio.SetTitle("")
        #--------------------------------
        h_ratio.GetXaxis().SetTitle("")

        h_ratio.GetYaxis().SetTitle( "%s/%s" % (h_main.GetTitle(), h_ref.GetTitle()) )
        h_ratio.GetYaxis().SetTitleOffset(0.51)
        h_ratio.GetYaxis().SetTitleSize(0.08)
        #--------------------------------
        l_h_ratio.append(h_ratio)
        #--------------------------------

    can_ratio = ROOT.TCanvas("can_rat_%s" % (reference_hist), "", can_width, can_height)
    can_ratio.SetBit(ROOT.kMustCleanup)
    can_ratio.Divide(1, 2, 0.01, 0.01, 0)

    pad_1=can_ratio.cd(1)
    ROOT.gPad.SetPad(0, 0.33, 1, 1)
    for h_main in l_h_main:
        h_main.Draw("same")

    if logy:
        pad_1.SetLogy()

    can_ratio.cd(2)
    ROOT.gPad.SetGridx()
    ROOT.gPad.SetGridy()
    ROOT.gPad.SetPad(0, 0.03, 1, 0.33)
    ROOT.gPad.SetRightMargin(0.08)

    for h_nume, h_ratio in zip(l_h_nume, l_h_ratio):
        y_axis=h_ratio.GetYaxis()
        y_max =h_ratio.GetMaximum()
        y_min =h_ratio.GetMinimum()

        if y_max > 1.5:
            h_ratio.SetMaximum(1.5)

        if y_min < 0.5:
            h_ratio.SetMinimum(0.5)

        if MAX_RAT != -1 or MIN_RAT != -1:
            h_ratio.GetYaxis().SetRangeUser(MIN_RAT, MAX_RAT)
            ROOT.Info('GetRatios', "Setting ratio histogram y axis to: {} --> {}".format(MIN_RAT, MAX_RAT))

        h_ratio.SetMarkerSize(0.3)
        if len(l_h_ratio) == 1:
            h_ratio.SetMarkerColor(4)
            h_ratio.SetLineColor(4)
        else:
            color=h_nume.GetLineColor()
            h_ratio.SetMarkerColor(color)
            h_ratio.SetLineColor(color)
            h_ratio.GetYaxis().SetTitle("X/%s" % h_ref.GetTitle() )

        h_ratio.Draw("same")

    line=ROOT.TLine(MIN_X, 1, MAX_X, 1)
    ROOT.SetOwnership(line, False)
    line.SetLineColor(2)

    line.Draw("same")

    return can_ratio
#-------------------------------------------------------
def saveGraphs(l_graph, l_opt, name, log=False, legend=0, ratio=False, setGrid=False, xtitle="", ytitle="", leg_title="", pdf=False):
    can_gr=ROOT.TCanvas(name, "", 600, 600)

    mg=ROOT.TMultiGraph()
    for graph, opt in zip(l_graph, l_opt):
        graph_clone=graph.Clone()
        mg.Add(graph_clone, opt)
    mg.GetHistogram().GetXaxis().SetTitle(xtitle)
    mg.GetHistogram().GetYaxis().SetTitle(ytitle)

    if MIN_GRP != -1 or MAX_GRP != -1:
        ROOT.Info("utils::saveGraphs", "Setting graphs y axis to: {} --> {}".format(MIN_GRP, MAX_GRP))
        mg.GetHistogram().GetYaxis().SetRangeUser(MIN_GRP, MAX_GRP)

    pad_up=None
    if ratio:
        can_gr.Divide(1, 2)
        pad_up=can_gr.cd(1)
        pad_up.SetPad(0, 0.33, 1, 1)
    else:
        pad_up=can_gr.cd(0)

    mg.Draw("a")

    if setGrid:
        pad_up.SetGridx()
        pad_up.SetGridy()

    if legend == 4:
        leg=pad_up.BuildLegend(0.6, 0.20, 0.9, 0.50, leg_title)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)

    if log:
        pad_up.SetLogy()

    if ratio:
        pad_dn=can_gr.cd(2)
        pad_dn.SetPad(0, 0.03, 1, 0.33)
        pad_dn.SetGridy()

        gr_den = l_graph[0]
        mg_rat=ROOT.TMultiGraph()
        for i_graph in range(1, len(l_graph)):
            gr_num = l_graph[i_graph]
            gr_rat = getGraphRatio(gr_num, gr_den)
            mg_rat.Add(gr_rat, "p")

        if MIN_RAT != -1 or MAX_RAT != -1:
            print("Setting ratio graphs y axis to: {} --> {}".format(MIN_RAT, MAX_RAT))
            mg_rat.GetHistogram().GetYaxis().SetRangeUser(MIN_RAT, MAX_RAT)

        mg_rat.Draw("a")

    can_gr.SaveAs(name + ".png")

    if pdf:
        can_gr.SaveAs(name + ".pdf")
#-------------------------------------------------------
def getGraphRatio(gr_num, gr_den):
    l_x_num = gr_num.GetX()
    l_x_den = gr_den.GetX()

    l_y_num = gr_num.GetY()
    l_y_den = gr_den.GetY()
    size    = len(l_x_num)

    l_y_nms = []
    l_y_dns = []
    for ibin in range(0, size):
        l_y_nms.append(gr_num.GetErrorY(ibin))
        l_y_dns.append(gr_den.GetErrorY(ibin))

    l_x_err = []
    for i_bin in range(0, len(l_x_num) ):
        x_err = gr_num.GetErrorX(i_bin)
        l_x_err.append(x_err)

    if len(l_x_num) != len(l_x_den):
        raise ValueError("Num {}, den {}".format(len(l_x_num), len(l_x_den)))

    for x_num, x_den in zip(l_x_num, l_x_den):
        if abs(x_num - x_den) / x_den > 0.001:
            print("Values of x are too far appart.")
            print("X num: {}".format(x_num))
            print("X den: {}".format(x_den))
            exit(0)

    arr_rat = array.array('f', [])
    arr_sig = array.array('f', [])
    arr_x   = array.array('f', l_x_num)
    arr_ex  = array.array('f', l_x_err)

    f_rat=ROOT.TFormula("f_rat", "x/y");
    for y_num, y_nms, y_den, y_dns in zip(l_y_num, l_y_nms, l_y_den, l_y_dns):
        rat=get_mean_2d(f_rat, (y_num, y_nms), (y_den, y_dns))
        sig=get_error_2d(f_rat, (y_num, y_nms), (y_den, y_dns))

        arr_rat.append(rat)
        arr_sig.append(sig)

    color=gr_num.GetMarkerColor()
    gr=ROOT.TGraphErrors(size, arr_x, arr_rat, arr_ex, arr_sig)
    gr.SetMarkerStyle(20)
    gr.SetMarkerSize(0.5)
    gr.SetMarkerColor(color)

    return gr
#-------------------------------------------------------
def SaveHistogram2D(histogram, filename, log=False):
    name = histogram.GetName()
    can = ROOT.TCanvas("can_%s" % name, "", 800, 600)
    histogram.Draw("colz")

    Reformat2D(can)

    can.SetLogz(log)
    can.SaveAs("%s.png" % filename)
#-------------------------------------------------------
def divide2DPoly(name, h_num, h_den):
    h_rat=h_num.Clone(name)

    l_bin_num = h_num.GetBins()
    l_bin_den = h_den.GetBins()
    l_bin_rat = h_rat.GetBins()

    size_num = l_bin_num.GetEntries()
    size_den = l_bin_den.GetEntries()

    if size_num != size_den:
        ROOT.Error("divide2DPoly", "Numerator and denominator have different sizes: {}/{}".format(size_num, size_den))
        exit(1)

    for i_bin in range(0, size_num):
        bin_num = l_bin_num[i_bin]
        bin_den = l_bin_den[i_bin]
        
        num = bin_num.GetContent()
        den = bin_den.GetContent()

        try:
            rat = num/den
        except:
            ROOT.Error("divide2DPoly", "Cannot get ratio = {}/{}".format(num, den))
            exit(1)

        bin_rat = l_bin_rat[i_bin]
        bin_rat.SetContent(rat)

    return h_rat
#-------------------------------------------------------
def SaveFrame(frame, pdf_names=[], data_names=[], kind="", process="", log=False, legend=False):
    can=ROOT.TCanvas("can", "", 800, 600)
    frame.Draw()

    if log:
        can.SetLogy()

    if legend:
        can.BuildLegend(0.6, 0.65, 0.9, 0.93)

    ReformatRooPlot(frame, pdf_names, data_names)
    #ATLASLabel(0.20, 0.86, kind, 1, can, process)

    can.SaveAs("%s.pdf" % frame.GetName() )
#-------------------------------------------------------
def zeroErrors(hist, clone=True):
    if clone:
        hist=hist.Clone()

    nbins=hist.GetNbinsX()
    for i_bin in range(1, nbins + 1):
        hist.SetBinError(i_bin, 0)

    hist.SetDirectory(0)

    return hist
#-------------------------------------------------------
def readCSVDict(filepath, separator_1, separator_2 = ""):
    if not os.path.isfile(filepath):
        log.error('Cannot find ' + filepath)
        exit(1)
    else:
        log.info('Reading ' + filepath)

    separator_1=separator_1.replace(" ", "")
    separator_2=separator_2.replace(" ", "")

    if separator_1 == "":
        print("Separator has to have at least one non-space character")
        exit(1)

    ifile=open(filepath)
    l_line=ifile.read().splitlines()

    d_csv={}
    for line in l_line:
        if separator_1 not in line:
            continue

        line=line.replace(" ", "")
        l_obj=line.split(separator_1)
        if len(l_obj) != 2:
            print("Cannot split {} into 2 objects with speratoro {}".format(line, separator_1))

        key=l_obj[0]
        val=l_obj[1]

        if separator_2 == "":
            d_csv[key] = val
        else:
            l_val = val.split(separator_2)
            d_csv[key] = l_val

    ifile.close()

    return d_csv
    if not os.path.isfile(filepath):
        print("utils.py::readCSVDict::Cannot find " + filepath)
        exit(1)

    separator_1=separator_1.replace(" ", "")
    separator_2=separator_2.replace(" ", "")

    if separator_1 == "":
        print("Separator has to have at least one non-space character")
        exit(1)

    ifile=open(filepath)
    l_line=ifile.read().splitlines()

    d_csv={}
    for line in l_line:
        if separator_1 not in line:
            continue

        line=line.replace(" ", "")
        l_obj=line.split(separator_1)
        if len(l_obj) != 2:
            print("Cannot split {} into 2 objects with speratoro {}".format(line, separator_1))

        key=l_obj[0]
        val=l_obj[1]

        if separator_2 == "":
            d_csv[key] = val
        else:
            l_val = val.split(separator_2)
            d_csv[key] = l_val

    ifile.close()

    return d_csv
#-------------------------------------------------------
def getTreeContainer(itree, branch, index):
    itree.SetBranchStatus(   "*", 0)
    itree.SetBranchStatus(branch, 1)

    l_val=[]
    for entry in itree:
        v_val=getattr(entry, branch)
        val=v_val[index]
        l_val.append(val)

    itree.SetBranchStatus("*", 1)

    return np.array(l_val)
#-------------------------------------------------------
def getTreeValues(itree, l_expr):
    itree.SetBranchStatus("*", 0)

    d_expr={}
    for expr in l_expr:
        setBranchStatusTTF(itree, expr)
        d_expr[expr] = ROOT.TTreeFormula(expr, expr, itree)

    d_expr_val={}
    for entry in itree:
        for expr in l_expr:
            val=d_expr[expr].EvalInstance()
            if expr not in d_expr_val:
                d_expr_val[expr] = [val]
            else:
                d_expr_val[expr].append(val)
    
    itree.SetBranchStatus("*", 1)
    
    return tuple(d_expr_val.values())
#--------------------
def Filter(itree, selection, allow_empty=True, l_keep_branch=[]):
    if len(l_keep_branch) != 0:
        itree.SetBranchStatus("*", 0)
        setBranchStatusTTF(itree, selection)
        for branch in l_keep_branch:
            itree.SetBranchStatus(branch, 1)

    treename=itree.GetName() 
    date=datetime.datetime.now()
    date=str(date).replace(" ", "_").replace(".", "_").replace(":", "_").replace("-", "_")
    filepath="/tmp/filter_{}_{}.root".format(treename, date)

    ofile=ROOT.TFile(filepath, "recreate")
    otree=itree.CopyTree(selection)
    otree.Write()
    
    ROOT.Info("Filter", "Applying filter: {}/{}".format(otree.GetEntries(), itree.GetEntries()))

    if not allow_empty and otree.GetEntries() == 0:
        ROOT.Error("Filter", "Selection: " + selection)
        ROOT.Error("Filter", "File: " + filepath)
        ROOT.Error("Filter", "Tree: " + treename)
        raise
    
    return (ofile, otree)
#-------------------------------------------------------
#Case 1 (x, y, z) = (hist, None, None)
#Case 2 (x, y, z) = (arr_bound, None, None)
#Case 3 (x, y, z) = (nbins, min, max)
#-------------------------------------------------------
def arr_to_hist(name, title, x, y, z, arr_data, color=1, style=20, d_opt={}):
    if   type(x) in [ROOT.TH1, ROOT.TH1F, ROOT.TH1D] and (y is None) and (z is None):
        h=x.Clone(name)
        h.SetTitle(title)
    elif type(x) in [array.array, np.ndarray]   and (y is None) and (z is None):
        h=ROOT.TH1F(name, title, len(x) - 1, x)
    else:
        h=ROOT.TH1F(name, title, x, y, z)

    if type(arr_data) == list:
        arr_data = np.array(arr_data)

    try:
        for val in arr_data:
            if   type(val) == np.ndarray and type(val[1]) != tuple:
                label = val[0]
                value = float(val[1])
                h.Fill(label, value)
            elif type(val) == np.ndarray and type(val[1]) == tuple:
                label = val[0]
                value, error = val[1]
                i_bin = h.Fill(label, value)
                h.SetBinError(i_bin, error)
            else:
                h.Fill(val)
    except:
        log.error('Cannot fill histogram {} with array of numbers: '.format(name))
        print(arr_data)
        print(arr_data.shape)
        raise

    if "xname" in d_opt:
        xname=d_opt["xname"]
        h.GetXaxis().SetTitle(xname)
        h.GetXaxis().SetDecimals()
        h.GetXaxis().SetMaxDigits(2)

    if "yname" in d_opt:
        yname=d_opt["yname"]
        h.GetYaxis().SetTitle(yname)
        h.GetYaxis().SetDecimals()
        h.GetYaxis().SetMaxDigits(2)

    if  'draw_all' in d_opt and d_opt['draw_all']:
        nbins = h.GetNbinsX()
        h.GetXaxis().SetRangeUser(-1, nbins + 1)

    if 'leg_stats' in d_opt and d_opt['leg_stats']:
        area=get_hist_area(h)
        title = '{}, {:.3e}'.format(title, area)
        h.SetTitle(title)

    h.SetLineColor(color)
    h.SetMarkerStyle(style)
    h.SetMarkerColor(color)
    h.LabelsDeflate()

    return h
#-------------------------------------------------------
def dic_to_hist(name, dic_data, title='', color=1, d_opt={}):
    h=ROOT.TH1F(name, title, 1, 0, 0)

    try:
        counter=1
        for label, (value, error) in dic_data.items():
            h.Fill(label, value)
            h.SetBinError(counter, error)
            counter+=1
    except:
        log.error('Cannot fill histogram {} with data from dictionary: '.format(name))
        print(dic_data)
        raise

    if "xname" in d_opt:
        xname=d_opt["xname"]
        h.GetXaxis().SetTitle(xname)
        h.GetXaxis().SetDecimals()
        h.GetXaxis().SetMaxDigits(2)

    if "yname" in d_opt:
        yname=d_opt["yname"]
        h.GetYaxis().SetTitle(yname)
        h.GetYaxis().SetDecimals()
        h.GetYaxis().SetMaxDigits(2)

    h.SetLineColor(color)
    h.SetMarkerColor(color)
    h.LabelsDeflate()

    return h
#-------------------------------------------------------
def makeTable(path, obj, caption="", sort=False, form=None, environ='figure'):
    dummy=ROOT.vector("std::vector<std::string>")()
    if   type(obj) == list:
        makeTable_from_list(path, obj, caption, sort=sort, form=form, environ=environ)
    elif type(obj) == type(dummy):
        makeTable_from_vector(path, obj, caption, sort=sort, form=form, environ=environ)
    else:
        log.error("Cannot make table from {}".format(type(obj)))
        raise
#-------------------------------------------------------
def makeTable_from_vector(path, v_v_string, caption = "", sort=False, form=None, environ='figure'):
    l_l_line=[]
    for v_string in v_v_string:
        l_line=[]
        for string in v_string:
            l_line.append(string)
        l_l_line.append(l_line)

    do_makeTable(path, l_l_line, caption, sort=sort, form=form, environ=environ)
#-------------------------------------------------------
def makeTable_from_list(path, l_line, caption = "", sort=False, form=None, environ='figure'):
    if type(l_line[0]) == list:
        do_makeTable(path, l_line, caption, sort=sort, form=form, environ=environ)
        return

    regex='([=,\w,\.,\s,\(,\),\',\/,|, <, >]+)&'

    l_row=[]
    for line in l_line:
        line=line + " "
        l_mtch=re.findall(regex, line)
        if len(l_mtch) == 0:
            ROOT.Error("makeTable", "Cannot match {} with {}".format(line, regex))
            exit(1)

        l_row.append(l_mtch)

    do_makeTable(path, l_row, caption, sort=sort, form=form, environ=environ)
#-------------------------------------------------------
def do_makeTable(path, l_l_line, caption="", sort = False, form=None, environ='figure'):
    if sort:
        head = l_l_line[0]
        l_l_line.remove(head)
        l_l_line = sorted(l_l_line, key=op.itemgetter(0))
        l_l_line.insert(0, head)

    ncols=len(l_l_line[0])
    if form is None:
        pass
    elif len(form) != ncols:
        log.error('Formatting string size and ncolumns do not agree: {}/{}'.format(ncols, len(form)))
        raise
    
    l_out=[]
    if   environ == 'figure':
        l_out.append("\\begin{figure}")
        l_out.append("\\centering")
    elif environ == 'table':
        l_out.append("\\begin{table}")
    else:
        log.error('Invalid environment: ' + environ)
        raise

    l_out.append("\\begin{tabular}{ " + "l " * ncols + "}")

    first=True
    for i_row, row in enumerate(l_l_line):
        out=''
        for i_obj, obj in enumerate(row):
            if   form is not None and type(obj) != str:
                formt=form[i_obj]
                obj = formt.format(obj)
            elif form is     None and type(obj) != str:
                obj = '{:.3e}'.format(obj)
                
            try:
                if i_obj == len(row) - 1:
                    out = '{} {} \\\\'.format(out, obj)
                else:
                    out = '{} {} & '.format(out, obj)
            except:
                log.error('Cannot use object {} of type {}'.format(obj, type(obj)))
                raise

        if i_row == len(l_l_line) - 1:
            out=out.replace("\\\\", "")

        l_out.append(out)
        if first:
            l_out.append("\\hline")
            first=False

    l_out.append("\\end{tabular}")
    if caption != "":
        l_out.append("\\caption{%s}" % (caption))

    if   environ == 'figure':
        l_out.append("\\end{figure}")
    elif environ == 'table':
        l_out.append("\\end{table}")
    else:
        log.error('Invalid environment: ' + environ)
        raise

    dirname=os.path.dirname(path)
    if not os.path.isdir(dirname)  and dirname != '':
        try:
            os.makedirs(dirname)
        except:
            log.error('Cannot make \'{}\''.format(dirname))
            raise

    ofile=open(path, "w")
    for out in l_out:
        ofile.write(out + "\n")
    ofile.close()
#-------------------------------------------------------
def unfoldNDArray(arr, tup_loc = ()):
    counter=0
    d_res={}
    d_tmp={}
    for obj in arr:
        this_tup_loc=tup_loc + (counter,)

        try:
            val=float(obj)
            d_res[this_tup_loc] = val
        except:
            d_tmp=unfoldNDArray(obj, this_tup_loc)

        d_res={**d_res, **d_tmp}

        counter+=1

    return d_res
#-------------------------------------------------------
def standardize(arr_source, arr_target):
    arr_shape=arr_target / arr_target

    shape_tgt=np.shape(arr_shape)
    shape_src=np.shape(arr_source)

    diff=len(shape_tgt) - len(shape_src)
    if diff <= 0:  
        print("Cannot standardize")
        print("Target = {}".format(str(shape_tgt)))
        print("Source = {}".format(str(shape_src)))
        exit(1)

    shape_new=shape_src + tuple([1] * diff)

    print("Standardizing: ")
    print(arr_source)
    print("--->")

    arr_source = arr_source.reshape(shape_new)

    arr_res = arr_source * arr_shape
    print(arr_res)

    return arr_res
#-------------------------------------------------------
def checkDir(objpath):
    dirpath=""

    filename=os.path.basename(objpath)
    if "." in filename:
        dirpath=os.path.dirname(objpath)
    else:
        dirpath=objpath

    if dirpath != "" and not os.path.isdir(dirpath):
        try:
            os.mkdir(dirpath)
        except:
            ROOT.Error("checkDir", "Cannot create " + dirpath)
            exit(1)
#-------------------------------------------------------
def printCovariance(outputpath, mat, l_header, form):
    nrow, ncol = np.shape(mat)
    nhead      = len(l_header)

    if nrow != ncol:
        ROOT.Error("printMatrix", "Non-square matrix: ({},{})".format(nrow, ncol))
        exit(1)

    if ncol != nhead:
        ROOT.Error("printMatrix", "Header and matrix not compatible {}/{}".format(nrow, nhead))
        exit(1)

    header=str(l_header).replace(",", "&").replace("'", " ").replace("]", "\\\\").replace("[", "")
    l_row=["\\begin{tabular}{ " + " l " * ncol  +  " | l }", header, "\\hline"]
    for i_row in range(0, nrow):
        row=""
        for i_col in range(0, ncol + 1):
            if i_col == ncol:
                val = l_header[i_row]
            else:
                val=mat[i_row][i_col]

            if i_row >= i_col:
                row+= " -  & "
            elif type(val) == str:
                row+= " {} & ".format(val)
            else:
                tmp = " " + form + " & "
                row+= tmp.format(val)

        row=row[:-2]
        if i_row != nrow - 1:
            row+="\\\\"

        l_row.append(row)

    l_row.append("\\end{tabular}")

    f=open(outputpath, "w")
    for row in l_row:
        f.write(row + "\n")
    f.close()
#-------------------------------------------------------
def saveCovariance(outputpath, arr):
    size=len(arr)
    mat=ROOT.TMatrixF(size, size) 
    for i in range(0, size):
        for j in range(0, size):
            mat[i][j]  = arr[i][j]
            
    ofile=ROOT.TFile(outputpath, "recreate")
    mat.Write()
    ofile.Close()
#-------------------------------------------------------
def saveHistogram(plotpath, histogram):
    can=ROOT.TCanvas("can", "", 600, 400)
    histogram.Draw()
    can.SaveAs(plotpath)
#-------------------------------------------------------
def read_2Dpoly(arr_point, hist):
    range_x, range_y = getPoly2DBoundaries(hist)

    l_val = []
    for x, y in arr_point:
        i_bin = findPoly2DBin(hist, x, y, range_x, range_y)
        bc    = hist.GetBinContent(i_bin)

        l_val.append(bc)

    return np.array(l_val)
#-------------------------------------------------------
def getPoly2DBoundaries(hist):
    l_bin=hist.GetBins()

    minx=+1e10
    maxx=-1e10

    miny=+1e10
    maxy=-1e10
    for BIN in l_bin:
        tmp=BIN.GetXMin()
        if tmp < minx:
            minx = tmp

        tmp=BIN.GetXMax()
        if tmp > maxx:
            maxx = tmp

        tmp=BIN.GetYMin()
        if tmp < miny:
            miny = tmp

        tmp=BIN.GetYMax()
        if tmp > maxy:
            maxy = tmp

    return (minx, maxx), (miny, maxy)
#-------------------------------------------------------
def findPoly2DBin(hist, x, y, range_x, range_y):
    i_bin=hist.FindBin(x,y)

    if i_bin >= 0:
        return i_bin 

    if i_bin == -5:
        histname=hist.GetName()
        log.error('Cannot find data in ({},{}) in histogram {}'.format(x, y, histname))
        raise

    x_orig=x
    y_orig=y

    epsilon = 1e-7
    if   i_bin in [-1, -4, -7]:
        x = range_x[0] + epsilon
    elif i_bin in [-3, -6, -9]:
        x = range_x[1] - epsilon

    if   i_bin in [-7, -8, -9]:
        y = range_y[0] + epsilon
    elif i_bin in [-1, -2, -3]:
        y = range_y[1] - epsilon

    log.debug('Fixing boundaries ({:.2e},{:.2e}) --> ({:.2e},{:.2e})'.format(x_orig, y_orig, x, y))

    i_bin=hist.FindBin(x,y)

    if i_bin < 0:
        log.error('Invalid bin index {} found in histogram {}'.format(i_bin, histname))
        raise

    return i_bin
#-------------------------------------------------------
def makePoly2D(name, arr_x, arr_y):
    len_x = len(arr_x)
    len_y = len(arr_y)

    h=ROOT.TH2Poly(name, "", min(arr_x), max(arr_x), min(arr_y), max(arr_y))
    for i_x in range(0, len_x - 1): 
        for i_y in range(0, len_y - 1): 

            x_lo=arr_x[i_x + 0]
            x_hi=arr_x[i_x + 1]

            y_lo=arr_y[i_y + 0]
            y_hi=arr_y[i_y + 1]

            h.AddBin(x_lo, y_lo, x_hi, y_hi)

    return h
#-------------------------------------------------------
def dividePoly2D(name, h_num, h_den):
    l_bin_num = h_num.GetBins()
    l_bin_den = h_den.GetBins()

    if len(l_bin_num) != len(l_bin_den):
        ROOT.Error("dividePolydenD", "Cannot divide histograms with different numbers of bins")
        exit(1)

    h_rat=h_num.Clone(name)
    l_bin_rat=h_rat.GetBins()

    for bin_num, bin_den, bin_rat in zip(l_bin_num, l_bin_den, l_bin_rat):
        num=bin_num.GetContent()
        den=bin_den.GetContent()
        if den != 0:
            rat=num/den
        else:
            rat=0

        bin_rat.SetContent(rat)

    return h_rat
#-------------------------------------------------------
def defineVars(df, l_exp):
    l_tmp=[]

    log.info('-----------------------------')
    for i_var, exp in enumerate(l_exp):
        var="getMatrix_var_" + str(i_var)
        l_tmp.append(var)

        try:
            df=df.Define(var, exp)
            log.info('{0:<20}{1:10}{2:<50}'.format(var, '--->', exp))
        except:
            log.error("Cannot define {} as {}, using expressions {}".format(var, exp, str(l_exp)))
            raise
    log.info('-----------------------------')

    return (df, l_tmp)
#-------------------------------------------------------
#Numpy structures
#-------------------------------------------------
def evalArray(name, index = "rdfentry_", typename = "float"):
    if index == "rdfentry_":
        return       'auto to_eval = std::string("{}[") + std::to_string({}) + "]"; return {}(TPython::Eval(to_eval.c_str()));'.format(       name, index, typename)
    else:
        ROOT.gInterpreter.Declare("int {}=-1;".format(index))
        return '{}++; auto to_eval = std::string("{}[") + std::to_string({}) + "]"; return {}(TPython::Eval(to_eval.c_str()));'.format(index, name, index, typename)
#-------------------------------------------------
def getMatrix(df, l_var, max_entries=-1):
    df, l_var = defineVars(df, l_var)

    if max_entries > 0:
        log.visible('Using {} entries'.format(max_entries) )
        df=df.Filter("rdfentry_ < {}".format(max_entries), 'max_entries')

    nentries=df.Count().GetValue()
    log.info("Reading {} entries".format(nentries))

    d_nam_arr=df.AsNumpy(l_var)
    l_l_val=[*d_nam_arr.values()]
    arr_val=np.array(l_l_val)

    arr_mat = np.transpose(arr_val)
    mat_size= arr_mat.size / len(l_var)

    if mat_size != nentries:
        log.error('Expected {}, got {}'.format(nentries, mat_size))
        print(d_nam_arr)
        print(arr_val.shape)
        print(arr_mat.shape)
        raise

    return arr_mat
#-------------------------------------------------
#Operations on histograms
#-------------------------------------------------
def average_2D_hist(name, l_hist):
    utnr.check_nonempty(l_hist)

    h_merged = l_hist[0].Clone(name)
    h_merged.Reset()

    tl_hist = ROOT.TList()
    for hist in l_hist:
        tl_hist.Add(hist)

    h_merged.Merge(tl_hist)

    size = len(l_hist)
    h_merged.Scale(1./size)

    return h_merged
#-------------------------------------------------
def get_hist_area(hist, opt='all', typ=None):
    nbins=hist.GetNbinsX()
    if opt == 'all':
        area=hist.Integral(0, nbins + 1)
    else:
        log.error('Unrecognized option ' + opt)
        raise

    if typ is not None and typ == 'int':
        area = int(area)

    return area
#-------------------------------------------------
def normalize(hist):
    hist=hist.Clone()
    area=hist.GetSumOfWeights()
    hist.Scale(1./area)

    return hist
#-------------------------------------------------
def scale(hist, value, error = 0):
    """
    Multipy histogram by value, propagating errors in quadrature
    """
    nbins=hist.GetNbinsX()
    for i_bin in range(0, nbins + 2):
        bc = hist.GetBinContent(i_bin)
        be = hist.GetBinError(i_bin)

        bc, be=value_and_covariance('x * y', x=(bc, be), y=(value, error))

        hist.SetBinContent(i_bin, bc)
        hist.SetBinError(  i_bin, be)

    hist.LabelsDeflate()

    return hist
#-------------------------------------------------
def divide_histograms(hist_num, hist_den, d_opt={}):
    num_name=hist_num.GetName()
    den_name=hist_den.GetName()

    hist_rat=hist_num.Clone("h_{}_over_{}".format(num_name, den_name))

    try:
        scale = d_opt['scale']
    except:
        scale = 1

    hist_rat.Divide(hist_num, hist_den, scale)

    if "zero_error" in d_opt and d_opt['zero_error']:
        log.visible('Zeroing errors')
        zeroErrors(hist_rat)

    return hist_rat
#-------------------------------------------------
def poly2D_to_1D(hist, suffix=''):
    l_bin_obj=hist.GetBins()
    l_bin_row=[]
    l_hist=[]

    last_minx=-1e10
    ihist=0

    nbins=hist.GetNumberOfBins()
    l_info=[]
    for index in range(1, nbins + 1):
        bc = hist.GetBinContent(index)
        be = hist.GetBinError(index)
        l_info.append((bc, be))

    for bin_obj in l_bin_obj:
        minx  = bin_obj.GetXMin()
        index = bin_obj.GetBinNumber()
        bc, be= l_info[index - 1]
        ct    = bin_obj.GetContent()

        if abs(ct - bc) > 1e-10:
            log.error('Missaligned/Non-matching bin contents')
            log.error('{0:5}{1:20.3e}{2:20.3e}{3:20.3e}'.format(index, bc, ct, be))
            exit(1)
        else:
            log.debug('{0:5}{1:20.3e}{2:20.3e}{3:20.3e}'.format(index, bc, ct, be))

        if minx > last_minx:
            l_bin_row.append((bin_obj, be))
            last_minx=minx
        else:
            if suffix != '':
                name='{}_{}_{}'.format(hist.GetName(), ihist, suffix)
            else:
                name='{}_{}'.format(hist.GetName(), ihist)

            hist=make_hist(name, l_bin_row)
            l_hist.append(hist)
            l_bin_row=[(bin_obj, be)]
            last_minx=-1e10
            ihist+=1

    if suffix != '':
        name='{}_{}_{}'.format(hist.GetName(), ihist, suffix)
    else:
        name='{}_{}'.format(hist.GetName(), ihist)

    hist=make_hist(name, l_bin_row)
    l_hist.append(hist)

    return l_hist
#-------------------------------------------------
def make_hist(name, l_bin):
    nbins=len(l_bin)
    s_edge=set()

    for bin_obj, error in l_bin:
        s_edge.add(bin_obj.GetXMin())
        s_edge.add(bin_obj.GetXMax())

    l_edge=list(s_edge)
    l_edge.sort()
    arr_edge = array.array('f', l_edge)

    h=ROOT.TH1F(name, '', nbins, arr_edge)

    for index, (bin_obj, be) in enumerate(l_bin):
        i_bin = index + 1

        bc = bin_obj.GetContent()
        h.SetBinContent(i_bin, bc)
        h.SetBinError(i_bin, be)

    return h
#-------------------------------------------------
def print_poly2D(hist):
    l_bin_obj = hist.GetBins()
    #print('{0:20}{1:20}{2:20}'.format('Bin', 'Content', 'Error'))
    print('{0:20}{1:20}'.format('Bin', 'Content'))
    for i_bin, bin_obj in enumerate(l_bin_obj):
        bc=bin_obj.GetContent()
        #be=bin_obj.GetError()
        #print('{0:<20}{1:<20}{2:<20}'.format(i_bin, bc, be))
        print('{0:<20}{1:<20}'.format(i_bin, bc))
#-------------------------------------------------
def getHistogram(name, title, nbins, minx, maxx, arr_data):
    h=ROOT.TH1F(name, title, nbins, minx, maxx)
    for data in arr_data:
        h.Fill(data)

    return h
#-------------------------------------------------
def getDicHistogram(name, title, d_data):
    h=ROOT.TH1F(name, title, 1, 0, 0)

    l_data = list(d_data.items())
    l_data.sort()

    for label, value in l_data:
        h.Fill(label, value)

    zeroErrors(h)
    h.LabelsDeflate()

    return h
#-------------------------------------------------
#Operations on dataframes
#-------------------------------------------------
def check_column(df, column_name):
    l_name = df.GetColumnNames()

    if column_name not in l_name:
        log.error('Column {} not found in dataframe'.format(column_name))
        raise
#-------------------------------------------------
def df_to_tree(df, identifier='', include_regex = None, exclude_regex=None):
    '''Will take a snapshot of an RDF and return corresponding tree
    Parameters
    ------------------
    df: ROOT dataframe
    identifier (str): suffix for naming file, which will go to /tmp/
    include_regex (str): Regular expression that will specify which branches to keep
    exclude_regex (str): Regular expression that will specify which branches to drop

    Returns
    ------------------
    TTree, TFile instances in the form of a tuple. The latter can be used to close the file.
    '''
    try:
        job_id = os.environ['_CONDOR_IHEP_JOB_ID']
    except:
        job_id = 'local'

    v_col = df.GetColumnNames()
    l_col =[ col.c_str() for col in v_col ]

    if exclude_regex is not None:
        log.info(f'Dropping branches for regex: {exclude_regex}')
        l_col = [ col for col in l_col if not re.match(exclude_regex, col) ]

    if include_regex is not None:
        log.info(f'Keeping branches for regex: {include_regex}')
        l_col = [ col for col in l_col if     re.match(include_regex, col) ]

    filepath = '/tmp/file_{}_{}.root'.format(job_id, identifier)
    df.Snapshot('tree', filepath, l_col)

    ifile=ROOT.TFile(filepath)
    try:
        tree = ifile.tree
    except:
        log.error('Cannot retrieve tree from file ' + filepath)
        ifile.ls()
        raise

    return (tree, ifile)
#-------------------------------------------------
#Operations on files
#-------------------------------------------------
def found_in_file(obj_path, file_path):
    try:
        ifile=ROOT.TFile.Open(file_path)
        obj=ifile.Get(obj_path)
    except:
        return False

    missing = not obj
    ifile.Close()

    return missing == False
#-------------------------------------------------
def getTrees(ifile, treename='', rtype='list'):
    if not ifile.InheritsFrom('TDirectoryFile'):
        log.error('Unrecognized object type ' + str(type(ifile)))
        raise

    dirname = ifile.GetName()

    d_tree={}
    l_key=ifile.GetListOfKeys()
    for key in l_key:
        obj=key.ReadObj()
        if   obj.InheritsFrom('TDirectoryFile'):
            d_tmp = getTrees(obj, treename=treename, rtype='dict')
            d_tree.update(d_tmp)
        elif obj.InheritsFrom('TTree') and treename == '':
            key = '{}/{}'.format(dirname, obj.GetName())
            d_tree[key] = obj
        elif obj.InheritsFrom('TTree') and treename == obj.GetName():
            key = '{}/{}'.format(dirname, obj.GetName())
            d_tree[key] = obj
        else:
            continue

    if   rtype == 'list':
        robj = list(d_tree.values())
    elif rtype == 'dict':
        robj = d_tree
    else:
        log.error('Unsupported object return type ' + rtype)
        raise

    return robj 
#-------------------------------------------------
def get_tree_entries(treepath, filepath):
    ifile=ROOT.TFile.Open(filepath)
    try:
        if not hasattr(ifile, treepath):
            log.error('File {} has no tree {}'.format(filepath, treepath))
            ifile.ls()
            raise
    except:
        log.error('Cannot access file ' + filepath)
        raise

    itree=getattr(ifile, treepath)
    nentries = itree.GetEntries()
    ifile.Close()

    return nentries
#-------------------------------------------------
def update_file_stats(filepath, d_stats):
    if not os.path.isfile(filepath):
        log.error('Cannot find ' + filepath)
        raise

    ifile=ROOT.TFile(filepath)
    l_tree=getTrees(ifile)
    for tree in l_tree:
        nentries=tree.GetEntries()
        treename=tree.GetName()
        if treename not in d_stats:
            d_stats[treename] = nentries
        else:
            d_stats[treename]+= nentries

    ifile.Close()
#-------------------------------------------------
def save_from_list(l_obj, file_path, mode=None):
    utnr.check_none(mode)

    if mode not in ['UPDATE', 'RECREATE']:
        log.error('Invalid mode used: ' + mode)
        raise

    ifile=ROOT.TFile(file_path, mode)
    for obj in l_obj:
        obj.Write()
    ifile.Close()
#-------------------------------------------------------
#RDataFrame
#-------------------------------------------------
def get_arr_exp(rdf, exp):
    v_col = rdf.GetColumnNames()
    l_col = [ col.c_str() for col in v_col ]

    if exp not in l_col:
        var=get_var_name(exp)
        rdf=rdf.Define(var, exp)
    else:
        var=exp

    arr_var = rdf.AsNumpy([var])[var]

    return arr_var
#-------------------------------------------------
def get_var_name(expr):
    var = expr
    var = var.replace('TMath::',    '')
    var = var.replace(' '      ,   '_')
    var = var.replace('('      ,   '_')
    var = var.replace(')'      ,   '_')
    var = var.replace(':'      ,   '_')
    var = var.replace('*'      , '_p_')
        
    return var
#------------------------------
def add_vars(rdf, l_expr):
    '''
    Adds extra columns to dataframe. Columns are added if not found already.
    Columns added are meant to be expresions depending on columns in dataframe.
    vars attribute is added, with the list of variables.
    '''
    l_col = rdf.GetColumnNames()
    l_var = []
    for expr in l_expr:
        if expr in l_col:
            l_var.append(expr)
            continue
    
        var_name = get_var_name(expr)

        rdf=rdf.Define(var_name, expr)

        l_var.append(var_name)

    rdf.vars = l_var

    return rdf
#-------------------------------------------------
def check_df_has_columns(df, l_col):
    s_ext_col= set(l_col)
    s_all_col= set(df.GetColumnNames())
    if not s_ext_col.issubset(s_all_col):
        log.error('At least one of the extra columns requested, does not belong to DataFrame:')
        print(s_all_col)
        raise
#-------------------------------------------------
def get_df_types():
    t1 = ROOT.RDF.RInterface('ROOT::Detail::RDF::RLoopManager,void')
    t2 = ROOT.RDF.RInterface('ROOT::Detail::RDF::RJittedFilter,void')
    t3 = ROOT.RDF.RInterface('ROOT::Detail::RDF::RRange<ROOT::Detail::RDF::RLoopManager>,void>')

    return (t1, t2, t3)
#-------------------------------------------------
def get_df_range(df, index, npartition):
    '''
    Will take a dataframe and return the index-th partition out of npartition(s)
    '''
    atr_obj = amgr(df)

    if index >= npartition:
        log.error(f'Index {index} cannot be larger than npartition {npartition}')
        raise

    tot_entries = df.Count().GetValue()

    arr_ind   = np.arange(0, tot_entries)
    l_arr_ind = np.array_split(arr_ind, npartition)
    sarr_ind  = l_arr_ind[index]

    start = int(sarr_ind[ 0]) 
    end   = int(sarr_ind[-1]) + 1

    log.info(f'Picking up ends [{start}, {end}] for {index}/{npartition}')

    df = df.Range(start, end)
    df = atr_obj.add_atr(df)

    return df
#-------------------------------------------------
def get_tree_from_df(df, tree_name='tree', file_path=None, l_col=None):
    if file_path is None:
        file_path = get_random_filename() 

    log.info(f'Taking snapshot of: {file_path}:{tree_name}')
    if l_col is None:
        df.Snapshot(tree_name, file_path)
    else:
        v_col = ROOT.std.vector('std::string')(l_col)
        df.Snapshot(tree_name, file_path, v_col)

    itree, ifile = get_from_file(tree_name, file_path)
    log.info('Loading tree')

    return (itree, ifile)
#-------------------------------------------------
def filter_df_by_flag(df, arr_flg):
    if not hasattr(df, 'filepath') or not hasattr(df, 'treename'):
        df = reload_df(df)

    filepath=df.filepath
    treename=df.treename

    itree, ifile=get_from_file(treename, filepath)

    tsize=itree.GetEntries()
    asize=arr_flg.size

    if tsize != asize:
        log.error('Flags and tree have different sizes flags/tree: {}/{}'.format(asize, tsize))
        raise

    ofilepath=get_random_filename()
    ofile=ROOT.TFile(ofilepath, 'RECREATE')

    otree=itree.CloneTree(0)
    for _, flag in zip(itree, arr_flg):
        if flag == False:
            continue

        otree.Fill()

    otree.Write()

    ientries = itree.GetEntries()
    fentries = otree.GetEntries()

    log.info('{0:<20}{1:<20}'.format('Input', ientries))
    log.info('{0:<20}{1:<20}'.format('Onput', fentries))

    ofile.Close()
    ifile.Close()

    df = ROOT.RDataFrame(treename, ofilepath)

    return df
#-------------------------------------------------
def merge_reports(l_report):
    """
    It takes a python list of CutFlowReport objects and returns one object, where the passed and total yields are added.
    """
    l_rep = ROOT.TList()
    for report in l_report:
        l_rep.Add(report)

    rep = ROOT.CutFlowReport()
    rep.Merge(l_rep)

    return rep
#-------------------------------------------------
def df_has_col(df, name, fail=False):
    """
    If fail is true, an exception is risen when `name` is not a  column in the dataframe.
    Otherwise a flag is is returned.
    """
    v_name = df.GetColumnNames()

    bg = v_name.begin()
    en = v_name.end()

    it = ROOT.std.find(bg, en, name)

    if it !=  en: 
        flag=True
    else:
        flag=False

    if flag == False and fail == True:
        log.error('Cannot find {} in dataframe, available:'.format(name))
        print(l_name)
        raise

    return flag
#-------------------------------------------------
def add_df_column(rdf, arr_val, name, d_opt={}):
    mgr   = amgr(rdf)

    if 'exclude_re' not in d_opt:
        d_opt['exclude_re'] = None 

    v_col_org = rdf.GetColumnNames()
    l_col_org = [name.c_str() for name in v_col_org ]
    l_col     = []

    tmva_rgx  = 'tmva_\d+_\d+'

    for col in l_col_org:
        rgx = d_opt['exclude_re']
        if   rgx is not None and re.match(rgx, col) and     re.match(tmva_rgx, col):
            log.debug(f'Dropping: {col}')
            continue
        elif rgx is not None and re.match(rgx, col) and not re.match(tmva_rgx, col):
            log.warning(f'Dropping: {col}')
            continue
        else:
            log.debug(f'Picking: {col}')
            l_col.append(col)

    data  = ak.from_rdataframe(rdf, columns=l_col)
    d_data= { col : data[col] for col in l_col }

    if arr_val.dtype == 'object':
        arr_val = arr_val.astype(float)

    d_data[name] = arr_val

    rdf = ak.to_rdataframe(d_data)
    rdf = mgr.add_atr(rdf)

    return rdf
#-------------------------------------------------
def reload_df(df, treename = 'tree'):
    filepath=get_random_filename()

    log.info('Reloading dataframe, using file/tree: {}/{}'.format(filepath, treename))
    df.Snapshot(treename, filepath)

    df=ROOT.RDataFrame(treename, filepath)
    df.filepath=filepath
    df.treename=treename

    return df
#-------------------------------------------------
def filter_df(df, fraction=None):
    if fraction is None:
        log.error('Fraction not specified')
        raise
    elif type(fraction) != float or fraction <= 0 or fraction > 1:
        log.error('Invalid fraction value: {}'.format(fraction))
        raise

    old_entries = df.Count().GetValue()
    new_entries = int(old_entries * fraction)

    log.info('{0:<20}{1:10}{2:<10}'.format(old_entries, '->', new_entries))

    from atr_mgr import mgr

    ob = mgr(df)
    df = df.Range(new_entries)
    df = ob.add_atr(df)

    return df
#-------------------------------------------------
def add_columns_df(df, d_arr_val_ext):
    df_size   = df.Count().GetValue()

    for key, arr_val in d_arr_val_ext.items():
        try:
            nentries, = arr_val.shape
        except:
            log.error(f'Array for key {key} has unsupported shape:')
            print(arr_val.shape)
            raise

        if nentries != df_size:
            log.error(f'For variable {key} size {nentries}, differs from dataframe {df_size}')
            raise

    ifile_path = get_random_filename()
    df.Snapshot('tree', ifile_path)

    ifile = ROOT.TFile(ifile_path)
    itree = ifile.tree

    ofile_path = get_random_filename()
    ofile = ROOT.TFile(ofile_path, 'recreate')
    otree = itree.CloneTree(0)

    d_arr_val_int = {}
    for branch_name in d_arr_val_ext:
        arr_val_int = array.array('f', [0])
        d_arr_val_int[branch_name] = arr_val_int
        otree.Branch(branch_name, arr_val_int, f'{branch_name}/F')

    for i_entry, entry in enumerate(itree):
        for branch_name, arr_val_ext in d_arr_val_ext.items():
            arr_val_int    = d_arr_val_int[branch_name]
            arr_val_int[0] = arr_val_ext[i_entry]

        otree.Fill()

    otree.Write()
    ofile.Close()
    ifile.Close()

    df = ROOT.RDataFrame('tree', ofile_path)

    return df
#-------------------------------------------------
def add_column_df(df, expr):
    name = get_var_name(expr)

    l_col= df.GetColumnNames()
    if name in l_col:
        log.warning(f'Column {name} was already found in RDF, not adding it')

        return (df, name)

    df   = df.Define(name, expr)

    return (df, name)
#-------------------------------------------------
#Miscellaneous
#-------------------------------------------------
def save_none_canvas(outpath, name, height=600, width=600, text='None'):
    c=ROOT.TCanvas(name, '', width, height)
    t=ROOT.TPaveText(.05,.1,.95,.8, 'NB')
    t.AddText(text)
    t.SetFillColor(0)
    t.Draw()
    c.SaveAs(outpath)
#-------------------------------------------------------
def get_random_filename():
    ran=ROOT.TRandom3(0)

    try:
        job_id = os.environ['_CONDOR_IHEP_JOB_ID']
    except:
        job_id = 'local'

    while True:
        ranint = ran.Integer(1000000)
        filename='/tmp/{}_{}.root'.format(job_id, ranint)
        if not os.path.isfile(filename):
            return filename
#-------------------------------------------------------
def is_type(obj, otype):
    itype=type(obj)
    if itype != otype:
        log.error('Type of object is not {}, but {}'.format(otype, itype))
        raise
#-------------------------------------------------------
def get_weights(h_num, h_den):
    h_num=h_num.Clone()
    h_den=h_den.Clone()

    nbins=h_num.GetNbinsX()

    h_num.Scale(1./h_num.Integral(0, nbins + 1))
    h_den.Scale(1./h_den.Integral(0, nbins + 1))

    h_num.Divide(h_den)

    return h_num
#-------------------------------------------------------
def get_ran_array(nentries, PDF, min_x, max_x, seed=0):
    ran=ROOT.TRandom3(seed)

    fun=ROOT.TF1(PDF, PDF, min_x, max_x) 

    l_ran_val = []
    for i_entry in range(nentries):
        ran_val = fun.GetRandom()
        l_ran_val.append(ran_val)

    return np.array(l_ran_val)
#-------------------------------------------------------
def cont_to_hist(name, cont, type_h='f'):
    if   type(cont) == list:
        arr_cont = array.array(type_h, cont)
    elif type(cont) == array.array:
        arr_cont = cont 
    elif type(cont) == np.ndarray:
        l_val    = cont.tolist()
        arr_cont = array.array(type_h, l_val)
    else:
        log.error('Type {} unsupported'.format(type(cont)))
        raise

    nbins = len(arr_cont) - 1

    if   type_h == 'f':
        hist = ROOT.TH1D(name, '', nbins, arr_cont)
    elif type_h == 'd':
        hist = ROOT.TH1D(name, '', nbins, arr_cont)
    else:
        log.error('Unrecognized type ' + type_h)
        raise

    return hist
#-------------------------------------------------------
#RooFit
#-------------------------------------------------------
def get_par_val(var, normalize=None):
    utnr.check_none(normalize)

    val = var.getVal()
    err = var.getError()

    if normalize == 'range':
        min_val = var.getMin()
        max_val = var.getMax()

        r = (val - min_val) / (max_val - min_val)
        e =  err            / (max_val - min_val)
    elif normalize == 'none':
        r = val
        e = err 
    else:
        log.error('Normalization setting {} not supported'.format(normalize))
        raise

    return (r, e)
#-------------------------------------------------------
def find_var(s_var, varname, missing_ok=False):
    var = s_var.find(varname)
    try:
        var.GetName()
        found=True
    except:
        found=False

    if not found and not missing_ok:
        log.error('Variable {} not found in:'.format(varname))
        s_var.Print()
        raise

    return var 
#-------------------------------------------------------
def get_data_weighted(data, obsname, weightname):
    s_var = data.get()

    obs = find_var(s_var,    obsname)
    wgt = find_var(s_var, weightname)

    s_var_w = ROOT.RooArgSet(obs, wgt)

    dataname = '{}_{}_{}'.format(data.GetName(), obsname, weightname)
    data_wgt = ROOT.RooDataSet(dataname, '', s_var_w, weightname)

    nentries = data.numEntries()

    for i_entry in range(nentries):
        data.get(i_entry)
        wgt_val = wgt.getVal()
        data_wgt.add(s_var_w, wgt_val)

    return data_wgt
#-------------------------------------------------------
def get_dataset(dataname, tree, var, weight = None): 
    min_obs  = var.getMin()
    max_obs  = var.getMax()
    varname  = var.GetName()

    tree.SetBranchStatus('*', 0)

    check_tree_var(tree, varname)
    tree.SetBranchStatus(varname, 1)

    f_var = ROOT.TTreeFormula('var', varname, tree)

    if weight is None:
        s_var   = ROOT.RooArgSet(var)
        data    = ROOT.RooDataSet(dataname, '', s_var) 
        f_wgt   = None
    else:
        check_tree_var(tree, weight)
        tree.SetBranchStatus(weight, 1)
        wgt_var = ROOT.RooRealVar(weight, '', -100, 100)
        s_var   = ROOT.RooArgSet(var, wgt_var)
        data    = ROOT.RooDataSet(dataname, '', s_var, weight )
        f_wgt   = ROOT.TTreeFormula('wgt', weight, tree)

    nentries = tree.GetEntries()
    for i_entry in range(1, nentries + 1): 
        tree.GetEntry(i_entry)
        val = f_var.EvalInstance()

        if val > max_obs or val < min_obs:
            continue

        var.setVal(val)

        if weight is None: 
            data.add(s_var)
        else:
            wgt_val = f_wgt.EvalInstance(0)
            wgt_var.setVal(wgt_val)
            data.add(s_var, wgt_val)

    tree.SetBranchStatus('*', 1)

    return data
#---------------------------------------------
def check_wks_obj(wks, name, kind, retrieve = False):
    if   kind ==  'pdf':
        obj = wks.pdf(name)
    elif kind == 'data':
        obj = wks.data(name)
    elif kind ==  'var':
        obj = wks.var(name)
    else:
        log.error('Cannot check objects of kind: ' + kind)
        raise

    if not obj:
        log.error('Cannot find \"{}\" of kind \"{}\" in workspace'.format(name, kind))
        wks.Print()
        raise

    if retrieve:
        return obj
#---------------------------------------------
def get_float_pars(wks, l_skip=[]):
    l_par = wks.allVars()
    l_par_name = []
    for par in l_par:
        par_name = par.GetName()
        if par_name in l_skip:
            continue

        if par.isConstant():
            continue

        l_par_name.append(par_name)

    return l_par_name
#---------------------------------------------
def get_objects(filepath, clas=None):
    """
    Will return a pair `(d_obj, file)` where the second object is the file.
    The first object is a dictionary, the keys are the object names, the values are the objects.
    The second argument is a string with the name of the class to which the objects belong.
    """
    utnr.check_none(clas)
    utnr.check_file(filepath)

    ifile=ROOT.TFile(filepath)
    l_key=ifile.GetListOfKeys()
    d_obj={}
    for key in l_key:
        obj = key.ReadObj()
        if not obj.InheritsFrom(clas):
            continue

        name = obj.GetName()
        d_obj[name] = obj

    if len(d_obj) == 0:
        log.error('Could not find any object of type {} in:'.format(clas))
        ifile.ls()

    return (d_obj, ifile)
#---------------------------------------------
def check_null(obj, name=''):
    if not obj:
        log.error('Object {} is null'.format(name))
        raise
#---------------------------------------------
def check_root_version(req_version):
    version = ROOT.gROOT.GetVersion()
    if version < req_version:
        log.error(f'Version has to be higher or equal than {req_version}, found {version}')
        raise
#------------------------------------------


