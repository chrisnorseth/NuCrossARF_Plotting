## Script Version of the NuCrossARF Plot Notebook

If you would rather run scripts instead of a Jupyter notebook, you can work here instead. Included is a set of two scripts and a configuration file. 

The final output is a set of two plots, one showing each region's spectrum and total model, and one showing each region's ratio between the spectrum and the model.

Before running the code, you need to save your xspec run with the 'save all' command and setup your configuration file.
Then you can run the two steps individually.

Step One will pull all of the plotting information out of xspec for each spectrum and model.
Step Two will plot everything in a nice way. Note that you only need to run Step One once. You can run Step Two as many times as you want.

## The Setup

### Save Your Xspec Run

Load your nucrossarf xcm script and fit it like you normally would. Adjust the binning to what you would like and note what you used (e.g., setpl rebin 5 12).
When you are satisfied, save your xspec run using 'save all saved_run_whatever.xcm'

### Configuration File
The configuration file contains all of the information necessary to run the code. An example txt file is contained in this directory, which you can modify directly. When you run the code, you simply point to the config.txt file. All of the information in the config.txt file is in the example config.txt and is also described at the very end of this README.


## Running the Code

### Step One: (Generate Plotting Information)

Step one is contained in 'stepOne_makeFiles.py'. It takes in one command line argument: the config.txt file.

To run, make sure you are in a heasoft environment (i.e. a terminal where you could run xspec) and simply run the following:

`python stepOne_makeFiles.py config.txt`

This script will launch xspec, load your fit, and sequentially save each spectrum and total model into a save file. It will also create a 'Plotting_Directory' inside of your 'crossarf_dir', where it will store all of the information. If you need to run it again (e.g. you want to change the binning), it will overwrite the previous run.

### Step Two: (Make the Plots)

Step two is contained in 'stepTwo_makePlots.py'. It takes in one command line argument: the config.txt file.

Once Step One is complete, simply run:

`python stepTwo_makePlots.py config.txt`

This script will load in the saved plotting information and produce two plots; a spectra plot of each region and total model, and a ratio plot. You will need to adjust the y limits of the spectra plot in the config.txt file to obtain the best visualization for your needs. The config.txt file also contains a flag and path for saving your plots. You can run this code as many times as you need as you adjust the plots. Any saved plots will be overwritten each run.



## Configuration File Description
A config.txt file is used across the two steps to provide relevant paths and parameters. An example config.txt file is located in this directory and can be edited directly. An in-depth description of each parameter can be found below:

- Full Paths
    - 'nustar_dir': The directory where your cluster is located. 
        - Following tradition, the organization will look like: 'nustar_dir/cluster/crossarf_dir', where 'crossarf_dir' is the output from running nucrossarf and will contain an obsid directory with all of the files.
        - e.g. 'nustar_dir = "/Users/christiannorseth/GradResearch/CrossARFRuns"'
    - 'crossarf_dir': The output directory from running nucrossarf.
        - e.g. 'crossarf_dir = "/Users/christiannorseth/GradResearch/CrossARFRuns/Abell2146/crossarf_trial5"'
    - 'saved_xcm_script': The path to your saved xcm script from running 'save all' in your xspec run.
        - e.g. 'saved_xcm_script = "/Users/christiannorseth/GradResearch/CrossARFRuns/Abell2146/crossarf_trial5/fit_6_29_26.xcm"'

- CrossARF Region Information
    - 'obsids': The obsids included in your nucrossarf run; a list of strings.
        - e.g. 'obsids = ["70401001002"]'
    - 'reg_base': The 'base' of each file; 'outbase' in the crossarf par file.
        - e.g. 'reg_base = "reg"'
    - 'num_reg': The number of spectral regions in your crossarf run.
        - e.g. 'num_reg = 14'
    - 'regs_to_include_in_plot': A list of the regions you'd like to plot.
        - e.g. 'regs_to_include_in_plot = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]'

- Spectra Binning Information
    - 'binning': The optimal binning you found when plotting in xspec; just the two numbers from 'setplot rebin x x'.
        - e.g.: 'binning = "5 12"'
    - 'e_low': Lower keV energy bound.
        - e.g. 'e_low = 3.0'
    - 'e_high': Upper keV energy bound.
        - e.g. 'e_high = 20.0'

- Plotting Preferences (can be changed as many times as you want when plotting)
    - 'plot_size': The size of the matplotlib plot.
        - e.g. 'plot_size = [8,8]'
    - 'spaced_spectra': Set to True if you want automatic spacing between each region spectrum to be performed for better visualization. Includes automatic labeling.
        - e.g. 'spaced_spectra = True'
    - Plot Limits:    
        - 'spectra_y_lim_lower': The lower y limit of the spectra plot. You will need to adjust these to get the optimal visualization, especially if you are using 'spaced_spectra'.
            - e.g. 'spectra_y_lim_lower = 1e-16'
        - 'spectra_y_lim_upper': The upper y limit of the spectra plot. You will need to adjust these to get the optimal visualization, especially if you are using 'spaced_spectra'.
            - e.g. 'spectra_y_lim_upper = 2e-2'
        - 'ratio_y_lim_lower': The lower y limit of the ratio plot.
            - e.g. 'ratio_y_lim_lower = 0.0'
        - 'ratio_y_lim_upper': The upper y limi of the ratio plot
            - e.g. 'ratio_y_lim_upper = 2.0'
    - 'plot_color_map': Color map to use for the plots, 'turbo' is a nice rainbow choice.
        - e.g. 'plot_color_map = 'turbo''

- Plot Output
    - 'save_plot': Set to True if you want the plots written to a file.
        - e.g. 'save_plot = True'
    - 'plot_output_path': The path where your plots will save to.
        - e.g. 'plot_output_path = "/Users/christiannorseth/GradResearch/CrossARFRuns/Abell2146/crossarf_trial5"'



