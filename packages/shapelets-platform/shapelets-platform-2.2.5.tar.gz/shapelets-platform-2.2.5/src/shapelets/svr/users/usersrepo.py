from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .iusersrepo import IUsersRepo
from ..db import connect, Connection, transaction
from ..model import PrincipalId, ResolvedPrincipalId, SuperUserProfile, UserAttributes, UserField, UserId, UserProfile


def _next_id(conn: Connection) -> int:
    conn.execute("SELECT nextval('shapelets.id_gen')")
    return int(conn.fetch_one()[0])


def _update_user_by_id(uid: UserId, profile: Dict[str, Any], conn: Connection):
    keys = list(profile.keys())
    query = "UPDATE users SET "
    query += ("=?, ".join(keys) + "=? ")
    query += f"WHERE uid = ?;"
    conn.execute(query, [profile[k] for k in keys] + [uid])


def _load_all(conn: Connection) -> List[Union[UserProfile, SuperUserProfile]]:
    base_query = f"SELECT * FROM users"
    conn.execute(base_query)
    records = conn.fetch_all()

    base_query = f"SELECT uid, nickName, email, firstName, familyName, locale, picture, bio, location, url, superAdmin FROM users"
    conn.execute(base_query)
    records = conn.fetch_all()
    users = []
    for record in records:
        super_admin = record[10]
        if super_admin is not None and super_admin == 1:
            # SuperAdmin User
            user = SuperUserProfile(uid=record[0], nickName=record[1], email=record[2], firstName=record[3],
                                    familyName=record[4], locale=record[5], picture=record[6],
                                    bio=record[7], location=record[8], url=record[9], superAdmin=super_admin)
        else:
            # Regular User
            user = UserProfile(uid=record[0], nickName=record[1], email=record[2], firstName=record[3],
                               familyName=record[4], locale=record[5], picture=record[6],
                               bio=record[7], location=record[8], url=record[9])
        users.append(user)
    return users


def _get_user_id(user_name: str, conn: Connection):
    conn.execute(""" 
        SELECT uid
        FROM users
        WHERE nickName = ?;
    """, [user_name])

    record = conn.fetch_one()
    if record is None:
        raise ValueError(f"User {user_name} not found")
    return record[0]


def _load_user_by_id(uid: UserId, conn: Connection) -> Optional[Union[UserProfile, SuperUserProfile]]:
    conn.execute(""" 
        SELECT nickName, email, firstName, familyName, locale, picture, bio, location, url, superAdmin
        FROM users
        WHERE uid = ?;
    """, [uid])

    record = conn.fetch_one()
    if record is None:
        return None
    super_admin = record[9]
    if super_admin is not None and super_admin == 1:
        # SuperAdmin User
        user = SuperUserProfile(uid=uid, nickName=record[0], email=record[1], firstName=record[2],
                                familyName=record[3], locale=record[4], picture=record[5],
                                bio=record[6], location=record[7], url=record[8], superAdmin=super_admin)
    else:
        # Regular User
        user = UserProfile(uid=uid, nickName=record[0], email=record[1], firstName=record[2],
                           familyName=record[3], locale=record[4], picture=record[5],
                           bio=record[6], location=record[7], url=record[8])
    conn.execute(""" 
        SELECT groups.uid
        FROM groups
        INNER JOIN users_groups ON users_groups.groupId = groups. uid
        WHERE users_groups.userId = ?;
    """, [uid])
    groups = conn.fetch_all()
    if groups is not None:
        user.groupIds = [group[0] for group in groups]
    return user


def _delete_user(uid: UserId, conn: Connection):
    conn.execute("DELETE FROM users WHERE uid = ?;", [uid]);
    # Delete every relation between a user and groups.
    conn.execute("DELETE FROM users_groups WHERE userId = ?;", [uid])
    # Clear temp users if needed
    conn.execute("DELETE FROM remote_temp_users WHERE temp_id = ?;", [uid])
    # TODO What about user's dataApps


