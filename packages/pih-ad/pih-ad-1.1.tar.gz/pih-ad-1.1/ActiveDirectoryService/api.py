from collections import defaultdict
import pywintypes
from pyad import pyadutils
from pyad.adgroup import ADObject, ADGroup
from pyad.adcomputer import ADComputer
from pyad.adcontainer import ADContainer
from pyad.adquery import ADQuery
from pyad.aduser import ADUser
import os
from typing import Any
import win32security
from wmi import WMI, x_wmi
import pythoncom

import ipih

from pih import A
from pih.consts.errors import NotAccesable
from pih.tools import if_else, j, n, nn
from pih.collections import FullName, User
from ActiveDirectoryService.const import *


class ActiveDirectoryApi:
    DEFAULT_AD_QUERY: ADQuery = ADQuery()

    @staticmethod
    def get_printer_list(driver_name: str | None = None) -> list[dict[str, str]]:
        def printer_mapper(item):
            for field in A.CT_FC.PRINTER.ITEM.get_name_list():
                if field in [
                    A.CT_FNC.DESCRIPTION,
                    A.CT_FNC.PORT_NAME,
                ]:
                    item[field] = A.D.get_first_item(item[field])
            return item

        return A.D.map(
            printer_mapper,
            ActiveDirectoryApi.printer_list_filter_by_driver_name(
                ActiveDirectoryApi.get_shared_printer_list(), driver_name
            ),
        )

    @staticmethod
    def printer_list_filter_by_driver_name(
        printer_list: list[dict[str, str]], driver_name: str | None = None
    ) -> list[dict[str, str]]:
        return if_else(
            n(driver_name),
            printer_list,
            lambda: list(
                filter(
                    lambda item: item["driverName"].lower().find(driver_name.lower())
                    != -1,
                    printer_list,
                )
            ),
        )

    @staticmethod
    def get_shared_printer_list() -> list[dict[str, str]]:
        ad_query: ADQuery = ADQuery()
        ad_query.execute_query(
            attributes=A.CT_FC.PRINTER.ITEM.get_name_list(),
            where_clause=(f"objectCategory = 'printqueue'"),
        )
        query_result = [] if ad_query.get_row_count() == 0 else ad_query.get_results()
        result: list[dict[str, str]] = []
        for item in query_result:
            result.append(item)
        return result

    @staticmethod
    def get_computer_description_list(dn: str) -> list[dict[str, Any]]:
        property_container: ADContainer = ADContainer.from_dn(A.CT_AD.PROPERTY_WS_DN)
        property_list: list[ADGroup] = property_container.get_children(False)
        computer_property_map: dict[str, int] = defaultdict(int)
        property_item: ADGroup
        for property_item in property_list:
            property_member_list: list[ADComputer] = ADGroup.from_dn(
                property_item.dn
            ).get_members()
            ws_prpoerty: A.CT_AD.WSProperies = A.D.get(
                A.CT_AD.WSProperies, property_item.name
            )
            property_member_item: ADObject
            for property_member_item in property_member_list:
                computer_property_map[property_member_item.name] |= ws_prpoerty.value
        ad_query: ADQuery = ADQuery()
        name_field_name: str = A.CT_FNC.NAME
        description_field_name: str = A.CT_FNC.DESCRIPTION
        ad_query.execute_query(
            attributes=[name_field_name, description_field_name],
            base_dn=dn,
            where_clause="objectClass = 'computer'",
        )
        query_result: list = (
            [] if ad_query.get_row_count() == 0 else ad_query.get_results()
        )
        result: list[dict[str, Any]] = []
        for query_item in query_result:
            query_item[A.CT_FNC.PROPERTIES] = computer_property_map[
                query_item[name_field_name]
            ]
            query_item[description_field_name] = A.D.get_first_item(
                query_item[description_field_name]
            )
            query_item[A.CT_FNC.DN] = dn
            result.append(query_item)
        return result

    @staticmethod
    def get_user_existance_status_for_child_in_user_home_directory() -> (
        list[UserExistanceStatusItem]
    ):
        return ActiveDirectoryApi.get_user_existance_status_for_child_in_directory(
            A.PTH.USER.HOME_FOLDER
        )

    @staticmethod
    def get_user_login_by_workstation_name_via_wmi(value: str) -> list[str] | None:
        if A.C_R.accessibility_by_ping(value):
            pythoncom.CoInitialize()
            try:
                wmi_object: WMI = WMI(value)
                login: str | None = None
                domain: str = A.CT_AD.DOMAIN_NAME.lower()
                for computer in wmi_object.Win32_ComputerSystem():
                    login = computer.userName
                    if not A.D_C.empty(login):
                        login = login.lower()
                        domain_index: int = login.find(domain)
                        login = (
                            login[domain_index + len(domain) + 1 :]
                            if domain_index > -1
                            else login
                        )
                return [login]
            except x_wmi:
                raise NotAccesable()
            finally:
                pythoncom.CoUninitialize()
        else:
            raise NotAccesable()

    @staticmethod
    def get_user_login_by_workstation_name_via_query(
        value: str, active: bool | None = True
    ) -> list[str] | None:
        if A.C_R.accessibility_by_ping(value):
            return A.EXC.get_users_logged_on(value, active=active)
        else:
            raise NotAccesable()

    @staticmethod
    def get_user_existance_status_for_child_in_directory(
        directory: str,
    ) -> list[UserExistanceStatusItem]:
        dir_list: list[str] = os.listdir(directory)
        result: list[UserExistanceStatusItem] = []
        for dir_item in dir_list:
            login: str = dir_item.lower()
            if login.find(j((".", A.CT_AD.DOMAIN_NAME.lower()))) != -1:
                login = login.split(".")[0]
            status: UserExistanceStatus | None = None
            if ActiveDirectoryApi.user_is_exists_by_login(dir_item, True):
                status = UserExistanceStatus.EXISTS
            elif ActiveDirectoryApi.user_is_exists_by_login(dir_item, False):
                status = UserExistanceStatus.INACTIVE
            else:
                status = UserExistanceStatus.NOT_EXISTS
            result.append(UserExistanceStatusItem(login, status))
        return result

    @staticmethod
    def query_user_by_login_for_dn(login: str, dn: str) -> Any:
        return ActiveDirectoryApi.query_by(A.CT_UP.LOGIN, login, [A.CT_UP.LOGIN], dn)

    @staticmethod
    def query_user_by_name_for_dn(login: str, dn: str) -> Any:
        return ActiveDirectoryApi.query_by(A.CT_UP.NAME, login, [A.CT_UP.NAME], dn)

    @staticmethod
    def user_is_exists_by_login(login: str, active: bool | None = None) -> bool:
        def internal_user_is_exists_by_login(login: str, active: bool) -> bool:
            return nn(
                ActiveDirectoryApi.query_user_by_login_for_dn(
                    login,
                    A.CT_AD.ACTIVE_USERS_CONTAINER_DN
                    if active
                    else A.CT_AD.INACTIVE_USERS_CONTAINER_DN,
                )
            )

        if n(active):
            return internal_user_is_exists_by_login(
                login, True
            ) or internal_user_is_exists_by_login(login, False)
        return internal_user_is_exists_by_login(login, active)

    @staticmethod
    def get_user_home_directory_path(login: str) -> str:
        return A.PTH.join(A.PTH.USER.HOME_FOLDER, login)

    @staticmethod
    def get_template_users() -> list[dict]:
        return ActiveDirectoryApi.find_users_by(
            A.CT_UP.LOGIN, A.CT_AD.TEMPLATED_USER_SERACH_TEMPLATE, True
        )

    @staticmethod
    def query_by(
        search_attribute: str,
        search_value: str,
        fields: list[str],
        base_dn: str = A.CT_AD.ACTIVE_USERS_CONTAINER_DN,
        ad_query=DEFAULT_AD_QUERY,
    ) -> dict[str, Any] | None:
        if search_attribute.find("name") != -1:
            if search_value != "*":
                search_value = f"*{search_value}*"
        if search_value == "":
            search_value = "*"
        ad_query.execute_query(
            attributes=fields,
            base_dn=base_dn,
            where_clause=f"objectClass = 'user' and objectCategory = 'person' and {search_attribute} = '{search_value}'",
        )
        if ad_query.get_row_count() == 0:
            return None
        return ad_query.get_results()

    @staticmethod
    def find_by_in_dn(attribute: str, value: str, base_dn: str) -> list[dict[str, Any]]:
        fields: list[str] = A.CT_FC.AD.USER.get_name_list()
        query_result = (
            ActiveDirectoryApi.query_by(attribute, value, fields, base_dn) or []
        )
        result: list[dict] = []
        for query_item in query_result:
            result_item: dict = {}
            for field_item in fields:
                item = query_item[field_item]
                if isinstance(item, (list, tuple)):
                    item = item[0]
                result_item[field_item] = item
            result.append(result_item)
        return result

    @staticmethod
    def user_set_dn(user_dn: str, status: str, container_dn: str) -> None:
        ad_user = ADUser.from_dn(user_dn)
        if status == A.CT_AD.INACTIVE_USERS_CONTAINER_DN:
            ad_user.disable()
        else:
            ad_user.enable()
        try:
            ad_user.move(ADContainer(container_dn))
        except:
            pass

    @staticmethod
    def user_set_password(user_dn: str, password: str) -> None:
        ADUser.from_dn(user_dn).set_password(password)

    @staticmethod
    def user_set_telephone_number(user_dn: str, telephone: str) -> None:
        ADUser.from_dn(user_dn).update_attribute(A.CT_UP.TELEPHONE_NUMBER, telephone)

    @staticmethod
    def user_move(user_dn: str, container_dn: str) -> None:
        user = ADUser.from_dn(user_dn)
        try:
            user.move(ADContainer(container_dn))
        except:
            pass

    @staticmethod
    def get_containers(
        root_dn: str = A.CT_AD.ACTIVE_USERS_CONTAINER_DN,
    ) -> list[dict[str, str]]:
        child_list = ADContainer.from_dn(root_dn).get_children(True)
        result: list = []
        container: ADContainer
        for container in child_list:
            if container.type == "organizationalUnit":
                result.append(
                    {
                        A.CT_UP.NAME: A.D_F.location_list(container.dn, False)[-1],
                        A.CT_UP.DESCRIPTION: A.D.get_first_item(
                            container.get_attribute(A.CT_UP.DESCRIPTION), ""
                        ),
                        A.CT_UP.DN: container.dn,
                    }
                )
        return result

    @staticmethod
    def filter_users(list: list[User], active: bool) -> list[User]:
        return A.D_FL.users_by_dn(
            list,
            A.CT_AD.ACTIVE_USERS_CONTAINER_DN
            if active
            else A.CT_AD.INACTIVE_USERS_CONTAINER_DN,
        )

    @staticmethod
    def find_users_by(attribute: str, value: str, active: bool | None = None) -> list:
        def internal_find_users_by(attribute: str, value: str, active: bool) -> list:
            return ActiveDirectoryApi.find_by_in_dn(
                attribute,
                value,
                A.CT_AD.ACTIVE_USERS_CONTAINER_DN
                if active
                else A.CT_AD.INACTIVE_USERS_CONTAINER_DN,
            )

        if n(active):
            return internal_find_users_by(
                attribute, value, True
            ) + internal_find_users_by(attribute, value, False)
        return internal_find_users_by(attribute, value, active)

    @staticmethod
    def by_group_name_in_container(group_name: str, container_dn: str) -> list[ADGroup]:
        group_name = group_name.lower()
        container: ADContainer = ADContainer.from_dn(container_dn)
        result: list[ADGroup] = []
        container_children = container.get_children(True)
        group_object: ADGroup
        for group_object in container_children:
            name: str = str(group_object.get_attribute(A.CT_UP.NAME)[0]).lower()
            if name == group_name:
                distinguished_name = group_object.dn
                user_list: list[ADUser] = ADGroup.from_dn(
                    distinguished_name
                ).get_members()
                user: ADUser
                for user in user_list:
                    result += ActiveDirectoryApi.find_users_by(A.CT_UP.DN, user.dn)
                break
        return result

    class UserContainer(ADObject):
        def __create_user_object(self, name):
            type: str = "user"
            prefix = "ou" if type == "organizationalUnit" else "cn"
            prefixed_name = j((prefix, name), "=")
            return self._ldap_adsi_obj.Create(type, prefixed_name)

        def create_user(
            self, login, name, password, upn_suffix, optional_attributes={}
        ):
            try:
                upn = j((login, upn_suffix), A.CT.EMAIL.SPLITTER)
                obj = self.__create_user_object(name)
                obj.Put(
                    "sAMAccountName", optional_attributes.get("sAMAccountName", login)
                )
                obj.Put("userPrincipalName", upn)
                obj.SetInfo()
                pyadobj = ADUser.from_com_object(obj)
                pyadobj.enable()
                pyadobj.set_password(password)
                pyadobj.update_attributes(optional_attributes)
                return pyadobj
            except pywintypes.com_error as e:
                pyadutils.pass_up_com_exception(e)

    class ACTION:
        @staticmethod
        def create_user_from_template(
            templated_user_dn: str,
            full_name: FullName,
            login: str,
            password: str,
            description: str,
            telephone: str,
            email: str,
        ) -> bool:
            templated_user = ADUser.from_dn(templated_user_dn)
            group_list = templated_user.get_memberOfs(True)
            result_group_list = {}
            for group in group_list:
                if group.dn not in result_group_list:
                    result_group_list[group.dn] = group
            user_container: ActiveDirectoryApi.UserContainer = (
                ActiveDirectoryApi.UserContainer.from_dn(
                    A.D_Ex.container_dn_from_dn(templated_user_dn)
                )
            )
            name = A.D.fullname_to_string(full_name)
            new_user: ADUser = user_container.create_user(
                login,
                name,
                password,
                A.CT_AD.DOMAIN_MAIN,
                optional_attributes={
                    "givenName": A.D.to_given_name(full_name),
                    "sn": full_name.last_name,
                    "userPrincipalName": A.D_F.user_principal_name(login),
                    "homeDirectory": A.PTH.adapt_for_windows(
                        j((A.PTH_U.HOME_FOLDER_FULL, login), "\\")
                    ),
                    "displayName": name,
                    "homeDrive": A.CT_AD.USER_HOME_FOLDER_DISK,
                    "mail": email,
                    "description": description,
                    "telephonenumber": telephone,
                },
            )
            new_user.set_user_account_control_setting("PASSWD_NOTREQD", False)
            new_user.set_user_account_control_setting("DONT_EXPIRE_PASSWD", True)
            for item in result_group_list:
                new_user.add_to_group(result_group_list[item])

            return True

        @staticmethod
        def authenticate(login: str, password: str) -> bool:
            try:
                win32security.LogonUser(
                    login,
                    A.CT_AD.DOMAIN_NAME,
                    password,
                    win32security.LOGON32_LOGON_NETWORK,
                    win32security.LOGON32_PROVIDER_DEFAULT,
                )
                return True
            except win32security.error as _:
                return False

        @staticmethod
        def user_remove(user_dn: str) -> bool:
            try:
                ADUser.from_dn(user_dn).delete()
                return True
            except:
                return False

        @staticmethod
        def create_user_in_container(
            container_dn: str,
            full_name: FullName,
            login: str,
            password: str,
            description: str,
            telephone: str,
            email: str,
        ) -> bool:
            return True

        @staticmethod
        def user_set_telephone_number(user_dn: str, telephone: str) -> bool:
            ActiveDirectoryApi.user_set_telephone_number(user_dn, telephone)
            return True

        @staticmethod
        def user_set_password(user_dn: str, password: str) -> bool:
            ActiveDirectoryApi.user_set_password(user_dn, password)
            return True

        @staticmethod
        def user_move(user_dn: str, container_dn: str) -> bool:
            ActiveDirectoryApi.user_move(user_dn, container_dn)
            return True

        @staticmethod
        def user_set_status(user_dn: str, status: str, container_dn: str) -> bool:
            ActiveDirectoryApi.user_set_dn(user_dn, status, container_dn)
            return True
