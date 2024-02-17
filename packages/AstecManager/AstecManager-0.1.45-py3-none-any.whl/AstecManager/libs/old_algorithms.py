import os


def compute_graphs_ondemand(self, emrbyofolder, embryo_name, begin, end, exp_post=None, align_ref=True):
    """from AstecManager.libs.compare import apply_analysis
    atlas_path = self.compute_atlas_path()
    ref_lineage = None
    if align_ref:
        ref_lineage = os.path.join(atlas_path.replace("\n", "").replace(".", ""), "atlas/pm1.xml")
    mincells_test = 64
    maxcells_test = 500
    folder_out = os.path.join(emrbyofolder, os.path.join("analysis/", "post_segmentation"))
    lineages = []
    names = []
    if exp_post is None:
        lineages = [emrbyofolder + "/POST/POST_01/" + embryo_name + "_post_lineage.xml"]
        names = [exp_post]
    else:
        for post in exp_post:
            lineages.append(emrbyofolder + "/POST/POST_" + str(
                post) + "/" + embryo_name + "_post_lineage.xml")
            names.append(post)

    apply_analysis(lineages, names, folder_out, embryo_name, mincells_test, maxcells_test, begin, end,
                   path=embryo_name + "_output_comparison.png", is_post=True, ref_lineage=ref_lineage,
                   data_path=folder_out)
    if os.path.isfile("histogram_branch_data.csv"):
        os.system("rm histogram_branch_data.csv")
    """
def start_cycling_post(self):
    print("Function has been deprecated for now")
    """thread_count = 1
    flag = True
    param = self.to_run_list[0]
    raw_seg_folder = os.path.join(param.embryo_name, "SEG")
    exp_seg_folder = os.path.join(os.path.join(param.embryo_name, "SEG"),
                                  "SEG_" + param.params_dict["EXP_SEG"].replace('"', '') + "/")
    exp_seg_folder_backup = os.path.join(os.path.join(param.embryo_name, "SEG"),
                                         "SEG_" + param.params_dict["EXP_SEG"].replace('"', '') + "_backup/")
    exp_post_folder = os.path.join(os.path.join(param.embryo_name, "POST"),
                                   "POST_" + param.params_dict["EXP_POST"].replace('"', '') + "/")
    exp_post_folder_backup = os.path.join(os.path.join(param.embryo_name, "POST"),
                                          "POST_" + param.params_dict["EXP_POST"].replace('"', '') + "_backup/")
    if not os.path.exists(exp_seg_folder_backup):
        os.system("cp -R " + exp_seg_folder + " " + exp_seg_folder_backup)
    os.system("mv " + exp_post_folder + " " + exp_post_folder_backup)
    while flag:
        logfile = ""
        tc = start_astec_command(param)
        tc.start()
        tc.join()
        logfolder = os.path.join(exp_post_folder, "LOGS")
        # Iterate directory
        for path in os.listdir(logfolder):
            # check if current path is a file
            if os.path.isfile(os.path.join(logfolder, path)):
                if ".log" in path and "astec_postcorrection" in path and not "history" in path:
                    logfile = os.path.join(logfolder, path)
                    break

        f = open(logfile, "r")
        lines = f.readlines()
        f.close()
        found_a_fuse = False
        nb_fuse_test = 0
        nb_nofuse = 0
        for line in lines:
            if "cell fusion of time #" in line:
                nb_fuse_test += 1
            if "no cell fusion to be done" in line:
                nb_nofuse += 1
        if nb_fuse_test > nb_nofuse:
            found_a_fuse = True
        if nb_fuse_test == 0:
            found_a_fuse = False
        if found_a_fuse:
            os.system("cd " + str(exp_seg_folder) + " && rm -rf *")
            os.system("cd " + str(exp_post_folder) + " && rm -rf LOGS")
            os.system("mv " + exp_post_folder + " " + raw_seg_folder)
            os.system("cd " + raw_seg_folder + " && mv " + "POST_" + param.params_dict["EXP_POST"].replace('"',
                                                                                                           '') + "/* " + "SEG_" +
                      param.params_dict["EXP_SEG"].replace('"', ''))
            os.system("cd " + raw_seg_folder + " && rm -rf POST_" + param.params_dict["EXP_POST"].replace('"', ''))
            os.system("cd " + str(exp_seg_folder) + " && rename 's/post/seg/' *")
        else:
            flag = False
        # else , clear seg folder , copy all post in seg, rename image and lineage with post , clear post"""