import ipih

from pih import A, PIHThread, PIHThreadPoolExecutor
from ActiveDirectoryService.const import SD

# version 0.3

ISOLATED = False

SR = A.CT_SR
SC = A.CT_SC

from typing import Any
from pih.collections import FullName, Result
from pih.tools import ParameterList, e, n, ne, while_excepted, one


class DH:
    computer_cache: dict[str, dict[str, Any]] = {}
    computer_description_list: list[dict[str, Any]] = []
    computer_lock: bool = False
    user_cache: dict[str, dict[str, Any]] = {}
    user_lock: bool = False


def start(as_standalone: bool = False) -> None:

    if A.U.for_service(SD, ["pyad", "pywin32", "wmi"]):

        from concurrent.futures import as_completed
        from pih.consts.errors import NotAccesable
        from pih.rpc import RPC

        import pythoncom
        from ActiveDirectoryService.api import ActiveDirectoryApi as Api

        def service_call_handler(sc: SC, pl: ParameterList) -> Any:
            with A.ER.detect(pythoncom.CoUninitialize):
                pythoncom.CoInitialize()
                if sc == SC.heart_beat:
                    if (
                        RPC.SESSION.life_time.seconds % A.CT.CACHE.TTL.WORKSTATIONS
                    ) == 0:
                        update_computer_cache()
                        return
                    if (RPC.SESSION.life_time.seconds % A.CT.CACHE.TTL.USERS) == 0:
                        update_users_cache()
                        return
                if sc == SC.drop_user_cache:
                    update_users_cache()
                    return
                if sc == SC.drop_workstaion_cache:
                    update_computer_cache()
                    return
                if sc == SC.check_user_exists_by_login:
                    return Api.user_is_exists_by_login(pl.next(), pl.next())
                if sc == SC.get_user_by_full_name:
                    return get_user_by_attribute(
                        A.CT_FNC.SEARCH_ATTRIBUTE_NAME,
                        A.D.fullname_to_string(pl.next(FullName())),
                        pl.next(),
                    )
                if sc == SC.get_users_by_name:
                    value: str = pl.next()
                    value = value.lower()
                    active: bool | None = pl.next()
                    cached: bool | None = pl.next()
                    cached = A.D.check_not_none(cached, cached, A.S_U.use_cache())
                    if cached:
                        return create_user_result(
                            A.D.filter(
                                lambda item: isinstance(item, dict)
                                and item[A.CT_FNC.SEARCH_ATTRIBUTE_NAME]
                                .lower()
                                .find(value)
                                != -1,
                                A.D.as_list(DH.user_cache),
                            )
                        )
                    return get_user_by_attribute(
                        A.CT_FNC.SEARCH_ATTRIBUTE_NAME, value, active
                    )
                if sc == SC.get_user_by_login:
                    value: str = pl.next()
                    value = value.lower()
                    active: bool | None = pl.next()
                    cached: bool | None = pl.next()
                    cached = A.D.check_not_none(cached, cached, A.S_U.use_cache())
                    if not cached or value not in DH.user_cache:
                        fetch_user_by_login(value, active)
                    return create_user_result(DH.user_cache[value])
                if sc == SC.get_user_by_telephone_number:
                    return get_user_by_attribute(
                        A.CT_FNC.TELEPHONE_NUMBER,
                        pl.next(),
                        pl.next(),
                    )
                if sc == SC.get_template_users:
                    return Result(
                        A.CT_FC.AD.TEMPLATED_USER,
                        Api.get_template_users(),
                    )
                if sc == SC.create_user_by_template:
                    templated_user_dn: str = pl.next()
                    full_name: FullName = pl.next(FullName())
                    login: str = pl.next()
                    password: str = pl.next()
                    description: str = pl.next()
                    telephone: str = pl.next()
                    email: str = pl.next()
                    result: bool = Api.ACTION.create_user_from_template(
                        templated_user_dn,
                        full_name,
                        login,
                        password,
                        description,
                        telephone,
                        email,
                    )
                    update_users_cache()
                    return result
                if sc == SC.set_user_telephone_number:
                    return Api.ACTION.user_set_telephone_number(pl.next(), pl.next())
                if sc == SC.authenticate:
                    return Api.ACTION.authenticate(pl.next(), pl.next())
                if sc == SC.set_user_password:
                    return Api.ACTION.user_set_password(pl.next(), pl.next())
                if sc == SC.set_user_status:
                    return Api.ACTION.user_set_status(
                        pl.next(),
                        pl.next(),
                        pl.next(),
                    )
                if sc == SC.get_containers:
                    return Result(A.CT_FC.AD.CONTAINER, Api.get_containers())
                if sc == SC.get_printer_list:
                    return Result(A.CT_FC.PRINTER.ITEM, Api.get_printer_list())
                target_sc_list: list[SC] = [
                    SC.get_user_list_by_job_position,
                    SC.get_user_list_by_group,
                    SC.get_user_list_by_property,
                ]
                sc_index: int = target_sc_list.index(sc) if sc in target_sc_list else -1
                if sc_index != -1:
                    value: str = pl.next()
                    return create_user_result(
                        while_excepted(
                            lambda: Api.by_group_name_in_container(
                                value,
                                [
                                    A.CT_AD.JOB_POSITION_CONTAINER_DN,
                                    A.CT_AD.GROUP_CONTAINER_DN,
                                    A.CT_AD.PROPERTY_USER_DN,
                                ][sc_index],
                            )
                        )
                    )
                if sc == SC.remove_user:
                    return Api.ACTION.user_remove(pl.next())
                if sc == SC.get_computer_list:
                    container_dn: str = pl.next()
                    return A.R.pack(
                        (
                            A.CT_FCA.WORKSTATION
                            if container_dn == A.CT_AD.WORKSTATIONS_CONTAINER_DN
                            else A.CT_FCA.SERVER
                        ),
                        get_computer_list_by_container_dn(container_dn),
                    )
                if sc == SC.get_computer_description_list:
                    return A.R.pack(
                        A.CT_FCA.COMPUTER_DESCRIPTION,
                        get_computer_discription_list_by_container_dn(pl.next()),
                    )
                if sc == SC.get_workstation_list_by_user_login:
                    login: str = pl.next()
                    login = login.lower()
                    return A.R.pack(
                        A.CT_FCA.WORKSTATION,
                        A.D.filter(
                            lambda item: (
                                login in item[A.CT_FNC.ACTIVE_USERS_LOGIN]
                                if A.D.if_is_in(item, A.CT_FNC.ACTIVE_USERS_LOGIN)
                                else False
                            ),
                            get_computer_list_by_container_dn(
                                A.CT_AD.WORKSTATIONS_CONTAINER_DN
                            ),
                        ),
                    )
                if sc == SC.get_user_by_workstation:
                    name: str = pl.next()
                    return A.R.pack(
                        A.CT_FC.AD.USER,
                        A.D.filter(
                            lambda item: str(item[A.CT_FNC.NAME]).lower() == name,
                            get_computer_list_by_container_dn(),
                        ),
                    )

        def get_computer_list_by_container_dn(value: str | None = None) -> dict:
            computer_cache: dict[str, dict[str, Any]] = DH.computer_cache
            if e(computer_cache):
                update_computer_cache()
            return A.D.filter(
                lambda item: True if n(value) else item[A.CT_FNC.DN] == value,
                [computer_cache[computer_name] for computer_name in computer_cache],
            )

        def get_computer_discription_list_by_container_dn(
            value: str | None = None,
        ) -> dict[str, dict[str, Any]]:
            computer_description_list: list[dict[str, Any]] = (
                DH.computer_description_list
            )
            if e(computer_description_list):
                update_computer_cache()
            return A.D.filter(
                lambda item: True if n(value) else item[A.CT_FNC.DN] == value,
                computer_description_list,
            )

        def create_user_result(data: Any) -> Result:
            return Result(A.CT_FC.AD.USER, data)

        def update_computer_cache() -> None:
            if not DH.computer_lock:
                DH.computer_lock = True
                with A.ER.detect():
                    DH.computer_description_list: list[dict] = (
                        Api.get_computer_description_list(
                            A.CT_AD.WORKSTATIONS_CONTAINER_DN
                        )
                        + Api.get_computer_description_list(
                            A.CT_AD.SERVERS_CONTAINER_DN
                        )
                    )
                    computer_cache: dict[str, dict[str, Any]] = {}
                    with PIHThreadPoolExecutor(
                        max_workers=len(DH.computer_description_list)
                    ) as executor:
                        future_to_computer = {
                            executor.submit(
                                A.ER.wrap(
                                    Api.get_user_login_by_workstation_name_via_query
                                ),
                                computer_description_item[A.CT_FNC.NAME],
                                active=True,
                            ): computer_description_item
                            for computer_description_item in DH.computer_description_list
                        }
                        for future_computer in as_completed(future_to_computer):
                            computer: dict[str, Any] = future_to_computer[
                                future_computer
                            ]
                            computer_name: str = computer[A.CT_FNC.NAME].lower()
                            computer_cache[computer_name] = computer
                            with A.ER.detect():
                                exception: BaseException | None = (
                                    future_computer.exception()
                                )
                                if e(exception):
                                    computer[A.CT_FNC.ACCESSABLE] = True
                                    login_list: list[str] = future_computer.result()
                                    computer[A.CT_FNC.ACTIVE_USERS_LOGIN] = login_list
                                    if ne(login_list):
                                        computer[A.CT_FNC.LOGIN] = login_list[0]
                                else:
                                    if isinstance(exception, NotAccesable):
                                        computer[A.CT_FNC.ACCESSABLE] = False
                                        computer[A.CT_FNC.ACTIVE_USERS_LOGIN] = None
                DH.computer_cache = computer_cache
                DH.computer_lock = False

        def get_user_by_attribute(
            attribute: str,
            value: str,
            active: bool | None = None,
            result_return: bool = True,
        ) -> (
            Result[list[dict[str, Any]] | dict[str, Any]]
            | list[dict[str, Any]]
            | dict[str, Any]
        ):
            data: dict[str, Any] = while_excepted(
                lambda: Api.find_users_by(attribute, value, active)
            )
            return create_user_result(data) if result_return else data

        def fetch_user_by_login(value: str | None, active: bool | None = None) -> None:
            if not DH.user_lock:
                with A.ER.detect():
                    DH.user_lock = True

                    class LDH:
                        user_cache: dict[str, dict[str, Any]] = {}

                    while True:
                        with A.ER.detect():
                            result: list[dict[str, Any]] = get_user_by_attribute(
                                A.CT_FNC.SEARCH_ATTRIBUTE_LOGIN,
                                value or A.CT_AD.SEARCH_ALL_PATTERN,
                                active,
                                False,
                            )

                            def every_action(user_data: dict[str, Any]) -> None:
                                LDH.user_cache |= {
                                    user_data[A.CT_UP.LOGIN].lower(): user_data
                                }

                            A.D.every(every_action, result)
                            break
                    if n(value):
                        DH.user_cache = LDH.user_cache
                    else:
                        DH.user_cache[value] = (lambda item: item, one)[
                            len(LDH.user_cache) == 1
                        ](A.D.as_list(LDH.user_cache))
                DH.user_lock = False

        def update_users_cache() -> None:
            fetch_user_by_login(None)

        def service_starts_handler() -> None:
            A.SRV_A.subscribe_on(SC.heart_beat, name="User computer update")
            DH.computer_lock = False
            DH.user_lock = False

            def start_action() -> None:
                pythoncom.CoInitialize()
                update_users_cache()
                update_computer_cache()
                pythoncom.CoUninitialize()

            PIHThread(start_action)

        A.SRV_A.serve(
            SD,
            service_call_handler,
            service_starts_handler,
            isolate=ISOLATED,
            as_standalone=as_standalone,
        )


if __name__ == "__main__":
    start()
