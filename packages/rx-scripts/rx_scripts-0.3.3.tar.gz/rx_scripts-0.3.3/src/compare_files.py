import ROOT

from tqdm import tqdm

import utils_noroot as utnr
import re
import utils
import numpy
import argparse

log=utnr.getLogger(__name__)
#------------------
def check_trees(d_tree_1, d_tree_2, l_exclude):
    l_treename_1 = list(d_tree_1.keys())
    l_treename_2 = list(d_tree_2.keys())

    if l_treename_1 != l_treename_2:
        log.warning('Files contain different trees')
        log.warning(l_treename_1)
        log.warning(l_treename_2)

    s_treename_1 = set(l_treename_1)
    s_treename_2 = set(l_treename_2)

    s_treename = s_treename_1.intersection(s_treename_2)

    for treename in s_treename:
        if treename in l_exclude:
            continue

        tree_1 = d_tree_1[treename]
        tree_2 = d_tree_2[treename]

        entries_1 = tree_1.GetEntries()
        entries_2 = tree_2.GetEntries()

        if entries_1 != entries_2:
            log.error('Tree {} differs in entries {}/{}'.format(treename, entries_1, entries_2))
            raise

    return list(s_treename) 
#------------------
def get_data(tree, max_entries):
    df = ROOT.RDataFrame(tree)
    if max_entries > 0:
        df = df.Range(max_entries)

    d_data = df.AsNumpy(exclude=[])

    return d_data
#------------------
def check_branches(l_branch_1, l_branch_2, non_overlap):
    s_branch_1 = set(l_branch_1)
    s_branch_2 = set(l_branch_2)

    if l_branch_1 != l_branch_2:
        s_branch_1_m_2 = s_branch_1.difference(s_branch_2)
        s_branch_2_m_1 = s_branch_2.difference(s_branch_1)

        log.info('In File 1, but not File 2')
        for branchname in s_branch_1_m_2:
            log.info('    ' + branchname)

        log.info('In File 2, but not File 1')
        for branchname in s_branch_2_m_1:
            log.info('    ' + branchname)

        if not non_overlap:
            log.error('Branches differ for tree ' + treename)
            raise
#------------------
def compare_branches(treename, d_data_1, d_data_2, non_overlap):
    l_branch_1 = list(d_data_1.keys())
    l_branch_2 = list(d_data_2.keys())

    l_branch_1.sort()
    l_branch_2.sort()

    s_branch_1 = set(l_branch_1)
    s_branch_2 = set(l_branch_2)

    s_branch = s_branch_1.intersection(s_branch_2)

    check_branches(l_branch_1, l_branch_2, non_overlap)

    return list(s_branch) 
#------------------
def compare(treename, d_data_1, d_data_2, non_overlap):
    log.info('Comparing branches') 
    l_branchname = compare_branches(treename, d_data_1, d_data_2, non_overlap)

    log.info('Comparing contents') 
    for branchname in l_branchname:
        arr_val_1 = d_data_1[branchname]
        arr_val_2 = d_data_2[branchname]

        str_type = arr_val_1.dtype.__str__()

        if   str_type == 'object':
            continue
        elif str_type not in ['int32', 'uint32', 'uint64', 'float64']:
            log.info('Skipping {}, {}'.format(branchname, str_type) )
            continue

        if not numpy.array_equal(arr_val_1, arr_val_2):
            log.error('Branch {} in tree {} differ'.format(branchname, treename))
            log.error(arr_val_1)
            log.error(arr_val_2)
            raise

    log.visible(f'Trees {treename} have same contents')
#------------------
def update_keys(d_tree):
    d_out = {}

    for key, val in d_tree.items():
        #Remove everything before .root/ and use it as new key
        new_key = re.sub(r'^.*\.root/', '', key)
        d_out[new_key] = val

    return d_out
#------------------
def validate(file_1, file_2, max_entries, l_exclude, non_overlap):
    utnr.check_file(file_1)
    utnr.check_file(file_2)

    ifile_1 = ROOT.TFile(file_1)
    ifile_2 = ROOT.TFile(file_2)

    d_tree_1 = utils.getTrees(ifile_1, rtype='dict')
    d_tree_1  = update_keys(d_tree_1)

    d_tree_2 = utils.getTrees(ifile_2, rtype='dict')
    d_tree_2  = update_keys(d_tree_2)

    l_key = check_trees(d_tree_1, d_tree_2, l_exclude) 

    log.info('Found common trees:')
    log.info(l_key)

    for treename in l_key: 
        if treename in l_exclude:
            log.info('Skipping ' + treename)
            continue
        else:
            log.info('Checking ' + treename)

        tree_1 = d_tree_1[treename]
        tree_2 = d_tree_2[treename]

        log.info('Getting reference')
        d_data_1= get_data(tree_1, max_entries)

        log.info('Getting new')
        d_data_2= get_data(tree_2, max_entries)

        log.info('Comparing')
        compare(treename, d_data_1, d_data_2, non_overlap)

    ifile_1.Close()
    ifile_2.Close()
#------------------
def main():
    parser = argparse.ArgumentParser(description='Used to validate versions of code that produce potentially different files')
    parser.add_argument('file1'         ,  type=str, help='First file')
    parser.add_argument('file2'         ,  type=str, help='Second file')
    parser.add_argument('--max_entries' ,  type=int, help='By default will run over everything', default=-1)
    parser.add_argument('--exclude'     , nargs='+', help='List of trees that should not be compared', default=[], )
    parser.add_argument('--non_overlap' , help='If used, will compare only common branches.', action='store_true')

    args = parser.parse_args()

    if args.max_entries != -1:
        log.info('Limiting to {} entries'.format(args.max_entries))

    validate(args.file1, args.file2, args.max_entries, args.exclude, args.non_overlap)
#------------------
if __name__ == '__main__':
    main()

