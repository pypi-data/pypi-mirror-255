import os
from dataclasses import MISSING, dataclass, field, fields, is_dataclass
from typing import TypeVar


@dataclass(frozen=True)
class PostgresConnectionConfig:
    host: str = field(metadata=dict(env_name_override="POSTGRES_DB_HOST"))
    user: str = field(metadata=dict(env_name_override="POSTGRES_DB_USER"))
    password: str = field(metadata=dict(env_name_override="POSTGRES_DB_PASSWORD"))

    port: str = "5432"
    dbname: str = field(
        default="plymouthdb", metadata=dict(env_name_override="POSTGRES_DB_NAME")
    )

    pool_size: int = 20


@dataclass(frozen=True)
class Auth0Config:
    client_id: str = field(metadata=dict(env_name_override="VITE_AUTH0_CLIENT_ID"))
    client_secret: str = field(
        metadata=dict(env_name_override="VITE_AUTH0_CLIENT_SECRET")
    )
    domain: str = field(metadata=dict(env_name_override="VITE_AUTH0_DOMAIN"))


T = TypeVar("T")


def read_config(x: type[T], env_prefix: str = "") -> T:
    res = {}
    for f in fields(x):
        val = None

        typ = f.type
        if is_dataclass(typ):
            val = read_config(typ, env_prefix + f.name + "_")

        env_name = ""
        if val is None:
            env_name = env_prefix + f.metadata.get("env", f.name)
            env_name = f.metadata.get("env_name_override", env_name)

            env_val = os.environ.get(env_name)
            if env_val is not None:
                parser = f.metadata.get("parser")
                if parser is not None:
                    val = parser(env_val)
                else:
                    val = typ(env_val)

        if val is None:
            if f.default != MISSING:
                val = f.default
            else:
                raise RuntimeError(f"missing value for '{f.name}' (${env_name})")

        res[f.name] = val

    return x(**res)
