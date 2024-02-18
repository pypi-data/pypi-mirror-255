import os
import re 
import sys
import glob
import json
import signal
import inspect
import logging
import subprocess
import numpy
import math
import tarfile
import socket
import random
import time

import dill              as pickle
import matplotlib.pyplot as plt
import pandas            as pnd

from functools import wraps

DEBUG_LEVELV_NUM = 25
logging.addLevelName(DEBUG_LEVELV_NUM, "VISIBLE")
logging.VISIBLE=DEBUG_LEVELV_NUM
def visible(self, message, *args, **kws):
    if self.isEnabledFor(DEBUG_LEVELV_NUM):
        self._log(DEBUG_LEVELV_NUM, message, args, **kws) 
logging.Logger.visible = visible 
#-------------------------------------------------------
#Timeout
#-------------------------------------------------------
def timeout_handler(signum, frame):
    raise TimeoutError("Timeout occurred.")
#------------------------------------------------------------------
def add_timeout(seconds=10):
    '''
    This is a function decorator to timeout functions

    Example:

    @utils_noroot.add_timeout(seconds=5)
    val = fun()

    if the function takes longer than 5 seconds, it will be interrupted
    anf val=None
    '''
    def decorator_function(original_function):
        def wrapper_function(*args, **kwargs):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)

            result = None
            try:
                result = original_function(*args, **kwargs)
            except TimeoutError:
                log.warning(f'Timeout: > {seconds} sec.')
                raise
            finally:
                signal.alarm(0)
        
                return result
            
        return wrapper_function
    return decorator_function
#-------------------------------------------------------
#FORMATTING
#-------------------------------------------------------
def df_from_wc(wc, form='json', ignore_index=True):
    '''Used to convert wildcard to JSON files into pandas dataframe
    Parameters
    ------------------
    wc (str): Wildcard, e.g. /a/b/c/file_*.json
    form (str): Format, supported: json
    '''
    df = None

    if form not in ['json']:
        log.error(f'Format {form} not supported')
        raise

    l_df = []
    for file_path in glob.glob(wc):
        if form == 'json':
            df_part = pnd.read_json(file_path)
            l_df.append(df_part)

    df = pnd.concat(l_df, ignore_index=ignore_index)

    return df
#-------------------------------------------------------
def remove_consecutive(in_str):
    '''Will remove consecutive characters from string. e.g. XXXyyyZZ -> ZyZ

    Parameters
    -------------
    in_str (str): Input string

    Returns
    -------------
    ot_str (str): Output string
    '''
    seen   = in_str[0]
    ot_str = in_str[0]
    for char in in_str[1:]:
        if char != seen:
            ot_str += char
            seen    = char

    return ot_str 
#-------------------------------------------------------
def get_var_name(exp, repeated_underscores=True):
    '''
    Will strip expression from math-like symbols
    so that it can be used as a filename
    '''
    exp = exp.replace(' ',  '')
    exp = exp.replace('TMath::',  '')
    exp = exp.replace('(', '_')
    exp = exp.replace(')', '_')
    exp = exp.replace(':', '_')
    exp = exp.replace(',', '_')
    exp = exp.replace('.', 'p')
    exp = exp.replace('+', '_p_')
    exp = exp.replace('-', '_m_')
    exp = exp.replace('*', '_x_')
    exp = exp.replace('/', '_d_')

    if not repeated_underscores:
        exp = ''.join(dict.fromkeys(exp))

    return exp
#-------------------------------------------------------
def check_python_version(min_ver):
    this_ver = sys.version_info
    if this_ver < min_ver:
        log.error(f'Version of python found: {this_ver}')
        log.error(f'Minimum version required: {min_ver}')
        raise
#-------------------------------------------------------
#LATEX
#-------------------------------------------------------
def save_to_latex(d_data, latex_path, indices=None):
    check_type(indices, list)

    latex_dir = os.path.dirname(latex_path)
    make_dir_path(latex_dir)

    df = pnd.DataFrame(d_data, indices)
    df = df.T
    df.to_latex(index=False, buf=open(latex_path, 'w'))
#-------------------------------------------------------
def find_in_file(path, clue=None, regex=None, igroup=1):
    check_file(path)
    check_none(clue)
    check_none(regex)

    l_target = []
    with open(path) as ifile:
        l_line = ifile.readlines()
        for line in l_line:
            if clue not in line:
                continue

            mtch = re.match(regex, line)
            if not mtch:
                log.error(f'Cannot match "{regex}" in "{line}"')
                raise

            target = mtch.group(igroup)
            l_target.append(target)

    if len(l_target) == 0:
        log.error(f'Could not find in "{path}", line with clue "{clue}" and regex "{regex}"')
        raise

    return l_target
