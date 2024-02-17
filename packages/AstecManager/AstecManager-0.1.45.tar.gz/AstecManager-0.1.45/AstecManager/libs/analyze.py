import os
from os import listdir
import numpy as np
import re
from os.path import isfile, join
from AstecManager.libs.data import imread
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
from AstecManager.libs.graphs import has_info_lineage, plot_variables,get_cell_names, auto_name_time, format_cell_id
from AstecManager.libs.lineage import temporal_alignment,get_aligned_time , build_all_leaves, count_cells
from AstecManager.libs.jsonlib import addDictToMetadata

def apply_analysis(list_lineage,list_noms,folder_out,embryo_name,mincells_test,maxcells_test,begin,end,path="",is_post=False,ref_lineage=None,data_path=None):
    print("-> Compute of the cell count plot")
    generate_compare(list_noms, list_lineage, folder_out=folder_out, embryo_name=embryo_name,ref_lineage_path=ref_lineage,data_path=data_path)

    folder_exp = folder_out

    print("-> compute all min max leaves in for ")

    begin_temp = begin
    end_temp = end
    if is_post:
        plotminmaxleaves_post(list_lineage[0], list_noms[0], begin_temp, end_temp,folder_out,data_path=None)
    else :
        plotminmaxleaves(list_lineage, list_noms, begin_temp, end_temp,embryo_name,folder_out,data_path=None)

    os.system("cd " + folder_exp + ' && `for f in *.py; do python3 "$f"; done`')
    os.system("cd "+ folder_out + ' && rm generate_cell_count_multiples_.py')
def is_image(f):
    return ".nii" in f or ".mha" in f or ".h5" in f or ".inr" in f


def generate_compare(input_names, list_lineage, folder_out="DATA/OUT/", title_suffix="", embryo_name="",
                     remove_times=[], only_times=[], mincells=64, maxcells=500,ref_lineage_path=None,data_path=None):
    folder_exp = ""
    for embryoname in input_names:
        if embryoname is not None:
            folder_exp += embryoname + "_"

    for lineage in list_lineage:
        if not os.path.isfile(lineage):
            print(lineage + " is not a file , check for typos")
            return

    if data_path is not None:
        if not os.path.isdir(data_path):
            os.makedirs(data_path)
    list_count = {}
    list_name = []
    list_histo = []
    ref_cell_count = None
    if ref_lineage_path != None:
        ref_cell_count = count_cells(ref_lineage_path, remove_time=remove_times, only_times=only_times)
    for i in range(0, len(list_lineage)):
        count = count_cells(list_lineage[i], remove_time=remove_times, only_times=only_times)
        txt = ""
        for key in count:
            txt += str(key)+":"+str(count[key])+";"
        if data_path is not None:
            f = open(os.path.join(data_path,str(input_names[i])+"-cell-count.csv"),"w+")
            f.write(txt)
            f.close()

        if ref_lineage_path != None:
            a,b = temporal_alignment(ref_lineage_path,list_lineage[i])
            temp_count = {}
            for time in count:
                print("aligned time : " + str(get_aligned_time(time, a, b)) + " get count " + str(
                    count[time]) + " from time init : " + str(time))
                #TODO : verifier si on doit pas prendre le temps aligné de l'embryon
                temp_count[get_aligned_time(time,a,b)] = count[time]
            count = temp_count
        list_histo.append(count)
        for t in count:
            list_count[input_names[i]] = [count[t]]
        list_name.append(input_names[i].replace("SEG_test_", ""))
        parameters = {}
        parameters["list_embryo_name"] = plot_variables(list_name, False)
        parameters["list_cell_count_by_time"] = plot_variables(list_histo, False)
        if embryo_name != "":
            parameters["embryo_name"] = plot_variables(embryo_name, True)
        if ref_lineage_path != None:
            save_cell_count_plot("cell_count_multiples", list_name, list_histo, folder_out,cell_count_ref=ref_cell_count)
        else:
            save_cell_count_plot("cell_count_multiples", list_name, list_histo, folder_out)
        parameters = {}
        #addDictToMetadata(path, parameters)


