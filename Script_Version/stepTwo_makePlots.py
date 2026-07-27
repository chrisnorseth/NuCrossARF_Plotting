import argparse
import os
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
crossarf_dir = getValue(str, 'crossarf_dir', '=', 'crossarf run directory')
nustar_dir = getValue(str, 'nustar_dir', '=', 'cluster parent directory')

### REGION INFORMATION ###
obsids = getValue(list, 'obsids', '=', 'obsids')
reg_base = getValue(str, 'reg_base', '=', 'reg base')
num_reg = getValue(int, 'num_reg', '=', 'number of regions')
regs_to_include_in_plot = getValue(list, 'regs_to_include_in_plot', '=', 'regions to plot')

### SPECTRA INFORMATION
binning = getValue(str, 'binning', '=', 'xspec binning')
e_low = getValue(float, 'e_low', '=', 'lower energy limit')
e_high = getValue(float, 'e_high', '=', 'upper energy limit')


### PLOT PREFERENCES ###
plot_size = getValue(list, 'plot_size', '=', 'size of plots')
spaced_spectra = getValue(bool, 'spaced_spectra', '=', 'spaced spectra flag')

# lims 
y_lim_lower = getValue(float, 'spectra_y_lim_lower', '=', 'lower limit y spec plot')
y_lim_upper = getValue(float, 'spectra_y_lim_upper', '=', 'upper limit y spec plot')

ratio_y_lim_lower = getValue(float, 'ratio_y_lim_lower', '=', 'lower limit y ratio plot')
ratio_y_lim_upper = getValue(float, 'ratio_y_lim_upper', '=', 'upper limit y ratio plot')

spectra_y_lims = (y_lim_lower,y_lim_upper)
ratio_y_lims = (ratio_y_lim_lower,ratio_y_lim_upper)

# color
plot_color_map = 'turbo'

# plot saving
save_plot = getValue(bool, 'save_plot', '=', 'save plot flag')
plot_output_path = getValue(str, 'plot_output_path', '=', 'plot save output path')



num_obsids = len(obsids)
plotting_directory = f"{crossarf_dir}/Plotting_Stuff"






#### PLOTTING DATA VS MODEL ####

## COLOR MAP TO USE ##
color_map = plot_color_map #'turbo'

# read in saved plotting info and organize it
saved_plot_info = f'{plotting_directory}/save.dat'
lines = []
with open(saved_plot_info) as file:
    for line in file:
        lines.append(line)

regions = {i:{o:{'A':{}, 'B':{}} for o in range(1,num_obsids+1)} for i in range(1,num_reg+1)}
for idx,line in enumerate(lines):
    if 'RegA' in line:
        num = line.split('RegA')[1].split(' ')[0]
        num = int(num)

        obs = 1
        if num > num_reg:
            num = num - num_reg*num_obsids
            obs = 2

        x_line = lines[idx+1]
        x = [float(val) for val in x_line.split('\n')[0].split('   ')[:-1]]

        xerr_line = lines[idx+2]
        xerr = [(float(val), float(val)) for val in xerr_line.split('\n')[0].split('   ')[:-1]]

        y_line = lines[idx+3]
        y = [float(val) for val in y_line.split('\n')[0].split('   ')[:-1]]
        
        yerr_line = lines[idx+4]
        yerr = [(float(val), float(val)) for val in yerr_line.split('\n')[0].split('   ')[:-1]]

        model_line = lines[idx+5]
        model = [float(val) for val in model_line.split('\n')[0].split('   ')[:-1]]

        regions[num][obs]['A'] = {'x': x,
                        'xerr': xerr,
                        'y': y,
                        'yerr': yerr,
                        'model': model}
    elif 'RegB' in line:
        num = line.split('RegB')[1].split(' ')[0]
        num = int(num) - num_reg

        obs = 1
        if num > num_reg:
            num = num - num_reg*num_obsids
            obs = 2
        
        x_line = lines[idx+1]
        x = [float(val) for val in x_line.split('\n')[0].split('   ')[:-1]]

        xerr_line = lines[idx+2]
        xerr = [(float(val), float(val)) for val in xerr_line.split('\n')[0].split('   ')[:-1]]

        y_line = lines[idx+3]
        y = [float(val) for val in y_line.split('\n')[0].split('   ')[:-1]]
        
        yerr_line = lines[idx+4]
        yerr = [(float(val), float(val)) for val in yerr_line.split('\n')[0].split('   ')[:-1]]

        model_line = lines[idx+5]
        model = [float(val) for val in model_line.split('\n')[0].split('   ')[:-1]]

        regions[num][obs]['B'] = {'x': x,
                        'xerr': xerr,
                        'y': y,
                        'yerr': yerr,
                        'model': model}


