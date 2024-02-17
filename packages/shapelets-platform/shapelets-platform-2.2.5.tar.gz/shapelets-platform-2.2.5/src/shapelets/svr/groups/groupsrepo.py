from __future__ import annotations

from typing import List, Optional, Tuple, Union

from .igroupsrepo import IGroupsRepo
from ..db import connect, Connection, transaction
from ..model import GroupAttributes, GroupField, GroupProfile, UserProfile, UserInGroup
from ..users import (
    add_to_user_group,
    user_id_for_name,
    create_temp_user,
    load_temp_user,
    modify_super_admin,
    remove_from_user_group
)

GroupLike = Union[int, GroupProfile]


def get_id(group_like: Union[int, GroupProfile]) -> int:
    if isinstance(group_like, GroupProfile):
        return group_like.uid
    return int(group_like)


def _next_id(conn: Connection) -> int:
    conn.execute("SELECT nextval('shapelets.id_gen')")
    return int(conn.fetch_one()[0])


def _insert_group(uid: int, details: GroupAttributes, conn: Connection, recreate: bool = True):
    # Use recreate flag to know if we are only updating group info
    # Note: this method is used when the group is created. Therefore, if there are new users, they will not have
    # permissions at first

    conn.execute("""
            INSERT INTO groups 
            (uid, groupName, description, provider, providerGroupId) 
            VALUES (?, ?, ?, ?, ?);
        """,
                 [uid, details.name, details.description, details.provider, details.providerGroupId])
    if details.usersInGroup and recreate:
        # Create user relation with group
        for user in details.usersInGroup:
            user_id = user_id_for_name(user, conn)
            if user_id:
                # user exists, add to group
                add_to_user_group(user_id, uid, False, False, conn)
            else:
                # add user to group with random id to keep track of permission. Once the user actually logs in, this
                # id will be replaced.
                temp_id = create_temp_user(user, conn)
                add_to_user_group(temp_id, uid, False, False, conn)


def _load_all(sort_by: Optional[List[Tuple[GroupField, bool]]],
              limit: Optional[int],
              conn: Connection) -> List[GroupProfile]:
    baseQuery = f"SELECT * FROM groups"
    if sort_by is not None:
        baseQuery += "ORDER BY "
        sortExpressions = [f"{s[0]} {'ASC' if s[1] else 'DESC'}" for s in sort_by]
        baseQuery += ', '.join(sortExpressions)
    if limit is not None:
        baseQuery += f" LIMIT {limit}"
    conn.execute(baseQuery)
    result = []
    for record in conn.fetch_all():
        result.append(GroupProfile(uid=record[0],
                                   name=record[1],
                                   description=record[2],
                                   provider=record[3],
                                   providerGroupId=record[4],
                                   usersInGroup=_load_users_in_group(record[0], conn)))
    return result


def _load_users_in_group(group_id: int, conn: Connection) -> List[str]:
    users_in_group = []
    conn.execute("""
            SELECT users_groups.userId, users.nickName, users.picture, users_groups.read_write, users_groups.admin
            FROM users_groups 
            LEFT JOIN users ON users.uid = users_groups.userId 
            WHERE groupId = ?;
            """, [group_id])
    # Load userId from users_groups and user table. If the id is not in users table, the user is not logged in yet.
    users = conn.fetch_all()
    for user in users:
        if user[1]:
            # User is logged in
            users_in_group.append(UserInGroup(uid=user[0], nickName=user[1], picture=user[2],
                                              read_write=user[3], admin=user[4]))
        else:
            conn.execute("SELECT nickName from remote_temp_users WHERE temp_id = ?", [user[0]])
            users_in_group.append(UserInGroup(uid=None, nickName=conn.fetch_one()[0], picture=None,
                                              read_write=user[3], admin=user[4]))
    return users_in_group