def save_cell_count_plot(plot_title,list_names,list_count,folder_out,cell_count_ref=None):

    list_cell_count_by_time =list_count
    folder_out =folder_out
    list_embryo_name =list_names
    title =plot_title
    if not os.path.isdir(folder_out):
        os.makedirs(folder_out)

    print(">>Cells counted, saving to image result")
    title = "cell_count"
    plt.figure(figsize=(10, 6))
    plt.title("Cell count along time" + "_" + title)
    plt.xlabel("Time")
    plt.ylabel("Cell count")
    for i in range(0, len(list_cell_count_by_time)):
        print(str(list_embryo_name[i]) + " -> " + str(list_cell_count_by_time[i]))
        times = []
        cell_counts = []
        cell_count_by_time = list_cell_count_by_time[i]
        for time in cell_count_by_time:
            times.append(time)
            cell_counts.append(cell_count_by_time[time])
        plt.plot(times, cell_counts, '-', label=list_embryo_name[i], alpha=0.5)
    print(str(cell_count_ref))
    if cell_count_ref is not None:
        timesref = []
        cell_countsref = []
        for time in cell_count_ref:
            timesref.append(time)
            cell_countsref.append(cell_count_ref[time])
        plt.plot(timesref, cell_countsref, '-', label="reference", color='grey', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(folder_out,title + ".png"))
    plt.clf()




def plotminmaxleaves(lineage_list, embryo_name_list, start_time, end_time, embryo_name, folder_out="DATA/OUT/",data_path=None):
    if folder_out != "":
        if not os.path.exists(folder_out):
            os.makedirs(folder_out)

    if data_path is not None:
        if not os.path.isdir(data_path):
            os.makedirs(data_path)
    fig, ax = plt.subplots(2, 2)

    fig.suptitle("Early cell death detection in branch")
    cell_keys_info = {}
    timefor64cells = start_time
    finalx = []
    current_axis_x = 0
    current_axis_y = 0
    for i in range(0, len(lineage_list)):
        lineage = lineage_list[i]
        if has_info_lineage(lineage, "cell_name") or has_info_lineage(lineage, "cell_contact_surface") and False:
            timefor64cells = -1
            cellcountfortime = 64
            cellforlineage = dict(sorted(count_cells(lineage).items()))
            for time in cellforlineage:
                if cellforlineage[time] >= 64:
                    timefor64cells = int(time)
                    cellcountfortime = int(cellforlineage[time])
                break
        cell_keys_by_time, final_proportion, mars_ids1, all_leaves = build_all_leaves(lineage, timefor64cells,
                                                                                      end_time)
        txt = ""
        if data_path is not None:
            for i in range(0, len(all_leaves)):
                txt += str(mars_ids1[i]) + ":" + str(all_leaves[i]) + ";"
            txt += str(final_proportion)
            f = open(os.path.join(data_path, str(embryo_name)) + "-early-cell-death.csv", "w+")
            f.write(txt)
            f.close()
        cell_keys_info[lineage] = cell_keys_by_time

        finalx = []
        lineagepath = None
        if has_info_lineage(lineage, "cell_name")  and False:
            nameinit = get_cell_names(lineage, mars_ids1)
            finalx = nameinit
        elif has_info_lineage(lineage, "cell_contact_surface")  and False:
            lineagepath = auto_name_time(lineage, cellcountfortime)
            nameinit = get_cell_names(lineagepath, mars_ids1)
            finalx = nameinit
        else:
            for idcell in mars_ids1:
                finalx.append(format_cell_id(idcell))
        if lineagepath is not None:
            os.system("rm " + str(lineagepath))
        ax[current_axis_x, current_axis_y].plot([], [], ' ',
                                                label="early cell death:" + str(round(final_proportion, 3)) + "%")
        print(str(len(all_leaves)) + " - " + str(len(finalx)))
        if len(all_leaves) > 0:
            ax[current_axis_x, current_axis_y].boxplot(all_leaves, labels=finalx)
        ax[current_axis_x, current_axis_y].set_ylim([start_time, end_time])
        ax[current_axis_x, current_axis_y].set_title(embryo_name_list[i].replace("SEG_test_", ""))
        ax[current_axis_x, current_axis_y].set_xticklabels([])
        if current_axis_y == 0:
            ax[current_axis_x, current_axis_y].set_ylabel("Time of cell death")
        if current_axis_x == 1:
            ax[current_axis_x, current_axis_y].set_xlabel("Lineage starting cell")
        ax[current_axis_x, current_axis_y].legend()
        current_axis_x = (current_axis_x + 1) % 2
        if current_axis_x == 0:
            current_axis_y += 1 % 2

    print("Saving to identity card")
    fig.tight_layout()
    fig.set_size_inches(18.5, 10.5)
    fig.suptitle("Early cell death for " + str(embryo_name), fontsize=14)
    fig.savefig(folder_out + "/early_cell_death.png")


