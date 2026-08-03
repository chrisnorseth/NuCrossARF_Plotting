import argparse
import subprocess
import os
import shutil

### Argument Handling ###
parser = argparse.ArgumentParser()
parser.add_argument("config_file")

args = parser.parse_args()
config_file = args.config_file

# load in the config info
config_lines = []
with open(config_file) as file:
    for line in file:
        config_lines.append(line)

# function to get stuff with err messages
def getValue(type, search_string, equator, message):
    num_check = 0
    for line in config_lines:
        if search_string in line and '#' not in line:
            num_check += 1
            try:
                value = type(line.split(equator)[1].strip())
                if type == list:
                    arr = line.split(equator)[1].strip()
                    content = arr.split('[')[1].split(']')[0].split(',')
                    value = [a.replace('"', '') if '"' in a else int(a) for a in content]
            except Exception:
                raise RuntimeError(f"Issue with establishing {message}.")
    if num_check != 1:
        if num_check == 0:
            raise RuntimeError(f"Could not find {message}.")
        elif num_check > 1:
            raise RuntimeError(f"Found multiple instances of: {message}.")
    if type == str:
        value = value.replace('"', '')    
    return value



### Read in all Info ###
### PATHS ###
nustar_dir = getValue(str, 'nustar_dir', '=', 'cluster parent directory')
cluster = getValue(str, 'cluster', '=', 'cluster dir only')
crossarf_dir_only = getValue(str, 'crossarf_dir', '=', 'crossarf run directory only')
crossarf_dir = f'{nustar_dir}/{cluster}/{crossarf_dir_only}'

### REGION INFORMATION ###
obsids = getValue(list, 'obsids', '=', 'obsids')
reg_base = getValue(str, 'reg_base', '=', 'reg base')
num_reg = getValue(int, 'num_reg', '=', 'number of regions')
regs_to_include_in_plot = getValue(list, 'regs_to_include_in_plot', '=', 'regions to plot')


### SPECTRA INFORMATION
binning = getValue(str, 'binning', '=', 'xspec binning')
e_low = getValue(float, 'e_low', '=', 'lower energy limit')
e_high = getValue(float, 'e_high', '=', 'upper energy limit')


# saved xcm file
saved_file = getValue(str, 'saved_xcm_script', '=', 'your saved xcm script with fit values')




num_obsids = len(obsids)

# Automatically make a directory to store intermediary files
plotting_directory = f"{crossarf_dir}/Plotting_Stuff"
plotting_directory_from_nustar_dir = f"{cluster}/{crossarf_dir_only}/Plotting_Stuff"
if os.path.exists(plotting_directory) == False:
    # create the cluster directory
    os.makedirs(plotting_directory)


# automatically copy the saved script over
shutil.copyfile(saved_file, f'{plotting_directory}/saved_run.xcm')

# run from cluster parent dir (since original crossarf scripts are meant to run there)
os.chdir(nustar_dir)

# files to be made (overwritten if run before)
files = ['color_script.xcm', 'save_ratios.dat', 'save.dat']
for file in files:
    full_path = f'{plotting_directory}/{file}'
    if os.path.exists(full_path):
        os.remove(full_path)

    
# load and setup the script
lines = []
# load script
lines.append(f'@{plotting_directory}/saved_run.xcm\n')

# plotting step
lines.append('notice all\n')
lines.append(f'ignore **:**-{e_low-1.0} {e_high+1.0}-**\n')
plotting_com = ['cpd /xs\n', 'setpl e\n', 'pl ld\n', f'setpl rebin {binning}\n']
lines.extend(plotting_com)

# wdata save lines
wdata_coms = [f'setpl com wdata {plotting_directory_from_nustar_dir}/save.dat\n', 'pl\n']
lines.extend(wdata_coms)

# now save ratios
ratio_coms = ['setpl delete all\n', f'setpl com wdata {plotting_directory_from_nustar_dir}/save_ratios.dat\n', 'pl ra\n', 'exit\n']
lines.extend(ratio_coms)


# write it in an xcm file
with open(f'{plotting_directory}/color_script.xcm', 'w') as file:
    file.writelines(lines)

# run it as bash file
bash_lines = ["#!/bin/bash\n"]
bash_lines.extend([f'cd {nustar_dir}\n', f'xspec - {plotting_directory}/color_script.xcm'])
with open(f'{plotting_directory}/bash_runner.sh', 'w') as file:
    file.writelines(bash_lines)
subprocess.run(f"chmod u+x {plotting_directory}/bash_runner.sh", shell=True)
subprocess.call(f"{plotting_directory}/bash_runner.sh")
subprocess.run(f'rm {plotting_directory}/bash_runner.sh', text=True, shell=True)


print('Done!')