import os
import matplotlib.pyplot as plt
from AstecManager.libs.lineage import Get_Cell_Contact_Surface, Get_Cell_Values_Float,Get_Cell_Names, get_id_t, build_all_leaves, count_cells,build_branch_length_no_both,count_small_cells
import matplotlib.ticker as ticker
from AstecManager.libs.data import imread
import numpy as np
import pandas as pd
import seaborn as sns
import math
def plot_volumes_mixed_histo(embryo_name,divs,folder_out="DATA/OUT/",embryo_name_2=None,divs2=None):
    f = open ("template_folders/real_histo_volume_mixed.py")
    lines = f.readlines()
    f.close()
    new_lines=[]

    for line in lines:
        new_line=line
        splitted_param = line.split('=')
        if len(splitted_param) == 2:
            if splitted_param[0] == "divs":
                new_line = splitted_param[0]+'='+str(divs)+'\n'
            elif splitted_param[0] == "embryo_name":
                new_line = splitted_param[0] + '="' + str(embryo_name)+'"\n'
            elif splitted_param[0] == "folder_out":
                new_line=splitted_param[0]+ '="' + str(folder_out)+'"\n'
            elif splitted_param[0] == "embryo_name_2":
                new_line=splitted_param[0]+ '="' + str(embryo_name_2)+'"\n'
            elif splitted_param[0] == "divs2":
                new_line=splitted_param[0]+ '=' + str(divs2)+'\n'
        new_lines.append(new_line)

    folder_exp = embryo_name
    if embryo_name_2 is not None:
        folder_exp += "_" + embryo_name_2

    if os.path.join(folder_out,folder_exp) != "":
        if not os.path.exists(os.path.join(folder_out,folder_exp)):
            os.makedirs(os.path.join(folder_out,folder_exp))

    title = "generate_"+str(folder_exp)+"_volumemix_histo"
    if embryo_name_2 is not None:
        title+= "_"+str(embryo_name_2)

    f2 = open(os.path.join(folder_out,folder_exp+"/"+title.replace(" ","_")+".py"),"w+")
    f2.writelines(new_lines)
    f2.close()
def plot_divisions_histo(embryo_name,divs,folder_out="DATA/OUT/",embryo_name_2=None,divs2=None,averageshift=0):
    f = open ("template_folders/real_histo_division.py")
    lines = f.readlines()
    f.close()
    new_lines=[]

    for line in lines:
        new_line=line
        splitted_param = line.split('=')
        if len(splitted_param) == 2:
            if splitted_param[0] == "divs":
                new_line = splitted_param[0]+'='+str(divs)+'\n'
            elif splitted_param[0] == "embryo_name":
                new_line = splitted_param[0] + '="' + str(embryo_name)+'"\n'
            elif splitted_param[0] == "average":
                new_line = splitted_param[0] + '=' + str(averageshift)+'\n'
            elif splitted_param[0] == "folder_out":
                new_line=splitted_param[0]+ '="' + str(folder_out)+'"\n'
            elif splitted_param[0] == "embryo_name_2":
                new_line=splitted_param[0]+ '="' + str(embryo_name_2)+'"\n'
            elif splitted_param[0] == "divs2":
                new_line=splitted_param[0]+ '=' + str(divs2)+'\n'
        new_lines.append(new_line)

    folder_exp = embryo_name
    if embryo_name_2 is not None:
        folder_exp += "_" + embryo_name_2

    if os.path.join(folder_out,folder_exp) != "":
        if not os.path.exists(os.path.join(folder_out,folder_exp)):
            os.makedirs(os.path.join(folder_out,folder_exp))

    title = "generate_"+str(folder_exp)+"_divions_histo"
    if embryo_name_2 is not None:
        title+= "_"+str(embryo_name_2)

    f2 = open(os.path.join(folder_out,folder_exp+"/"+title.replace(" ","_")+".py"),"w+")
    f2.writelines(new_lines)
    f2.close()

def plot_volume_histo(embryo_name,volumes,folder_out="DATA/OUT/",embryo_name_2=None,volumes2=None,filter_background=False):
    f = open ("template_folders/histo_volumes.py")
    lines = f.readlines()
    f.close()
    new_lines=[]

    for line in lines:
        new_line=line
        splitted_param = line.split('=')
        if len(splitted_param) == 2:
            if splitted_param[0] == "volumes":
                new_line = splitted_param[0]+'='+str(volumes)+'\n'
            elif splitted_param[0] == "embryo_name":
                new_line = splitted_param[0] + '="' + str(embryo_name)+'"\n'
            elif splitted_param[0] == "folder_out":
                new_line=splitted_param[0]+ '="' + str(folder_out)+'"\n'
            elif splitted_param[0] == "embryo_name_2":
                new_line=splitted_param[0]+ '="' + str(embryo_name_2)+'"\n'
            elif splitted_param[0] == "volumes2":
                new_line=splitted_param[0]+ '=' + str(volumes2)+'\n'
            elif splitted_param[0] == "filter_background":
                new_line=splitted_param[0]+ '=' + str(filter_background)+'\n'
        new_lines.append(new_line)

    folder_exp = embryo_name
    if embryo_name_2 is not None:
        folder_exp += "_" + embryo_name_2

    if os.path.join(folder_out,folder_exp) != "":
        if not os.path.exists(os.path.join(folder_out,folder_exp)):
            os.makedirs(os.path.join(folder_out,folder_exp))

    title = "generate_"+str(folder_exp)+"_volume_histo"
    if filter_background:
        title += "_filtered"
    if embryo_name_2 is not None:
        title+= "_"+str(embryo_name_2)
    f2 = open(os.path.join(folder_out,folder_exp+"/"+title.replace(" ","_")+".py"),"w+")
    f2.writelines(new_lines)
    f2.close()

