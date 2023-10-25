import os

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


if __name__ == '__main__':
    path1 = r"D:\test2"
    path2 = r"D:\test1"
    tag = "8.2331.2_0_"
    complete_folders(path1, path2, tag)
