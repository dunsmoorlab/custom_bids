# custom_bids
custom bids conversion script utilizing python

assumes that you have installed dcm2niix and dcm2bids
    <p>conda install -c conda-forge dcm2niix</p>
    <p>pip install dcm2bids</p>

also assumes that you have all of the config files in the dicom folder
<blockquote>
<p>CCX_dcm/ccx_ses-1.json</p> 
<p>CCX_dcm/ccx_ses-2.json</p>
<p>CCX_dcm/ccx_ses-3.json</p>
<p>CCX_dcm/ccx_ses-3-pre-10.json</p>  
<p>CCX_dcm/ccx_nda.json</p>
</blockquote>

#to run:
1. navigate terminal to the directory one level above the dicom folder  
    `current_dir/CCX_dcm`
2. initialize output folder by running:
    `python custom_bids.py -i True -o CCX-bids`
3. convert a single subject by replacing CCX000 with the desired subject and running: 
    `python custom_bids.py -s CCX000 -d CCX_dcm -o CCX-bids`

display this message:
    `python custom_bids.py --help`

written by gus hennings
"""