def plot_leaves_histo(embryo_name,leaves,folder_out="DATA/OUT/",embryo_name_2=None,leaves2=None):
    f = open ("template_folders/histo_min_max_leaves.py")
    lines = f.readlines()
    f.close()
    new_lines=[]

    for line in lines:
        new_line=line
        splitted_param = line.split('=')
        if len(splitted_param) == 2:
            if splitted_param[0] == "leaves":
                new_line = splitted_param[0]+'='+str(leaves)+'\n'
            elif splitted_param[0] == "embryo_name":
                new_line = splitted_param[0] + '="' + str(embryo_name)+'"\n'
            elif splitted_param[0] == "folder_out":
                new_line=splitted_param[0]+ '="' + str(folder_out)+'"\n'
            elif splitted_param[0] == "embryo_name_2":
                new_line=splitted_param[0]+ '="' + str(embryo_name_2)+'"\n'
            elif splitted_param[0] == "leaves2":
                new_line=splitted_param[0]+ '=' + str(leaves2)+'\n'
        new_lines.append(new_line)

    folder_exp = embryo_name
    if embryo_name_2 is not None:
        folder_exp += "_" + embryo_name_2

    if os.path.join(folder_out,folder_exp) != "":
        if not os.path.exists(os.path.join(folder_out,folder_exp)):
            os.makedirs(os.path.join(folder_out,folder_exp))

    title = "generate_"+str(folder_exp)+"_leaves_histo"
    if embryo_name_2 is not None:
        title+= "_"+str(embryo_name_2)
    f2 = open(os.path.join(folder_out,folder_exp+"/"+title.replace(" ","_")+".py"),"w+")
    f2.writelines(new_lines)
    f2.close()

def plot_branch_histo(embryo_name,branch_length_by_start,folder_out="DATA/OUT/",embryo_name_2=None,histo_branch2=None):
    f = open ("template_folders/histo_branch.py")
    lines = f.readlines()
    f.close()
    new_lines=[]

    for line in lines:
        new_line=line
        splitted_param = line.split('=')
        if len(splitted_param) == 2:
            if splitted_param[0] == "branch_length_by_start":
                new_line = splitted_param[0]+'='+str(branch_length_by_start)+'\n'
            elif splitted_param[0] == "embryo_name":
                new_line = splitted_param[0] + '="' + str(embryo_name)+'"\n'
            elif splitted_param[0] == "folder_out":
                new_line=splitted_param[0]+ '="' + str(folder_out)+'"\n'
            elif splitted_param[0] == "embryo_name_2":
                new_line=splitted_param[0]+ '="' + str(embryo_name_2)+'"\n'
            elif splitted_param[0] == "histo_branch2":
                new_line=splitted_param[0]+ '=' + str(histo_branch2)+'\n'
        new_lines.append(new_line)

    folder_exp = embryo_name
    if embryo_name_2 is not None:
        folder_exp += "_" + embryo_name_2
    if os.path.join(folder_out,folder_exp) != "":
        if not os.path.exists(os.path.join(folder_out,folder_exp)):
            os.makedirs(os.path.join(folder_out,folder_exp))

    title = "generate_"+str(folder_exp)+"_branch_length_histo"
    if embryo_name_2 is not None:
        title+= "_"+str(embryo_name_2)

    f2 = open(os.path.join(folder_out,folder_exp+"/"+title.replace(" ","_")+".py"),"w+")
    f2.writelines(new_lines)
    f2.close()

def plot_branch_histo_multiple(axis,list_embryo_name,list_branch_length_by_start,compare_to_ref=None):
    axis.set_ylabel("Number of branches")
    axis.set_xlabel("Branches size")
    axis.set_title("Distribution of branch length")
    for i in range(0, len(list_branch_length_by_start)):
        branches_length_suffle = []
        for key in list_branch_length_by_start[i]:
            branches_length_suffle.append(list_branch_length_by_start[i][key])
        axis.hist(branches_length_suffle, label=list_embryo_name[i], alpha=0.5)
    if compare_to_ref is not None:
        axis.hist(compare_to_ref, label="reference", color='grey',alpha=0.5)

