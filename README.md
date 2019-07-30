# custom_bids
custom bids conversion script utilizing python

assumes that you have installed dcm2niix and dcm2bids
    <p>conda install -c conda-forge dcm2niix</p>
    <p>pip install dcm2bids</p>

also assumes that you have all of the config files in the dicom folder
<blockquote>
CCX_dcm/ccx_ses-1.json  
CCX_dcm/ccx_ses-2.json  
CCX_dcm/ccx_ses-3.json  
CCX_dcm/ccx_ses-3-pre-10.json  
CCX_dcm/ccx_nda.json
</blockquote>

#to run:
1. navigate terminal to the directory one level above the dicom folder  
    <p>current_dir/CCX_dcm</p>
2. initialize output folder by running:
    <p>python custom_bids.py -i True -o CCX-bids</p>
3. convert a single subject by replacing CCX000 with the desired subject and running: 
    <p>python custom_bids.py -s CCX000 -d CCX_dcm -o CCX-bids</p>

display this message:
    <p>python custom_bids.py --help</p>

written by gus hennings
"""