#-------------------------------------------------------
#Regex
#-------------------------------------------------------
def get_regex_group(name, rgx, i_group=None, default=None):
    """
    Will match the second argument (a regex) to the first argument and return
    a specific group (third integer argument).
    If the match fails it will raise an exception. 
    If default is specified, it will instead, return it.
    """
    check_none(i_group)
    if i_group <= 0:
        log.error('Group index has to be larger than 1.')
        raise

    mtch = re.match(rgx, name)
    if   not mtch and default is     None:
        log.error('Cannot match {} to {}'.format(name, rgx))
        raise
    elif not mtch and default is not None:
        return default

    tp_group = mtch.groups()
    if i_group > len(tp_group):
        log.error('Cannot extract group {} from: {}'.format(i_group, str(tp_group)))
        raise

    return mtch.group(i_group)
#-------------------------------------------------------
#Plots
#-------------------------------------------------------
def add_labels(arr_x, arr_y1, arr_y2, xoff, yoff, l_color=['#1f77b4', '#ff7f0e'], form='{:.3f}', angle=0):
    """
    Use yoff = 20 and xoff=0 for a reasonable plot
    """
    [color_1, color_2] = l_color
    for x, y1, y2 in zip(arr_x, arr_y1, arr_y2):
        label_1 = form.format(y1)
        label_2 = form.format(y2)

        if y1 > y2:
            yoff_1 = + yoff
            yoff_2 = - yoff
        else:
            yoff_1 = - yoff
            yoff_2 = + yoff

        plt.annotate(label_1, (x,y1), textcoords="offset points", xytext=(xoff, yoff_1), color=color_1, ha='center', rotation=angle)
        plt.annotate(label_2, (x,y2), textcoords="offset points", xytext=(xoff, yoff_2), color=color_2, ha='center', rotation=angle)
#-----------------------------
def errorbox(xdata, ydata, xerr=None, yerr=None, label=None, color='r', alpha=0.5, ax=None):
    '''
    Used to plot data with error bars as bands
    '''

    from matplotlib.collections import PatchCollection
    from matplotlib.patches     import Rectangle

    errorboxes = [Rectangle((x - xe[0], y - ye[0]), xe.sum(), ye.sum()) for x, y, xe, ye in zip(xdata, ydata, xerr.T, yerr.T)]
    pc = PatchCollection(errorboxes, facecolor=color, alpha=alpha)

    if ax is None:
        ax = plt.gca()

    ax.add_collection(pc)
    ax.errorbar(x, y, fmt='none', ecolor='k', label=label)

    return ax
#-------------------------------------------------------
#Checks
#-------------------------------------------------------
def check_included(element, container):
    if element not in container:
        log.error(f'{element} does not belong to container:')
        print(container)
        raise
#-------------------------------------------------------
def check_null(obj, name='Unnamed'):
    if not obj:
        log.error('Object with name {} not found'.format(name))
        raise
#-------------------------------------------------------
def check_type(obj, typ):
    if isinstance(obj, typ):
        return

    exp=str(typ)
    fnd=str(type(obj))
    log.error(f'Object {obj} is not of type {exp} but {fnd}')
    raise
#-------------------------------------------------------
def check_numeric(obj, l_kind=None):
    if l_kind is None:
        l_type = [int, float]
    else:
        l_type = l_kind

    obj_typ    = type(obj)
    np_num_typ = numpy.issubdtype(obj_typ, numpy.number)

    if obj_typ not in l_type and np_num_typ == False:
        log.error('Object is not numeric')
        print(obj)
        print(type(obj))
        raise
#-------------------------------------------------------
def check_contained(l_x, l_y, retrieve=False):
    '''
    Takes lists as input.

    Raises exception if:
    1. Lists do not have unique elements
    2. Neither list contains the other.

    Returns the (l_big, l_small) tuple.
    '''
    repeated = utnr.list_has_repeated(l_x) or utnr.list_has_repeated(l_y)
    if repeated:
        log.error(f'Either list has repeated elements')
        print(l_x)
        print(l_y)
        raise

    l_sup = None
    l_sub = None

    s_x = set(l_x)
    s_y = set(l_y)

    if   s_x.issubset(s_y):
        l_sub = list(s_x)
        l_sup = list(s_y)
    elif s_y.issubset(s_x):
        l_sub = list(s_y)
        l_sup = list(s_x)
    else:
        log.error('Neither list is contained in the other:')
        print(l_x)
        print(l_y)
        raise

    if retrieve:
        return (l_sup, l_sub)
#----------------------------------------
def cmp_subset(l_x, l_y):
    '''
    Comparator function

    Args: 
    Lists representing sets

    Exceptions: 
    1. Lists must have non repeated elements
    2. Either list must contain other.

    Usage:
    Pass to:

    `sorted_list_of_lists = sorted(list_of_lists, key=functools.cmp_to_key(cmp_subset))`
    '''
    if list_has_repeated(l_x) or list_has_repeated(l_y): 
        log.error(f'Either list has repeated elements')
        print(l_x)
        print(l_y)
        raise
    
    s_x = set(l_x)
    s_y = set(l_y)
    
    if   s_x.issubset(s_y) or s_y.issubset(s_x):
        return len(s_y) - len(s_x)
    else:
        log.error('Neither list is contained in the other:')
        print(l_x)
        print(l_y) 
        raise