def split_range_in_bins(minb,maxb,bin_number):
	rangenumber = maxb-minb
	part_duration = int(rangenumber / bin_number)
	parts = []
	marker = 0

	for _ in range(bin_number):
	    part = [marker, marker + part_duration]
	    marker += part_duration
	    parts.append(part)
	return parts

def plot_branch_histo_multiplenodeath(axis, list_lineage,compare_to_ref=False,mincells=None,maxcells=None):
    axis.set_ylabel("Number of branches")
    axis.set_xlabel("Branches size")
    axis.set_title("Distribution of branch length leading to division")
    branches_length_suffle = []
    minbinaries = 10000
    maxbinaries = -10000
    for lineage in list_lineage:
        cell_count_by_time = count_cells(lineage)
        mintime = 10000
        maxtime = -100000
        for time in cell_count_by_time:
            timecount = cell_count_by_time[time]
            if timecount >= mincells and timecount <= maxcells:
                if mintime > time:
                    mintime = time
                if maxtime < time:
                    maxtime = time
        histogram=build_branch_length_no_both(lineage,mintime=mintime,maxtime=maxtime)
        for key in histogram:
            if compare_to_ref:
                bl = histogram[key]
                if bl < minbinaries:
                    minbinaries = bl
                if bl > maxbinaries:
                    maxbinaries = bl
            branches_length_suffle.append(histogram[key])
        if not compare_to_ref:
            axis.hist(branches_length_suffle, label=lineage, alpha=0.5)
    if compare_to_ref:
        refhistograms = generate_ref_histogram_no_death(mincells,maxcells)
        distribs = []
        for histo in refhistograms:
            localdistrib=[]
            for key in histo:
                localdistrib.append(histo[key])
            distribs.append(localdistrib)
        for hist in distribs:
            for bl in hist:
                val = hist[bl]
                if val < minbinaries:
                    minbinaries = val
                if val > maxbinaries:
                    maxbinaries = val
        binaries_boundaries = split_range_in_bins(minbinaries,maxbinaries,10)
        print(str(minbinaries)+" => "+str(maxbinaries)+" : "+str(binaries_boundaries))
        number_in_boundaries=[]
        number_embryo_in_boundaries=[]
        for i in range(0,len(binaries_boundaries)):
            number_in_boundaries.append(0)
            number_embryo_in_boundaries.append(0)
            range_actual = range(binaries_boundaries[i][0],binaries_boundaries[i][1]-1)
            print("range = "+str(range_actual))
            for histo in refhistograms:
                written_in_boundaries=False
                for elem in histo:
                    if histo[elem] in range_actual:
                        number_in_boundaries[i] += 1
                        if not written_in_boundaries:
                            number_embryo_in_boundaries[i] += 1
                            written_in_boundaries=True
            print(str(number_embryo_in_boundaries[i])+" => "+str(number_in_boundaries[i]))
        final_boundaries = []
        for i in range(0,len(number_in_boundaries)):
            if number_embryo_in_boundaries[i] > 0:
                count = int(number_in_boundaries[i]/number_embryo_in_boundaries[i])
                for j in range(0,count):
                    final_boundaries.append(binaries_boundaries[i][0])
        matbins = []
        for bin in binaries_boundaries:
            matbins.append(bin[0])
        matbins.append(binaries_boundaries[-1][1])
        count,bins,patches=axis.hist(final_boundaries,bins=matbins,label="reference",color='grey', alpha=0.5)
        xlim = axis.get_xlim()
        ylim = axis.get_ylim()
        axis.hist(branches_length_suffle,bins=matbins , label=list_lineage[0], alpha=0.5)
        xlim2 = axis.get_xlim()
        ylim2 = axis.get_ylim()
        realx = [min(xlim[0],xlim2[0]),max(xlim[1],xlim2[1])]
        realy = [min(ylim[0],ylim2[0]),max(ylim[1],ylim2[1])]
        axis.set_xlim(realx)
        axis.set_ylim(realy)

def lineage_path_with_names(lineagepath):
    lineagepathsplited=lineagepath.split('.')
    return lineagepathsplited[0]+"_minmaxnamed"+"."+lineagepathsplited[1]

def auto_name_time(lineage,cellcount):
    outlineage=lineage_path_with_names(lineage)
    parameters = ""
    parameters += 'cell_number='+str(cellcount)+'\n'
    parameters += 'inputFile="'+str(lineage)+'"\n'
    parameters += 'outputFile="'+str(outlineage)+'"\n'
    parameters += "atlasFiles="+str(get_atlas())+"\n"
    f=open("parameters_naming.py","w+")
    f.write(parameters)
    f.close()
    os.system("conda run -n astec astec_atlas_init_naming -p parameters_naming.py")
    os.remove("parameters_naming.py")
    os.system("rm *.log")
    return outlineage

