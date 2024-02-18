import win32security
import ntsecuritycon as con
from api import ActiveDirectoryApi, UserExistanceStatus
import colorama
from colorama import Back, Style


def apply_acl_for_user_home_directory(user_login: str):
    user_path = ActiveDirectoryApi.get_user_home_directory_path(user_login)
    user, domain, type = win32security.LookupAccountName("", user_login)
    sd = win32security.GetFileSecurity(
        user_path, win32security.DACL_SECURITY_INFORMATION)
    admins, domain, type = win32security.LookupAccountName(
        "", "Администраторы")
    dacl = win32security.ACL()
    #con.FILE_GENERIC_READ | con.FILE_GENERIC_WRITE
    #dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, admins)
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION, 3, con.FILE_ALL_ACCESS, user)
    dacl.AddAccessAllowedAceEx(
        win32security.ACL_REVISION, 3, con.FILE_ALL_ACCESS, admins)
    sd.SetSecurityDescriptorDacl(1, dacl, 0)
    win32security.SetFileSecurity(
        user_path, win32security.DACL_SECURITY_INFORMATION, sd)


def main():
    user_exsistance_status_list = ActiveDirectoryApi.get_user_exsistance_status_for_child_in_user_home_directory()
    for item in user_exsistance_status_list:
        status = item.status
        login = item.login
        if status == UserExistanceStatus.EXISTS:
            apply_acl_for_user_home_directory(login)
            print(
                f"{Back.GREEN}User \"{login}\" was found!{Style.RESET_ALL}")
        elif status == UserExistanceStatus.DEADDLIST:
            print(
                f"{Back.RED}User with given login \"{login}\" is in deadlist!{Style.RESET_ALL}")
        elif status == UserExistanceStatus.NOT_EXISTS:
            print(
                f"{Back.RED}User with given login \"{login}\" not found!{Style.RESET_ALL}")


if __name__ == "__main__":
    colorama.init()
    main()