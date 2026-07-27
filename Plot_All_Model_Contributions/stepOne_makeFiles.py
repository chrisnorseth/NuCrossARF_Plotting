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
reg_base = getValue(str, 'reg_base', '=', 'reg base')
num_reg = getValue(int, 'num_reg', '=', 'number of regions')
num_srcs = getValue(int, 'num_srcs', '=', 'number of sources')
reg_to_include_in_plot = getValue(int, 'reg_to_include_in_plot', '=', 'region to plot')
det = getValue(str, 'det', '=', 'detector to plot')


### SPECTRA INFORMATION
binning = getValue(str, 'binning', '=', 'xspec binning')
e_low = getValue(float, 'e_low', '=', 'lower energy limit')
e_high = getValue(float, 'e_high', '=', 'upper energy limit')


# saved xcm file
saved_file = getValue(str, 'saved_xcm_script', '=', 'your saved xcm script with fit values')


# Automatically make a directory to store intermediary files
plotting_directory = f"{crossarf_dir}/Plotting_Stuff_All_Model_Lines"
plotting_directory_from_nustar_dir = f"{cluster}/{crossarf_dir_only}/Plotting_Stuff_All_Model_Lines"
if os.path.exists(plotting_directory) == False:
    # create the cluster directory
    os.makedirs(plotting_directory)

# automatically copy the saved script over
shutil.copyfile(saved_file, f'{plotting_directory}/saved_run.xcm')

# run from cluster parent dir (since original crossarf scripts are meant to run there)
os.chdir(nustar_dir)


files = ['color_script.xcm']
for file in files:
    full_path = f'{plotting_directory}/{file}'
    if os.path.exists(full_path):
        os.remove(full_path)

# run everything
reg = reg_to_include_in_plot
if det == 'B':
    reg += num_reg

# load and setup the script
lines = []
# load script
lines.append(f'@{plotting_directory}/saved_run.xcm\n')

# plotting step
lines.append('notice all\n')
lines.append(f'ignore **:**-{e_low-1.0} {e_high+1.0}-**\n')
plotting_com = ['cpd /xs\n', 'setpl e\n', 'pl ld\n', f'setpl rebin {binning}\n']
lines.extend(plotting_com)


# step one (remove spectra):
# for 1st reg, remove all data above it
if reg == 1:
    lines.append('data 2 none\n')
else:
# for the rest, remove all data below and above it
    # below
    for k in range(reg-1):
        lines.append('data 1 none/\n')
    # above (its now data 1)
    lines.append('data 2 none\n')

lines.append('pl\n')

# step two (save everything)
save_commands = [
                f'echo "Run this command and then exit: wdata {plotting_directory_from_nustar_dir}/wdataSave.dat"\n',
                'iplot\n',
                'exit\n'
                ]
lines.extend(save_commands)


# write it in an xcm file
with open(f'{plotting_directory}/color_script.xcm', 'w') as file:
    file.writelines(lines)

# run it as bash
bash_lines = ["#!/bin/bash\n"]#,
bash_lines.extend([f'cd {nustar_dir}\n', f'xspec - {plotting_directory}/color_script.xcm'])
with open(f'{plotting_directory}/bash_runner.sh', 'w') as file:
    file.writelines(bash_lines)
subprocess.run(f"chmod u+x {plotting_directory}/bash_runner.sh", shell=True)
subprocess.call(f"{plotting_directory}/bash_runner.sh")
subprocess.run(f'rm {plotting_directory}/bash_runner.sh', text=True, shell=True)