def remove_from_user_group(user_id: UserId, group_id: int, conn: Connection):
    conn.execute(
        """
            DELETE FROM users_groups WHERE userId = ? AND groupId = ?;
        """,
        [user_id, group_id])


def add_to_user_group(user_id: UserId, group_id: int, write: bool, admin: int, conn: Connection):
    conn.execute("SELECT * from users_groups WHERE userId = ? AND groupId = ?", [user_id, group_id])
    is_there_user = conn.fetch_one()
    if is_there_user:
        # Update permission
        conn.execute(
            """
            UPDATE users_groups 
            SET read_write = ?, admin = ?
            WHERE userId = ? AND groupId = ?;
            """,
            [write, admin, user_id, group_id])
    else:
        # Insert new relation between user and group
        conn.execute(
            """
                INSERT INTO users_groups 
                (userId, groupId, read_write, admin) 
                VALUES (?, ?, ?, ?);
            """,
            [user_id, group_id, write, admin])


def _get_user_principals(uid: UserId, conn: Connection) -> List[PrincipalId]:
    conn.execute("SELECT scope, id FROM principals where uid = ?;", [uid])
    records = conn.fetch_all()
    return [PrincipalId(scope=str(r[0]), id=str(r[1])) for r in records]


def _find_user_by_principal(scope: str, pid: str, conn: Connection) -> Optional[int]:
    conn.execute("SELECT uid FROM principals where scope = ? and id = ?;", [scope, pid])
    record = conn.fetch_one()
    return None if record is None else int(record[0])


def _delete_all_principals_for_user(uid: UserId, conn: Connection):
    conn.execute("DELETE FROM principals WHERE uid = ?;", [uid]);


def _clear_all_principals(conn: Connection):
    conn.execute("DELETE FROM principals;")


def _principal_association_exists(uid: UserId, scope: str, pid: str, conn: Connection) -> bool:
    conn.execute("SELECT 1 from principals where uid = ? and scope = ? and id = ?;", [uid, scope, pid])
    return conn.fetch_one() is not None


def _associate_principal(uid: UserId, principal: PrincipalId, conn: Connection):
    conn.execute("INSERT INTO principals VALUES(?,?,?);", [principal.scope, principal.id, uid])


def _dissociate_principal(principal: PrincipalId, conn: Connection):
    conn.execute("DELETE FROM principals where scope = ? and id = ?;", [principal.scope, principal.id])


def user_id_for_name(name: str, conn: Connection) -> Optional[int]:
    conn.execute("SELECT uid FROM users WHERE nickName = ?;", [name])
    result = conn.fetch_one()
    return None if result is None else int(result[0])


def create_temp_user(nickname: str, conn: Connection) -> int:
    # First, check that the user does not have a temp id already
    conn.execute("SELECT temp_id FROM remote_temp_users WHERE nickname = ?", [nickname])
    result = conn.fetch_one()
    if result is None:
        temp_id = _next_id(conn)
        conn.execute("INSERT INTO remote_temp_users VALUES(?,?,?);", [temp_id, nickname, 0])
        return temp_id
    return result[0]


def load_temp_user(nickname: str, conn: Connection) -> int:
    conn.execute("SELECT temp_id from remote_temp_users where nickname = ?;", [nickname])
    result = conn.fetch_one()
    if result:
        return result[0]
    return None


def remove_temp_user(nickname: str, conn: Connection) -> int:
    conn.execute("DELETE FROM remote_temp_users where nickname = ?;", [nickname])
    return True


def update_remote_user_id(old_id: int, new_id: int, conn: Connection) -> bool:
    conn.execute("SELECT superAdmin FROM remote_temp_users WHERE temp_id = ?;", [old_id])
    result = conn.fetch_one()
    if not result:
        raise Exception("No such user")
    # is this a superAdmin?
    super_admin = result[0] == 1
    if super_admin:
        conn.execute(
            """
            UPDATE users 
            SET uid = ?, superAdmin = ? 
            WHERE uid = ?;
            """,
            [new_id, 1, old_id])
    else:
        conn.execute(
            """
            UPDATE users 
            SET uid = ? 
            WHERE uid = ?;
            """,
            [new_id, old_id])
    conn.execute(
        """
        UPDATE
        users_groups
        SET userId = ?
        WHERE userId = ?;
        """,
        [new_id, old_id])
    return True


