from .native import Connection, transaction
from .schema_builder import SchemaBuilder


class BuilderV7(SchemaBuilder):
    """
    Database Schema Version 7
    - Modify Groups Table
        add provider: name of the provider (azure, google, etc.)
        add providerGroupId: ID of the group when it is from a remote provider
    - Modify users_groups table
        add admin field to check if user has administration permission, which allow to add/delete users and delete group.
    - Modify Users table
        add superAdmin field.
        set superAdmin to true for admin user
    - Create remote_temp_users table. A table for users that are imported from a provider (azure, google, etc.) but they have
    not logged in in the platform yet. We save the nickname of the user with a temp random id. Later, when the user logs
    in the temp id is replaced with the actual login ID.
    - Admin Group:
        Establish an administrative group for super administrators and include the user 'admin' within it.
    """

    @staticmethod
    def _alter_groups_table(conn: Connection):
        conn.execute("""
        ALTER TABLE groups ADD COLUMN provider VARCHAR; 
        ALTER TABLE groups ADD COLUMN providerGroupId VARCHAR;
        """)

    @staticmethod
    def _alter_users_groups_table(conn: Connection):
        conn.execute("ALTER TABLE users_groups ADD COLUMN admin TINYINT;")

    @staticmethod
    def _alter_users_table(conn: Connection):
        conn.execute("ALTER TABLE users ADD COLUMN superAdmin TINYINT;")
        conn.execute("UPDATE users SET superAdmin = 1 WHERE nickName = 'admin';")

    @staticmethod
    def _remote_user_table(conn: Connection):
        conn.execute("""
        CREATE TABLE remote_temp_users(
                temp_id BIGINT PRIMARY KEY,
                nickname VARCHAR NOT NULL UNIQUE,
                superAdmin TINYINT NULL)
        """)

    @staticmethod
    def _creat_admin_group(conn: Connection):
        group_name = "Super Admin Group"
        description = "Exclusive group for system administrators."
        conn.execute("""
                    INSERT INTO groups 
                    (uid, groupName, description, provider, providerGroupId) 
                    VALUES (?, ?, ?, ?, ?);
                """,
                     [-1, group_name, description, 'admin', None])
        conn.execute("SELECT uid FROM users WHERE nickName = 'admin';")
        uid = conn.fetch_one()[0]
        conn.execute("""
                    INSERT INTO users_groups 
                    (userId, groupId, read_write, admin) 
                    VALUES (?, ?, ?, ?);
                """,
                     [uid, -1, 1, 1])

    @property
    def version(self) -> int:
        return 7

    def setup(self):
        pass

    def patch(self, conn: Connection):
        with transaction() as conn:
            self._alter_groups_table(conn)
            self._alter_users_groups_table(conn)
            self._alter_users_table(conn)
            self._remote_user_table(conn)
            self._creat_admin_group(conn)
