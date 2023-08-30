import re
from typing import List

from acheck.utils import filehelper as fh


def get_actions_with_var_type(domain) -> dict:
    """Function to get actions with parameters from domain

    Args:
        domain: domain file path

    Returns:
        actions_with_var_type:  dictionary where the keys are actions and their
                                values are the parameters defined inside the domain
    """
    with open(domain, "r") as f:
        pddl = f.read().replace("\n", " ").split()

    flag_action = False
    flag_param = False
    actions_with_var_type = {}
    temp_list = []
    for i, w in enumerate(pddl):
        if w == "(:action":
            flag_action = True
            temp_list.append(pddl[i + 1])
        if flag_action:
            if flag_param:
                temp_list.append(w.replace("(", "").replace(")", ""))
                if w == ":precondition":
                    var_list = [x for x in temp_list if "-" not in x]
                    var_list.pop(0)
                    var_list.pop()
                    index_of_last_var_name = 0
                    to_be_deleted = []
                    for index, var in enumerate(var_list):
                        if "?" not in var and index < len(var_list):
                            for count in range(1, index - index_of_last_var_name + 1):
                                var_list[index + count * (-1)] = var
                            to_be_deleted.append(index)
                            index_of_last_var_name = index + 1
                    for ind, deleted in enumerate(to_be_deleted):
                        var_list.pop(deleted - ind)

                    actions_with_var_type.update({temp_list[0]: var_list})
                    temp_list = []
                    flag_param = False
                    flag_action = False
            if w == ":parameters":
                flag_param = True

    return actions_with_var_type


def get_actions_with_vars(domain) -> dict:
    """Function to get actions with parameters from domain

       Args:
           domain: domain file path

       Returns:
           actions_with_var_type:  dictionary where the keys are actions and their
                                   values are the parameters defined inside the domain
       """
    warnings.warn("This method is deprecated. Use get_actions_with_var_type instead", category=DeprecationWarning)
    with open(domain, "r") as f:
        pddl = f.read().replace("\n", " ").split()

    flag_action = False
    flag_param = False
    actions_with_variables = {}
    temp_list = []
    for i, w in enumerate(pddl):
        if w == "(:action":
            flag_action = True
            temp_list.append(pddl[i + 1])
        if flag_action:
            if flag_param:
                temp_list.append(w.replace("(", "").replace(")", ""))
                if w == ":precondition":
                    var_list = [x for x in temp_list if "?" in x]
                    actions_with_variables.update({temp_list[0]: var_list})
                    temp_list = []
                    flag_param = False
                    flag_action = False
            if w == ":parameters":
                flag_param = True

    return actions_with_variables


def get_world_objects_with_type(problem) -> dict:
    """Parses domain world objects

    Args:
        problem: problem pddl file

    Returns:
        world_objects: dictionary where the keys are all world objects and the values are their type
    """
    with open(problem, "r") as f:
        pddl = f.read().replace("\n", " ").split()

    flag = False
    skip = True
    world_objects = {}
    temp_list = []
    for i, w in enumerate(pddl):
        if w == "(:objects":
            flag = True
        if flag:
            if w == ")":
                return world_objects
            if not skip:
                temp_list.append(w)
                if w == "-":
                    temp_list.pop()
                    world_objects.update({str(pddl[i + 1]): temp_list.copy()})
                    temp_list = []
                    skip = True
            else:
                skip = False
    return world_objects


def get_world_objects(problem) -> list:
    l = list(get_world_objects_with_type(problem).values())
    temp = []
    for elem in l:
        temp += elem
    return temp




def parse_domain(domain_file):
    actions = {}
    world_objects = {}

    string_list = fh.read_file(domain_file).splitlines()
    # crop comments
    for index, line in enumerate(string_list):
        string_list[index] = re.sub(re.compile(r";.*"), "", line)


    # crop whitespace and tabs etc.
    cropped_string = re.sub(re.compile(r"[\s]{2,}"), " ", " ".join(string_list))

    tokens = cropped_string.split(" ")



    parsed_groups = __slice_list("(:", tokens)



    for group in parsed_groups:
        if ":types" in group[0]:
            world_objects.update(__extract_objects(group[1:]))
        if ":constants" in group[0]:
            world_objects.update(__extract_objects(group[1:]))
        if ":action" in group[0]:
            actions.update(__extract_action(group[1:]))

    return actions, world_objects



def __slice_list(slice_string: str, to_slice: List[str]):

    groups = []
    last_slice_index = 0
    for index, token in enumerate(to_slice):
        if slice_string not in "".join(to_slice[index:len(to_slice)]):
            groups.append(to_slice[index-1:len(to_slice)])
            break
        if slice_string in token:

            groups.append(to_slice[last_slice_index:index])
            last_slice_index = index

    return groups


def __extract_action(group):
    group_n = __slice_list(":", group)
    for index, elem in enumerate(group_n):
        if index == 0:
            continue
        if ":parameters" in group_n[index-1]:

            return {group_n[0][0]: group_n[index - 1][1:]}
    return {}


def __extract_objects(group):
    objects = []
    world_objects = {}
    for index, elem in enumerate(group):
        if index == 0:
            objects.append(elem)
            continue
        if group[index - 1] == "-":
            for obj in objects:
                world_objects.update({obj: elem})
            objects.clear()
        elif elem != "-":
            objects.append(elem)
    return world_objects


