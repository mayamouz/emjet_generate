from string import Template
from collections import OrderedDict
import os
import subprocess

cmssw_base = os.environ['CMSSW_BASE'] #MA
print cmssw_base
genfraglinkdir = os.path.join(cmssw_base, 'src/Configuration/GenProduction/python/EmJet/')
print 'genfraglinkdir: ' , genfraglinkdir
if not os.path.exists(genfraglinkdir):
    os.makedirs(genfraglinkdir)

def getjobname(mass_X_d, mass_pi_d, tag_tau_pi_d):
    jobname = 'mass_X_d_%d_mass_pi_d_%d_tau_pi_d_%s' % (mass_X_d, mass_pi_d, tag_tau_pi_d)
    return jobname


jobdirname = 'jobs'
crabconfigname = 'crabConfig.py'
values = {}
#values['mass_X_d']   = [400, 600, 800, 1000, 1500, 2000]
#values['tau_pi_d']   = [0.001, 0.1, 1., 5., 150., 300.]
#values['mass_pi_d']  = [1, 2, 5, 10]
values['mass_X_d']   = [400]
values['tau_pi_d']   = [0.001]
values['mass_pi_d']  = [1]

tags_tau_pi_d = {0.001 : '0p001', 0.1 : '0p1', 1. : '1', 5. : '5', 150. : '150', 300. : '300'}

for mass_X_d in values['mass_X_d']:
    for tau_pi_d in values['tau_pi_d']:
        for mass_pi_d in values['mass_pi_d']:
            tag_tau_pi_d = tags_tau_pi_d[tau_pi_d]
            jobname = getjobname(mass_X_d, mass_pi_d, tag_tau_pi_d)
            ########################################
            # Generate generator fragment
            ########################################
            mass_q_d   = 2 * mass_pi_d
            mass_rho_d = 4 * mass_pi_d
            tag_tau_pi_d = tags_tau_pi_d[tau_pi_d]
            genfragname = '%s_cfi.py' % jobname
            configname = '%s_cfg.py' % jobname
            print 'Outputfile name: ', genfragname
            if not os.path.exists(os.path.join(jobdirname, jobname)):
                os.makedirs(os.path.join(jobdirname, jobname))

            kwdict = {}
            kwdict['mass_X_d']   = mass_X_d
            kwdict['mass_rho_d'] = mass_rho_d
            kwdict['mass_q_d']   = mass_q_d
            kwdict['mass_pi_d']  = mass_pi_d
            kwdict['tau_pi_d']   = tau_pi_d

            cwd = os.getcwd() #MA
            genfragtemplate = open('template_genfragment_cfi.py', 'r')
            genfragpath = os.path.join(cwd, jobdirname, jobname, genfragname)
            genfragfile = open (genfragpath, 'w')
            configpath = os.path.join(cwd, jobdirname, jobname, configname)
            for line in genfragtemplate:
                t = Template(line)
                subline = t.substitute(kwdict)
                # print subline.rstrip('\n')
                genfragfile.write(subline)
            genfraglinkpath = os.path.join(genfraglinkdir, genfragname)
            print 'genfraglinkpath: ', genfraglinkpath
            os.system('ln -sf %s %s' % (genfragpath, genfraglinkpath) ) #MA
            # Call `scram b` to compile generator fragment
            cwd = os.getcwd() #MA
            print cwd         #MA
            os.chdir(os.path.join(cmssw_base, 'src')) #MA
            result = subprocess.check_output('scram b', shell=True) #MA
            print result
            os.chdir(cwd)      #MA


            ########################################
            # Generate config file using cmsDriver
            ########################################
	    genfraglinkrelpath = os.path.relpath(genfraglinkpath, os.path.join(cmssw_base, 'src') )
            command_runCmsDriver = './runCmsDriver.sh %s %s' % (genfraglinkrelpath, configpath)
            print command_runCmsDriver
            os.system(command_runCmsDriver)

            ########################################
            # Generate CRAB config file
            ########################################
            kwdict_crab = {}
            kwdict_crab['configpath'] = configpath
            kwdict_crab['jobname'] = jobname
            kwdict_crab['eventsperjob'] = 100
            kwdict_crab['totalevents'] = 100
            kwdict_crab['lfndirbase'] = '/store/user/mamouzeg/EmJet/'
            kwdict_crab['storagesite'] = 'T3_US_UMD'

            crabconfigtemplate = open('template_crabConfig.py', 'r')
            crabconfigpath = os.path.join(jobdirname, jobname, crabconfigname)
            crabconfigfile = open(crabconfigpath, 'w')
            for line in crabconfigtemplate:
                t = Template(line)
                subline = t.substitute(kwdict_crab)
                # print subline.rstrip('\n')
                crabconfigfile.write(subline)


for mass_X_d in values['mass_X_d']:
    for tau_pi_d in values['tau_pi_d']:
        for mass_pi_d in values['mass_pi_d']:
            jobname = getjobname(mass_X_d, mass_pi_d, tag_tau_pi_d)
            ########################################
            # Submit CRAB tasks
            ########################################
	    print os.getcwd()
            crabconfigpath = os.path.join(jobdirname, jobname, crabconfigname)
	    print 'crab submit %s' % crabconfigpath
            #os.system('crab submit %s' % crabconfigpath)