def get_cell_names(lineage,cells):

    result_names=[]
    names = Get_Cell_Names(lineage)
    for cell in cells:
        if cell in names:
            namesplitted = names[cell].split('.')
            result_names.append(namesplitted[0] + "." + namesplitted[1].lstrip("0").replace("_", "-"))
        else :
            result_names.append(str(format_cell_id(cell)))
    return result_names

def has_info_lineage(lineage,info_name):
    return Get_Cell_Contact_Surface(lineage,info_name) is not None
def format_cell_id(cellid):
    tc,idc = get_id_t(int(cellid))
    return str(tc)+","+str(idc)
def plot_min_max_leaves(axis,list_lineage,start_time,end_time):
    axis.set_title("Early cell death detection in branch")
    axis.set_ylabel("Time of cell death")
    cell_keys_info = {}
    for lineage in list_lineage:
        timefor64cells = start_time
        finalx=[]
        if has_info_lineage(lineage,"cell_name") or has_info_lineage(lineage,"cell_contact_surface"):
            timefor64cells = -1
            cellcountfortime = 64
            cellforlineage = dict(sorted(count_cells(lineage).items()))
            for time in cellforlineage:
                if cellforlineage[time] >= 64:
                    timefor64cells = int(time)
                    cellcountfortime = int(cellforlineage[time])
                break
        cell_keys_by_time,final_proportion,mars_ids1,all_leaves = build_all_leaves(lineage, timefor64cells,end_time)
        cell_keys_info[lineage] = cell_keys_by_time
        finalx=[]
        lineagepath = None
        if has_info_lineage(lineage,"cell_name"):
            nameinit = get_cell_names(lineage, mars_ids1)
            finalx = nameinit
        elif has_info_lineage(lineage,"cell_contact_surface"):
            lineagepath=auto_name_time(lineage,cellcountfortime)
            nameinit=get_cell_names(lineagepath,mars_ids1)
            finalx = nameinit
        else:
            for idcell in mars_ids1:
                finalx.append(format_cell_id(idcell))
        if lineagepath is not None:
            os.system("rm "+str(lineagepath))
        axis.plot([], [], ' ', label="early cell death:"+str(round(final_proportion,3))+"%")
        print(str(len(all_leaves))+" - "+str(len(finalx)))
        if len(all_leaves)> 0:
            axis.boxplot(all_leaves, labels=finalx)
        axis.set_xticklabels(axis.get_xticklabels(),rotation=90)
        axis.legend()
        return cell_keys_info





def plot_div_histo(axis,list_embryo_name,list_division_histo):
    plt.rcParams["figure.autolayout"] = True
    axis.set_title("Division histogram")
    maxc = -1000000
    minc = 1000000
    for i in range(0, len(list_division_histo)):
        division_histo_1 = list_division_histo[i]
        for key in division_histo_1:
            branches_length_suffle = []
            index1 = []
            branches_length_suffle.append(division_histo_1[key])
            index1.append(key)
        (markerline, stemlines, baseline) = axis.stem(index1, branches_length_suffle, markerfmt=' ', bottom=1,
                                                     use_line_collection=True, linefmt='grey', )
        plt.setp(baseline, visible=False)
        axis.scatter(index1, branches_length_suffle, label=list_embryo_name[i])  # A bar chart
        for val in branches_length_suffle:
            if int(val) > maxc:
                maxc = int(val)
            if int(val) < minc:
                minc = int(val)


class plot_variables:
    def __init__(self, value, isstring):

        self.value = value

        self.isstring = isstring

def save_plot_to_generate(plot_template,plot_title,list_params,folder_out="DATA/OUT/",title_suffix=""):
    f = open (plot_template)
    lines = f.readlines()
    f.close()
    new_lines=[]

    for line in lines:
        new_line=line
        splitted_param = line.split('=')
        if len(splitted_param) == 2:
            if splitted_param[0] in list_params.keys():
                found_param = list_params[splitted_param[0]]
                if found_param.isstring:
                    new_line = splitted_param[0]+'="'+str(found_param.value)+'"\n'
                else :
                    new_line = splitted_param[0] + '=' + str(found_param.value) + '\n'
            elif splitted_param[0] == "folder_out":
                new_line = splitted_param[0] + '="' + str(folder_out) + '"\n'
            elif splitted_param[0] == "title":
                new_line = splitted_param[0] + '="' +str(title_suffix)+ '"\n'
        new_lines.append(new_line)
    if folder_out != "":
        if not os.path.exists(folder_out):
            os.makedirs(folder_out)
    #title = "generate_"+str(folder_exp)+"_"+plot_title+"_"+title_suffix
    filename = "generate_"+plot_title+"_"+title_suffix
    f2 = open(folder_out+"/"+filename.replace(" ","_")+".py","w+")
    f2.writelines(new_lines)
    f2.close()