def plotminmaxleaves_post(lineage, embryo_name, start_time, end_time, folder_out="DATA/OUT/",data_path=None):
    if folder_out != "":
        if not os.path.exists(folder_out):
            os.makedirs(folder_out)
    if data_path is not None:
        if not os.path.isdir(data_path):
            os.makedirs(data_path)
    fig = plt.figure()

    fig.suptitle("Early cell death detection in branch")
    cell_keys_info = {}
    timefor64cells = start_time
    finalx = []
    if has_info_lineage(lineage, "cell_name") or has_info_lineage(lineage, "cell_contact_surface")  and False:
        timefor64cells = -1
        cellcountfortime = 64
        cellforlineage = dict(sorted(count_cells(lineage).items()))
        for time in cellforlineage:
            if cellforlineage[time] >= 64:
                timefor64cells = int(time)
                cellcountfortime = int(cellforlineage[time])
            break
    cell_keys_by_time, final_proportion, mars_ids1, all_leaves = build_all_leaves(lineage, timefor64cells,
                                                                                  end_time)

    txt = ""
    if data_path is not None:
        for i in range(0,len(all_leaves)):
            txt += str(mars_ids1[i])+":"+str(all_leaves[i])+";"
        txt += str(final_proportion)
        f = open(os.path.join(data_path,str(embryo_name))+"-early-cell-death.csv","w+")
        f.write(txt)
        f.close()
        name = lineage.replace("\\","/").split("/")[-1]
    cell_keys_info[lineage] = cell_keys_by_time

    finalx = []
    lineagepath = None
    if has_info_lineage(lineage, "cell_name")  and False:
        nameinit = get_cell_names(lineage, mars_ids1)
        finalx = nameinit
    elif has_info_lineage(lineage, "cell_contact_surface")  and False:
        lineagepath = auto_name_time(lineage, cellcountfortime)
        nameinit = get_cell_names(lineagepath, mars_ids1)
        finalx = nameinit
    else:
        for idcell in mars_ids1:
            finalx.append(format_cell_id(idcell))
    if lineagepath is not None:
        os.system("rm " + str(lineagepath))
    plt.plot([], [], ' ', label="early cell death:" + str(round(final_proportion, 3)) + "%")
    if len(all_leaves) > 0:
        plt.boxplot(all_leaves, labels=finalx)
    plt.ylim([start_time, end_time])
    plt.title(embryo_name.replace("SEG_test_", ""))
    plt.xticks(rotation=90)
    plt.legend()
    plt.ylabel("Time of cell death")

    print("Saving to identity card")
    # fig.tight_layout()
    # fig.set_size_inches(18.5, 10.5)
    plt.title("Early cell death for " + str(embryo_name), fontsize=14)
    fig.savefig(folder_out + "/early_cell_death.png")


def camerastacksignaltonoise(axis, folder_images,analysisfolder, title, boundaries=None, display_x_label=True,
                             display_y_label=True):
    print("     -> Intensities analysis for folder : "+str(folder_images))
    if boundaries is None:
        boundaries = [0, 2000]
    average_by_time = {}
    max_by_time = {}
    if not os.path.isdir(join(analysisfolder,"raw")):
        os.makedirs(join(analysisfolder,"raw"))
    csv_data = join(join(analysisfolder,"raw"),title.replace(" ","_")+".csv")
    if os.path.isfile(csv_data):
        f = open(csv_data,"r")
        datacsv = f.read()
        f.close()
        for line in datacsv.split(":"):
            if line != "":
                data = line.split(";")
                time = int(data[0])
                mean = float(data[1])
                std = float(data[2])
                average_by_time[time] = mean
                max_by_time[time] = std

    else :
        image_name_list = [f for f in listdir(folder_images) if isfile(join(folder_images, f)) and is_image(f)]
        image_name_list.sort()
        csv = ""
        for image_name in image_name_list:
            image_path = join(folder_images, image_name)
            image_time = int(re.findall(r'\d+', image_name.split(".")[0])[-1])
            image_np = imread(image_path)
            mean = np.mean(image_np)
            intensities = list(np.unique(image_np.reshape(-1)))
            intensities.sort()
            intensities.reverse()
            cumulated = []
            for intensity in intensities:
                if len(cumulated) < 0.05*len(intensities):
                    cumulated.append(intensity)
            max_cumulated = min(cumulated)
            maxt = np.max(image_np)
            print("Image max : "+str(maxt)+" cumulated max : "+str(max_cumulated))
            # Get the list of intensities in images
            # Sort them
            # Take the one at 95%
            average_by_time[image_time] = mean
            max_by_time[image_time] = max_cumulated
            csv += str(image_time)+";"+str(mean)+";"+str(max_cumulated)+":"
        f = open(csv_data,"w+")
        f.write(csv)
        f.close()
    data_means = list(average_by_time.values())
    data_std = list(max_by_time.values())
    times = list(average_by_time.keys())
    axis.plot(times, data_means, '-')
    mins = min([a - b for a, b in zip(data_means, data_std)])
    maxs = max([a + b for a, b in zip(data_means, data_std)])
    axis.fill_between(times, [a + b for a, b in zip(data_means, data_std)], [a  for a in data_means], alpha=0.2)
    axis.set_ylim(boundaries)
    if display_x_label:
        axis.set_xlabel("Time")
    if display_y_label:
        axis.set_ylabel("Signal mean (line) and amplitude")
    axis.legend()
    axis.set_title(title)
    return mins,maxs,csv_data




