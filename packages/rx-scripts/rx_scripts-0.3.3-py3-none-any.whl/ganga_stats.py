from sys import exit

import utils_noroot as utnr
import re
import os
import json

#log=utnr.getLogger(__name__)

#-------------------------------
class stats:
    def __init__(self, slc, rgx_proc = ''):
        self.slc      = slc
        self.d_stat   = {}
        self.rgx_skip = '\d+\.\d+\.\d+'
        self.rgx_proc = rgx_proc
    #-------------------------------
    def get_stats(self, filepath):
        print('Collecting statistics for:')
        for job in self.slc:
            name = job.name

            mtch = re.match(self.rgx_skip, name)
            if mtch:
                continue

            if self.rgx_proc != '' and not re.match(self.rgx_proc, name):
                continue

            print('{0:4}{1:<30}'.format('', name))
            self.__calculate_stats(job)

        json.dump(self.d_stat, open(filepath, 'w'))
    #-------------------------------
    def __calculate_stats(self, job):
        l_sj=job.subjobs
        jobname=job.name
        for sj in l_sj:
            if   sj.status == 'failed':
                prefix='{}.{}'.format(job.id, sj.id)
                self.__add_stats(jobname, prefix)
                continue
            elif sj.status != 'completed':
                print('Job {} / subjob {} has status {}'.formt(jobname, sj.id, sj.status))
                exit(1)

            logfile=self.__get_logfile(sj)

            self.__read_stats(jobname, logfile)
    #-------------------------------
    def __get_logfile(self, sj):
        logfile=sj.outputdir + '/Script1_Ganga_GaudiExec.log'
        if not os.path.isfile(logfile):
            print('Cannot find ' + logfile)
            return None

        return logfile
    #-------------------------------
    def __read_stats(self, jobname, logfile):
        l_jobname=jobname.split('_')
        self.ntrees = 1 if len(l_jobname) == 3 else 2

        evt_line, l_tree_line = self.__get_lines(logfile)
        evt, l_tree_evt = self.__get_entries(evt_line, l_tree_line)

        if jobname not in self.d_stat:
            fnd=len(l_tree_evt)
            if self.ntrees != fnd: 
                print('Found {} trees in {}, expected {}'.format(fnd, logfile, self.ntrees) )
                exit(1)

            self.d_stat[jobname] = (evt, l_tree_evt, 1) 
        else:
            evt_sum, l_tree_evt_sum, nfile = self.d_stat[jobname] 

            evt_sum += evt
            nfile   += 1

            exp=len(l_tree_evt_sum)
            fnd=len(l_tree_evt)

            if exp != fnd: 
                print('Found {} trees when expected {} for file {}'.format(fnd, exp, logfile))
                exit(1)

            for i_entry in range(0, exp):
                l_tree_evt_sum[i_entry] += l_tree_evt[i_entry]

            self.d_stat[jobname] = (evt_sum, l_tree_evt_sum, nfile)
    #-------------------------------
    def __add_stats(self, jobname, prefix):
        print('Reading recovered stats for ' + prefix)
        l_job=[]
        for job in self.slc:
            if prefix not in job.name:
                continue

            if job.status != 'completed':
                continue

            logfile=self.__get_logfile(job)
            self.__read_stats(jobname, logfile)
    #-------------------------------
    def __get_entries(self, evt_line, l_tree_line):
        l_evt_line=evt_line.split('|')
        tmp=l_evt_line[4]
        evt=int(tmp)
        l_tree_entries=[]
        for tree_line in l_tree_line:
            if self.ntrees == 2:
                l_tmp = tree_line.split('|')
                tmp   = l_tmp[3]
            elif self.ntrees == 1:
                l_tmp = tree_line.split(':')
                tmp   = l_tmp[1]
            else:
                print('Wrong number of trees {}'.format(self.ntrees))
                exit(1)

            tmp   = int(tmp)
    
            l_tree_entries.append(tmp)
    
        return (evt, l_tree_entries)
    #------------------------------------------
    def __get_line(self, ifile):
        try:
            line=ifile.readline()
        except:
            return ''
    
        return line
    #------------------------------------------
    def __get_lines(self, filepath):
        evt_line=''
        l_tree_line=[]
        with open(filepath) as ifile:
            while len(l_tree_line) < self.ntrees or evt_line == '':
                line=self.__get_line(ifile)

                if  not line:
                    break
                elif line == '': 
                    print('Cannot get line {} in file {}'.format(i_line, filepath))
                    continue
                elif 'EVENT LOOP' in line:
                    evt_line=line
                elif self.ntrees == 2 and '# Leptonic/Phys/B2LLX' in line:
                    l_tree_line.append(line)
                elif self.ntrees == 1 and '*Tree    :DecayTree : DecayTree' in line:
                    line=self.__get_line(ifile)
                    l_tree_line.append(line)

        return (evt_line, l_tree_line)
#------------------------------------------

