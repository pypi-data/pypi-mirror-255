from api import ActiveDirectoryApi
from pih.const import FIELD_NAME_COLLECTION, USER_PROPERTIES
from pih.collections import User
from ActiveDirectoryService.api import ActiveDirectoryApi as Api
import time
import os

print(Api.get_user_login_by_workstation_name("ws-240"))