# Defining the plot things will be added to
plt.rcParams["figure.figsize"] = plot_size
fig, ax = plt.subplots(num_obsids,2,squeeze=False)

# defining colors to use
cmap = plt.get_cmap(color_map)
colors = [cmap(i/(len(regs_to_include_in_plot)-1)) for i in range(len(regs_to_include_in_plot))] if len(regs_to_include_in_plot) > 1 else [cmap(0)]

# if you want to shift all the lines so they are seperated
def doTheShifts(obs, det, shift_dif):
   
    first_digits = []
    for reg in regions.keys():
        if reg in regs_to_include_in_plot:
            y = regions[reg][obs][det]['model']
            first_digits.append(y[0])

    shifts = [0]*len(regs_to_include_in_plot)
    for idx in range(1,len(first_digits)):
        shift = -50
        
        largest_val = first_digits[idx-1]
        next_val = first_digits[idx]
        difference = np.abs(np.log10(largest_val*10**shifts[idx-1])-np.log10(next_val*10**shift))

        while difference > shift_dif:
            shift += 0.1
            difference = np.abs(np.log10(largest_val*10**shifts[idx-1])-np.log10(next_val*10**shift))

        shifts[idx] = shift
    
    return shifts


do_shift = spaced_spectra
shifts = [0]*num_reg
if do_shift:
    shifts = doTheShifts(1,'A', 0.9)

for obs in range(1,num_obsids+1):
    
    color_idx = 0
    for reg in regions.keys():
        if reg in regs_to_include_in_plot:
            # plot A data
            x = regions[reg][obs]['A']['x']
            xerr = regions[reg][obs]['A']['xerr']
            y = [val*10**shifts[color_idx] for val in regions[reg][obs]['A']['y']]
            yerr = [(val*10**shifts[color_idx], val2*10**shifts[color_idx]) for val,val2 in regions[reg][obs]['A']['yerr']]
            ax[obs-1,0].errorbar(x,y,xerr=np.array(xerr).T,yerr=np.array(yerr).T,fmt='none',linewidth=1.5,color=colors[color_idx])
            
            # plot B data
            x = regions[reg][obs]['B']['x']
            xerr = regions[reg][obs]['B']['xerr']
            y = [val*10**shifts[color_idx] for val in regions[reg][obs]['B']['y']]
            yerr = [(val*10**shifts[color_idx], val2*10**shifts[color_idx]) for val,val2 in regions[reg][obs]['B']['yerr']]
            ax[obs-1,1].errorbar(x,y,xerr=np.array(xerr).T,yerr=np.array(yerr).T,fmt='none',linewidth=1.5,color=colors[color_idx])#, alpha=0.5)

            # plot A model
            xerr = regions[reg][obs]['A']['xerr']
            x = [val-xerr[idx][0] for idx,val in enumerate(regions[reg][obs]['A']['x'])]
            y = [val*10**shifts[color_idx] for val in regions[reg][obs]['A']['model']]
            x.append(e_high)
            y.append(y[-1])
            ax[obs-1,0].step(x,y,linewidth=1.5,color=colors[color_idx], where='post',alpha=0.8)

            # plot B model
            xerr = regions[reg][obs]['B']['xerr']
            x = [val-xerr[idx][0] for idx,val in enumerate(regions[reg][obs]['B']['x'])]
            y = [val*10**shifts[color_idx] for val in regions[reg][obs]['B']['model']]
            x.append(e_high)
            y.append(y[-1])
            ax[obs-1,1].step(x,y,linewidth=1.5,color=colors[color_idx], where='post', alpha=0.8)

            # add labels
            if do_shift:
                x_max = max(x)
                x_min = min(x)
                y_max = max(y)
                y_min = min(y)
                # ax.scatter(x[0] * 1.01, y_max*1.3, s=10)
                y_pts = []
                for idx_pt, y_pt in enumerate(y):
                    x_pt = x[idx_pt]
                    if x_pt < e_high:
                        y_pts.append(y_pt)
                y_min = y[len(y_pts)-1]
                
                for det in range(2):
                    ax[obs-1,det].annotate(fr"$\times$10$^{{{shifts[color_idx]:.1f}}}$",
                        xy=(e_low, y_max),
                        xytext=(e_low * 1.01, y_max*1.3),
                    ha='left', fontsize=6)
                    ax[obs-1,det].annotate(f"Region {reg}",
                        xy=(x_max, y_min),
                        xytext=(e_high *1.02, y_min),
                        fontsize=6, annotation_clip=False)
            
            color_idx += 1