def _load_one(conn: Connection,
              group_id: int = None,
              group_name: str = None,
              provider_group_id: str = None) -> Optional[GroupProfile]:
    """
    Load group details using either its group id, name or provider_group_id.
    """
    if group_id is not None:
        conn.execute("SELECT * FROM groups WHERE uid = ?;", [group_id])
    elif group_name is not None:
        conn.execute("SELECT * FROM groups WHERE groupName = ?;", [group_name])
    elif provider_group_id is not None:
        conn.execute("SELECT * FROM groups WHERE providerGroupId = ?;", [provider_group_id])
    else:
        return None
    result = conn.fetch_one()
    if result is None:
        return []
    if group_id is None:
        group_id = result[0]
    users_in_group = _load_users_in_group(group_id, conn)
    users_in_other_groups = _all_users_in_groups(conn)
    nicknames_in_group = {user.nickName for user in users_in_group}
    users_not_in_group = [user for user in users_in_other_groups if user.nickName not in nicknames_in_group]
    return GroupProfile(uid=result[0],
                        name=result[1],
                        description=result[2],
                        provider=result[3],
                        providerGroupId=result[4],
                        usersInGroup=users_in_group,
                        usersNotInGroup=users_not_in_group)


def _load_all_by_user(user_id: int, conn: Connection) -> List[GroupProfile]:
    conn.execute("""
        SELECT * FROM groups
        LEFT JOIN users_groups ON users_groups.groupId = groups.uid
        WHERE users_groups.userId = ?;
    """, [user_id])
    result = []
    for record in conn.fetch_all():
        result.append(GroupProfile(uid=record[0],
                                   name=record[1],
                                   description=record[2],
                                   provider=record[3],
                                   providerGroupId=record[4],
                                   usersInGroup=_load_users_in_group(record[0], conn))
                      )
    return result


def _update_group_info(new_attributes: GroupAttributes, conn: Connection):
    conn.execute(""" 
        UPDATE groups 
        SET description = ? 
        WHERE uid = ? ;
    """, [new_attributes.description, new_attributes.uid])


def _all_users_in_groups(conn) -> List[UserInGroup]:
    """
    Return all user in the system that belong to at least one group.
    """
    conn.execute("""
    SELECT DISTINCT users_groups.userId, users.uid, users.nickName, users.picture
    FROM users_groups LEFT JOIN users ON users_groups.userId = users.uid;
    """)

    # Load userId from users_groups and user table. If the id is not in users table, the user is not logged in yet.
    users_in_group = conn.fetch_all()
    if users_in_group is None:
        return None

    users = []
    for r in users_in_group:
        if r[1] is not None:
            # user in the system
            users.append(UserInGroup(uid=r[0], nickName=r[2], picture=r[3]))
        else:
            # temp user, find nickname.
            conn.execute("SELECT  nickname from remote_temp_users where temp_id = ?;", [r[0]])
            nickname = conn.fetch_one()[0]
            users.append(UserInGroup(uid=None, nickName=nickname, picture=None))
    return users


def _delete_group_by_id(uid: int, conn: Connection):
    conn.execute("DELETE FROM groups WHERE uid = ?;", [uid])
    conn.execute("DELETE FROM users_groups WHERE groupId = ?", [uid])


def _delete_group_by_name(group_name: str, conn: Connection):
    uid = _load_one(conn, group_name=group_name).uid
    _delete_group_by_id(uid, conn)


def _clear_all_groups(conn: Connection):
    conn.execute("DELETE FROM groups WHERE provider = 'local';")


def group_has_group_name(group_name: str, conn: Connection) -> bool:
    conn.execute("SELECT 1 FROM groups where groupName = ?", [group_name])
    result = conn.fetch_one()
    return None if result is None else int(result[0]) == 1


def _update_user_group(user_id: Union[int, str], group_id: int, read_write: int, admin: int, conn: Connection):
    add_to_user_group(user_id, group_id, read_write, admin, conn)


def _create_groups_table(conn: Connection):
    conn.execute("""
        CREATE TABLE groups (
            uid INTEGER PRIMARY KEY,
            groupName VARCHAR UNIQUE NOT NULL, 
            description VARCHAR NULL,
            provider VARCHAR NULL,
            providerGroupId VARCHAR NULL
            );
    """)


def _drop_groups(conn: Connection):
    conn.execute("DROP TABLE groups;")