#-------------------------------------------------------
#Containers
#-------------------------------------------------------
def add_rows_to_df(df, l_row, l_ind=None):
    if   l_ind is None:
        l_ind = [None] * len(l_row)
    elif len(l_ind) != len(l_row):
        log.error(f'Indices and rows are of different sizes: {len(l_ind)}/{len(l_row)}')
        raise

    for row, ind in zip(l_row, l_ind):
        df = add_row_to_df(df, row, index=ind)

    return df
#-------------------------------------------------------
def add_row_to_df(df, row, index=None):
    if index is None:
        l_index = df.index
        index   = len(l_index)

    try:
        df.loc[index] = row
    except:
        log.error(f'Cannot add row to dataframe at {index}:')
        print(row)
        print(df)
        raise

    return df
#-------------------------------------------------------
def glob_wc(wc, allow_empty=False):
    l_path = glob.glob(wc)

    if len(l_path) == 0 and allow_empty == False:
        log.error(f'No file found for "{wc}"')
        raise

    return l_path
#-------------------------------------------------------
def get_unique_element(arr_val):
    equal = numpy.all(arr_val == arr_val[0])
    if equal == False:
        log.error('Array has different elements')
        raise

    elm = arr_val[0]

    return elm 
#-------------------------------------------------------
def patch_dict(d_source, d_target, patch_value=None):
    check_none(patch_value)

    d_output = dict(d_target)
    for key in d_source:
        if key not in d_target:
            d_output[key] = patch_value

    return d_output
#-------------------------------------------------------
def find_dic_val(d_data, key_regex = None):
    check_none(key_regex)

    l_obj = []
    l_key = []
    for key in d_data:
        mtch = re.match(key_regex, key)
        if not mtch:
            continue

        obj = d_data[key]
        l_key.append(key) 
        l_obj.append(obj) 

    if len(l_obj) != 1:
        log.error('Not found one and only one object')
        log.info(l_key)
        raise

    return l_obj[0]
#-----------------------------------
def shrink_relation(arr_key, arr_val):
    """
    The keys are assumed to be values for the independent variable of a function
    The values are from the dependent variable.
    Thus, you are passing `(x,y)` points. 

    If for an `x` there are two different `y` the code will
    raise an exception. Otherwise, it will remove all the repeated points
    and the remaining ones will go into a dictionary that the function returns.
    """
    d_data = {}
    for key, val in zip(arr_key, arr_val):
        add_to_dic_set(d_data, key, val)

    for key, val in d_data.items():
        if len(val) != 1:
            log.error('Found key without one and only one value')
            pretty_print(d_data)
            raise

    d_out = {}
    for key, (val,) in d_data.items():
        d_out[key] = val

    return d_out
#-------------------------------------------------------
def get_instance(obj, instance):
    try:
        val = obj[instance]
        return val
    except:
        return obj
#-------------------------------------------------------
def get_elm(l_elm, i_pos):
    try:
        elm=l_elm[i_pos]
    except:
        nelm=len(l_elm)
        log.error('Cannot extract {} element in list of size {}'.format(i_pos, nelm))
        raise

    return elm
#-------------------------------------------------------
def add_to_dic_set(dic, key, val):
    if key not in dic:
        dic[key] = {val}
    else:
        dic[key].add(val)
#-------------------------------------------------------
def add_to_dic_lst(dic, key, val):
    if key not in dic:
        dic[key] = [val]
    else:
        dic[key].append(val)
#-------------------------------------------------------
def add_to_dic(dic, key, val):
    if key in dic:
        log.error('Key {} already in dictionary'.format(key))
        raise

    dic[key]=val
#-------------------------------------------------------
def get_from_dic(dic, key, fall_back=None, now=False, no_error=False):
    try:
        check_type(dic, dict)
    except:
        raise

    if   key not in dic and fall_back is     None:
        keys=str(dic.keys())
        if no_error == False:
            log.error(f'Cannot find key {key} among {keys}')
        raise
    elif key not in dic and fall_back is not None:
        keys=str(dic.keys())
        if now == False:
            log.warning(f'Cannot find key {key} among {keys}')
        obj = fall_back
    else:
        obj = dic[key]

    return obj 
#-------------------------------------------------------
def is_subset(arr_large, arr_small):
    arr_small = numpy.unique(arr_small)
    arr_inter = numpy.intersect1d(arr_large, arr_small)

    return arr_inter.size == arr_small.size
#-------------------------------------------------------
def split_list(l_data, ngroups):
    total_size=len(l_data)
    group_size=total_size/float(ngroups)
    group_size=math.ceil(group_size)

    l_l_data=[]
    for i_elem in range(0, total_size, group_size): 
        tmp=l_data[i_elem : i_elem + group_size]
        l_l_data.append(tmp)

    return l_l_data
#-------------------------------------------------------
def check_array_nonempty(arr_val):
    if arr_val.size == 0:
        log.error('Array is empty')
        print(arr_val.shape)
        raise
#-------------------------------------------------------
def check_array_size(arr_val, size, label='no-label'):
    if arr_val.size != size:
        log.error('Array {} has size {}, expected {}'.format(label, arr_val.size, size))
        print(arr_val.shape)
        raise