def compute_volume_reference():

    final_volume = 0
    atlas=get_atlas()
    min_volume = 1000000000000
    for lineage in atlas:
        minv, maxv, volumes = Get_Cell_Values_Float(lineage, "cell_volume", True)
        names = Get_Cell_Names(lineage)
        for volume in volumes:
            if volume in names:
                min_volume=min(min_volume,float(volumes[volume]))
    return min_volume/2

def plot_small_cell_count_multiple(axis,list_lineage,ratio=1):

    volume_small_cells = compute_volume_reference()
    axis.set_title("Cells under volume " + str(volume_small_cells) + " through time")
    axis.set_xlabel("Time")
    axis.axes.get_yaxis().set_major_locator(ticker.MaxNLocator(integer=True))
    minv=10000000
    maxv = -1000000
    cell_keys_info = {}
    for lineage in list_lineage:
        cell_keys_by_time,cell_count_by_time=count_small_cells(lineage, volume_max=volume_small_cells, volume_ratio=ratio)
        cell_keys_info[lineage] = cell_keys_by_time
        times = []
        cell_counts = []
        for time in cell_count_by_time:
            minv = min(minv, cell_count_by_time[time])
            maxv = max(maxv, cell_count_by_time[time])
            times.append(time)
            cell_counts.append(cell_count_by_time[time])
        axis.plot(times, cell_counts, 'o', label=lineage)
        if minv == maxv:
            maxv = minv+1
        axis.set_ylim([minv,maxv])
    return cell_keys_info

def align_with(reference_atlas,property_to_align):
    import astec.utils.atlas_embryo as uatlase
    import astec.utils.atlas_division as uatlasd
    from AstecManager.libs.ioproperties import read_dictionary
    parameters = uatlase.AtlasParameters()
    atlases = uatlasd.DivisionAtlases()
    atlases.add_atlases([reference_atlas], parameters)

    ref_atlases = atlases.get_atlases()
    ref_atlas = atlases.get_reference_atlas()

    embryo_prop = read_dictionary(property_to_align, inputpropertiesdict={})
    embryo = uatlase.Atlas(embryo_prop)
    embryo.temporally_align_with(ref_atlases[ref_atlas])
    return embryo._properties['temporal_alignment']

def plotrefcellcount(ref_embryo="atlas/Astec-pm1_properties.xml"):
    reftimes, refcells = generate_ref_cell_count(ref_embryo)
    plt.plot(reftimes, refcells, '-', label="Reference",color='grey',alpha=0.5)
    plt.savefig("ref_cell_count.png")
def plot_cell_count_multiple(axis,list_lineage_properties,compare_to_ref=False,ref_embryo="atlas/Astec-pm1_properties.xml"):
    axis.set_title("Cell count along time")
    axis.set_xlabel("Time")
    for lineage in list_lineage_properties:
        times = []
        cell_counts = []
        dictcount = count_cells(lineage)
        if compare_to_ref:
            a,b=align_with(ref_embryo,lineage)
            for time in dictcount:
                times.append(a * time + b)
                cell_counts.append(dictcount[time])
        else:
            for time in dictcount:
                times.append(time)
                cell_counts.append(dictcount[time])
        axis.plot(times, cell_counts, '-', label=lineage,alpha=0.5)
    if compare_to_ref is not None:
        reftimes, refcells = generate_ref_cell_count(ref_embryo)
        axis.plot(reftimes, refcells, '-', label="Reference",color='grey',alpha=0.5)

def plot_connected_components_multiples(axis,list_embryo_name,list_component_by_time,minlim=None,maxlim=None):
    axis.set_title("Multiple connected components cells count")
    axis.set_xlabel("Time")
    for i in range(0, len(list_component_by_time)):
        times = []
        cell_counts = []
        cell_count_by_time = list_component_by_time[i]
        for time in cell_count_by_time:
            times.append(time)
            cell_counts.append(cell_count_by_time[time])
        axis.plot(times, cell_counts, 'o', label=list_embryo_name[i])
    if minlim is not None and maxlim is not None:
        axis.set_ylim(minlim,maxlim)
