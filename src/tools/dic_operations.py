"""Module that contains functions to make operations on dictionaries"""


def get_classified_object_id(table_other_infos: list[dict]) -> dict[str, str]:
    """Creates a dictionary that maps the data module ids
    to the other_info names associated.

    Args:
        - table_other_infos (list[dict]): The table containing
        all the data of the followed other_infos.

    Returns (dict): A dictionary that maps the data module ids
    to the other_info names associated.
    """
    dic_object_id_other_info = {}
    for dic_other_info in table_other_infos:
        other_info_name = dic_other_info["title"]
        list_object_id = dic_other_info["objectlist"]
        dic_object_id_other_info.update(
            dict(
                zip(
                    list_object_id,
                    [other_info_name for i in range(len(list_object_id))],
                )
            )
        )
    return dic_object_id_other_info