#-------------------------------------------------------
def check_array_shape(arr_x, arr_y, label='no-label'):
    if arr_x.shape != arr_y.shape:
        log.error('Arrays {} have different shapes'.format(label)) 
        print(arr_x.shape)
        print(arr_y.shape)
        raise
#-------------------------------------------------------
def check_array_dim(arr, dim, label='no-label'):
    arr_dim = arr.ndim
    if arr_dim != dim:
        log.error('Array {} has dimension {}, not {}'.format(label, arr_dim, dim))
        raise
#-------------------------------------------------------
def make_map(arr_key, arr_val):
    key_size = len(arr_key) 
    val_size = len(arr_val)

    if key_size != val_size: 
        log.error('Arrays have different sizes: {}/{}'.format(key_size, val_size))
        raise

    d_key_val={}
    for key, val in zip(arr_key, arr_val):
        if type(key) == numpy.ndarray:
            key = key.tolist()

        if type(key) != tuple:
            key = tuple(key)

        key = str(key)
        if key in d_key_val:
            log.error('Key {} already in dictionary'.format(key))
            raise

        d_key_val[key]=val

    return d_key_val
#-------------------------------------------------------
def is_sublist(l_x, l_y):
    s_x = set(l_x)
    s_y = set(l_y)

    return s_x.issubset(s_y)
#-------------------------------------------------------
def lists_intersect(l_x, l_y):
    s_x = set(l_x)
    s_y = set(l_y)

    s_i = s_x.intersection(s_y)

    return len(s_i) > 0
#-------------------------------------------------------
def list_has_repeated(l_x):
    s_x = set(l_x)

    return len(s_x) < len(l_x)
#-------------------------------------------------------
def intersect_lists(l_x, l_y):
    s_x = set(l_x)
    s_y = set(l_y)

    s_i = s_x.intersection(s_y)

    return list(s_i)
#-------------------------------------------------------
def symetdiff_lists(l_x, l_y):
    s_x = set(l_x)
    s_y = set(l_y)

    s_d = s_x.symmetric_difference(s_y)

    return list(s_d)
#-------------------------------------------------------
def diference_lists(l_x, l_y):
    s_x = set(l_x)
    s_y = set(l_y)

    s_d = s_x.difference(s_y)

    return list(s_d)
#-------------------------------------------------------
def check_list_equal(l_in_1, l_in_2, same_order=None):
    check_none(same_order)

    if not same_order:
        l_in_1.sort()
        l_in_2.sort()

    if l_in_1 != l_in_2:
        log.error('Lists differ:')
        log.error(l_in_1)
        log.error(l_in_2)
        raise
#-------------------------------------------------------
#File system
#-------------------------------------------------------
def extract_version(ver):
    mtch = re.match('(v(\d+\.?\d?)+).*', ver)

    if not mtch:
        log.error(f'Cannot extract version from: {ver}')
        raise

    return mtch.group(1)

def earlier_version(v1, v2):
    v1 = extract_version(v1)
    v2 = extract_version(v2)

    from packaging import version

    earlier = version.parse(v1) < version.parse(v2)

    return earlier
#-------------------------------------------------------
def add_version(path):
    '''
    Takes the path to a directory which contains or will contain subdirectories named v0, v1...

    Finds the next version and returns the path to it, i.e. /a/b/c/vx

    Makes the directory if it does not exist
    '''
    if 'VERSION' not in path:
        log.error('Invalid path, it must contain VERSION keyword')
        raise

    path_wc = path.replace('VERSION', '*')

    l_path = glob_wc(path_wc, allow_empty=True)
    if len(l_path) == 0:
        path = path.replace('VERSION', 'v0')
        return make_dir_path(path)

    l_path.sort()
    last_version = l_path[-1]

    try:
        [path_1, path_2] = path.split('VERSION')
    except:
        log.error(f'Cannot split {path} in two using VERSION delimiter')
        raise

    version = last_version.replace(path_1, '').replace(path_2, '')
    mtch = re.match('v(\d+)', version)
    if not mtch:
        log.error(f'Invalid version: {version}')
        raise

    ver_num = int(mtch.group(1)) + 1
    up_dir  = f'{path_1}/v{ver_num}'
    dn_dir  = f'{path_1}/v{ver_num}/{path_2}'

    return make_dir_path(dn_dir)
#-------------------------------------------------------
def get_latest(path):
    '''
    Takes path containing VERSION and replaces it with the latest version, then returns it
    '''
    if 'VERSION' not in path:
        log.error(f'VERSION not found in {path}')
        raise

    path = path.replace('VERSION', '*')

    l_path = glob_wc(path)
    l_path.sort()

    return l_path[-1]
#-------------------------------------------------------
def get_path_from_wc(path_wc):
    l_path = glob.glob(path_wc)

    if len(l_path) != 1:
        log.error('Not found one and only one files for: ' + path_wc)
        print(l_path)
        raise

    return l_path[0]
#-------------------------------------------------------
def check_host(host_regex = '\w+\.ihep\.ac\.cn'): 
    hostname = socket.gethostname()
    mtch = re.match(host_regex, hostname) 
    if mtch:
        return True
    else:
        return False