def plot_cell_count(embryo_name,cell_count_by_time,folder_out="DATA/OUT/",embryo_name_2=None, cell_count_2=None):
    f = open ("template_folders/cell_count.py")
    lines = f.readlines()
    f.close()
    new_lines=[]

    for line in lines:
        new_line=line
        splitted_param = line.split('=')
        if len(splitted_param) == 2:
            if splitted_param[0] == "cell_count_by_time":
                new_line = splitted_param[0]+'='+str(cell_count_by_time)+'\n'
            elif splitted_param[0] == "embryo_name":
                new_line = splitted_param[0] + '="' + str(embryo_name)+'"\n'
            elif splitted_param[0] == "folder_out":
                new_line=splitted_param[0]+ '="' + str(folder_out)+'"\n'
            elif splitted_param[0] == "cell_count_2":
                new_line = splitted_param[0] + '=' + str(cell_count_2) + '\n'
            elif splitted_param[0] == "embryo_name2":
                new_line = splitted_param[0] + '="' + str(embryo_name_2) + '"\n'
        new_lines.append(new_line)
    folder_exp = embryo_name
    if embryo_name_2 is not None:
        folder_exp += "_" + embryo_name_2
    if os.path.join(folder_out,folder_exp) != "":
        if not os.path.exists(os.path.join(folder_out,folder_exp)):
            os.makedirs(os.path.join(folder_out,folder_exp))
    title = "generate_"+str(folder_exp)+"_cell_count"
    if embryo_name_2 is not None:
        title += "_" + str(embryo_name_2)
    f2 = open(os.path.join(folder_out,folder_exp+"/"+title.replace(" ","_")+".py"),"w+")
    f2.writelines(new_lines)
    f2.close()


def histo_compare_embryos_volume(volfile1, volfile2, embryo_name, embryo_name2, folder_out, fig_suffix=""):
    histo1 = []
    histo2 = []
    index1 = []
    index2 = []

    f1 = open(volfile1, "r")
    txt = f1.read().split(",")
    f1.close()
    f2 = open(volfile2, "r")
    txt2 = f2.read().split(",")
    f2.close()

    folder_exp = embryo_name
    if embryo_name2 is not None:
        folder_exp += "_" + embryo_name2

    for keyvalue in txt:
        if keyvalue != "":
            keyvalsplit = keyvalue.split(":")
            index1.append(keyvalsplit[0])
            histo1.append(float(keyvalsplit[1]))

    for keyvalue in txt2:
        if keyvalue != "":
            keyvalsplit = keyvalue.split(":")
            index2.append(keyvalsplit[0])
            histo2.append(float(keyvalsplit[1]))

    f = open("template_folders/histo_compare_volumes.py")
    lines = f.readlines()
    f.close()
    new_lines = []

    for line in lines:
        new_line = line
        splitted_param = line.split('=')
        if len(splitted_param) == 2:
            if splitted_param[0] == "histo1":
                new_line = splitted_param[0] + '=' + str(histo1) + '\n'
            elif splitted_param[0] == "histo2":
                new_line = splitted_param[0] + '=' + str(histo2) + '\n'
            elif splitted_param[0] == "index1":
                new_line = splitted_param[0] + '=' + str(index1) + '\n'
            elif splitted_param[0] == "index2":
                new_line = splitted_param[0] + '=' + str(index2) + '\n'
            elif splitted_param[0] == "embryo_name":
                new_line = splitted_param[0] + '="' + str(embryo_name) + '"\n'
            elif splitted_param[0] == "folder_out":
                new_line = splitted_param[0] + '="' + str(folder_out) + '"\n'
            elif splitted_param[0] == "fig_suffix":
                new_line = splitted_param[0] + '="' + str(fig_suffix) + '"\n'
            elif splitted_param[0] == "embryo_name2":
                new_line = splitted_param[0] + '="' + str(embryo_name2) + '"\n'
        new_lines.append(new_line)
    if os.path.join(folder_out, folder_exp) != "":
        if not os.path.exists(os.path.join(folder_out, folder_exp)):
            os.makedirs(os.path.join(folder_out, folder_exp))
    title = "generate_" + str(folder_exp) + "_mars_volume_histo"
    if embryo_name2 is not None:
        title += "_" + str(embryo_name2)
    f2 = open(os.path.join(folder_out, folder_exp + "/" + title.replace(" ", "_") + "_" + str(fig_suffix) + ".py"),
              "w+")
    f2.writelines(new_lines)
    f2.close()


def generate_ref_cell_count(ref_embryo):
    import astec.utils.atlas_embryo as uatlase
    import astec.utils.atlas_division as uatlasd
    from astec.utils.ioproperties import read_dictionary
    file_to_align_with = [ref_embryo]
    properties_files = get_atlas()
    times = []
    cells = []
    name = []

    parameters=uatlase.AtlasParameters()
    atlases = uatlasd.DivisionAtlases()
    atlases.add_atlases(file_to_align_with,parameters)

    ref_atlases = atlases.get_atlases()
    ref_atlas = atlases.get_reference_atlas()

    for at_property in properties_files:
        embryo_prop = read_dictionary(at_property, inputpropertiesdict={})
        embryo = uatlase.Atlas(embryo_prop)
        embryo.temporally_align_with(ref_atlases[ref_atlas])
        a,b = embryo._properties['temporal_alignment']
        name.append(at_property)
        cell_count=count_cells(at_property)
        new_times=[]
        ccount = []
        for time in cell_count:
            new_times.append(a*time+b)
            ccount.append(cell_count[time])
        times.append(new_times)
        cells.append(ccount)

    average_cells={}

    for j in range(0,len(times)):
        for i in range(0,len(times[j])):
            currenttime = int(times[j][i])
            if not currenttime in average_cells:
                average_cells[currenttime] = []
            average_cells[currenttime].append(cells[j][i])

    average_cells = dict(sorted(average_cells.items()))

    finaltimes=[]
    finalcells=[]
    for time in average_cells:
        finaltimes.append(time)
        aggrcount=0
        for countc in average_cells[time]:
            aggrcount += countc
        finalcells.append(int(aggrcount/len(average_cells[time])))

    return finaltimes,finalcells