class GroupsRepo(IGroupsRepo):

    def __init__(self) -> None:
        pass

    def create(self, details: GroupAttributes) -> Optional[GroupProfile]:
        with transaction() as conn:
            uid = _next_id(conn)
            _insert_group(uid, details, conn)
            return _load_one(conn, group_id=uid)

    def get_group_by_remote_id(self, provider_group_id: str) -> Optional[GroupProfile]:
        """
        Return group details for the giving remote groupID
        param group_id: Group ID.
        """
        with transaction() as conn:
            return _load_one(conn, provider_group_id=provider_group_id)

    @staticmethod
    def recreate_table(users: List[UserProfile], conn: Connection):
        _drop_groups(conn)
        _create_groups_table(conn)
        for user in users:
            _insert_group(user.uid, user, conn, False)

    def update_group_info(self, new_attributes: GroupProfile):
        # Note: when modifying groups table, copy table, drop it and recreated, as if it is a table with index and
        # therefore  updates mean drop and create row, and this raise error violates primary key constraint
        # https://github.com/duckdb/duckdb/issues/4023
        with transaction() as conn:
            current_group = _load_one(conn, group_id=new_attributes.uid)
            if new_attributes.name == current_group.name:
                # If group name did not change, no need to recreate table, just update description.
                _update_group_info(new_attributes, conn)
            else:
                current_groups = _load_all(None, None, conn)
                current_groups = [group for group in current_groups if group.uid != current_group.uid]
                current_groups.append(new_attributes)
                self.recreate_table(current_groups, conn)

    def group_name_exists(self, group_name: str) -> bool:
        with connect() as conn:
            return group_has_group_name(group_name, conn)

    def delete_by_id(self, uid: int):
        with connect() as conn:
            _delete_group_by_id(uid, conn)

    def delete_by_name(self, group_name: str) -> str:

        if self.group_name_exists(group_name):
            with connect() as conn:
                _delete_group_by_name(group_name, conn)
                return 'Group %s has been deleted' % group_name
        else:
            return 'Group %s does not exist' % group_name

    def delete_all(self):
        with connect() as conn:
            _clear_all_groups(conn)

    def get_all(self,
                sort_by: Optional[List[Tuple[GroupField, bool]]] = None,
                limit: Optional[int] = None
                ) -> List[GroupProfile]:
        with connect() as conn:
            groups = _load_all(sort_by, limit, conn)
            # Eliminate the admin group to ensure it does not appear in the UI group section.
            groups = [group for group in groups if group.uid != -1]
            return groups

    def get_one(self, group_id: int = None, group_name=None) -> Optional[GroupProfile]:
        with connect() as conn:
            return _load_one(conn, group_id=group_id, group_name=group_name)

    def get_all_by_user(self, user_id: int) -> List[GroupProfile]:
        with connect() as conn:
            groups = _load_all_by_user(user_id, conn)
            # Eliminate the admin group to ensure it does not appear in the UI group section.
            groups = [group for group in groups if group.uid != -1]
            return groups

    def all_users_in_group(self, group_id: int) -> List[UserProfile]:
        with transaction() as conn:
            return _load_users_in_group(group_id, conn)

    def update_group_user_permission(self, users: List[UserInGroup], group_id) -> bool:
        # Update permissions for users
        with transaction() as conn:
            # First, retrieve the current user list to identify the ones that need removal.
            current_users_in_group = _load_users_in_group(group_id, conn)
            nicknames_in_group = [user.nickName for user in users]
            users_to_remove = [user for user in current_users_in_group if user.nickName not in nicknames_in_group]
            # Update incoming users. Could be new users or current users with new permissions.
            for user in users:
                user_id = user.uid
                if user_id is None:
                    nickname = user.nickName
                    # Check if the user already exists
                    user_id = user_id_for_name(nickname, conn)
                    if user_id is None:
                        # temp user
                        user_id = load_temp_user(nickname, conn)
                read_write = int(user.read_write) if user.read_write else 0
                admin_perm = int(user.admin) if user.admin else 0
                _update_user_group(user_id, group_id, read_write, admin_perm, conn)
                if group_id == -1:
                    # Admin Group, add superAdmin flag to user
                    modify_super_admin(user.nickName, False, conn)
            # Remove users
            for user in users_to_remove:
                user_id = user.uid
                if user_id is None:
                    # temp user
                    nickname = user.nickName
                    user_id = load_temp_user(nickname, conn)
                remove_from_user_group(user_id, group_id, conn)
                if group_id == -1:
                    # Admin Group, remove the 'superAdmin' designation for the specified user.
                    modify_super_admin(user.nickName, True, conn)

        return True

    def admin_group(self) -> GroupProfile:
        with transaction() as conn:
            return _load_one(conn, group_id=-1, group_name=None)
