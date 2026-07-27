import argparse
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

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
e_low = getValue(float, 'e_low', '=', 'lower energy limit')
e_high = getValue(float, 'e_high', '=', 'upper energy limit')


### PLOT PREFERENCES ###
plot_size = getValue(list, 'plot_size', '=', 'size of plots')
spectra_y_lim_lower = getValue(float, 'spectra_y_lim_lower', '=', 'lower y plot limit')
spectra_y_lim_upper = getValue(float, 'spectra_y_lim_upper', '=', 'upper y plot limit')
spectra_y_lims = (spectra_y_lim_lower, spectra_y_lim_upper)


# color
plot_color_map = 'turbo'

# plot saving
save_plot = getValue(bool, 'save_plot', '=', 'save plot flag')
plot_output_path = getValue(str, 'plot_output_path', '=', 'plot save output path')


plotting_directory = f"{crossarf_dir}/Plotting_Stuff_All_Model_Lines"




#### PLOTTING DATA VS MODEL ####

## COLOR MAP TO USE ##
color_map = plot_color_map #'turbo'


# read in saved plotting info and organize it
saved_plot_info = f'{plotting_directory}/wdataSave.dat'
lines = []
with open(saved_plot_info) as file:
    # skip first 3 lines
    i = 0
    for line in file:
        if i > 2:
            lines.append(line)
        i += 1

# check if lines overflowed
proper_lines = []
idx = 0
while idx <= len(lines)-1:
    line = lines[idx]
    if line.endswith("-\n"):
        top = line.split("-\n")[0]
        bottom = lines[idx+1].split("  ")[1]
        new_line = f"{top} {bottom}"
        proper_lines.append(new_line)
        idx += 2
    else:
        proper_lines.append(line)
        idx += 1

# organize into seperate arrays
data = {'x':[], 'y':[], 'x_err':[], 'y_err':[], 'model_sum':[], 'models':{i:[] for i in range(num_srcs)}}
for idx,line in enumerate(proper_lines):
    vals = line.split(' ')

    x = float(vals[0])
    x_err = float(vals[1])
    y = float(vals[2])
    y_err = float(vals[3])
    model_sum = float(vals[4])

    data['x'].append(x)
    data['y'].append(y)
    data['x_err'].append((x_err, x_err))
    data['y_err'].append((y_err, y_err))
    data['model_sum'].append(model_sum)

    mod = 0
    for i in range(5,len(vals)):
        model_val = float(vals[i].strip())
        data['models'][mod].append(model_val)
        mod += 1
            


# Defining the plot things will be added to
plt.rcParams["figure.figsize"] = plot_size
fig, ax = plt.subplots()

# defining colors to use
cmap = plt.get_cmap(color_map)
colors = [cmap(i/(num_srcs-1)) for i in range(num_srcs)]


# plot data
x = data['x']
xerr = data['x_err']
y = data['y']
yerr = data['y_err']
ax.errorbar(x,y,xerr=np.array(xerr).T,yerr=np.array(yerr).T,fmt='none',linewidth=1.5,color='black')

# plot model
x = [val-xerr[idx][0] for idx,val in enumerate(x)]
y = data['model_sum']
y.append(y[-1])
x.append(e_high)
ax.step(x,y,linewidth=1.5,color='red', where='post',alpha=0.8, label='Model Sum')

# plot individual models
color_idx = 0
for mod_key in data['models']:
    mod = data['models'][mod_key]
    mod.append(mod[-1])
    ax.step(x,mod,linewidth=1.5,color=colors[color_idx], where='post',alpha=0.8, label=f'Source {color_idx+1}')
    color_idx += 1


# formatting the plot
plot = ax
plot.set(yscale="log",xscale="log",xlabel='Energy (keV)',ylabel=r'counts s$^{-1}$ keV$^{-1}$',xlim=(e_low,e_high))
plot.xaxis.set_major_formatter(ticker.FuncFormatter(lambda val, pos: '{:.0f}'.format(val)))
plot.xaxis.set_major_locator(ticker.FixedLocator([5, 10, 15]))
plot.xaxis.set_minor_locator(ticker.NullLocator())  # Suppress minor ticks
plot.set(title=f'FPM{det} Region {reg_to_include_in_plot}')
plot.set(ylim=spectra_y_lims)
plt.tight_layout()


# Legend:
from matplotlib.lines import Line2D
def create_dummy_line(**kwds):
    return Line2D([], [], **kwds)

lines = [
        ('Data', {'color': 'black','marker':'+','linestyle':'none'}),
        ('Total', {'color': 'red','linestyle':'solid'})
         ]

for r in range(num_srcs):
    color = colors[r]
    label = f'Source {r+1}'
    legend_item = (label, {'color': color,'linestyle':'solid'})
    lines.append(legend_item)

ax.legend(
        # Line handles
        [create_dummy_line(**l[1]) for l in lines],
        # Line titles
        [l[0] for l in lines],
        loc='lower left',
        fontsize=8
    )


if save_plot:
    fig.savefig(f'{plot_output_path}/crossarf_all_models_{det}{reg_to_include_in_plot}.pdf')


plt.show()