def histo_compare_embryos_dice(ground_truth_image,compare_image,embryo_name,embryo_name2,ouput_txt,folder_out,fig_suffix=""):
    histo1 = []
    histo2 = []
    index1 = []
    index2 = []

    folder_exp = embryo_name
    if embryo_name2 is not None:
        folder_exp+="_"+embryo_name2
    command = "conda run -n astec bash segmentationComparison.sh " + ground_truth_image + " " + compare_image +" "+ os.path.join(folder_out,folder_exp)+"/interpretation_"+fig_suffix+".txt -bckgrdA 1 -bckgrdB 1 -image-in-out "+os.path.join(folder_out,folder_exp)+"/cutview_475_out_"+fig_suffix+".mha -image-ext-out "+os.path.join(folder_out,folder_exp)+"/cutview_491_out_"+fig_suffix+".mha -max -graph " + os.path.join(folder_out,folder_exp)+"/"+ouput_txt + " -v "

    os.system(command)
    #ouput_txt = "DATA/OUT/idaddglaceaubert.txt"
    lines = None
    f = open(os.path.join(folder_out,folder_exp)+"/"+ouput_txt, "r+")
    if f is not None:
        lines = f.read()
        f.close()
    print(str(lines))
    lines = lines.split('\n')
    if lines is not None:
        index = 0
        for line in lines:
            values = line.strip().split("-")
            if len(values) > 1:
                gt_cell = values[0].split(' ')
                gt_cell.remove('')
                em_cell = values[1].split(' ')
                em_cell.remove('')
                if len(gt_cell) != len(em_cell):
                    if len(gt_cell) == 0:
                        histo1.append(len(gt_cell))
                        index1.append(em_cell[0])
                        histo2.append(len(em_cell))
                        index2.append(em_cell[0])
                    else :
                        histo1.append(len(gt_cell))
                        index1.append(gt_cell[0])
                        histo2.append(len(em_cell))
                        index2.append(gt_cell[0])
            index+=1
    index1, histo1 = (list(t) for t in zip(*sorted(zip(index1, histo1))))

    index2, histo2 = (list(t) for t in zip(*sorted(zip(index2, histo2))))
    f = open("template_folders/histo_compare_embryos.py")
    lines = f.readlines()
    f.close()
    new_lines = []

    for line in lines:
        new_line = line
        splitted_param = line.split('=')
        if len(splitted_param) == 2:
            if splitted_param[0] == "histo1":
                new_line = splitted_param[0] + '=' + str(histo1) + '\n'
            elif splitted_param[0] == "histo2":
                new_line = splitted_param[0] + '=' + str(histo2) + '\n'
            elif splitted_param[0] == "index1":
                new_line = splitted_param[0] + '=' + str(index1) + '\n'
            elif splitted_param[0] == "index2":
                new_line = splitted_param[0] + '=' + str(index2) + '\n'
            elif splitted_param[0] == "embryo_name":
                new_line = splitted_param[0] + '="' + str(embryo_name) + '"\n'
            elif splitted_param[0] == "folder_out":
                new_line = splitted_param[0] + '="' + str(folder_out) + '"\n'
            elif splitted_param[0] == "fig_suffix":
                new_line = splitted_param[0] + '="' + str(fig_suffix) + '"\n'
            elif splitted_param[0] == "embryo_name2":
                new_line = splitted_param[0] + '="' + str(embryo_name2) + '"\n'
        new_lines.append(new_line)
    if os.path.join(folder_out, folder_exp) != "":
        if not os.path.exists(os.path.join(folder_out, folder_exp)):
            os.makedirs(os.path.join(folder_out, folder_exp))
    title = "generate_" + str(folder_exp) + "_embryos_comparaison_histo"
    if embryo_name2 is not None:
        title += "_" + str(embryo_name2)
    f2 = open(os.path.join(folder_out, folder_exp + "/" + title.replace(" ", "_") + ".py"), "w+")
    f2.writelines(new_lines)
    f2.close()

