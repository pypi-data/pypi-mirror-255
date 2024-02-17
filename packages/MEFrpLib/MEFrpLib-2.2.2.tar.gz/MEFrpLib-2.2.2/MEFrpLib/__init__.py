# -*- coding:utf-8 -*-
"""
MEFrpLib is a Python module that helps developers use MEFrp API easily.
YOU ARE NOT ALLOWED TO USE THIS MODULE TO DO THINGS THAT VIOLATE MEFRP'S TERMS OF USE.
Copyright (c) 2024 LxHTT
"""
from .auth import (
    me_get_user_info,  # noqa
    me_user_get_sign_info,  # noqa
    me_user_sign,  # noqa
    me_refresh_user_token,  # noqa
    me_get_realname_status,  # noqa
    me_post_realname,  # noqa
    me_get_tunnel_list,  # noqa
    me_get_tunnel_config_node,  # noqa
    me_get_tunnel_config_id,  # noqa
    me_create_tunnel,  # noqa
    me_edit_tunnel,  # noqa
    me_close_tunnel,  # noqa
    me_delete_tunnel,  # noqa
    me_get_tunnel_info,  # noqa
    me_node_list,  # noqa
    me_get_free_port,  # noqa
    me_reset_password,  # noqa
)
from .public import (
    me_login,  # noqa
    me_get_sponsor,  # noqa
    me_get_statistics,  # noqa
    me_register,  # noqa
    me_send_register_email,  # noqa
    me_forgot_password,  # noqa
    me_get_setting,  # noqa
)

__version__ = "2.2.2"