# formatting the plot
for det in range(2):
    for obs in range(num_obsids):
        plot = ax[obs,det]
        plot.set(yscale="log",xscale="log",xlabel='Energy (keV)',ylabel=r'counts s$^{-1}$ keV$^{-1}$',xlim=(e_low,e_high))
        plot.xaxis.set_major_formatter(ticker.FuncFormatter(lambda val, pos: '{:.0f}'.format(val)))
        plot.xaxis.set_major_locator(ticker.FixedLocator([5, 10, 15]))
        plot.xaxis.set_minor_locator(ticker.NullLocator())  # Suppress minor ticks
        plot.set(title=f'{obsids[obs]}:{'A' if det==0 else 'B'}')
        plot.set(ylim=spectra_y_lims)





# #### PLOTTING RATIOS ####

# read in saved plotting info and organize it
saved_plot_info = f'{plotting_directory}/save_ratios.dat'
lines = []
with open(saved_plot_info) as file:
    for line in file:
        lines.append(line)

regions = {i:{o:{'A':{}, 'B':{}} for o in range(1,num_obsids+1)} for i in range(1,num_reg+1)}
for idx,line in enumerate(lines):
    if 'RegA' in line:
        num = line.split('RegA')[1].split(' ')[0]
        num = int(num)

        obs = 1
        if num > num_reg:
            num = num - num_reg*num_obsids
            obs = 2

        x_line = lines[idx+1]
        x = [float(val) for val in x_line.split('\n')[0].split('   ')[:-1]]

        xerr_line = lines[idx+2]
        xerr = [(float(val), float(val)) for val in xerr_line.split('\n')[0].split('   ')[:-1]]

        y_line = lines[idx+3]
        y = [float(val) for val in y_line.split('\n')[0].split('   ')[:-1]]
        
        yerr_line = lines[idx+4]
        yerr = [(float(val), float(val)) for val in yerr_line.split('\n')[0].split('   ')[:-1]]

        regions[num][obs]['A'] = {'x': x,
                        'xerr': xerr,
                        'y': y,
                        'yerr': yerr}
    elif 'RegB' in line:
        num = line.split('RegB')[1].split(' ')[0]
        num = int(num) - num_reg

        obs = 1
        if num > num_reg:
            num = num - num_reg*num_obsids
            obs = 2

        x_line = lines[idx+1]
        x = [float(val) for val in x_line.split('\n')[0].split('   ')[:-1]]

        xerr_line = lines[idx+2]
        xerr = [(float(val), float(val)) for val in xerr_line.split('\n')[0].split('   ')[:-1]]

        y_line = lines[idx+3]
        y = [float(val) for val in y_line.split('\n')[0].split('   ')[:-1]]
        
        yerr_line = lines[idx+4]
        yerr = [(float(val), float(val)) for val in yerr_line.split('\n')[0].split('   ')[:-1]]

        regions[num][obs]['B'] = {'x': x,
                        'xerr': xerr,
                        'y': y,
                        'yerr': yerr}


