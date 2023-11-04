import os
import time

'''
path1 is SwVersions tags: folder example: FasAdaptAs
path2 is sas test run: folder example: FasAdaptAsImpl-8.2331.2_0_BCI
'''


def compute_implementation_folders(folder_name):
    component_name = folder_name.split("-")
    # we now have a list with 2 elements, but we need just the firt part which contains the component name and implementation
    return component_name[0]


def create_file_name(component, tag, word1):
    return component + "Impl" + "-" + tag + word1


def get_needed_scal_value(directory_name):
    # we need just the final part of the directory name
    list_words = directory_name.split("_")
    return list_words[len(list_words) - 1]


def complete_folders(path1, path2, tag):
    folders_checkout = os.listdir(path1)
    folders_sil_test = os.listdir(path2)
    final_word = "BCI"
    list_components = list()
    for component_run in folders_sil_test:
        component_name = compute_implementation_folders(component_run)
        list_components.append(component_name[:-4])  # delete Impl
    # now we check what is missing and what is not missing and we create the mssing folders
    list_folders_to_add_raw = list()
    # the idea is to traverse every component from tags and check if it is present in the sil folder list
    for component_tag in folders_checkout:
        if component_tag in list_components:
            continue
        else:
            # we just add in the list what is missing
            list_folders_to_add_raw.append(component_tag)
    print(list_folders_to_add_raw)

    list_folders_to_add_final = list()
    for folder in list_folders_to_add_raw:
        folder_renamed = create_file_name(folder, tag, final_word)
        list_folders_to_add_final.append(folder_renamed)
    print(list_folders_to_add_final)
    # now create the missing folders there
    os.chdir(path2)
    for folder_new in list_folders_to_add_final:
        if not os.path.exists(folder_new):
            os.mkdir(folder_new)
    '''
    list_folders_add_raw-> folders which we need in Swc\ tags
    list_folders_to_add_final -> folders we need in no-baseline-export
    '''
    return list_folders_to_add_raw, list_folders_to_add_final


def create_additional_folders(list_sw_tags_added, list_baseline_exports_added, path1, path2, constant_folder1,
                              constant_folder2):
    ''''
        :param list_sw_tags_added:
        :param list_baseline_exports_added:
        :param path1:
        :param path2:
        :param constant_folder1:
        :param constant_folder2:
        :return: create addtional folders using the script that already generated the folders
        the main idea is to go at every sw_tags which was missing from baseline_export and to traverse into the correct folders and take the final value for the scal
        we will use as helper the list_baseline_exports_added as we need to go in the correct sw version folder
        '''
    # first we iterate through both list -> they will have same size from previous script
    list_needed_scal_values = list()
    for (sw_tag_folder, baseline_export_folder) in zip(list_sw_tags_added, list_baseline_exports_added):
        # change to folder path1 and the correct list
        path_wanted_folder = os.path.join(path1, sw_tag_folder)
        os.chdir(path_wanted_folder)
        # in that folder we are checking all directories and find the name of the version that we have created the folder already
        # in case there is no such folder then we must raise an error -> IT NEEDS TO BE THERE FROM MY OPINION
        if not os.path.exists(baseline_export_folder):
            raise Exception("There is no such folder with this tag!! WTF??")
        # we go inside that folder
        path_wanted_folder2 = os.path.join(path_wanted_folder, baseline_export_folder)
        # WE KNOW THE EXACT LOCATION FROM WHERE WE SHOULD GET TAGS:Documentation\SwcTags
        path_wanted_folder3 = os.path.join(path_wanted_folder2, constant_folder1, constant_folder2)
        os.chdir(path_wanted_folder3)
        # now we check if there is a folder which starts with the component name
        # Ex: FasCdi_Dev_167_004_2 -> search to start with FasCdi and also check for Dev maybe to be sure
        list_directories = os.listdir()
        for directory in list_directories:
            if sw_tag_folder in directory and "Dev" in directory:
                scal_value = get_needed_scal_value(directory)
                list_needed_scal_values.append(scal_value)
                print("We are in the directory named {} and we have the following scal value {}".format(directory,
                                                                                                        scal_value))
    # the final step is to create the folders now in the newly generated baseline export values
    for (baseline_export_folder, scal_value) in zip(list_baseline_exports_added, list_needed_scal_values):
        folder_export_needed_path = os.path.join(path2, baseline_export_folder)
        os.chdir(folder_export_needed_path)
        name_scal_folder = "scal_" + scal_value
        if not os.path.exists(name_scal_folder):
            os.mkdir(name_scal_folder)
            print("We have created in {} the folder named {}".format(baseline_export_folder, name_scal_folder))


if __name__ == '__main__':
    path1 = r"D:\test2"
    path2 = r"D:\test1"
    tag = "8.2331.2_0_"
    constant_folder1 = "Documentation"
    constant_folder2 = "SWCTest"
    list_sw_tags_added, list_baseline_exports_added = complete_folders(path1, path2, tag)
    print("Step1 completed")
    time.sleep(2)
    create_additional_folders(list_sw_tags_added, list_baseline_exports_added, path1, path2, constant_folder1,
                              constant_folder2)
    print("Step2 completed")
    time.sleep(1)
