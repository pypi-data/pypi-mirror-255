#!/usr/bin/env python

import ROOT

import glob
import argparse
import os
import re

import utils
import utils_noroot as utnr
import style 
import pandas       as pnd

from matplotlib import pyplot as plt

ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.ERROR)
log=utnr.getLogger(__name__)
#-----------------------------
def readSetting(settingspath, name):
    regex="^{}\s*:\s*(.*)\s*".format(name)

    ifile=open(settingspath)
    l_line=ifile.read().splitlines()
    ifile.close()
    for line in l_line:
        match = re.search(regex, line)
        if match:
            setting=match.group(1)
            return setting.replace(" ", "")

    log.info('Could not find {} line in {}'.format(name, settingspath) )
    raise 
#-----------------------------
def printResults(filepath):
    ifile=ROOT.TFile(filepath)
    l_key=ifile.GetListOfKeys()
    for key in l_key:
        obj=key.ReadObj()
        if obj.InheritsFrom("RooFitResult"):
            name=obj.GetName()
            print("---------------------------")
            print(name)
            print("---------------------------")
            obj.Print()

    ifile.Close()
#-----------------------------
def printWorkspace(filepath):
    ifile=ROOT.TFile(filepath)
    ifile.wks.Print()
    ifile.Close()
#-----------------------------
def getSlices():
    try:
        SLICE=readSetting("slice")
    except:
        log.info("Could not find any slice")
        return ("none", [])

    regex="([0-9a-zA-Z_]+),([0-9]+),([-0-9.]+),([-0-9.]+)(;\[([0-9]+)-([0-9]+)\])?"
    l_bound=[]

    mtch=re.search(regex, SLICE)
    if not mtch:
        log.error('Cannot match ' + SLICE)
        raise

    varname= mtch.group(1)
    nbins  = int(mtch.group(2))
    minvar = float(mtch.group(3))
    maxvar = float(mtch.group(4))

    dx=(maxvar - minvar)/nbins

    for i_bound in range(0, nbins + 1):
        bound = minvar + dx * i_bound
        l_bound.append(bound)

    str_min_mrg = mtch.group(6)
    str_max_mrg = mtch.group(7)
    if (str_min_mrg is not None) and (str_max_mrg is not None):
        min_mrg = int(mtch.group(6))
        max_mrg = int(mtch.group(7))

        l_bound = l_bound[0 : min_mrg] + l_bound[max_mrg : ]

    return (varname, l_bound) 
#-----------------------------
def plot(fitdir, d_opt = {}):
    d_pars = doPlot(fitdir, d_opt = d_opt)

    return d_pars
#-----------------------------
def doPlot(fitdir, d_opt = {}):
    log.info(f'Using fit directory: {fitdir}')
    filepath=utnr.get_path_from_wc(f'{fitdir}/*.root')

    log.info(f'Plotting: {filepath}')
    utils.plotFit(filepath, l_save_scale=['lin', 'log'], d_opt=d_opt)

    skip_regex  = None
    if 'skip'   in d_opt:
        skip_regex = d_opt['skip']

    filter_regex= None
    if 'filter' in d_opt:
        filt_regex = d_opt['filter']

    file_dir = filepath.replace('.root', '')
    d_pars   = get_dpars(filepath, skip_regex = skip_regex, filter_regex = filter_regex, normalize='range')

    if 'pars' in d_opt and d_opt['pars']:
        plot_pars(d_pars, file_dir, d_opt)

    if 'reso' in d_opt and d_opt['reso']:
        plot_reso(d_pars, file_dir, d_opt)

    d_pars = get_dpars(filepath, skip_regex = skip_regex, filter_regex = filter_regex, normalize='none')
    if 'pref' in d_opt and d_opt['pref']:
        l_yield = get_model_yields(filepath)
        plot_pref(d_pars, file_dir, l_yield, d_opt)

    return d_pars 
#-----------------------------
def plot_pars(d_pars, plot_dir, d_opt):
    l_label=[]
    l_fnl=[]
    l_err=[]
    for label, (_, _, fnl, err) in d_pars.items():
        l_label.append(label)
        l_fnl.append(fnl)
        l_err.append(err)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.errorbar(l_fnl, l_label, xerr = l_err, label='Fitted', marker='o', linestyle='none')

    ax.set_xlim(0, 1)
    if 'title' in d_opt:
        title = d_opt['title']
        ax.set_title(title)
    ax.xaxis.tick_top()
    ax.grid(True)

    plt.xlabel('Normalized value')
    plt.ylabel('Parameter')

    plot_path = f'{plot_dir}/pars_fit.png'
    log.visible(f'Saving to: {plot_path}')
    plt.savefig(plot_path)
    plt.close('all')