#-------------------------------------------------------
def force_symlink(source, target):
    try:
        os.symlink(source, target)
    except:
        os.remove(target)
        os.symlink(source, target)
#-------------------------------------------------------
def make_dir_path(dirpath):
    try:
        os.makedirs(dirpath, exist_ok=True)
    except:
        log.error('Cannot make: ')
        print(dirpath)
        raise

    return dirpath
#-------------------------------------------------------
def readCSVDict(filepath, separator_1, separator_2 = ""):
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
def check_file(filepath):
    if not os.path.isfile(filepath):
        log.error(f'Cannot find {filepath}')
        raise
#-------------------------------------------------------
def check_dir(dirpath, fail=True):
    check_none(dirpath)

    if       fail and not os.path.isdir(dirpath):
        log.error('Cannot find ' + dirpath)
        raise
    elif not fail and not os.path.isdir(dirpath):
        return False
    else:
        return True
#-------------------------------------------------------
def newer_than(path_1, path_2):
    if not os.path.isfile(path_1):
        log.error("Cannot find " + path_1)
        exit(1)

    if not os.path.isfile(path_2):
        log.error("Cannot find " + path_2)
        exit(1)

    t1 = os.path.getmtime(path_1)
    t2 = os.path.getmtime(path_2)

    return t1 > t2
#-------------------------------------------------------
def update_file(source, target):
    if not os.path.isfile(target):
        return True

    return newer_than(source, target)
#-------------------------------------------------------
def get_file_paths(dir_path):
    l_file_path = []
    for root, _, l_file_name in os.walk(dir_path):
        for file_name in l_file_name:
            file_path = os.path.join(root, file_name)
            l_file_path.append(file_path)

    return l_file_path
#-------------------------------------------------------
def tardir(dir_path, tar_name):
    handle = tarfile.open(tar_name, "w:gz")

    l_file_path = get_file_paths(dir_path)
    for file_path in l_file_path:
        log.info(f'Adding: {file_path}')
        handle.add(file_path)

    handle.close()
#-------------------------------------------------------
def untardir(source, target):
    if not os.path.isfile(source):
        log.error('TAR file {} missing'.format(source))
        raise

    obj = tarfile.open(source)
    try:
        obj.extractall(target)
    except:
        log.error('Cannot untar to {}'.format(target))
        raise

    obj.close()
#-------------------------------------------------------
def tardirs(path_wc, tar_name, compression='w:gz'):
    with tarfile.open(tar_name, compression) as tar_handle:
        l_dir = glob.glob(path_wc)
        if len(l_dir) == 0:
            log.error(f'Nothing found in {path_wc}')
            raise

        log.visible(f'Taring from {path_wc} into {tar_name} with compression {compression}')
        for path in l_dir: 
            for root, dirs, files in os.walk(path):
                for file in files:
                    filepath = os.path.join(root, file)
                    log.debug(f'Adding: {filepath}')
                    tar_handle.add(filepath)
#-------------------------------------------------------
def get_subdirs(dir_path):
    check_dir(dir_path)

    l_obj = glob.glob(dir_path + '/*')
    l_dir = []
    for obj in l_obj:
        if not os.path.isdir(obj):
            continue

        l_dir.append(obj)

    l_dir.sort()

    return l_dir
#-------------------------------------------------------
#Network
#-------------------------------------------------------
def download_file(source, target_dir = './downloaded_data'):
    target_name = os.path.basename(source)
    target='{}/{}'.format(target_dir, target_name)
    if os.path.isfile(target):
        os.remove(target)

    os.makedirs(target_dir, exist_ok=True)
    subprocess.run(['xrdcp', source, target], check=True)

    log.info('Downloading ' + target)

    return target
#-------------------------------------------------------
#Plotting
#-------------------------------------------------------
def plot_matrix(plotpath, l_x, l_y, mat, title='', upper=None, zrange=(-1, +1), form='{:.3f}', fsize=None):
    if upper is None:
        mat_p = mat
    elif     upper:
        mat_p = numpy.triu(mat, 0)
    elif not upper:
        mat_p = numpy.tril(mat, 0)

    mat_p = numpy.ma.masked_where(mat_p == 0, mat_p)

    fig, ax = plt.subplots() if fsize is None else plt.subplots(figsize=fsize)
    palette = plt.cm.viridis#.with_extremes(bad='white')
    im      = ax.imshow(mat_p, cmap=palette, vmin=zrange[0], vmax=zrange[1])
    
    ax.set_xticks(numpy.arange(len(l_x)))
    ax.set_yticks(numpy.arange(len(l_y)))

    ax.set_xticklabels(l_x)
    ax.set_yticklabels(l_y)
    
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    if form is None:
        fig.colorbar(im)
    else:
        for i_x, xval in enumerate(l_x):
            for i_y, yval in enumerate(l_y):
                try:
                    val  = mat_p[i_y, i_x]
                    if numpy.ma.is_masked(val):
                        text = ''
                    else:
                        text = form.format(val)
                except:
                    log.error(f'Cannot access ({i_x}, {i_y}) in:')
                    print(mat_p)
                    raise

                _ = ax.text(i_x, i_y, text, ha="center", va="center", color="k")
    
    ax.set_title(title)
    fig.tight_layout()
    plt.savefig(plotpath)
    plt.close('all')