def plotsignaltonoise(embryo_name, parameters,one_stack_only=False,stack_chosen=0):
    fig, ax = plt.subplots(2, 2)

    path = "."
    folder_out = os.path.join(path, "analysis")
    if folder_out != "":
        if not os.path.exists(folder_out):
            os.makedirs(folder_out)
    raw_path = os.path.join(path, parameters["DIR_RAWDATA"].replace('"','').replace("'",""))
    if (one_stack_only and stack_chosen == 0) or not one_stack_only:
        stack_0_left_cam = os.path.join(raw_path, parameters["DIR_LEFTCAM_STACKZERO"].replace('"','').replace("'",""))
        stack_0_right_cam = os.path.join(raw_path, parameters["DIR_RIGHTCAM_STACKZERO"].replace('"','').replace("'",""))
    if (one_stack_only and stack_chosen == 1) or not one_stack_only:
        stack_1_left_cam = os.path.join(raw_path, parameters["DIR_LEFTCAM_STACKONE"].replace('"','').replace("'",""))
        stack_1_right_cam = os.path.join(raw_path, parameters["DIR_RIGHTCAM_STACKONE"].replace('"','').replace("'",""))
    mins = []
    maxs = []
    if (one_stack_only and stack_chosen == 0) or not one_stack_only:
        miny,maxy,csv = camerastacksignaltonoise(ax[0, 0], stack_0_left_cam,folder_out, "Left camera of stack 0", display_x_label=False,
                                 display_y_label=True)
        mins.append(miny)
        maxs.append(maxy)
    if (one_stack_only and stack_chosen == 0) or not one_stack_only:
        miny,maxy,csv = camerastacksignaltonoise(ax[0, 1], stack_0_right_cam,folder_out, "Right camera of stack 0", display_x_label=False,
                                 display_y_label=False)
        mins.append(miny)
        maxs.append(maxy)
    if (one_stack_only and stack_chosen == 1) or not one_stack_only:
        miny,maxy,csv = camerastacksignaltonoise(ax[1, 0], stack_1_left_cam,folder_out, "Left camera of stack 1", display_x_label=True,
                                 display_y_label=True)
        mins.append(miny)
        maxs.append(maxy)
    if (one_stack_only and stack_chosen == 1) or not one_stack_only:
        miny,maxy,csv = camerastacksignaltonoise(ax[1, 1], stack_1_right_cam,folder_out, "Right camera of stack 1", display_x_label=True,
                                 display_y_label=False)
        mins.append(miny)
        maxs.append(maxy)
    realmin = min(mins)
    realmax = max(maxs)
    ax[0,0].set_ylim([0,realmax])
    ax[0,1].set_ylim([0,realmax])
    ax[1,0].set_ylim([0,realmax])
    ax[1,1].set_ylim([0,realmax])
    fig.tight_layout()
    fig.set_size_inches(18.5, 10.5)
    fig.suptitle("Signal mean and amplitude though time for " + str(embryo_name)+" raw images", fontsize=14)
    fig.savefig(os.path.join(os.path.join(folder_out,"raw"), "images_intensities.png"))
    parameters["step"] = "rawdata_intensities_plot"
    parameters["embryo_name "] = embryo_name
    addDictToMetadata(path, parameters)


