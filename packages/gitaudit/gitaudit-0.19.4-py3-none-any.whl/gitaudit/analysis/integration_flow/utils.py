"""Utils for Integration Flow Analysis."""

from typing import List, Tuple, Set
from .int_flow import IntflowPullRequest


def find_last_stage_in_names(
    names_arr: List[List[str]],
    min_occurence_perc_threshold: float = 0.0,
) -> Tuple[Set[str], List[List[str]]]:
    """
    Finds the last stage in a list of lists of names.

    Args:
        names_arr: A list of lists of names.
        min_occurence_perc_threshold: The minimum percentage of occurence of a name
            in all lists to be considered as part of the stage.

    Returns:
        A tuple of the stage names and the new list of lists of names.
    """

    # get the last name of all arrays and find the most used one
    last_names = list(map(lambda x: x[-1], names_arr))
    most_used_name = max(set(last_names), key=last_names.count)

    # initialize the stage names and other helper variables
    stage_names = set()
    new_found_names = set([most_used_name])
    index_of_names_arr = list(map(len, names_arr))

    while new_found_names:
        current_name = new_found_names.pop()
        stage_names.add(current_name)

        additional_names_occurrence = {}

        # find the index of the current name in all arrays, this calculates the furthest reach
        index_of_names_arr = list(
            map(
                lambda names, index, c_name=current_name: min(
                    index,
                    names.index(c_name) if c_name in names else len(names),
                ),
                names_arr,
                index_of_names_arr,
            )
        )

        for names, index in zip(names_arr, index_of_names_arr):
            add_names = names[index:]

            for a_name in add_names:
                additional_names_occurrence[a_name] = (
                    additional_names_occurrence.get(a_name, 0) + 1
                )

        for a_name, n_count in additional_names_occurrence.items():
            if (
                a_name not in stage_names
                and n_count / len(names_arr) >= min_occurence_perc_threshold
            ):
                new_found_names.add(a_name)

    new_names_arr = list(
        map(
            lambda names, index: names[:index],
            names_arr,
            index_of_names_arr,
        )
    )

    new_names_arr = list(filter(None, new_names_arr))

    return stage_names, new_names_arr


def extract_integration_stages_by_names(
    names_arr: List[List[str]],
    min_occurence_perc_threshold: float = 0.0,
) -> List[Set[str]]:
    """
    Extracts the integration stages from a list of lists of names.

    Args:
        names_arr: A list of lists of names.
        min_occurence_perc_threshold: The minimum percentage of occurence of a name
            in all lists to be considered as part of the stage.

    Returns:
        A list of sets of integration stages.
    """
    stage_names = []

    names_arr = list(filter(None, names_arr))

    while names_arr:
        new_stage_names, names_arr = find_last_stage_in_names(
            names_arr, min_occurence_perc_threshold
        )
        stage_names.append(new_stage_names)

    return list(reversed(stage_names))


def extract_integration_stages(
    intflow_prs: List[IntflowPullRequest],
    min_occurence_perc_threshold: float = 0.0,
) -> List[Set[str]]:
    """
    Extracts the integration stages from a list of IntflowPullRequest objects.

    Args:
        intflow_prs: A list of IntflowPullRequest objects.

    Returns:
        A list of sets of integration stages.
    """
    sorted_status_check_names = []

    for int_pr in intflow_prs:
        pr_sorted_status_checks = sorted(
            int_pr.required_status_checks, key=lambda x: x.triggered_at
        )
        names = list(map(lambda x: x.name, pr_sorted_status_checks))

        sorted_status_check_names.append(names)

    return extract_integration_stages_by_names(
        sorted_status_check_names,
        min_occurence_perc_threshold,
    )
