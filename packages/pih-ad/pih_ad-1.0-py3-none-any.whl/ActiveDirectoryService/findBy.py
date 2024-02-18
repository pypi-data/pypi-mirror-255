from sys import argv
from typing import List
from api import ActiveDirectoryApi
from pih.collections import Result, User
from pih.const import USER_PROPERTIES
from pih.pih import PIH

#init version


def get_result(search_attribute: str, search_value: str) -> Result[List[User]]:
    if search_attribute == USER_PROPERTIES.LOGIN:
        result = PIH.RESULT.USER.by_login(search_value)
    else:
        result = PIH.RESULT.USER.by_name(search_value)
    return result


if __name__ == "__main__":
    argv_len = len(argv)
    run_once: bool = argv_len > 2
    search_attribute: str = ""
    search_value: str = ""
    if argv_len == 2:
        search_attribute = argv[1]
    elif run_once: 
        search_value = argv[2]
    if not PIH.CHECK.USER.search_attribute(search_attribute):
        search_attribute = PIH.input.user.search_attribute()
    try:
        if not run_once:
            search_value = PIH.input.user.search_value(search_attribute)
        data = get_result(search_attribute, search_value)
        if run_once:
            pass
            #AD.DATA.represent(data)
        else:
            ActiveDirectoryApi.VISUAL.all_result(data)
    except KeyboardInterrupt:
        pass