def plotsignaltonoise_tofolder(folder,embryo_name,one_stack_only=False,stack_chosen=0):
    fig, ax = plt.subplots(2, 2)
    path = "."
    folder_out = os.path.join(folder, "analysis")
    if folder_out != "":
        if not os.path.exists(folder_out):
            os.makedirs(folder_out)
    raw_path = os.path.join(folder,"RAWDATA")
    stack_0_left_cam = os.path.join(raw_path,"stack_0_channel_0_obj_left")
    stack_0_right_cam = os.path.join(raw_path, "stack_0_channel_0_obj_right")
    stack_1_left_cam = os.path.join(raw_path, "stack_1_channel_0_obj_left")
    stack_1_right_cam = os.path.join(raw_path, "stack_1_channel_0_obj_right")
    mins = []
    maxs = []
    if (one_stack_only and stack_chosen == 0) or not one_stack_only:
        miny,maxy,csv = camerastacksignaltonoise(ax[0, 0], stack_0_left_cam,folder_out, "Left camera of stack 0", display_x_label=False,
                                 display_y_label=True)
        mins.append(miny)
        maxs.append(maxy)
    if (one_stack_only and stack_chosen == 0) or not one_stack_only:
        miny,maxy,csv = camerastacksignaltonoise(ax[0, 1], stack_0_right_cam,folder_out, "Right camera of stack 0", display_x_label=False,
                                 display_y_label=False)
        mins.append(miny)
        maxs.append(maxy)
    if (one_stack_only and stack_chosen == 1) or not one_stack_only:
        miny,maxy,csv = camerastacksignaltonoise(ax[1, 0], stack_1_left_cam,folder_out, "Left camera of stack 1", display_x_label=True,
                                 display_y_label=True)
        mins.append(miny)
        maxs.append(maxy)
    if (one_stack_only and stack_chosen == 1) or not one_stack_only:
        miny,maxy,csv = camerastacksignaltonoise(ax[1, 1], stack_1_right_cam,folder_out, "Right camera of stack 1", display_x_label=True,
                                 display_y_label=False)
        mins.append(miny)
        maxs.append(maxy)
    realmin = min(mins)
    realmax = max(maxs)
    ax[0,0].set_ylim([0,realmax])
    ax[0,1].set_ylim([0,realmax])
    ax[1,0].set_ylim([0,realmax])
    ax[1,1].set_ylim([0,realmax])
    fig.tight_layout()
    fig.set_size_inches(18.5, 10.5)
    fig.suptitle("Intensities mean and standard deviation though time for " + str(folder)+" raw images", fontsize=14)
    fig.savefig(os.path.join(folder_out, "raw_images_intensities.png"))


def compute_image_cellcount_and_volumes(mars_path,resolution):

    mars_image = imread(mars_path)
    if mars_image is None:
        return None,None
    cell_list,counts = np.unique(mars_image,return_counts=True)
    final_cells = []
    final_volume_count = []
    for i in range(len(cell_list)):
        if cell_list[i] != 1:
            final_volume_count.append(counts[i]*resolution)
            final_cells.append(cell_list[i])
    return final_cells,final_volume_count



def plotmarsinfos(embryo_name, exp_seg,begin_time,resolution):

    fig = plt.figure()
    analysis_folder = os.path.join(".","analysis")
    folder_out = os.path.join(analysis_folder,"mars")
    if not os.path.isdir(folder_out):
        os.makedirs(folder_out)
    mars_seg = os.path.join(os.path.join(".","SEG"),"SEG_"+str(exp_seg).replace('"','').replace("'",""))
    mars_path = os.path.join(mars_seg,"."+"_mars_t{:03d}".format(int(begin_time))+".nii")
    print(mars_path)
    if not os.path.isfile(mars_path):
        print("Mars not found, leaving")
        return
    final_cells,volumes = compute_image_cellcount_and_volumes(mars_path,resolution)
    txt = ""
    for i in range(0,len(volumes)):
        txt += str(final_cells[i])+":"+str(volumes[i])+";"
    txt += str(len(final_cells))
    f = open(os.path.join(folder_out,"mars_data.csv"),"w+")
    f.write(txt)
    f.close()
    plt.hist(volumes,bins=len(final_cells))
    plt.annotate("Cell count : " + str(len(final_cells)), xy=(0.01,0.95),xycoords='axes fraction',
             fontsize=12)
    fig.set_size_inches(18.5, 10.5)
    ax = plt.figure().gca()
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.ylabel("Number of cells")
    plt.xlabel("Volumes (um3)")
    plt.xlim([0,40000*resolution])
    plt.title("Cell count and volume distribution for mars " + str(exp_seg).replace('"','').replace("'",""))
    fig.savefig(os.path.join(folder_out, "cell_count_and_volume_"+str(exp_seg)+".png"))