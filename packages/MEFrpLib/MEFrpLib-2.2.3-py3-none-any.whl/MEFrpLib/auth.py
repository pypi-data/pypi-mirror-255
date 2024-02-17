from .models import JSONReturnModel, AuthRequestModel, TextReturnModel, APIRouter

AuthRouter = APIRouter.AuthRouter


def me_get_user_info(
    authorization: str,
    bypass_proxy: bool = False,
    ua: str = "MEFrpLib/Not Modified Version",
) -> JSONReturnModel:
    return AuthRequestModel(
        url=AuthRouter.user_info.apiPath(),
        method="GET",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        authorization=authorization,
        ua=ua,
    ).run()


def me_user_get_sign_info(
    authorization: str,
    bypass_proxy: bool = False,
    ua: str = "MEFrpLib/Not Modified Version",
) -> JSONReturnModel:
    return AuthRequestModel(
        url=AuthRouter.user_sign.apiPath(),
        method="GET",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        authorization=authorization,
        ua=ua,
    ).run()


def me_user_sign(
    authorization: str,
    bypass_proxy: bool = False,
    ua: str = "MEFrpLib/Not Modified Version",
) -> JSONReturnModel:
    return AuthRequestModel(
        url=AuthRouter.user_sign.apiPath(),
        method="POST",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        authorization=authorization,
        ua=ua,
    ).run()


def me_refresh_user_token(
    authorization: str,
    bypass_proxy: bool = False,
    ua: str = "MEFrpLib/Not Modified Version",
) -> JSONReturnModel:
    return AuthRequestModel(
        url=AuthRouter.refresh_token.apiPath(),
        method="POST",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        authorization=authorization,
        ua=ua,
    ).run()


def me_get_realname_status(
    authorization: str,
    bypass_proxy: bool = False,
    ua: str = "MEFrpLib/Not Modified Version",
) -> JSONReturnModel:
    return AuthRequestModel(
        url=AuthRouter.realname_get.apiPath(),
        method="GET",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        authorization=authorization,
        ua=ua,
    ).run()


def me_post_realname(
    authorization: str,
    idcard: str,
    name: str,
    bypass_proxy: bool = False,
    ua: str = "MEFrpLib/Not Modified Version",
) -> JSONReturnModel:
    return AuthRequestModel(
        data={"idcard": idcard, "name": name},
        url=AuthRouter.realname_post.apiPath(),
        method="POST",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        authorization=authorization,
        ua=ua,
    ).run()


def me_get_tunnel_list(
    authorization: str,
    bypass_proxy: bool = False,
    ua: str = "MEFrpLib/Not Modified Version",
) -> JSONReturnModel:
    return AuthRequestModel(
        url=AuthRouter.tunnel_list.apiPath(),
        method="GET",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        authorization=authorization,
        ua=ua,
    ).run()


def me_get_tunnel_config_node(
    authorization: str,
    node: int,
    bypass_proxy: bool = False,
    ua: str = "MEFrpLib/Not Modified Version",
) -> JSONReturnModel:
    return AuthRequestModel(
        url=AuthRouter.tunnel_conf_node.apiPath().format(node),
        method="GET",
        bypass_proxy=bypass_proxy,
        model=TextReturnModel,
        authorization=authorization,
        ua=ua,
    ).run()


def me_get_tunnel_config_id(
    authorization: str,
    id: int,
    bypass_proxy: bool = False,
    ua: str = "MEFrpLib/Not Modified Version",
) -> JSONReturnModel:
    return AuthRequestModel(
        url=AuthRouter.tunnel_conf_id.apiPath().format(id),
        method="GET",
        bypass_proxy=bypass_proxy,
        model=TextReturnModel,
        authorization=authorization,
        ua=ua,
    ).run()


