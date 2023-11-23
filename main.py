import os
import time
import shutil

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
        list_searched_sw_tags = list()
        # need to check in case we have some duplicate folders (like report version 1.1000000001 :) )-> have a list for directory names to enter only once
        for directory in list_directories:
            if sw_tag_folder in directory and "Dev" in directory and sw_tag_folder not in list_searched_sw_tags and os.path.isdir(
                    directory):
                scal_value = get_needed_scal_value(directory)
                list_searched_sw_tags.append(sw_tag_folder)
                list_needed_scal_values.append(scal_value)
                print("We are in the directory named {} and we have the following scal value {}".format(directory,
                                                                                                        scal_value))
    # the final step is to create the folders now in the newly generated baseline export values
    # use a list to store scal values for the next part of the script
    scal_values_list = list()
    for (baseline_export_folder, scal_value) in zip(list_baseline_exports_added, list_needed_scal_values):
        folder_export_needed_path = os.path.join(path2, baseline_export_folder)
        os.chdir(folder_export_needed_path)
        name_scal_folder = "scal_" + scal_value
        scal_values_list.append(name_scal_folder)
        if not os.path.exists(name_scal_folder):
            os.mkdir(name_scal_folder)
            print("We have created in {} the folder named {}".format(baseline_export_folder, name_scal_folder))

    return scal_values_list


def copy_folders(list_sw_tags_added, list_baseline_exports_added, list_scals_added, constant_folder_documentation,
                 constant_folder_swc_test, constant_folder_config, path1, path2):
    '''

    :param list_sw_tags_added:
    :param list_baseline_exports_added:
    :param list_scals_added:
    :param constant_folder_documentation:
    :param constant_folder_swc_test:
    :param path1 - the tags folder
    :param path2 - the baseline export folder
    :return: using the previous 2 functions we now have 3 lists in which in each iteration we can copy the respective needed folders in the correct generated scal folders
    we need to copy both configs and SwcTest to the scal folders so we will traverse in tags in 2 different layers and copy each needed folder
    '''
    for (sw_tag, list_baseline_export_folder, scal) in zip(list_sw_tags_added, list_baseline_exports_added,
                                                           list_scals_added):
        # create destination_folder
        dest_folder = os.path.join(path2, list_baseline_export_folder, scal)
        #create here the 2 folders needed Configs and SwcTest
        os.chdir(dest_folder)
        os.mkdir(constant_folder_config)
        os.mkdir(constant_folder_swc_test)
        # now go and copy each thing starting with configs
        source_config_folder = os.path.join(path1, sw_tag, list_baseline_export_folder)
        os.chdir(source_config_folder)
        list_dirs_tag = os.listdir()
        for directory in list_dirs_tag:
            if directory == constant_folder_config:
                # make the copy
                shutil.copytree(src=os.path.join(source_config_folder, constant_folder_config), dst=os.path.join(dest_folder,constant_folder_config), dirs_exist_ok=True)
                print("Copying from {} to {}".format(os.path.join(source_config_folder, constant_folder_config),
                                                     os.path.join(dest_folder,constant_folder_config)))
                break
        # copy now swc_test
        source_swc_test_folder = os.path.join(source_config_folder, constant_folder_documentation)
        os.chdir(source_swc_test_folder)
        list_dirs_documentation = os.listdir()
        for directory in list_dirs_documentation:
            if directory == constant_folder_swc_test:
                shutil.copytree(src=os.path.join(source_swc_test_folder,constant_folder_swc_test), dst=os.path.join(dest_folder,constant_folder_swc_test), dirs_exist_ok=True)
                print("Copying from {} to {}".format(os.path.join(source_swc_test_folder, constant_folder_swc_test),
                                                     os.path.join(dest_folder,constant_folder_swc_test)))
                break


if __name__ == '__main__':
    path1 = r"D:\test2"
    path2 = r"D:\test1"
    tag = "8.2331.2_0_"
    constant_folder1 = "Documentation"
    constant_folder2 = "SWCTest"
    config_folder = "Configs"
    list_sw_tags_added, list_baseline_exports_added = complete_folders(path1, path2, tag)
    print("Step1 completed")
    time.sleep(2)
    list_scals = create_additional_folders(list_sw_tags_added, list_baseline_exports_added, path1, path2,
                                           constant_folder1,
                                           constant_folder2)
    print("Step2 completed")
    time.sleep(2)
    copy_folders(list_sw_tags_added, list_baseline_exports_added, list_scals, constant_folder1, constant_folder2,
                 config_folder, path1, path2)
    print("Step 3 completed")
    time.sleep(2)
    print("Script has finished successfully")