#-----------------------------
def plot_reso(d_pars, plot_dir, d_opt):
    l_labl=[]
    l_reso=[]

    for labl, (_, _, fnl, err) in d_pars.items():
        if err <= 0:
            log.warning(f'Error {err:.3f} found')
            reso = 0
        else:
            reso = 100 * err /fnl

        l_labl.append(labl)
        l_reso.append(reso)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.errorbar(l_reso, l_labl, marker='o', linestyle='none')

    ax.set_xlim(0, 100)
    ax.xaxis.tick_top()
    if 'title' in d_opt:
        title = d_opt['title']
        ax.set_title(title)
    ax.grid(True)

    plt.xlabel('Resolution[%]')
    plt.ylabel('Parameter')

    plot_path = f'{plot_dir}/pars_reso.png'
    log.visible(f'Saving to: {plot_path}')
    plt.savefig(plot_path)
    plt.close('all')
#-----------------------------
def plot_pref(d_pars, plot_dir, l_yield, d_opt):
    df = pnd.DataFrame(columns=['Parameter', 'Prefit value', 'Prefit error', 'Postfit value', 'Postfit error'])

    for labl, (val_pre, err_pre, val_pos, err_pos) in d_pars.items():
        if labl in l_yield:
            continue

        l_row_val = [labl, val_pre, err_pre, val_pos, err_pos]
        df = utnr.add_row_to_df(df, l_row_val) 

    nrow=df.shape[0]

    fig, axes = plt.subplots(nrow, 1, figsize=(6, 10))

    for i_row, row in df.iterrows():
        v1 = row['Prefit value' ]
        e1 = row['Prefit error' ]

        v2 = row['Postfit value']
        e2 = row['Postfit error']

        ax=axes[i_row]
        ax.errorbar([v2], [row['Parameter']], xerr=[e2], label='Postfit', marker='o', color='red' , linestyle='none')
        ax.errorbar([v1], [row['Parameter']], xerr=[e1], label= 'Prefit', marker='*', color='blue', linestyle='none')

        min_x = min(v1 - 4 * e1, v2 - 4 * e2)
        max_x = max(v1 + 4 * e1, v2 + 4 * e2)

        ax.set_xlim(min_x, max_x)
        ax.grid(True)

    handles, labels = axes[i_row].get_legend_handles_labels()
    fig.legend(handles, labels)

    title = ''
    if 'title' in d_opt:
        title = d_opt['title']
    fig.suptitle(title)

    plot_path = f'{plot_dir}/pars_pref.png'
    log.visible(f'Saving to: {plot_path}')
    plt.savefig(plot_path)
    plt.close('all')
#-----------------------------
def get_dpars(filepath, normalize=None, skip_regex=None, filter_regex=None):
    result = get_result(filepath, slc=0)

    l_par_fnal = result.floatParsFinal()
    l_par_init = get_model_pars(filepath)

    d_par = {}
    for par_fnal in l_par_fnal:
        par_name = par_fnal.GetName()
        if   skip_regex is not None and     re.match(  skip_regex, par_name):
            log.info(f'Skipping {par_name}')
            continue

        if filter_regex is not None and not re.match(filter_regex, par_name):
            log.info(f'Filter out {par_name}')
            continue

        par_init = utils.find_var(l_par_init, par_name)

        fval, ferr = utils.get_par_val(par_fnal, normalize=normalize)
        ival, ierr = utils.get_par_val(par_init, normalize=normalize)

        d_par[par_name] = (ival, ierr, fval, ferr)

    return d_par
#-----------------------------
def get_model_pars(filepath):
    d_obj, _ = utils.get_objects(filepath, clas='RooWorkspace')

    wks = utnr.find_dic_val(d_obj, key_regex = 'wks')
    wks.loadSnapshot('prefit')

    l_var = wks.allVars()

    return l_var 
#-----------------------------
def get_model_yields(filepath):
    d_obj, _ = utils.get_objects(filepath, clas='RooWorkspace')

    wks = utnr.find_dic_val(d_obj, key_regex = 'wks')

    model = utils.check_wks_obj(wks, 'model', 'pdf', retrieve=True)

    if model.InheritsFrom('RooProdPdf'):
        l_pdf = model.pdfList()
        log.info(f'Found RooProdPdf, taking first PDF as model, assumming the rest are constraints')
        model = l_pdf.at(0)

    if not model.InheritsFrom('RooAddPdf'):
        log.error(f'PDF does not inherit from RooAddPdf => cannot get yields.')
        model.Print()
        raise

    l_yield_var  = model.coefList()
    l_yield_name = [ yield_var.GetName() for yield_var in l_yield_var ]

    return l_yield_name
#-----------------------------
def get_result(filepath, slc=None):
    utnr.check_none(slc)

    d_obj, _ = utils.get_objects(filepath, clas='RooFitResult')

    try:
        regex  = f'result_.*_{slc:02}'
        result = utnr.find_dic_val(d_obj, key_regex = regex)
    except:
        log.error(f'Cannot find result object in {filepath} matching {regex}')
        raise

    return result
#-----------------------------
def main():
    parser = argparse.ArgumentParser(description='Used to make fit plots from ROOT file containing model')
    parser.add_argument('fitdir' , type=str, help='Directory with fit output.')
    args = parser.parse_args()
    doPlot(args.fitdir)
#-----------------------------
if __name__ == '__main__':
    main()