def me_create_tunnel(
    authorization: str,
    node: int,
    proxy_type: str,
    local_ip: str,
    local_port: int,
    remote_port: int,
    proxy_name: str,
    bypass_proxy: bool = False,
    domain: str = "",
    ua: str = "MEFrpLib/Not Modified Version",
) -> JSONReturnModel:
    if "http" not in proxy_type:
        return AuthRequestModel(
            data={
                "node": node,
                "proxy_type": proxy_type,
                "local_ip": local_ip,
                "local_port": local_port,
                "remote_port": remote_port,
                "proxy_name": proxy_name,
            },
            url=AuthRouter.tunnel_create.apiPath(),
            method="POST",
            bypass_proxy=bypass_proxy,
            model=JSONReturnModel,
            authorization=authorization,
            ua=ua,
        ).run()
    else:
        return AuthRequestModel(
            data={
                "node": node,
                "proxy_type": proxy_type,
                "local_ip": local_ip,
                "local_port": local_port,
                "proxy_name": proxy_name,
                "domain": domain,
            },
            url=AuthRouter.tunnel_create.apiPath(),
            method="POST",
            bypass_proxy=bypass_proxy,
            model=JSONReturnModel,
            authorization=authorization,
            ua=ua,
        ).run()


def me_edit_tunnel(
    authorization: str,
    tunnel_id: int,
    tunnel_name: str,
    local_port: int,
    local_ip: str,
    bypass_proxy: bool = False,
    ua: str = "MEFrpLib/Not Modified Version",
):
    return AuthRequestModel(
        data={
            "tunnel_id": tunnel_id,
            "tunnel_name": tunnel_name,
            "local_port": local_port,
            "local_ip": local_ip,
        },
        url=AuthRouter.edit_tunnel.apiPath(),
        method="POST",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        authorization=authorization,
        ua=ua,
    )


def me_close_tunnel(
    authorization: str,
    tunnel_id: int,
    bypass_proxy: bool = False,
    ua: str = "MEFrpLib/Not Modified Version",
) -> JSONReturnModel:
    return AuthRequestModel(
        data={},
        url=AuthRouter.tunnel_close.apiPath().format(tunnel_id),
        method="POST",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        authorization=authorization,
        ua=ua,
    )


def me_delete_tunnel(
    authorization: str,
    tunnel_id: int,
    bypass_proxy: bool = False,
    ua: str = "MEFrpLib/Not Modified Version",
) -> JSONReturnModel:
    return AuthRequestModel(
        url=AuthRouter.tunnel_delete.apiPath().format(tunnel_id),
        method="POST",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        authorization=authorization,
        ua=ua,
    ).run()


def me_get_tunnel_info(
    authorization: str,
    tunnel_id: int,
    bypass_proxy: bool = False,
    ua: str = "MEFrpLib/Not Modified Version",
) -> JSONReturnModel:
    return AuthRequestModel(
        url=AuthRouter.tunnel_info.apiPath().format(tunnel_id),
        method="GET",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        authorization=authorization,
        ua=ua,
    ).run()


def me_node_list(
    authorization: str,
    bypass_proxy: bool = False,
    ua: str = "MEFrpLib/Not Modified Version",
) -> JSONReturnModel:
    return AuthRequestModel(
        url=AuthRouter.node_list.apiPath(),
        method="GET",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        authorization=authorization,
        ua=ua,
    ).run()


def me_get_free_port(
    authorization: str,
    id: int,
    protocol: str,
    bypass_proxy: bool = False,
    ua: str = "MEFrpLib/Not Modified Version",
) -> JSONReturnModel:
    return AuthRequestModel(
        url=AuthRouter.get_free_port.apiPath().format(id=id, protocol=protocol),
        method="GET",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        authorization=authorization,
        ua=ua,
    ).run()


def me_reset_password(
    authorization: str,
    old_password: str,
    password: str,
    bypass_proxy: bool = False,
    ua: str = "MEFrpLib/Not Modified Version",
) -> JSONReturnModel:
    return AuthRequestModel(
        data={"oldpassword": old_password, "password": password},
        url=AuthRouter.reset_password.apiPath(),
        method="POST",
        bypass_proxy=bypass_proxy,
        model=JSONReturnModel,
        authorization=authorization,
        ua=ua,
    ).run()
