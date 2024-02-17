import numpy as np
import matplotlib.pyplot as plt
import treex as tx
from treex.visualization.matplotlib_plot import view_tree
from treex.analysis.edit_distance.zhang_labeled_trees import zhang_edit_distance
from scipy.cluster import hierarchy
import pickle as pkl
from collections import defaultdict
import re
def get_atlas():
    properties_files = []
    properties_files.append("atlas/Astec-pm1_properties.pkl")
    properties_files.append("atlas/Astec-pm3_properties.pkl")
    properties_files.append("atlas/Astec-pm4_properties.pkl")
    properties_files.append("atlas/Astec-pm5_properties.pkl")
    properties_files.append("atlas/Astec-pm7_properties.pkl")
    properties_files.append("atlas/Astec-pm8_properties.pkl")
    properties_files.append("atlas/Astec-pm9_properties.pkl")
    return properties_files

def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v
                     for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v)
                        for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d



# NEW DEFINITION OF LOCAL COST FUNCTIONS FOR TREE-EDIT DISTANCES
# Definition of a LOCAL COST function.
# this function computes the elementary distance between to any vertices of two trees
def new_local_cost(v1=None,v2=None):
    '''
    Compute distance between two vertices
    Parameters
    ----------
    v1,v2: tree vertices
    Returns
    -------
    the distance  between the 2 vertices
    '''
    if isinstance(v1,tuple)==True:
        if v2 == None:
            cost = 0
            v = list(v1)
            for i in range(len(v)):
                cost+=v[i]
            return cost
        else:
            d=len(v1)
            return sum( [abs(v1[i]-v2[i]) for i in range(0,d)])
    else:
        if v2==None:
            return v1
        else:
            return abs(v1-v2)

# A first function to defined an attribute called 'label_for_distance' with a constant value
# on each node of a given tree (to make simple tests)
def give_label_dist_constant(tree,value):
    # associate a constant attribute value with all the vertices of the tree
    # Parameters
    # ----------
    # tree: treex tree
    # value: number vector
    tree.add_attribute_to_id('label_for_distance',value)
    for child in tree.my_children:
        give_label_dist_constant(child,value)

# Define a more general function to attach a 'label_for_distance' to a tree
# with more general values (by copying the value of another given attribute in 'label_for_distance')
# and so that the edit-distance can then be used with this tree.

def give_label_dist_attribute(tree,name):
    # associate a constant attribute value with all the vertices of the tree
    # Parameters
    # ----------
    # tree: treex tree
    # value: number vector
    value = tree.get_attribute(name)
    tree.add_attribute_to_id('label_for_distance',value)
    for child in tree.my_children:
        give_label_dist_attribute(child,name)

