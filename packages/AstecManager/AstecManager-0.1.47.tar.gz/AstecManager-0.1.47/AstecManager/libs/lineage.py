from AstecManager.libs.data import get_longid,get_id_t,Cell
import xml.etree.ElementTree as ET
import os
import numpy as np
from AstecManager.libs.ioproperties import read_dictionary

def indent_xml(elem, level=0):
    i = "\n" + level*"  "
    j = "\n" + (level-1)*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent_xml(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem

def SaveTabToXMLInfo(path_input,path_output,tab,node_name):
    source = open(path_input)
    tree = ET.parse(source)
    tree = tree.getroot()
    selec_node = node_name
    name_selec_elem = tree.find(selec_node)
    if name_selec_elem is None:
        name_selec_elem = ET.SubElement(tree, selec_node)
    for cell in name_selec_elem.findall('cell'):
        if int(cell.get('cell-id')) in tab.keys() or cell.get(
                'cell-id') in tab.keys() and tab is not None and tab[cell.get('cell-id')] is not None:
            cell.text =str(tab[cell.get('cell-id')])
            tab.pop(cell.get('cell-id'), None)
    for cell in tab:
        new_cell = ET.SubElement(name_selec_elem, 'cell')
        new_cell.set('cell-id', cell)
        new_cell.text = str(tab[cell])
    indent_xml(tree)
    source.close()
    mydata = ET.tostring(tree, encoding='utf8', method='xml').decode("utf8")
    myfile = open(path_output, "w+")
    myfile.write(mydata)
    myfile.close()


def AddNodeToXML(xml_file, value_dict, node_name,node_subname,identifier_text='value'):
    print(str(xml_file))
    if not os.path.isfile(xml_file) or os.stat(xml_file).st_size == 0:
        print("XML file not found , create it with path : "+str(xml_file))
        f = open(xml_file,"w+")
        f.close()
        root = ET.Element('root')
        tree = ET.ElementTree(root)
        tree.write(xml_file)
    source = open(xml_file)
    tree = ET.parse(source)
    tree = tree.getroot()
    selec_node = node_name
    name_selec_elem = tree.find(selec_node)
    if name_selec_elem is None:
        name_selec_elem = ET.SubElement(tree, selec_node)
    for cell in name_selec_elem.findall(node_subname):
        if cell.get(identifier_text) in value_dict.keys() or cell.get(
                identifier_text) in value_dict.keys() and value_dict is not None and value_dict[cell.get(identifier_text)] is not None:
            cell.text =str(value_dict[cell.get(identifier_text)])
            value_dict.pop(cell.get(identifier_text), None)
    for cell in value_dict:
        new_cell = ET.SubElement(name_selec_elem, node_subname)
        if cell != "":
            new_cell.set(identifier_text, str(cell))
        new_cell.text = str(value_dict[cell])
    indent_xml(tree)
    source.close()
    mydata = ET.tostring(tree, encoding='utf8', method='xml').decode("utf8")
    myfile = open(xml_file, "w+")
    myfile.write(mydata)
    myfile.close()

def SaveTabToTxtInfo(path_output,name_file,tab, time_string):
    if not os.path.isdir(path_output):
        os.mkdir(path_output)
    f = open(os.path.join(path_output,name_file), "w+")
    f.write("#Information that matches names with a selection" + "\n")
    f.write("#Generated on : " + time_string + "\n")
    f.write("type:selection" + "\n")
    for id in tab:
        t, ida = get_id_t(id)
        f.write(str(t) + "," + str(ida) + ",0:" + str(tab[id]) + "\n")
    f.close()


def LoadCellList(path_lineage):
    try:
        source = open(path_lineage)
    except:
        return None
    tree = ET.parse(source)
    cell_list_g = {}
    tree = tree.getroot()
    lineage_elem = tree.find('cell_lineage')
    if lineage_elem is not None:
        for cell in lineage_elem.findall('cell'):
            cell_t,cell_id = get_id_t(cell.get('cell-id').replace("'","").replace('[','').replace(']','').replace(" ",""))
            cell_key = str(get_longid(cell_t,cell_id))
             #cell_key = str(cell_t)+","+str(cell_id)
            if not cell_key in cell_list_g:
                cell_object = Cell(int(cell_id),int(cell_t))
                cell_list_g[cell_key] = cell_object
            cell_childs = cell.text.split(',')
            for cell_child_in_list in cell_childs:
                cell_child_t,cell_child_id = get_id_t(cell_child_in_list.replace("'","").replace('[','').replace(']','').replace(" ",""))
                cell_child_key = str(get_longid(cell_child_t,cell_child_id))
                if not cell_child_key in cell_list_g:
                    cell_child_object = Cell(int(cell_child_id), int(cell_child_t))
                    cell_list_g[cell_child_key] = cell_child_object

                if not cell_list_g[cell_child_key] in cell_list_g[cell_key].daughters:
                    cell_list_g[cell_child_key].add_mother(cell_list_g[cell_key])
        return cell_list_g
    return None

def list_ids_by_time(lineage):
    ids = {}
    local_list = LoadCellList(lineage)
    for cell in local_list:
        tc,idc=get_id_t(cell)
        if not tc in ids:
            ids[tc] = [idc]
        else :
            ids[tc].append(idc)
    return ids

def GetCellLastBranchCount(list_cell,endtime):
    lastcells = []
    finalcount = 0
    for cell in list_cell:
        if cell.t == endtime:
            lastcells.append(cell)
    if len(lastcells)==0:
        return 0
    for cell in lastcells:
        cell_obj = cell
        while (cell_obj is not None and cell_obj.mothers is not None and len(cell_obj.mothers) > 0 and
               cell_obj.mothers[0] is not None and cell_obj.mothers[0].daughters is not None and len(
                    cell_obj.mothers[0].daughters) == 1):
            finalcount+=1
            cell_obj = cell_obj.mothers[0]
    return finalcount
def GetCellLifetime(cell):
    list_cells = [cell,]
    daughters = GetCellLifeFutur(cell)
    mothers = GetCellLifePast(cell)
    for dau in daughters:
        if not dau in list_cells:
            list_cells.append(dau)
    for mot in mothers:
        if not mot in list_cells:
            list_cells.append(mot)
    #print("cell : "+str(cell))
    #print("Cells found : "+str(len(list_cells)))
    return list_cells

def GetCellLifetimenodeath(cell):
    list_cells = [cell,]
    daughters = GetCellLifeFuturnodeath(cell)
    mothers = GetCellLifePastnodeath(cell)
    for dau in daughters:
        if not dau in list_cells:
            list_cells.append(dau)
    for mot in mothers:
        if not mot in list_cells:
            list_cells.append(mot)
    #print("cell : "+str(cell))
    #print("Cells found : "+str(len(list_cells)))
    return list_cells



def GetCellLifeFutur(cell):
    list_cells = [cell,]
    if cell is None or cell.daughters is None or len(cell.daughters) != 1:
        #print("Futur : cell is : "+str(cell))
        #print("Futur : cell has no daughters")
        return list_cells
    cells = GetCellLifeFutur(cell.daughters[0])
    #print("number of daughters found : "+str(len(cells)))
    if cells is not None:
        cells.append(cell)
    return cells

def GetCellLifeFuturnodeath(cell):
    list_cells = [cell,]
    if cell is None or cell.daughters is None or len(cell.daughters) != 1:
        #print("Futur : cell is : "+str(cell))
        #print("Futur : cell has no daughters")
        return list_cells
    cells = GetCellLifeFuturnodeath(cell.daughters[0])
    #print("number of daughters found : "+str(len(cells)))
    if cells is not None:
        cells.append(cell)
    return cells

def GetCellLifePast(cell):
    list_cells = [cell,]
    #if cell is not None and cell.mothers is not None:
    #    print(cell.mothers)
    if cell is None or cell.mothers is None or len(cell.mothers) == 0 or cell.mothers[0].daughters is None or len(cell.mothers[0].daughters) != 1:
        #print("Past : cell is : "+str(cell))
        #print("Past : cell has no mothers")
        return list_cells
    cells =GetCellLifePast(cell.mothers[0])
    #print("number of mothers found : "+str(len(cells)))
    if cells is not None:
        cells.append(cell)
    return cells

def GetCellLifePastnodeath(cell):
    list_cells = [cell,]
    #if cell is not None and cell.mothers is not None:
    #    print(cell.mothers)
    if cell is None or cell.mothers is None or len(cell.mothers) == 0 or cell.mothers[0].daughters is None or len(cell.mothers[0].daughters) != 1:
        #print("Past : cell is : "+str(cell))
        #print("Past : cell has no mothers")
        return list_cells
    cells =GetCellLifePastnodeath(cell.mothers[0])
    #print("number of mothers found : "+str(len(cells)))
    if cells is not None:
        cells.append(cell)
    return cells


def save_comparison_to_info(lineage_input_path,embryo_name,over_list,under_list,timepoint,color_under=1,color_over=3,folder_out="DATA/OUT/"):
    selection_by_errors = {}
    for cell_l in under_list:
        for cell in cell_l:
            name = str(get_longid(timepoint, int(cell)))
            selection_by_errors[name] = str(color_under)
    for cell_l in over_list:
        for cell in cell_l:
            name = str(get_longid(timepoint, int(cell)))
            selection_by_errors[name] = str(color_over)
    SaveTabToXMLInfo(lineage_input_path, lineage_input_path, selection_by_errors, "selection_embryo_comparison")
    SaveTabToTxtInfo(folder_out + embryo_name, "embryo_comparison_selection.txt", selection_by_errors,
                          "generated_by_analysis")

def Get_Cell_Names(path_lineage, info="cell_name"):
    cell_values={}
    source = open(path_lineage)
    tree = ET.parse(source)
    tree = tree.getroot()
    lineage_elem = tree.find(info)
    if lineage_elem is not None:
        for cell in lineage_elem.findall('cell'):
            cell_id = cell.get('cell-id')
            cell_child = cell.text
            if cell_child is not None and cell_child != "None":
                new_val = str(cell_child.replace("'", "").replace(" ", ""))
                cell_values[cell_id] = new_val
        # print(str(result))
        return cell_values
    return None

def Get_Cell_Names_Swapped(path_lineage, info="cell_name"):
    cell_values={}
    source = open(path_lineage)
    tree = ET.parse(source)
    tree = tree.getroot()
    lineage_elem = tree.find(info)
    if lineage_elem is not None:
        for cell in lineage_elem.findall('cell'):
            cell_id = cell.get('cell-id')
            cell_child = cell.text
            if cell_child is not None and cell_child != "None":
                new_val = str(cell_child.replace("'", "").replace(" ", ""))
                if not new_val in cell_values:
                    cell_values[new_val] = []
                cell_values[new_val].append(cell_id)
        # print(str(result))
        return cell_values
    return None

def Get_Cell_Contact_Surface(path_lineage, info="cell_contact_surface"):
    cell_values={}
    source = open(path_lineage)
    tree = ET.parse(source)
    tree = tree.getroot()
    lineage_elem = tree.find(info)
    if lineage_elem is not None:
        for cell in lineage_elem.findall('cell'):
            cell_id = cell.get('cell-id')
            cell_child = cell.text
            if cell_child is not None and cell_child != "None":
                new_val = str(cell_child.replace("'", "").replace(" ", ""))
                cell_values[cell_id] = new_val
        # print(str(result))
        return cell_values
    return None

def Get_Cell_Values_Float(path_lineage, info, filter_background=False):
    cell_values = {}
    min_val = 1000000000
    max_val = -1000000000
    source = open(path_lineage)
    tree = ET.parse(source)
    tree = tree.getroot()
    lineage_elem = tree.find(info)
    if lineage_elem is not None:
        for cell in lineage_elem.findall('cell'):
            cell_id = cell.get('cell-id')
            ct, cid = get_id_t(cell_id)
            if not filter_background or cid != 1:
                cell_child = cell.text
                if cell_child is not None and cell_child != "None":
                    new_val = float(cell_child.replace("'", "").replace(" ", ""))
                    if new_val > max_val:
                        max_val = new_val
                    if new_val < min_val:
                        min_val = new_val
                    cell_values[cell_id] = new_val
        # print(str(result))
        return min_val, max_val, cell_values
    return 0, 0, None


def _find_t(cells_per_time, n):
    if n in cells_per_time.values():
        times = [t for t in cells_per_time if cells_per_time[t] == n]
        return (min(times) + max(times))/2.0
    smaller_times = [t for t in cells_per_time if cells_per_time[t] < n]
    larger_times = [t for t in cells_per_time if cells_per_time[t] > n]
    ts = max(smaller_times)
    tl = min(larger_times)
    return ts + (tl - ts) * (n - cells_per_time[ts]) / (cells_per_time[tl] - cells_per_time[ts])


def _temporal_alignement(ref_cells_per_time, cells_per_time):
    first = max(min(ref_cells_per_time.values()), min(cells_per_time.values()))
    last = min(max(ref_cells_per_time.values()), max(cells_per_time.values()))
    ref_times = []
    times = []
    for n in range(first, last+1):
        if n not in ref_cells_per_time.values() and n not in cells_per_time.values():
            continue
        ref_times += [_find_t(ref_cells_per_time, n)]
        times += [_find_t(cells_per_time, n)]
    num = sum(np.multiply(times, ref_times)) - sum(times) * sum(ref_times) / len(times)
    den = sum(np.multiply(times, times)) - sum(times) * sum(times) / len(times)
    a = num/den
    b = (sum(ref_times) - a * sum(times)) / len(times)
    return a, b



def temporal_alignment(ref_lineage, lineage, ref_time_digits_for_cell_id=4, time_digits_for_cell_id=4):
    """

    Parameters
    ----------
    ref_lineage: reference lineage
    lineage: lineage to be aligned with the reference lineage
    time_digits_for_cell_id: number of digits for the cell number in the unique cell identifier

    Returns
    -------
    a, b: coefficients of the linear warping. The number of cells at time 't' of the lineage is
        made comparable to the number of cells at time 'a * t + b' of the reference lineage.

    """
    ref_div = 10 ** ref_time_digits_for_cell_id
    div = 10 ** time_digits_for_cell_id

    ref_lineage_o = read_dictionary(ref_lineage)["cell_lineage"]
    cells = list(set(ref_lineage_o.keys()).union(set([v for values in list(ref_lineage_o.values()) for v in values])))
    cells = sorted(cells)
    ref_cells_per_time = {}
    for c in cells:
        t = int(c) // ref_div
        ref_cells_per_time[t] = ref_cells_per_time.get(t, 0) + 1
    lineage_o = read_dictionary(lineage)["cell_lineage"]
    cells = list(set(lineage_o.keys()).union(set([v for values in list(lineage_o.values()) for v in values])))
    cells = sorted(cells)
    cells_per_time = {}
    for c in cells:
        t = int(c) // div
        cells_per_time[t] = cells_per_time.get(t, 0) + 1

    return _temporal_alignement(ref_cells_per_time, cells_per_time)

def get_aligned_time(t,a,b):
    return int((a*t)+b)


def get_prev_mother(cell_lineage,cell_id):
    tc,idc = get_id_t(cell_id)
    for ckey in cell_lineage:
        for childcell in cell_lineage[ckey].daughters:
            if int(childcell.t) == int(tc) and int(childcell.id) == int(idc):
                return str(ckey)
    return None
            
def count_cells(lineage_input_path,cell_list=None,remove_time=[],only_times=[]):
    cell_count_by_time = {}
    local_list = cell_list
    if local_list is None:
        local_list = LoadCellList(lineage_input_path)
    for cell_key in local_list:
        cell_obj = local_list[cell_key]
        if not cell_obj.t in remove_time and (only_times==[] or cell_obj.t in only_times):
            if not cell_obj.t in cell_count_by_time:
                cell_count_by_time[cell_obj.t] = 0
            cell_count_by_time[cell_obj.t] += 1
    return dict(sorted(cell_count_by_time.items()))

def count_small_cells(lineage_input_path,cell_list=None,volume_max=1000,volume_ratio=1):
    cell_count_by_time = {}
    cell_keys_by_time = []
    local_list = cell_list
    if local_list is None:
        local_list = LoadCellList(lineage_input_path)
    minv, maxv, volumes = Get_Cell_Values_Float(lineage_input_path, "cell_volume", False)
    for cell_key in local_list:
        cell_obj = local_list[cell_key]
        if not cell_obj.t in cell_count_by_time:
            cell_count_by_time[cell_obj.t] = 0
        if (float(volumes[cell_key]) *volume_ratio) <= volume_max:
            cell_count_by_time[cell_obj.t] += 1
            cell_keys_by_time.append(str(cell_key))
    return cell_keys_by_time,cell_count_by_time



def get_t_start_ids(start_time,cell_list):
    id_list = []
    for cell in cell_list:
        cell_t,cell_id = get_id_t(str(cell))
        if cell_t == start_time:
            id_list.append(str(cell))
    return id_list

def get_t_start_objs(start_time,cell_list):
    obj_list = []
    for cell in cell_list:
        cell_t,cell_id = get_id_t(str(cell))
        if cell_t == start_time:
            obj_list.append(cell_list[cell])
    return obj_list

def match_cells(start_time,lineage1,lineage2):
    result = []
    cell_list_1 = LoadCellList(lineage1)
    cell_list_2 = LoadCellList(lineage2)
    id_list = get_t_start_ids(start_time,cell_list_1)
    for idc in id_list:
        if idc in cell_list_2:
            cell1 = cell_list_1[idc]
            cell2 = cell_list_2[idc]
            result.append((cell1,cell2))
    return result

def build_leaves(cellobj):
    leaves_list = {}
    if cellobj is None or cellobj.daughters is None or len(cellobj.daughters) == 0:
        leaves_list[cellobj.t] = [get_longid(cellobj.t,cellobj.id)]
        return leaves_list
    for daughter in cellobj.daughters:
        d_list = build_leaves(daughter)
        for time in d_list:
            if not time in leaves_list:
                leaves_list[time] = []
            for idc in d_list[time]:
                if not idc in leaves_list[time]:
                    leaves_list[time].append(idc)
    return leaves_list

def get_leaves_times(cellobj,time):
    leaves = build_leaves(cellobj)
    if not time in leaves:
        return []
    else :
        return leaves[time]

def get_leaves(cellobj):
    result = []
    leaves = build_leaves(cellobj)
    for timepoint in leaves:
        for leavesid in leaves[timepoint]:
            result.append(leavesid)
    return result

def get_branches_count(cellobj):
    branches=1
    if cellobj is None or cellobj.daughters is None or len(cellobj.daughters) == 0:
        return branches
    for daughter in cellobj.daughters:
        dcount = get_branches_count(daughter)
        branches += dcount
    return branches

def get_division_count(cellobj):
    branches=0
    if cellobj is None or cellobj.daughters is None or len(cellobj.daughters) == 0:
        return branches
    if len(cellobj.daughters) == 1:
        return get_division_count(cellobj.daughters[0])
    else:
        branches = 1
        for daughter in cellobj.daughters:
            dcount = get_branches_count(daughter)
            branches += dcount
    return branches

def build_division_histogram(start_time,lineage1):
    result = {}
    cell_list_1 = LoadCellList(lineage1)
    id_list = get_t_start_ids(start_time, cell_list_1)
    for idc in id_list:
        if idc in cell_list_1:
            cellt,cellid = get_id_t(idc)
            countd = get_division_count(cell_list_1[idc])
            result[str(cellid)] = countd
    return result


def compute_all_volumes(lineage,info_name,filter_background=False,ratio=1):
    result = []
    min,max,volumes = Get_Cell_Values_Float(lineage,info_name,filter_background)
    for key in volumes:
        result.append(float(volumes[key])*ratio)
    return result

def get_min_timepoint_leaf(cellobj):
    minc = 100000000
    if cellobj.daughters is None or len(cellobj.daughters) <1:
        return cellobj.t
    if len(cellobj.daughters) == 1:
        return get_min_timepoint_leaf(cellobj.daughters[0])
    else:
        for daughter in cellobj.daughters:
            minc = min(minc,get_min_timepoint_leaf(daughter))
    return minc

def get_max_timepoint_leaf(cellobj):
    maxc = -100000000
    if cellobj.daughters is None or len(cellobj.daughters) <1:
        return cellobj.t
    if len(cellobj.daughters) == 1:
        return get_max_timepoint_leaf(cellobj.daughters[0])
    else:
        for daughter in cellobj.daughters:
            maxc = max(maxc,get_max_timepoint_leaf(daughter))
    return maxc

def get_timepoint_leaf(cellobj):
    result = []
    cells_leaves=[]
    if cellobj.daughters is None or len(cellobj.daughters) <1:
        return [str(get_longid(cellobj.t,cellobj.id))],[cellobj.t]
    if len(cellobj.daughters) == 1:
        return get_timepoint_leaf(cellobj.daughters[0])
    else:
        for daughter in cellobj.daughters:
            cells_leaves_c,leaveschildren = get_timepoint_leaf(daughter)
            for leaves in leaveschildren:
                result.append(leaves)
            for celll in cells_leaves_c:
                cells_leaves.append(celll)
    return cells_leaves,result

def build_all_leaves(lineage_input_path,start_time,end_time,cell_list=None):
    all_leaves=[]
    mars_ids = []
    cells_ids = []
    total_leaves_count = 0
    early_death_count = 0
    local_list = cell_list
    if local_list is None:
        local_list = LoadCellList(lineage_input_path)
    obj_list = get_t_start_objs(start_time,local_list)
    for objcell in obj_list:
        cellsleaf,leaves = get_timepoint_leaf(objcell)
        found_early_leave = False
        for i in range(0,len(leaves)):
            total_leaves_count += 1
            if int(leaves[i]) != int(end_time):
                early_death_count += 1
                found_early_leave = True
                cells_ids.append(str(cellsleaf[i]))
        if found_early_leave:
            all_leaves.append(leaves)
            mars_ids.append(str(get_longid(objcell.t,objcell.id)))
    final_proportion = 0
    if total_leaves_count > 0:
        final_proportion = (early_death_count/total_leaves_count)*100
    return cells_ids,final_proportion,mars_ids,all_leaves

def build_min_max_leaves(lineage_input_path,start_time,end_time,cell_list=None):
    min_values=[]
    max_values=[]
    mars_ids=[]
    local_list = cell_list
    if local_list is None:
        local_list = LoadCellList(lineage_input_path)
    obj_list = get_t_start_objs(start_time,local_list)
    for objcell in obj_list:
        minc = get_min_timepoint_leaf(objcell)
        maxc = get_max_timepoint_leaf(objcell)
        if maxc != -100000000 and minc != 100000000:

            min_values.append(minc)
            max_values.append(maxc)
    return mars_ids,min_values,max_values

def get_min_branches_length(cellobj):
    if cellobj is None or cellobj.daughters is None or len(cellobj.daughters) == 0:
        return 0
    if len(cellobj.daughters) == 1:
        return 1+get_min_branches_length(cellobj.daughters[0])
    minbranch = 10000000
    for daughter in cellobj.daughters:
        minbranch = min(get_branches_count(daughter),minbranch)
    return minbranch

def get_max_branches_length(cellobj):
    if cellobj is None or cellobj.daughters is None or len(cellobj.daughters) == 0:
        return 0
    if len(cellobj.daughters) == 1:
        return 1+get_max_branches_length(cellobj.daughters[0])
    maxbranch = 0
    for daughter in cellobj.daughters:
        maxbranch = max(get_branches_count(daughter),maxbranch)
    return maxbranch
"""
def get_avg_branches_length(cellobj):
    if cellobj is None or cellobj.daughters is None or len(cellobj.daughters) == 0:
        return 1,
    if len(cellobj.daughters) == 1:
        return 1+get_max_branches_length(cellobj.daughters[0])
    maxbranch = 0
    for daughter in cellobj.daughters:
        maxbranch = max(get_branches_count(daughter),maxbranch)
    return maxbranch"""

def compare_leafs_at_time(start_time,time,lineage1,lineage2):
    returnarray = {}
    matched_cells = match_cells(start_time,lineage1,lineage2)
    for cellpair in matched_cells:
        leaves1 = get_leaves_times(cellpair[0],time)
        leaves2 = get_leaves_times(cellpair[1],time)
        shift = len(leaves2)-len(leaves1)/len(leaves1)*100
        returnarray[str(cellpair[0].id)]=shift
        if len(leaves2)-len(leaves1) > 0:
            print("id "+str(cellpair[1].id)+ " has "+str(len(leaves2)-len(leaves1))+" more leaves in "+lineage1+" for time : "+str(time)+" with a shift of "+str(shift)+"%")
        elif len(leaves2)-len(leaves1)<0:
            print("id "+str(cellpair[1].id)+ " has "+str(len(leaves1)-len(leaves2))+" more leaves in "+lineage2+" for time : "+str(time)+" with a shift of "+str(shift)+"%")
        else:
            print("id "+str(cellpair[1].id) + " have the same number of leaves for time : " + str(time))
    return returnarray

def compare_leafs(start_time,lineage1,lineage2):
    returnarray = {}
    matched_cells = match_cells(start_time,lineage1,lineage2)
    for cellpair in matched_cells:
        leaves1 = get_leaves(cellpair[0])
        leaves2 = get_leaves(cellpair[1])
        shift = len(leaves2) - len(leaves1) / len(leaves1) * 100
        returnarray[str(cellpair[0].id)] = shift
        if len(leaves2)-len(leaves1) > 0:
            print("id "+str(cellpair[1].id)+ " has "+str(len(leaves2)-len(leaves1))+" more leaves in "+lineage1+" with a shift of "+str(shift)+"%")
        elif len(leaves2)-len(leaves1)<0:
            print("id "+str(cellpair[1].id)+ " has "+str(len(leaves1)-len(leaves2))+" more leaves in "+lineage2+" with a shift of "+str(shift)+"%")
        else:
            print("id "+str(cellpair[1].id) + " have the same number of leaves ")
    return returnarray

def compares_branch_count(start_time,lineage1,lineage2):
    returnarray = {}
    matched_cells = match_cells(start_time,lineage1,lineage2)
    for cellpair in matched_cells:
        leaves1 = get_branches_count(cellpair[0])
        leaves2 = get_branches_count(cellpair[1])
        shift = len(leaves2) - len(leaves1) / len(leaves1) * 100
        returnarray[str(cellpair[0].id)] = shift
        if leaves2-leaves1 > 0:
            print("id "+str(cellpair[1].id)+ " has "+str(leaves2-leaves1)+" more branches in "+lineage1+" with a shift of "+str(shift)+"%")
        elif leaves2-leaves1<0:
            print("id "+str(cellpair[1].id)+ " has "+str(leaves1-leaves2)+" more branches in "+lineage2+" with a shift of "+str(shift)+"%")
        else:
            print("id "+str(cellpair[1].id) + " have the same number of branches ")
    return returnarray

def compares_branch_max(start_time,lineage1,lineage2):
    returnarray = {}
    matched_cells = match_cells(start_time,lineage1,lineage2)
    for cellpair in matched_cells:
        max1 = get_max_branches_length(cellpair[0])
        max2 = get_max_branches_length(cellpair[1])
        shift = max2 - max1 / max1 * 100
        returnarray[str(cellpair[0].id)] = shift
        print("id "+str(cellpair[0].id)+ " maximum branch length is "+str(max1)+" in "+lineage1+" but is "+str(max2)+" in "+str(lineage2)+" with a shift of "+str(shift)+"%")
    return returnarray

def compares_branch_min(start_time, lineage1, lineage2):
    returnarray = {}
    matched_cells = match_cells(start_time, lineage1, lineage2)
    for cellpair in matched_cells:
        max1 = get_min_branches_length(cellpair[0])
        max2 = get_min_branches_length(cellpair[1])
        shift = max2 - max1 / max1 * 100
        returnarray[str(cellpair[0].id)] = shift
        print("id " + str(cellpair[0].id) + " maximum branch length is " + str(
            max1) + " in " + lineage1 + " but is " + str(max2) + " in " + str(lineage2)+" with a shift of "+str(shift)+"%")
    return returnarray

def build_branch_length(lineage_input_path,cell_list=None,mincellcount=64,maxcellcount=500):
    branch_length_by_start={}
    cell_count = count_cells(lineage_input_path)
    mintime = 10000
    maxtime = -1000
    for time in cell_count:
        if cell_count[time] >= mincellcount or cell_count[time] <= maxcellcount:
            if time < mintime:
                mintime = time
            if time > maxtime:
                maxtime = time
    local_list = cell_list
    if local_list is None:
        local_list = LoadCellList(lineage_input_path)
    for cell_key in local_list:
        cell_obj = local_list[cell_key]
        while (cell_obj is not None and cell_obj.mothers is not None and len(cell_obj.mothers) > 0 and
               cell_obj.mothers[0] is not None and cell_obj.mothers[0].daughters is not None and len(
                    cell_obj.mothers[0].daughters) == 1):
            cell_obj = cell_obj.mothers[0]
        if cell_obj is not None and (cell_obj.t >= mintime and cell_obj.t <= maxtime):
            new_cell_key = str(get_longid(cell_obj.t, cell_obj.id))
            if not new_cell_key in branch_length_by_start:
                if new_cell_key in local_list:
                    cell_life = GetCellLifetime(local_list[new_cell_key])
                    if cell_life is not None:
                        branch_length_by_start[new_cell_key] = len(cell_life)
    return branch_length_by_start

def get_endtime_in_lineage(lineage):
    end =-10000
    local_list = LoadCellList(lineage)
    for cell in local_list:
        if local_list[cell].t > end:
            end = local_list[cell].t
    return end

def build_branch_length_no_finaldeath(lineage_input_path,endtime=None,cell_list=None,mintime=None,maxtime=None):
    branch_length_by_start={}
    local_list = cell_list
    if local_list is None:
        local_list = LoadCellList(lineage_input_path)
    for cell_key in local_list:
        cell_obj = local_list[cell_key]
        if cell_obj is not None and ((mintime is None or cell_obj.t >= mintime) and (maxtime is None or cell_obj.t <= maxtime)):
            while (cell_obj is not None and cell_obj.mothers is not None and len(cell_obj.mothers) > 0 and
                   cell_obj.mothers[0] is not None and cell_obj.mothers[0].daughters is not None and len(
                        cell_obj.mothers[0].daughters) == 1):
                cell_obj = cell_obj.mothers[0]

            new_cell_key = str(get_longid(cell_obj.t, cell_obj.id))
            if not new_cell_key in branch_length_by_start:
                if new_cell_key in local_list:
                    cell_life = GetCellLifetime(local_list[new_cell_key])
                    if cell_life is not None:
                        cell_last_life = GetCellLastBranchCount(cell_life, endtime)
                        branch_length_by_start[new_cell_key] = len(cell_life)-cell_last_life
    return branch_length_by_start

def build_branch_length_no_both(lineage_input_path,cell_list=None,mintime=None,maxtime=None):
    branch_length_by_start={}
    local_list = cell_list
    if local_list is None:
        local_list = LoadCellList(lineage_input_path)
    for cell_key in local_list:
        cell_obj = local_list[cell_key]
        original_obj = local_list[cell_key]
        if cell_obj is not None and ((cell_obj.t >= mintime or mintime is None) and (cell_obj.t <= maxtime or maxtime is None)):
            while (cell_obj is not None and cell_obj.mothers is not None and len(cell_obj.mothers) > 0 and
                   cell_obj.mothers[0] is not None and cell_obj.mothers[0].daughters is not None and len(
                        cell_obj.mothers[0].daughters) == 1):
                cell_obj = cell_obj.mothers[0]
            flag = True
            #do not count if first branch
            if cell_obj.mothers is None or len(cell_obj.mothers)==0:
                flag = False
            # do not count if last branch
            while (original_obj is not None and original_obj.daughters is not None and len(original_obj.daughters) == 1):
                original_obj = original_obj.daughters[0]
            if original_obj.daughters is None or len(original_obj.daughters) == 0:
                flag= False
            if flag:
                new_cell_key = str(get_longid(cell_obj.t, cell_obj.id))
                if not new_cell_key in branch_length_by_start:
                    if new_cell_key in local_list:
                        cell_life = GetCellLifetime(local_list[new_cell_key])
                        if cell_life is not None:
                            branch_length_by_start[new_cell_key] = len(cell_life)
    return branch_length_by_start
def find_ids_at_end(current_cell,end_time):
    result = []
    if current_cell.t == end_time:
        result.append(current_cell.id)
        return result
    if current_cell is None or current_cell.daughters is None or len(current_cell.daughters) ==0 or current_cell.t > end_time:
        return result
    if len(current_cell.daughters)==1:
        temp_r = find_ids_at_end(current_cell.daughters[0],end_time)
        for cell in temp_r:
            result.append(cell)
    else:
        for cell_d in current_cell.daughters:
            temp_r = find_ids_at_end(cell_d,end_time)
            for cell in temp_r:
                result.append(cell)
    return result


def match_start_cells_and_end(input_lineage,start_time,end_time):
    cell_list = LoadCellList(input_lineage)
    result = {}
    start_cells = []
    for cell in cell_list:
        if cell_list[cell].t == start_time:
            if not cell in start_cells:
                start_cells.append(cell_list[cell])
    for cell_obj in start_cells:
        end_cells_obj = find_ids_at_end(cell_obj,end_time)
        if len(end_cells_obj)>0:
            if not cell_obj.id in result:
                result[cell_obj.id] = []
            for obj in end_cells_obj:
                result[cell_obj.id].append(obj)
    return result