#-------------------------------------------
def plot_arrays(d_data, nbins, min_x, max_x):
    for label, arr_data in d_data.items():
        plt.hist(arr_data, nbins, range=(min_x, max_x), label = label, alpha=0.75)
#-------------------------------------------
def plot_dict(d_data, label, axis=None, color='blue'):
    l_label = list(d_data.keys()) 
    l_value = list(d_data.values())
    
    if axis is None:
        fig = plt.figure()
        axis = fig.add_subplot(111)

    axis.errorbar(l_label, l_value, label=label, color=color, marker='o', linestyle='none')

    if label is not None:
        axis.legend()
    
    return axis 
#-------------------------------------------------------
#Classes
#-------------------------------------------------------
class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""
    bold_red = "\x1b[31;1m"
    grey     = "\x1b[38;21m"
    green    = "\x1b[32;21m"
    red      = "\x1b[31;21m"
    reset    = "\x1b[0m"
    yellow   = "\x1b[33;21m"
    white    = "\x1b[37;21m"
    #---------------------------------------------------
    def __init__(self, level, colors=True, length='short'):
        super(CustomFormatter, self).__init__()
        if   length == 'long':
            form = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
        elif length == 'short' and     colors:
            form = "[%(filename)20s:%(lineno)4s ] %(message)s"
        elif length == 'short' and not colors:
            form = "[%(levelname)10s:%(filename)20s:%(lineno)4s ] %(message)s"
        else:
            print('Wrong length ' + length)
            raise

        self.FORMATS={}

        if colors:
            self.FORMATS[logging.DEBUG   ]= self.grey     + form + self.reset
            self.FORMATS[logging.INFO    ]= self.white    + form + self.reset
            self.FORMATS[logging.VISIBLE ]= self.green    + form + self.reset
            self.FORMATS[logging.WARNING ]= self.yellow   + form + self.reset
            self.FORMATS[logging.ERROR   ]= self.red      + form + self.reset
            self.FORMATS[logging.CRITICAL]= self.bold_red + form + self.reset
        else:
            self.FORMATS[logging.DEBUG   ]= form
            self.FORMATS[logging.INFO    ]= form
            self.FORMATS[logging.VISIBLE ]= form
            self.FORMATS[logging.WARNING ]= form
            self.FORMATS[logging.ERROR   ]= form
            self.FORMATS[logging.CRITICAL]= form
    #---------------------------------------------------
    def format(self, record):
        log_fmt   = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)

        return formatter.format(record)
#-------------------------------------------------------
#Math
#-------------------------------------------------------
def correlation_from_covariance(covariance):
    v = numpy.sqrt(numpy.diag(covariance))
    outer_v = numpy.outer(v, v)
    correlation = covariance / outer_v
    correlation[covariance == 0] = 0
    return correlation
#-------------------------------------------------------
def getLogger(name, level = logging.INFO, length='short', filename="", skip_handler=False):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if os.path.isfile(filename):
        os.remove(filename)

    if filename != '':
        h=logging.FileHandler(filename)
        f=CustomFormatter(level, colors=False, length=length)
    else:
        h=logging.StreamHandler(sys.stdout)
        f=CustomFormatter(level, colors=True , length=length)
   
    h.setFormatter(f)
    if not skip_handler: 
        logger.addHandler(h)

    return logger
#-------------------------------------------------------
def get_closeness(a, b, epsilon=1e-7):
    tol = 2 * abs(a - b) / (a + b)

    is_close = True
    if tol > epsilon:
        log.warning('{:.3e} = 2 * abs({:.3e} - {:.3e}) / ({:.3e} + {:.3e}) > {:.3e}'.format(tol, a, b, a, b, epsilon))
        is_close = False

    return (tol, is_close) 
#-------------------------------------------------------
def check_close(a, b, epsilon=1e-7, fail=True, verbose=False):
    tol = 2 * abs(a - b) / (a + b)

    if   tol > epsilon and not fail:
        log.warning('{:.3e} = 2 * abs({:.3e} - {:.3e}) / ({:.3e} + {:.3e}) > {:.3e}'.format(tol, a, b, a, b, epsilon))
        return False
    elif tol > epsilon and     fail: 
        log.error('{:.3e} = 2 * abs({:.3e} - {:.3e}) / ({:.3e} + {:.3e}) > {:.3e}'.format(tol, a, b, a, b, epsilon))
        raise

    if verbose:
        log.visible('{:.3e} = 2 * abs({:.3e} - {:.3e}) / ({:.3e} + {:.3e}) > {:.3e}'.format(tol, a, b, a, b, epsilon))

    return True
#-------------------------------------------------------
def check_attr(obj, name):
    if not hasattr(obj, name):
        typename = type(obj)
        log.error('Object of type {} does not have attribute {}'.format(typename, name))
        raise
#-------------------------------------------------------
def check_none(obj):
    if obj is None:
        log.error('Object is None')
        raise
