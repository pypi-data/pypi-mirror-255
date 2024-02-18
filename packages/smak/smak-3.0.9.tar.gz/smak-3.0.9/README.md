# SMAK3.0
MicroAnalysis Toolkit v3

If you haven't recently used conda, it is a good idea to update your installation before beginning. `conda update conda`

## Installation with Conda
1. Create a new environment from Anaconda prompt/navigator. Choose 'y' when prompted.
`conda create -n smakenv python==3.10
`
2. Activate the new environment
`conda activate smakenv
`
3. Install package via pip
`pip install smak
`
4. Navigate to the folder within your anaconda environment where smak has been installed. This can be tricky to find. 
   - To start, type in `PATH` (windows) or `$PATH` (mac). This will provide a list of Anaconda directories. Yours may look something like this: "C:\Users\yourUsername\AppData\Local\anaconda3\envs\smakenv" (windows)
   - Copy the first of the paths from the previous step and navigate to that folder on your computer in finder/file explorer. This is the folder for your smak specific virtual environment. 
   - From the virtual environment folder, navigate to "Lib\site-packages\smak" (windows) or "Lib\python 3.10\site-packages\smak"(mac)
   - In this folder, you will see the code for smak, including "smak.py". Bookmark this folder, you will need to access it frequently.

## Optional: Segmentation and image registration
To use the full functionality of SMAK, you will need to follow a few additional steps. This is not necessary unless you plan to use segmentation and image registration. 
1. Download the files from the following links. They are quite large and may take a while to download.
  - [sam_vit_b_01ec64.pth](https://www.dropbox.com/scl/fi/b0gt93cgqwyeksb1wb0gw/sam_vit_b_01ec64.pth?rlkey=zza3ehiroiow3celno7iw8gza&dl=1)
  - [sam_vit_h_4b8939.pth](https://www.dropbox.com/s/brcy0416evm772m/sam_vit_h_4b8939.pth?dl=1)
  - [sam_vit_l_0b3195.pth](https://www.dropbox.com/s/21rtkc1s0vaxapm/sam_vit_l_0b3195.pth?dl=1)
  - [vgg16partial.npy](https://www.dropbox.com/scl/fi/evb0yte787q7ng6aax6m3/vgg16partial.npy?rlkey=fu8xw941sv87x3q8o5jg0prwo&dl=1)
2. Move the files into the main smak folder. This is the folder you found and bookmarked in step 4 of "Installation with Conda".
3. From Anacoda prompt, with your smakenv virtual environment active, run the following commands to install packages. Please follow this exact order of package installation. 
 - `pip install pycocotools`
 - `conda install git`
 - `pip install git+https://github.com/facebookresearch/segment-anything.git`
 - `pip install torch`
 - `pip install torchvision`
 - `conda install lap -c conda-forge`
 - `pip install numpy==1.24`
4. To check this functionality, open SMAK and navigate to the Analyze/Segmentation. An expanded menu including "Initialize SAM" will be available to you. 

## Running SMAK
1. Open Anaconda prompt/navigator.
2. Activate the environment you use to run smak
`conda activate smakenv
`
3. Navigate to the folder within your anaconda environment where smak has been installed. This is the folder you found and bookmarked in step 4 of "Installation with Conda". Using quotes aroung the path may be helpful. 
5. Run smak
`python smak.py
`

Improvements on this installation process and guide are underway! In the meantime, don't hesitate to reach out to Joy (joy.a.wood@dartmouth.edu) or Sam (samwebb@slac.stanford.edu) for assistance. 
