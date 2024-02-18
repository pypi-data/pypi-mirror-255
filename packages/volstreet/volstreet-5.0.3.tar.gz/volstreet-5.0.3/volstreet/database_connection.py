import os
from attrs import define, field
from contextlib import contextmanager
from sqlalchemy import create_engine
from abc import ABC, abstractmethod


@define
class BaseDBConnection(ABC):
    # Database attributes
    _database_name = field(repr=False)
    _user = field(repr=False)
    _password = field(repr=False)
    _host = field(repr=False)
    _port = field(repr=False)

    database_connection_url: str = None
    alchemy_engine_url: str = None

    @property
    @abstractmethod
    def prefix(self):
        pass

    def __attrs_post_init__(self):
        self.database_connection_url = (
            f"postgres://{self._user}:{self._password}@{self._host}:"
            f"{self._port}/{self._database_name}?sslmode=require"
        )
        self.alchemy_engine_url = self.database_connection_url.replace(
            "postgres", "postgresql"
        )

    @_database_name.default
    def _get_database_name(self):
        return self._get_env_var(f"{self.prefix}_NAME")

    @_user.default
    def _get_user(self):
        return self._get_env_var(f"{self.prefix}_USER")

    @_password.default
    def _get_password(self):
        return self._get_env_var(f"{self.prefix}_PASS")

    @_host.default
    def _get_host(self):
        return self._get_env_var(f"{self.prefix}_HOST")

    @_port.default
    def _get_port(self):
        return self._get_env_var(f"{self.prefix}_PORT")

    @staticmethod
    def _get_env_var(var_name: str):
        """Fetch environment variables safely."""
        var_value = os.getenv(var_name)
        if var_value is None:
            raise EnvironmentError(f"Environment variable '{var_name}' is not set.")
        return var_value

    def create_engine(self):
        return create_engine(self._alchemy_engine_url)

    @contextmanager
    def generate_connection(self):
        """Context manager for temporary database connections."""
        engine = self.create_engine()
        connection = engine.connect()
        try:
            yield connection
        finally:
            connection.close()
            engine.dispose()