#-------------------------------------------------------
def check_no_none(obj):
    if obj is not None:
        log.error('Object is not None')
        raise
#-------------------------------------------------------
def check_nonempty(cont):
    if len(cont) == 0:
        log.error('Container is empty')
        raise
#-------------------------------------------------------
def get_attr(obj, name):
    check_attr(obj, name)

    return getattr(obj, name)
#-------------------------------------------------------
def str_to_tup(str_tup, kind):
    stripped = str_tup.replace('(', '').replace(')', '')
    l_val    = stripped.split(',')

    tp_val    = tuple(map(kind, l_val))

    str_tup_out = str(tp_val)

    #if str_tup_out != str_tup:
    #    log.error('Could not convert {}, output {}'.format(str_tup, str_tup_out))
    #    raise

    return tp_val
#-------------------------------------------------------
def glob_regex(path, regex, empty_ok=False):
    """
    Given the path to a directory, it will return, in a list, the paths
    to all the files whose names follow the regex.
    By default an exception is risen if no files are found, unless `empty_ok=False`
    """
    l_obj = glob.glob(path + '/*')
    l_res = []
    for obj in l_obj:
        name = os.path.basename(obj)
        if not re.match(regex, name):
            continue
        l_res.append(obj)

    l_res.sort()

    if len(l_res) == 0 and empty_ok == False:
        log.error('No files/directories found in {} for {}'.format(path, regex))
        raise

    return l_res
#-------------------------------------------------------
def get_efficiency(arr_val, weight=None, rng=None):
    try:
        a, b  = rng
        min_x = min(a, b)
        max_x = max(a, b)
    except:
        log.error('Invalid range:')
        print(rng)
        raise

    if weight is None:
        arr_wgt = numpy.ones(arr_val.size)
    else:
        arr_wgt = weight

    if arr_wgt.size != arr_val.size:
        log.error('Values and weights have different sizes: {}/{}'.format(arr_val.size, arr_wgt.size))
        raise

    total = numpy.sum(arr_wgt)
    passd = 0
    for val, wgt in zip(arr_val, arr_wgt):
        if val > min_x and val < max_x:
            passd+=wgt

    return float(passd) / total
#-------------------------------------------------------
def normalize_weights(arr_wgt, kind='area'):
    if   kind == 'area':
        sum_wgt   = numpy.sum(arr_wgt)
        num_wgt   = arr_wgt.size
        fac       = num_wgt / sum_wgt
    elif kind == 'error':
        sum_wgt_1 = numpy.sum(arr_wgt)
        sum_wgt_2 = numpy.sum(arr_wgt * arr_wgt)
        fac       = sum_wgt_1 / sum_wgt_2
    elif kind == 'none':
        fac       = 1
    else:
        log.error('Wrong normalization kind: ' + kind)
        raise

    log.info('Normalizing with factor/type:{:.3f}/{}'.format(fac, kind))
    arr_wgt_norm = fac * arr_wgt

    return arr_wgt_norm
