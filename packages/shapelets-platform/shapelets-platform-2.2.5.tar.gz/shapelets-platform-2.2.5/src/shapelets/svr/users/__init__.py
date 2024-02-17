from rodi import Container

from .iusersrepo import IUsersRepo
from .iusersservice import IUsersService, UserDoesNotBelong, WritePermission
from .usershttp import UsersHttpProxy, UsersHttpServer
from .usersrepo import (
    add_to_user_group,
    create_temp_user,
    load_temp_user,
    modify_super_admin,
    remove_from_user_group,
    user_id_for_name,
    UsersRepo)
from .usersservice import UsersService
from .user_identity import check_user_identity, super_admin


def setup_remote_client(container: Container):
    container.add_singleton(IUsersService, UsersHttpProxy)


def setup_services(container: Container):
    container.add_singleton(IUsersRepo, UsersRepo)
    container.add_singleton(IUsersService, UsersService)


__all__ = [
    'setup_remote_client', 'setup_services', 'check_user_identity', 'super_admin',
    'IUsersRepo', 'IUsersService', 'UsersHttpServer', 'modify_super_admin',
    'UserDoesNotBelong', 'WritePermission', 'remove_from_user_group',
    'add_to_user_group', 'user_id_for_name', 'create_temp_user', 'load_temp_user'
]