def _get_groups(group_name, conn: Connection):
    """
    If group exist, return its id. Otherwise, raise error.
    """
    conn.execute("SELECT * FROM groups WHERE groupName = ?;", [group_name])
    result = conn.fetch_one()
    if result is not None:
        return result[0]


def _get_user_remote_groups(user_id: int, conn: Connection) -> List[int]:
    conn.execute("""
            SELECT users_groups.groupId FROM users_groups
            LEFT JOIN groups ON users_groups.groupId = groups.uid
            WHERE users_groups.userId = ? and provider != ?;
        """, [user_id, "local"])
    result = conn.fetch_all()
    if result is None:
        return []
    group_ids = []
    for r in result:
        group_ids.append(r[0])
    return group_ids


def _all_temp_users(conn: Connection) -> List[Union[SuperUserProfile, UserProfile]]:
    conn.execute("SELECT temp_id, nickname, superAdmin FROM remote_temp_users;")
    result = conn.fetch_all()
    temp_users = []
    for r in result:
        admin = r[2]
        if admin == 1:
            temp_users.append(SuperUserProfile(uid=r[0], nickName=r[1], superAdmin=admin))
        else:
            temp_users.append(UserProfile(uid=r[0], nickName=r[1]))
    return temp_users


def modify_super_admin(nick_name: str, delete: bool, conn: Connection):
    # Modify temp users as well, so when the user logs in for the firs time, it is a superAdmin
    if delete:
        conn.execute("UPDATE users SET superAdmin = 0 WHERE nickName = ?;", [nick_name])
        conn.execute("UPDATE remote_temp_users SET superAdmin = 0 WHERE nickName = ?;", [nick_name])
    else:
        conn.execute("UPDATE users SET superAdmin = 1 WHERE nickName = ?;", [nick_name])
        conn.execute("UPDATE remote_temp_users SET superAdmin = 1 WHERE nickName = ?;", [nick_name])