def time_stamp(cell_id):
    return int(cell_id // 10000)

def cell_lifespan_list(c,cell_lineage):
    cell_list = [c]
    if c in cell_lineage:
        child = cell_lineage[c]
        while len(child) == 1:
            cell_list.append(child[0])
            if child[0] in cell_lineage:
                child = cell_lineage[child[0]]
            else:
                child = []
    return cell_list

def life_span(cell_id,cell_lineage):
    lst = cell_lifespan_list(cell_id,cell_lineage)
    return time_stamp(lst[-1])-time_stamp(lst[0])+1

# Two functions to create (Treex) trees from lineage data

# definition of a function to build a tree from astec cell lineages
# Note: this accesses the astec lineage as a global variable, as well as the translation dict from tree to astec
def add_child_tree(t,astec_child,cell_lineage,astec2tree,maxtime=None):
    if maxtime == None:
        if astec_child == None :
            return False
    else:
        if astec_child == None or time_stamp(astec_child) > maxtime:
            return False
    ct = tx.Tree()
    ct.add_attribute_to_id('astec_id',astec_child)
    astec2tree[astec_child] = ct.my_id
    t.add_subtree(ct)
    if astec_child in cell_lineage: # astec_child is not terminal
        for c in cell_lineage[astec_child]:
            #print(c)
            add_child_tree(ct, c,cell_lineage,astec2tree,maxtime) # recursive call on children of astec_child
    return True

def daughters(c,cell_lineage):
    if c in cell_lineage:
        child = cell_lineage[c] #
        if len(child) == 0:
            return None
        elif len(child) == 1:
            return daughters(child[0],cell_lineage)
        else:
            return child
    else:
        return None

def mother(c,cell_lineage):
    mother_dic = {}
    for c in cell_lineage:
        child = daughters(c,cell_lineage)
        if child is not None:
            mother_dic[child[0]] = c
            mother_dic[child[1]] = c
    if c in mother_dic:
        return mother_dic[c]
    else:
        return None

def has_sister(c,cell_lineage):
    m = mother(c)
    if m is not None:
        if m in cell_lineage:
            child = cell_lineage[m]
            if len(child) == 1:
                return has_sister(m,cell_lineage)
            else:
                return True
        else:
            return False
    else:
        return False

def sister(c,cell_lineage):
    m = mother(c)
    if m is not None:
        if m in cell_lineage:
            child = cell_lineage[m]
            if len(child) == 1:
                return has_sister(m,cell_lineage)
            else: # len == 2
                return child[0] if child[0] != c else child[1]
        else:
            return None
    else:
        return None

# Create the lineage tree of the cell given in argument
def create_lineage_tree(astec_id,cell_lineage,maxtime=None):
    t = tx.Tree() # create tree (in treex, nodes are actually trees)
    astec2tree = {}
    # setting root data
    t.add_attribute_to_id('astec_id',astec_id)
    # store mapping between vertices
    astec2tree[astec_id] = t.my_id

    if astec_id in cell_lineage:
        for c in cell_lineage[astec_id]:
            #print(c)
            add_child_tree(t,c,cell_lineage,astec2tree,maxtime)
    return t

def create_compressed_lineage_tree(astec_id,cell_lineage,cellnames=None):
    # print(astec_id)
    astec2tree = {}
    lifespan = life_span(astec_id,cell_lineage)
    t = tx.Tree()  # create tree (in treex, nodes are actually trees)
    # setting root data
    if cellnames is not None and astec_id in cellnames:
        t.add_attribute_to_id('astec_id', cellnames[astec_id])
    else:
        t.add_attribute_to_id('astec_id', astec_id)
    t.add_attribute_to_id('lifespan', lifespan)
    # store mapping between vertices
    keytree = astec_id
    if cellnames is not None and astec_id in cellnames:
        keytree = cellnames[astec_id]
    astec2tree[keytree] = t.my_id

    dlist = daughters(astec_id,cell_lineage)  # find the daughters (cell ids just after a division)

    if dlist != None and dlist != []:
        assert len(dlist) == 2
        for c in dlist:
            if c in cell_lineage:
                tchild = create_compressed_lineage_tree(c,cell_lineage,cellnames)
                if tchild != None:
                    t.add_subtree(tchild)
    return t

def apply_compressed_compare(lineage_prop1,lineage_prop2,cell_key,cell_key2):
    tree1 = create_compressed_lineage_tree(cell_key, lineage_prop1)
    tree2 = create_compressed_lineage_tree(cell_key2, lineage_prop2)
    give_label_dist_attribute(tree1, 'lifespan')
    give_label_dist_attribute(tree2, 'lifespan')

    # Compute the zhang edit-distance between them (then making use of the information 'lifespan' on the nodes)
    d = zhang_edit_distance(tree1, tree2, "lifespan", new_local_cost)
    return d

def apply_compare(lineage_prop1,lineage_prop2,cell_key,cell_key2):
    tree1 = create_lineage_tree(cell_key, lineage_prop1)
    tree2 = create_lineage_tree(cell_key2, lineage_prop2)
    give_label_dist_constant(tree1, (1))
    give_label_dist_constant(tree2, (1))
    d = zhang_edit_distance(tree1, tree2, "label_for_distance", new_local_cost)
    return d

def read_lineage(lineage):
    f = open(lineage, 'rb')
    astec_output1 = pkl.load(f)  # astec_output is the set of all dictionary returned by ASTEC (itself a dic)
    f.close()
    return astec_output1

def load_cell_names(lineage):
    astec_output = read_lineage(lineage)
    if not 'cell_name' in astec_output:
        print("Name information is missing")
        exit()
    return astec_output['cell_name']
def name_to_id(output_astec,namecell):
    if not 'cell_name' in output_astec:
        print("Name information is missing")
        exit()

    cell_names1 = output_astec['cell_name']
    cell_key_1 =""
    for keyc in cell_names1:
        if cell_names1[keyc] == namecell:
            cell_key_1 = keyc
            break

    return cell_key_1
def compare_cell_by_name(lineage_path_1,lineage_path_2,cell_name1,cell_name2):
    astec_output1 = read_lineage(
        lineage_path_1)  # astec_output is the set of all dictionary returned by ASTEC (itself a dic)
    astec_output2 = read_lineage(
        lineage_path_2)  # astec_output is the set of all dictionary returned by ASTEC (itself a dic)
    cell_lineage1 = astec_output1['cell_lineage']
    cell_lineage2 = astec_output2['cell_lineage']
    cell_key_1 = name_to_id(astec_output1,cell_name1)
    cell_key_2 = name_to_id(astec_output2,cell_name2)

    return apply_compressed_compare(cell_lineage1, cell_lineage2, cell_key_1,cell_key_2)

def compare_cell_by_key(lineage_path_1,lineage_path_2,cell_key_1,cell_key_2):
    astec_output1 = read_lineage(lineage_path_1)  # astec_output is the set of all dictionary returned by ASTEC (itself a dic)
    astec_output2 = read_lineage(lineage_path_2)  # astec_output is the set of all dictionary returned by ASTEC (itself a dic)
    cell_lineage1 = astec_output1['cell_lineage']
    cell_lineage2 = astec_output2['cell_lineage']

    return apply_compare(cell_lineage1,cell_lineage2,cell_key_1,cell_key_2)

def print_tree(lineage,cell_key,compressed=False,name=None):
    astec_output = read_lineage(lineage)
    cell_lineage = astec_output['cell_lineage']
    treeforcell = None
    if compressed:
        treeforcell=create_compressed_lineage_tree(cell_key, cell_lineage)
    else :
        treeforcell=create_lineage_tree(cell_key, cell_lineage)
    fig = view_tree(treeforcell)
    displayname = cell_key
    if name is not None:
        displayname = name
    prefixfig = "dendogram_plots/"
    if compressed:
        prefixfig=prefixfig+"compressed_tree_"
    else:
        prefixfig = prefixfig + "tree_"
    fig.savefig(prefixfig+lineage.split('.')[0].replace('/','_')+"_"+displayname.replace(".","")+".png")

def print_tree_by_name(lineage,cell_name,compressed=False):
    astec_output = read_lineage(lineage)
    cell_key_1 = name_to_id(astec_output,cell_name)
    print_tree(lineage,cell_key_1,compressed,cell_name)



# Transform distance matrix into a condensed matrix (used by linkage function below)
# (= vector array made from upper triangular part of the distance matrix)
# i<j<m, where m is the number of original observations
# m * i + j - ((i + 2) * (i + 1)) // 2.
def condensed_matrix(dist_mat):
    m = np.shape(dist_mat)[0]
    cm = np.zeros(m*(m-1)//2)
    for j in range(m):
        for i in range(j):
            cm[m * i + j - ((i + 2) * (i + 1)) // 2] = dist_mat[j][i]
    return cm
def count_cells(cell_list,remove_time=[]):
    cell_count_by_time = {}
    for cell_key in cell_list:
        cell_obj_t = time_stamp(cell_key)
        if not cell_obj_t in remove_time:
            if not cell_obj_t in cell_count_by_time:
                cell_count_by_time[cell_obj_t] = 0
            cell_count_by_time[cell_obj_t] += 1
    return cell_count_by_time

def get_cell_generation(cell_names,cellkey):
    if cell_names is None or len(cell_names)==0:
        return None
    if not cellkey in cell_names:
        return None
    findgenin = cell_names[cellkey].split(".")[0]
    return int(re.findall(r'\d+', findgenin)[-1])


def compute_dendogram(lineage_trees):
    nbcell=len(lineage_trees)
    dist_array = np.zeros((nbcell, nbcell))
    for i in range(nbcell):
        for j in range(i, nbcell):
            dist_array[i][j] = zhang_edit_distance(lineage_trees[i], lineage_trees[j], "lifespan", new_local_cost)
            dist_array[j][i] = dist_array[i][j]
    return hierarchy.linkage(condensed_matrix(dist_array), method='average', optimal_ordering=True)

def compute_cluster_for_names(lineage_list,namelist,lineage_names):
    mapping_index={}
    i=0
    lineage_trees = []
    lin=0
    for lineage in lineage_list:
        cells_to_compute = []
        workedids = []
        astec_output = read_lineage(lineage)  # astec_output is the set of all dictionary returned by ASTEC (itself a dic)
        cell_lineage = astec_output['cell_lineage']
        cellnames = None
        if 'cell_name' in astec_output:
            cellnames = astec_output['cell_name']
        if cellnames is None:
            print("No names found in : "+lineage)
        filteredlineage = list(filter(lambda x: (cellnames is not None and x in cellnames and cellnames[x] in namelist), cell_lineage))
        for cell in filteredlineage:
                if cellnames[cell] in namelist:
                    mother_cell = get_direct_mother(cell, cell_lineage,cellnames)
                    if mother_cell is not None and not mother_cell in workedids:
                        if mother_cell in cellnames and cellnames[mother_cell] in namelist:
                            print("Added cell "+str(mother_cell)+" with name "+str(cellnames[mother_cell]))
                            cells_to_compute.append(mother_cell)
                            workedids.append(mother_cell)
        # Compute the lineage trees:
        for cellc in cells_to_compute:
            print("cell "+str(cellc)+" found name : "+str(cellnames[cellc])+" at index "+str(i))
            mapping_index[i]=cellnames[cellc]+" "+lineage_names[lin]
            t = create_compressed_lineage_tree(cellc,cell_lineage,cellnames)
            give_label_dist_attribute(t, 'lifespan')
            lineage_trees.append(t)
            i+=1
        lin+=1
    Z = compute_dendogram(lineage_trees)
    return mapping_index, lineage_trees, Z

def get_next_mother(cell,cell_lineage):
    for celltest in cell_lineage:
        for cellval in cell_lineage[celltest]:
            if cellval==cell:
                return celltest
    return None

def get_daughters(cell,cell_lineage):
    d = []
    for celltest in cell_lineage:
        if celltest==cell:
            d=cell_lineage[celltest]
    return d

def get_direct_mother(cell,cell_lineage,cellnames=None):
    if not cell in cell_lineage:
        return None
    directmother = get_next_mother(cell,cell_lineage)
    if directmother is None:
        return cell
    daughters = get_daughters(directmother,cell_lineage)
    directmothertwice = get_next_mother(directmother, cell_lineage)
    if directmothertwice is None or len(daughters) > 1:
        return directmother
    return get_direct_mother(directmother,cell_lineage)

def compute_cluster_for_generation(lineage_list,generation_list,lineage_names):
    mapping_index={}
    i=0
    lineage_trees = []
    lin=0
    for lineage in lineage_list:
        workedids = []
        cells_to_compute = []
        astec_output = read_lineage(lineage)  # astec_output is the set of all dictionary returned by ASTEC (itself a dic)
        cell_lineage = astec_output['cell_lineage']
        cellnames = None
        if 'cell_name' in astec_output:
            cellnames = astec_output['cell_name']
        if cellnames is None:
            print("No names found in : "+lineage)
        filtered_lineage=list(filter(lambda x: (x in cellnames and int(get_cell_generation(cellnames,x)) in generation_list), cell_lineage))
        for cell in filtered_lineage:
            mother_cell = get_direct_mother(cell,cell_lineage,cellnames)
            if mother_cell is not None and not mother_cell in workedids:
                cells_to_compute.append(mother_cell)
                workedids.append(mother_cell)
        # Compute the lineage trees:
        for cellc in cells_to_compute:
            mapping_index[i] = cellnames[cellc] + " " + lineage_names[lin]
            t = create_compressed_lineage_tree(cellc,cell_lineage,cellnames)
            give_label_dist_attribute(t, 'lifespan')
            lineage_trees.append(t)
            i+=1
        lin += 1
    Z = compute_dendogram(lineage_trees)
    return mapping_index, lineage_trees, Z


def compute_cluster_for_stage(lineage_list,cell_count,lineage_names):

    mapping_index={}
    i=0
    lineage_trees = []
    lin=0
    for lineage in lineage_list:
        workedids = []
        cells_to_compute = []
        astec_output = read_lineage(lineage)  # astec_output is the set of all dictionary returned by ASTEC (itself a dic)
        cell_lineage = astec_output['cell_lineage']
        cell_count_time=dict(sorted(count_cells(cell_lineage).items()))
        cellnames = None
        if 'cell_name' in astec_output:
            cellnames = astec_output['cell_name']
        timepoint = None
        for time in cell_count_time:
            if timepoint is None and cell_count_time[time] == cell_count:
                timepoint=int(time)
        if timepoint is None:
            for time in cell_count_time:
                if timepoint is None and cell_count_time[time] >= cell_count:
                    timepoint = int(time)
        filteredlineage = list(filter(lambda x: (int(time_stamp(x))==timepoint), cell_lineage))
        for cell in filteredlineage:
            mother_cell = get_direct_mother(cell,cell_lineage,cellnames)
            if mother_cell is not None and not mother_cell in workedids:
                cells_to_compute.append(mother_cell)
                workedids.append(mother_cell)
        # Compute the lineage trees:
        for cellc in cells_to_compute:
            mapping_index[i] = cellnames[cellc] + " " + lineage_names[lin]
            t = create_compressed_lineage_tree(cellc,cell_lineage,cellnames)
            give_label_dist_attribute(t, 'lifespan')
            lineage_trees.append(t)
            i+=1
        lin += 1
    Z = compute_dendogram(lineage_trees)
    return mapping_index, lineage_trees, Z

def compute_cluster_for_time(lineage_list,timepoint_list,lineage_names):
    cells_to_compute = []
    mapping_index={}
    i=0
    lineage_trees = []
    lin=0
    for lineage in lineage_list:
        workedids = []
        astec_output = read_lineage(lineage)  # astec_output is the set of all dictionary returned by ASTEC (itself a dic)
        cell_lineage = astec_output['cell_lineage']
        cellnames = None
        if 'cell_name' in astec_output:
            cellnames = astec_output['cell_name']
        filteredlineage = list(filter(lambda x: (time_stamp(x) is not None and int(time_stamp(x)) in timepoint_list), cell_lineage))
        for cell in filteredlineage:
            if cell is not None and not cell in workedids:
                cells_to_compute.append(cell)
                workedids.append(cell)
        # Compute the lineage trees:
        for cellc in cells_to_compute:
            cname = str(cellc)
            if cellc in cellnames:
                cname=cellnames[cellc]
            mapping_index[i] = cname + " " + lineage_names[lin]
            t = create_compressed_lineage_tree(cellc,cell_lineage,cellnames)
            give_label_dist_attribute(t, 'lifespan')
            lineage_trees.append(t)
            i+=1
        lin += 1
    Z = compute_dendogram(lineage_trees)
    return mapping_index, lineage_trees, Z
def compute_cluster_for_time_single_lineage(lineage,timepoint):
    cells_to_compute = []
    mapping_index={}
    astec_output = read_lineage(lineage)  # astec_output is the set of all dictionary returned by ASTEC (itself a dic)
    cell_lineage = astec_output['cell_lineage']
    cellnames = None
    if 'cell_name' in astec_output:
        cellnames = astec_output['cell_name']
    for cell in cell_lineage:
        timecell = time_stamp(cell)
        if timecell==timepoint:
            cells_to_compute.append(cell)
    nbcell = len(cells_to_compute)
    lineage_trees = []
    # Compute the lineage trees:
    for i in range(nbcell):
        cname=cells_to_compute[i]
        if cellnames is not None and cname in cellnames:
            cname = cellnames[cname]
        mapping_index[i]=cname
        t = create_compressed_lineage_tree(cells_to_compute[i],cell_lineage,cellnames)
        give_label_dist_attribute(t, 'lifespan')
        lineage_trees.append(t)
    Z = compute_dendogram(lineage_trees)
    return mapping_index,lineage_trees,Z
def plot_cluster(dendogram,filename,axismapping=None,title=None,figxsize=None,figysize=None):
    dist_threshold = 350  # this is used to define the grain of the classes (see horizontal dashed line on the figure)

    # Function linkage performs the hirarchical clustering based on a condensed version of the distance matrix
    # print(Z)

    # - Then the cell hierarchy is computed as a dendrogram data-structure
    # It contains the labels of the points, their color code and more (see scipy doc)

    fig = plt.figure()
    curr_axis = fig.gca()  # current viewport (called axis) in the fig window (fig)

    # prepare the plot of the dendrogram and select the level of the classes see: 'color_threshold'
    dn = hierarchy.dendrogram(dendogram, color_threshold=dist_threshold, ax=curr_axis, leaf_font_size=14)

    curr_axis.axhline(y=dist_threshold, linestyle='--', linewidth=1)
    curr_axis.set_title(title if title is not None else 'Hierarchical Clustering Dendrogram', size=24)
    curr_axis.set_xlabel("cell lineage", size=18)
    curr_axis.set_ylabel("edit-distance", size=18)
    labels = [item.get_text() for item in curr_axis.get_xticklabels()]
    for i in range(0,len(labels)):
        previouslabs = labels[i]
        if int(previouslabs) in axismapping:
            print("Working on id : "+str(previouslabs)+" with label "+ str(axismapping[int(previouslabs)]))
            writtenname = str(axismapping[int(previouslabs)])
            if "." in writtenname:
                namesplitted=writtenname.split('.')
                labels[i]=namesplitted[0]+"."+namesplitted[1].lstrip("0").replace("_","-")
            else :
                labels[i] = writtenname
    curr_axis.set_xticklabels(labels)
    plt.xticks(fontsize=8)
    fig.set_size_inches(figxsize if figxsize is not None else 40,figysize if figysize is not None else 15)  # size of the plot
    #fig.set_size_inches(figxsize if figxsize is not None else 40, figysize if figysize is not None else 15)  # size of the plot
    plt.savefig(filename)
    plt.clf()
def compute_classes_dendogram(dendogram,lineage_trees):
    # - Finally Extract the classes from the dendrogram:
    dist_threshold = 350
    fig = plt.figure()
    curr_axis = fig.gca()
    classes = hierarchy.fcluster(dendogram, t=dist_threshold, criterion='distance')
    dn = hierarchy.dendrogram(dendogram, color_threshold=dist_threshold, ax=curr_axis, leaf_font_size=14)

    # and print the detailed results corresponding to the above figure
    classlist = {}
    for i in range(len(classes)):
        k = dn['leaves'][i]
        if not classes[k] in classlist:
            classlist[k] = []
        cell_id = lineage_trees[k].get_attribute('astec_id')
        classlist[k].append(cell_id)
    for k in classlist:
        print("> Cells in class "+str(k))
        for cell in classlist[k]:
            print('     -> ', cell)