# Defining the plot things will be added to
# fig2, ax2 = plt.subplots(len(regs_to_include_in_plot)*num_obsids,2)#,gridspec_kw={'hspace': 0},sharex=True)
fig2 = plt.figure()
outer = fig2.add_gridspec(num_obsids,2, hspace=0.35, wspace=0.25)

# for each obsid
for o in range(num_obsids):
    # for each detector
    for det in range(2):
        inner = outer[o,det].subgridspec(len(regs_to_include_in_plot), 1, hspace=0)
        master = None
        # there are r regions, which share an x axis
        for r in range(len(regs_to_include_in_plot)):
            # row = r + o*len(regs_to_include_in_plot)
            # column = det
            # print(row,column)

            if master is None:
                ax0 = fig2.add_subplot(inner[r,0])
                master = ax0
            else:
                ax0 = fig2.add_subplot(inner[r,0], sharex=master)

            ax0.label_outer()

            regions[r+1][o+1]['A' if det==0 else 'B']['plot'] = ax0

# plot Ratio
for obs in range(1,num_obsids+1):
    color_idx = 0
    for reg in regions.keys():
        if reg in regs_to_include_in_plot:
            for det in ['A', 'B']:
                data = regions[reg][obs][det]
                x = data['x']
                xerr = data['xerr']
                y = data['y']
                yerr = data['yerr']
                plot = data['plot']
                plot.errorbar(x,y,xerr=np.array(xerr).T,yerr=np.array(yerr).T,fmt='none',linewidth=1.5,color=colors[color_idx])

                # Formatting the plot
                plot.set(yscale="linear",xscale="log",xlabel='Energy (keV)',ylabel=f'R:{reg}',
                    ylim=(-0.3,2.3),xlim=(e_low,e_high))
                plot.plot([0,30],[1,1], color='red', linewidth=1.0)
                plot.set_yticks([0.2, 1.0, 1.8])
                plot.xaxis.set_major_formatter(ticker.FuncFormatter(lambda val, pos: '{:.0f}'.format(val)))
                plot.xaxis.set_major_locator(ticker.FixedLocator([5, 10, 15]))
                plot.xaxis.set_minor_locator(ticker.NullLocator())  # Suppress minor ticks

                if reg == 1:
                    plot.set_title(f'{obsids[obs-1]}:{det}')



            color_idx += 1

# Add a single y-axis label on the right (adjust position as needed)
for o in range(num_obsids):
    for det in range(1):
        bbox = outer[o, det].get_position(fig2)
        fig2.text(bbox.x0 - 0.1, (bbox.y0 + bbox.y1)/2, 'data/model', rotation=90, va='center', fontsize='12')




## Plot limits (defined in top block for convinience, but you could also just change them here)
## spec plot
for det in range(2):
    for obs in range(num_obsids):
        plot = ax[obs,det]
        plot.set(ylim=spectra_y_lims)
        # plot.set(ylim=(1e-16,2e-2))
fig.tight_layout()

## ratio plot
for obs in range(1,num_obsids+1):
    for reg in regions.keys():
        if reg in regs_to_include_in_plot:
            for det in ['A', 'B']:
                plot = data['plot']
                plot.set(ylim=ratio_y_lims)
                plot.set_yticks([0.2, 1.0, 1.8])


if save_plot:
    fig.savefig(f'{plot_output_path}/crossarf_spectra_plots.pdf')
    fig2.savefig(f'{plot_output_path}/crossarf_ratio_plots.pdf')

    
plt.show()