class UsersRepo(IUsersRepo):
    # Note: when modifying users table, copy table, drop it and recreated, as if it is a table with index and therefore
    # updates mean drop and create row, and this raise error violates primary key constraint
    # https://github.com/duckdb/duckdb/issues/4023

    @staticmethod
    def group_name_to_id(groups: List[str], conn: Connection) -> List[int]:
        return [_get_groups(group_name, conn) for group_name in groups]

    def add_to_group(self, user_name: str, groups: List[str], write: bool = False, admin: bool = False) -> bool:
        with transaction() as conn:
            group_ids = self.group_name_to_id(groups, conn)
            user_id = _get_user_id(user_name, conn)
            for group in group_ids:
                add_to_user_group(user_id, group, write, admin, conn)
            return True

    def add_remote_groups(self, user_id: int, group_ids: List[int], write: bool = False, admin: bool = False) -> bool:
        with transaction() as conn:
            # Get all remote groups and compare to the ones trying to add. Those that are in current_remote_groups but
            # not in group_ids are those where the user has no access anymore
            current_remote_groups = _get_user_remote_groups(user_id, conn)
            groups_to_remove = list(set(current_remote_groups) - set(group_ids))
            for old_group in groups_to_remove:
                remove_from_user_group(user_id, old_group, conn)
            for group in group_ids:
                add_to_user_group(user_id, group, write, admin, conn)
            return True

    def remove_from_group(self, user_name: str, groups: List[str]) -> bool:
        with transaction() as conn:
            group_ids = self.group_name_to_id(groups, conn)
            user_id = _get_user_id(user_name, conn)
            for group in group_ids:
                remove_from_user_group(user_id, group, conn)
            return True

    def find_remote_temp_user(self, user_name: str) -> int:
        with transaction() as conn:
            return load_temp_user(user_name, conn)

    def delete_remote_temp_user(self, user_name: str) -> bool:
        with transaction() as conn:
            return remove_temp_user(user_name, conn)

    def update_remote_user_id(self, old_id: int, new_id: int) -> bool:
        with transaction() as conn:
            return update_remote_user_id(old_id, new_id, conn)

    def load_by_id(self, uid: UserId) -> Optional[Union[UserProfile, SuperUserProfile]]:
        with connect() as conn:
            return _load_user_by_id(str(uid), conn)

    def load_by_name(self, name: str) -> Optional[UserProfile]:
        with transaction() as conn:
            uid = user_id_for_name(name, conn)
            if uid is None:
                return None
            return _load_user_by_id(uid, conn)

    def load_by_principal(self, principal: PrincipalId) -> Optional[UserProfile]:
        with transaction() as conn:
            uid = _find_user_by_principal(principal, conn)
            if uid is None: return None
            return _load_user_by_id(uid, conn)

    def delete_by_name(self, name: str):
        with transaction() as conn:
            uid = user_id_for_name(name, conn)
            if uid is None: return None
        self.delete_by_id(uid)

    def delete_by_id(self, uid: UserId):
        with transaction() as conn:
            _delete_all_principals_for_user(uid, conn)
            _delete_user(uid, conn)

    def update_by_id(self, uid: UserId, new_details: UserAttributes) -> Optional[UserProfile]:
        update_data = new_details.dict(exclude_unset=True)
        with transaction() as conn:
            if len(update_data) > 0:
                if update_data.get("nickName"):
                    raise ValueError("Nickname cannot be updated.")
                _update_user_by_id(uid, update_data, conn)
            return _load_user_by_id(uid, conn)

    def update_by_name(self, name: str, new_details: UserAttributes) -> Optional[UserProfile]:
        with transaction() as conn:
            uid = user_id_for_name(name, conn)
            if uid is None: return None
        return self.update_by_id(uid, new_details)

    def nickname_exists(self, name: str) -> bool:
        with connect() as conn:
            return user_id_for_name(name, conn) is not None

    def load_all(self,
                 attributes: Optional[Set[UserField]] = None,
                 skip: Optional[int] = None,
                 sort_by: Optional[List[Tuple[UserField, bool]]] = None,
                 limit: Optional[int] = None) -> List[UserProfile]:
        with connect() as conn:
            return _load_all(conn)

    def delete_all(self):
        # Only no super admin users can be deleted.
        with transaction() as conn:
            all_users = _load_all(conn) + _all_temp_users(conn)
            no_admin_users = [user for user in all_users if not isinstance(user, SuperUserProfile)]
            for user in no_admin_users:
                _delete_user(user.uid, conn)

    def principals_by_name(self, name: str) -> List[PrincipalId]:
        with transaction() as conn:
            uid = user_id_for_name(name)
            if uid is None:
                return []
            return _get_user_principals(uid, conn)

    def principals_by_id(self, id: str) -> List[PrincipalId]:
        with connect() as conn:
            return _get_user_principals(id, conn)

    def associate_principal(self, uid: UserId, principal: PrincipalId) -> ResolvedPrincipalId:
        with transaction() as conn:
            if not _principal_association_exists(uid, principal.scope, principal.id, conn):
                existing_user_id = _find_user_by_principal(principal.scope, principal.id, conn)
                if existing_user_id is not None:
                    raise RuntimeError(f"Principal {principal} is already associated with a different user")
                _associate_principal(uid, principal, conn)

        return ResolvedPrincipalId(scope=principal.scope, id=principal.id, userId=uid)

    def dissociate_principal(self, principal: PrincipalId):
        with connect() as conn:
            _dissociate_principal(principal, conn)

    def association_exists(self, rp: ResolvedPrincipalId) -> bool:
        with connect() as conn:
            return _principal_association_exists(rp.userId, rp.scope, rp.id)

    def find_user_id_by_principal(self, scope: str, pid: str) -> Optional[int]:
        with connect() as conn:
            return _find_user_by_principal(scope, pid, conn)
