"""Custom dicom to bids conversion script for NDA submission

assumes that you have installed dcm2niix and dcm2bids
	"conda install -c conda-forge dcm2niix"
	"pip install dcm2bids"

also assumes that you have all of the config files in the dicom folder
	i.e. CCX_dcm/ccx_ses-1.json
	     CCX_dcm/ccx_ses-2.json
		 CCX_dcm/ccx_ses-3.json
		 CCX_dcm/ccx_ses-3-pre-10.json
		 CCX_dcm/ccx_nda.json

to run:
	1. navigate terminal to the directory one level above the dicom folder
		i.e. current_dir/CCX_dcm
	2. initialize output folder by running:
		"python custom_bids.py -i True -o CCX-bids"
	3. convert a single subject by replacing CCX000 with the desired subject and running: 
		"python custom_bids.py -s CCX000 -d CCX_dcm -o CCX-bids"

display this message - python custom_bids.py --help

written by gus hennings
"""

#imports
import os
import sys
import argparse
import json
from shutil import copyfile
from warnings import warn

#set up argparse
parser = argparse.ArgumentParser(description=__doc__,
	formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument('-s', '--subj',  default='s666',type=str, help='subject #')
parser.add_argument('-d', '--dcm',   default=None,  type=str, help='dicom directory')
parser.add_argument('-o', '--out',   default=None,  type=str, help='bids outputdir')
parser.add_argument('-n', '--nda', 	 default=False, type=bool,help='NDA conversion for CCX')
parser.add_argument('-i', '--init',  default=False, type=bool,help='initialize the output')
args = parser.parse_args()


output = os.path.join(os.getcwd(),args.out) #find the output dir

#check to see if we are just initializing the output
if args.init:
	print('initializing output')
	if not os.path.exists(output): os.mkdir(output) #create output if doesn't exists
	for file_name in ['README','participants.tsv','CHANGES','dataset_description.json']: #create bids necessary files 
		if file_name == 'README':
			with open(os.path.join(output,file_name),'w+') as file: file.write('CCX bids'); file.close() #readme can't be empty
		else: open(os.path.join(output,file_name),'w+') #just make empty files with 'w+'

	deriv = os.path.join(output,'derivatives') #we'll probably need this
	if not os.path.exists(deriv): os.mkdir(deriv)

	sys.exit()

data_dir = os.path.join(os.getcwd(),args.dcm) #find the dicom dir

sub_arg = 'CCX_%s'%(args.subj[-3:]) #this is format the dicom folders are in

#make sure we can find all three dicom folders for this subject
day1dcm = os.path.join(data_dir,sub_arg + '_01')
day2dcm = os.path.join(data_dir,sub_arg + '_02')
day3dcm = os.path.join(data_dir,sub_arg + '_03')

#and raise an error if we can't
for _dir in [day1dcm,day2dcm,day3dcm]: 
	try: assert os.path.exists(_dir)
	except: print('Dicom directory not found: %s'%(_dir)); sys.exit()

print('Found 3 dicom folders for %s'%(args.subj)) #we found all the dirs

############################################################
#this section is specific to NDA conversion - ignore if not doing that
if args.nda:
	print('Copying renewal dicoms to day1 for bids conversion')

	#first we have to copy all of the renewal dicoms from day2 to day1
	renewal_dcms = []
	for _dir in os.walk(day2dcm):
		files = _dir[2]
		for file in files:
			if 'Run4_renewal' in file and '.dcm' in file and 'Mosaics' not in file:	#ignore the mosiac files
				renewal_dcms.append(os.path.join(_dir[0],file))

	try: assert len(renewal_dcms) == 370 #make sure we have the right number of dicoms
	except: print('found %s instead of 370 renewal dicoms'%(len(renewal_dcms))); sys.exit()

	dest = os.path.join(day1dcm,'temp_renewal_dcms') #make a tmp folder to copy to
	if not os.path.exists(dest): os.mkdir(dest)

	for file in renewal_dcms: os.system('cp %s %s'%(file,os.path.join(dest,os.path.split(file)[-1]))) #copy the files

	#run bids conversion
	nda_cmd = 'dcm2bids -d %s -c %s/ccx_nda.json -p %s -o %s -s 1'%(day1dcm,data_dir,args.subj,output)
	try: os.system(nda_cmd)
	except: print('BIDS conversion failed with the following command: %s'%(nda_cmd))
	os.system('rm -R %s'%(dest))
	os.system('rm -R %s'%(os.path.join(output,'tmp_dcm2bids'))) #delete the tmp folder that dcm2bids makes
	sys.exit()
#############################################################
#if not running conversion for NDA, convert each session one at a time
for i, dcm in enumerate([day1dcm,day2dcm,day3dcm]):
	ses = i+1 #fix pythonic indexing (no ses-0)
	print('running BIDS coversion for sub-%s ses-%s'%(args.subj,ses))
	
	#some subjects are missing a field map so they need their own config for ses-3
	if ses == 3 and int(args.subj[-3:]) <= 10:
			cfg = 'ccx-ses-%s-pre-10.json'%(ses)
			warn('skipping run 10 fielmaps!')
	else: cfg = 'ccx-ses-%s.json'%(ses) #otherwise this is the config file
	
	config = os.path.join(data_dir,cfg) #load the config file
	
	try: assert os.path.exists(config) #and make sure it exists
	except: print('config file does not exist: %s'%(config)); sys.exit()

	dcm2bids_call = 'dcm2bids -d %s -c %s -p %s -o %s -s %s'%(dcm,config,args.subj,output,ses) #set up the command
	
	try: os.system(dcm2bids_call) #and run it
	except: print('bids conversion failed with call: %s'%(dcm2bids_call)); sys.exit()
	
	os.system('rm -R %s'%(os.path.join(output,'tmp_dcm2bids'))) #delete the tmp folder that dcm2bids makes

#write in the task name to the json - doesn't happen in the conversion for some reason
#need this for bids validation
#very lazy loop - scans all files in the subject directory
for _dir in os.walk(output):
	for file in _dir[2]:
		if 'task' in file and '.json' in file:
			with open(os.path.join(_dir[0],file)) as json_file:
				json_decoded = json.load(json_file)

			name_start = file.find('task-') + 5 #file is a string
			try: 
				name_end = file.find('_run')
				assert name_end != -1
			except: 
				name_end = file.find('_bold')

			json_decoded['TaskName'] = file[name_start:name_end]

			with open(os.path.join(_dir[0],file), 'w') as json_file:
				json.dump(json_decoded, json_file)

#much less lazy loop to add the "intended for" value to .json of field maps
fmaps = {	'Run1':'fear',
			'Run2':'fearextinction',
			'Run3':'extinction',
			'Run4':'renewal',
			'Run5':'memory',
			'Run8':'renewal',
			'Run9':'memory_run-01',
			'Run10':'memory_run02',
			'Run11':'localizer_run-01',
			'Run12':'localizer_run-02',
			'SMS':'dwi'
			}

sub_bid = os.path.join(output,'sub-' + args.subj)
for ses in [1,2,3]:
	ses_dir = os.path.join(sub_bid,'ses-%s'%(ses))
	fmap_dir = os.path.join(ses_dir,'fmap')
	files = os.listdir(fmap_dir) 
	for file in files:
		if '.json' in file:
			with open(os.path.join(fmap_dir,file)) as json_file:
				json_decoded = json.load(json_file)

			iF = fmaps[json_decoded['SeriesDescription'][:json_decoded['SeriesDescription'].find('_')]]
			
			if iF == 'dwi':  full_iF = 'ses-%s/dwi/sub-%s_ses-%s_dwi.nii.gz'%(ses,args.subj,ses)	
			else: full_iF = 'ses-%s/func/sub-%s_ses-%s_task-%s_bold.nii.gz'%(ses,args.subj,ses,iF)
			json_decoded['IntendedFor'] = full_iF
			
			with open(os.path.join(fmap_dir,file), 'w') as json_file:
				json.dump(json_decoded, json_file)
print('Bids conversion for sub-%s complete!'%(args.subj))