def compute_and_plot_intensities_histo(embryo_name,begin_time,end_time,intensity_image_pattern,tensor_image_pattern,folder_plot="PLOTS/normal_log/"):
    if not os.path.isdir(folder_plot):
        os.makedirs(folder_plot)

    min_t = 10000
    max_t = -100000
    min_i = 10000
    max_i = -1000000

    for time in range(begin_time, end_time + 1,30):
        print("Start of time t : " + str(time))
        histo_name = "conjoint_histogram_noninterpolated_log_t_" + str(time) + "_" + embryo_name.replace("/", "_")
        if not os.path.isfile("HISTOGRAMS/" + histo_name + ".txt"):
            intensity = intensity_image_pattern.format(time+1,time+1)
            tensor = tensor_image_pattern.format(time+1,time+1)
            os.system("pigz -d "+intensity+".gz")
            os.system("pigz -d " + tensor + ".gz")
            intensities_intensity = np.array(imread(intensity))
            intensities_tensor = np.array(imread(tensor))
            unique_vals = np.unique(intensities_intensity)
            unique_tensor = np.unique(intensities_tensor)
            print("Extracted uniques")
            sorted_intensities = np.sort(unique_vals)
            sorted_tensor = np.sort(unique_tensor)
            print("Sorted intensities")
            final_count = {}
            txt = ""
            for x in range(0, intensities_intensity.shape[0]):
                for y in range(0, intensities_intensity.shape[1]):
                    for z in range(0, intensities_intensity.shape[2]):
                        val_intensity = intensities_intensity[x, y, z]
                        val_tensor = intensities_tensor[x, y, z]
                        if val_intensity < min_i:
                            min_i = val_intensity
                        if val_intensity > max_i:
                            max_i = val_intensity
                        if val_tensor < min_t:
                            min_t = val_tensor
                        if val_tensor > max_t:
                            max_t = val_tensor
            for x in range(0, intensities_intensity.shape[0]):
                for y in range(0, intensities_intensity.shape[1]):
                    for z in range(0, intensities_intensity.shape[2]):
                        int_i = intensities_intensity[x, y, z]
                        int_t = intensities_tensor[x, y, z]
                        if not int_i in final_count:
                            final_count[int_i] = {}
                        if not int_t in final_count[int_i]:
                            final_count[int_i][int_t] = 0
                        final_count[int_i][int_t] += 1
            print("computed Arrays")
            for i in final_count:
                for j in final_count[i]:
                    txt += str(i) + ":" + str(j) + ":" + str(final_count[i][j]) + ","
            print("Computed counts")
            f = open("HISTOGRAMS/" + histo_name + ".txt", "w+")
            f.write(txt)
            f.close()
            txt = ""
        int_int = []
        ten_int = []
        vals = []
        print("Reading time file : " + str("HISTOGRAMS/" + histo_name + ".txt"))
        f = open("HISTOGRAMS/" + histo_name + ".txt", "r")
        lines = f.read().split(',')
        f.close()
        print("Loading values histogram")
        for line in lines:
            if line != "":
                values = line.split(':')
                val_intensity = int(values[0])
                val_tensor = int(values[1])
                int_int.append(val_intensity)
                ten_int.append(val_tensor)
                vals.append(math.log(int(values[2])))
        df = pd.DataFrame({'Intensity': int_int, 'Tensor': ten_int, 'Values': vals})
        df_wide = df.pivot_table(index='Intensity', columns='Tensor', values='Values')
        ax = sns.heatmap(df_wide, cmap="coolwarm")
        print("Plotting histogram")
        plt.title("Conjoint histograme intensity vs tensor for " + str(embryo_name) + " at t " + str(time))
        plt.yticks(range(0, 3500, 150))
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0f'))
        plt.savefig(os.path.join(folder_plot, histo_name + ".png"))
        plt.clf()
        print("End of time t : " + str(time))


def get_atlas():
    properties_files = []
    properties_files.append("atlas/Astec-pm1_properties.xml")
    properties_files.append("atlas/Astec-pm3_properties.xml")
    properties_files.append("atlas/Astec-pm4_properties.xml")
    properties_files.append("atlas/Astec-pm5_properties.xml")
    properties_files.append("atlas/Astec-pm7_properties.xml")
    properties_files.append("atlas/Astec-pm8_properties.xml")
    properties_files.append("atlas/Astec-pm9_properties.xml")
    return properties_files


def generate_ref_histogram_no_death(min_cell,max_cell):
    properties_files = get_atlas()

    min_max_properties = []
    histograms = []


    #compute min max for each property
    for property_embryo in properties_files:
        cell_count_by_time = count_cells(property_embryo)
        mint = 10000
        maxt = -100000
        for time in cell_count_by_time:
            timecount = cell_count_by_time[time]
            if timecount >= min_cell and timecount <= max_cell:
                if mint > time:
                    mint = time
                if maxt < time:
                    maxt = time
        min_max_properties.append((mint,maxt))
    #compute histograms
    for i in range(0,len(properties_files)):
        mintime=min_max_properties[i][0]
        maxtime=min_max_properties[i][1]
        histograms.append(build_branch_length_no_both(properties_files[i],mintime=mintime,maxtime=maxtime))
    return histograms




