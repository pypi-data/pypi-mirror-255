from .models import JSONReturnModel, BaseRequestModel, APIRouter

PublicRouter = APIRouter.PublicRouter


def me_login(username: str, password: str, bypass_proxy: bool = False, ua: str = "MEFrpLib/Not Modified Version"):
    return BaseRequestModel(
        data={"username": username, "password": password},
        url=PublicRouter.login.apiPath(),
        method="POST",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        ua=ua,
    ).run()


def me_get_sponsor(bypass_proxy: bool = False, ua: str = "MEFrpLib/Not Modified Version") -> JSONReturnModel:
    return BaseRequestModel(
        data={},
        url=PublicRouter.sponsor.apiPath(),
        method="GET",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        ua=ua,
    ).run()


def me_get_statistics(bypass_proxy: bool = False, ua: str = "MEFrpLib/Not Modified Version") -> JSONReturnModel:
    return BaseRequestModel(
        data={},
        url=PublicRouter.statistics.apiPath(),
        method="GET",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        ua=ua,
    ).run()


def me_register(
    email: str, username: str, password: str, code: int, bypass_proxy: bool = False, ua: str = "MEFrpLib/Not Modified Version"
):
    return BaseRequestModel(
        data={"email": email, "username": username, "password": password, "code": code},
        url=PublicRouter.register.apiPath(),
        method="POST",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        ua=ua,
    ).run()


def me_send_register_email(email: str, bypass_proxy: bool = False, ua: str = "MEFrpLib/Not Modified Version") -> JSONReturnModel:
    return BaseRequestModel(
        data={"email": email},
        url=PublicRouter.register_email.apiPath(),
        method="POST",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        ua=ua,
    ).run()


def me_forgot_password(email: str, username: str, bypass_proxy: bool = False, ua: str = "MEFrpLib/Not Modified Version"):
    return BaseRequestModel(
        data={"email": email, "username": username},
        url=PublicRouter.forgot_password.apiPath(),
        method="POST",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        ua=ua,
    ).run()


def me_get_setting(bypass_proxy: bool = False, ua: str = "MEFrpLib/Not Modified Version") -> JSONReturnModel:
    return BaseRequestModel(
        data={},
        url=PublicRouter.setting.apiPath(),
        method="GET",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        ua=ua,
    ).run()