#-------------------------------------------------------
def timeit(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        mod_nam = inspect.getmodule(f).__name__
        fun_nam = f.__name__
        log.visible(f'{mod_nam}.py:{fun_nam}; Time: {te-ts:.3f}s')

        return result
    return wrap
#-------------------------------------------------------
#Math
#-------------------------------------------------------
def avg(*l_arg):
    tot = 0 
    size = float(len(l_arg))

    if size == 0:
        log.error('Empty array introduced')
        raise

    for arg in l_arg:
        if type(arg) not in [int, float]:
            log.error('Argument {} is not a number'.format(arg))
            raise
        tot += arg 

    return tot / size
#-------------------------------------------------------
#Saving/Loading
#-------------------------------------------------------
def make_path_dir(file_path):
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
#-------------------------------------------------------
def dump_list(l_data, file_path):
    make_path_dir(file_path)

    ofile = open(file_path, 'w')
    for data in l_data:
        ofile.write(data + '\n')
    ofile.close()
#-------------------------------------------------------
def dump_pickle(data, file_path):
    make_path_dir(file_path)

    file_dir = os.path.dirname(file_path)
    make_dir_path(file_dir)

    pickle.dump(data, open(file_path, 'wb'))
#-------------------------------------------------------
def load_pickle(path, fail_return=None):
    try:
        check_file(path)
    except:
        if fail_return is not None:
            return fail_return
        else:
            raise

    try:
        obj=pickle.load(open(path, 'rb'))
    except:
        log.error(f'Cannot load {path}')
        raise
    
    return obj
#-------------------------------------------------------
def load_text(path):
    check_file(path)

    with open(path) as ifile:
        l_line = ifile.read().splitlines()

    return l_line
#-------------------------------------------------------
#JSON
#-------------------------------------------------------
def load_json(jsonpath, decoder=None):
    check_file(jsonpath)

    with open(jsonpath) as ifile:
        obj=json.loads(ifile.read(), object_hook=decoder)

    return obj
#-------------------------------------------------------
def dump_json(data, json_path, sort_keys=False, encoder=None):
    json_dir = os.path.dirname(json_path)
    make_dir_path(json_dir)

    json.dump(data, open(json_path, 'w'), indent=4, sort_keys=sort_keys, default=encoder)
#-------------------------------------------------------
def filter_list(l_value, zscore = 3):
    from scipy import stats

    df=pnd.DataFrame({'data': l_value})
    df['z_score']=stats.zscore(df['data'])
    df = df.loc[df['z_score'].abs() <= zscore]

    return df['data'].to_list()
#-------------------------------------------------------
def remove_outliers(l_value, l_zscore=[4, 4, 3]):
    for zscore in l_zscore:
        l_value = filter_list(l_value, zscore = zscore)

    return l_value
#-------------------------------------------------------
def remove_nan_inf(arr_val, var_name = 'Untitled'):
    arr_nan  = numpy.isnan(arr_val)
    n_nan    = numpy.count_nonzero(arr_nan)
    arr_val  = arr_val[~arr_nan]
    if n_nan != 0:
        log.warning('{0:<10}{1:<20}{2:<20}'.format('NaN', var_name, n_nan))

    arr_inf  = numpy.isinf(arr_val)
    n_inf    = numpy.count_nonzero(arr_inf)
    arr_val  = arr_val[~arr_inf]
    if n_inf != 0:
        log.warning('{0:<10}{1:<20}{2:<20}'.format('Inf', var_name, n_inf))

    return arr_val
#-------------------------------------------------------
#Printers
#-------------------------------------------------------
def print_dict(d_data, header = ''):
    log.info('-------------')
    log.info(header)
    log.info('-------------')
    for key, val in d_data.items():
        log.info('{0:<20}{1:<20}'.format(key, val))
    log.info('-------------')
#-------------------------------------------------------
def pretty_print(obj, sort=True):
    import pprint

    pprint.pprint(obj, indent=4)
#-------------------------------------------------------
def print_list(l_data, col_width=10):
    line = f''
    for data in l_data:
        line += f'{data:<{col_width}}'
    print(line)
#-------------------------------------------------------
def trim_substring(string, substr):
    orig_string=string
    while True:
        string=string.replace(substr+substr, substr)
        if string == orig_string:
            break
        else:
            orig_string = string

    return string
#-------------------------------------------------------
#Pandas
#---------------------------
def pad_df(df, index, pad):
    if index in df.index:
        return df

    row = pnd.Series(pad, name=index, index=df.columns)
    df  = df.append(row)

    return df
#---------------------------
def equalize(df_1, df_2, pad=None):
    '''
    Given two dataframes whose indices do not match, this function
    will add the missing indices and the columns will be padded with a
    given value.
    '''
    l_id_1 = df_1.index.tolist()
    l_id_2 = df_2.index.tolist()

    s_id = set(l_id_1 + l_id_2)
    l_id = list(s_id)
    l_id.sort()

    for index in l_id:
        df_1 = pad_df(df_1, index, pad)
        df_2 = pad_df(df_2, index, pad)

    df_1 = df_1.sort_index()
    df_2 = df_2.sort_index()

    return df_1, df_2
#---------------------------
def get_axis(df, column):
    '''
    When plotting in function of a given column, this returns the 
    locations and labels that go in:

    plt.xticks(l_loc, l_lab, rotation=30)
    '''
    l_lab=getattr(df, column).tolist()
    l_loc=range(len(l_lab))

    return (l_loc, l_lab)
#---------------------------
def df_to_tex(df, path, hide_index=True, d_format=None, caption=None):
    '''
    Saves pandas dataframe to latex

    Parameters
    -------------
    d_format (dict) : Dictionary specifying the formattinng of the table, e.g. `{'col1': '{}', 'col2': '{:.3f}', 'col3' : '{:.3f}'}`
    '''

    if path is not None:
        dir_name = os.path.dirname(path)
        make_dir_path(dir_name)

    st = df.style
    if hide_index:
        st=st.hide(axis='index')

    if d_format is not None:
        st=st.format(formatter=d_format)

    log.visible(f'Saving to: {path}')
    buf = st.to_latex(buf=path, caption=caption, hrules=True)

    return buf
#---------------------------
#Numpy
#---------------------------
def numpy_multiply(arr_1, arr_2, same_size=None):
    check_included(same_size, [True, False])

    if same_size == True and arr_1.shape != arr_2.shape:
        log.error(f'Cannot multiply arrays of different size:')
        print(arr_1.shape)
        print(arr_2.shape)
        raise

    try:
        arr_t = arr_1 * arr_2
    except:
        log.error(f'Cannot multiply arrays:')
        print(arr_1.shape, arr_1.dtype)
        print(arr_2.shape, arr_2.dtype)
        raise

    return arr_t
#---------------------------
def get_binning(nbins, arr_data, quant=0.02):
    '''
    For a given array with data, will get uniform binning array with nbins, 
    between boundaries that are at the quant and 1-quant quantiles of the data
    '''
    min_data = numpy.quantile(arr_data,     quant)
    max_data = numpy.quantile(arr_data, 1 - quant)

    arr_bin  = numpy.linspace(min_data, max_data, nbins)

    return arr_bin
#---------------------------
log=getLogger(__name__)

