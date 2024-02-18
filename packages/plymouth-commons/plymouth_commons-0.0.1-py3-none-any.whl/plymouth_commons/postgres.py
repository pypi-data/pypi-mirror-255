from typing import Optional
import asyncpg
from plymouth_commons.config import PostgresConnectionConfig, read_config


async def get_pool(config: Optional[PostgresConnectionConfig] = None):
    if config is None:
        config = read_config(PostgresConnectionConfig)

    return await asyncpg.create_pool(
        user=config.user,
        password=config.password,
        database=config.dbname,
        host=config.host,
        port=config.port,
        max_size=config.pool_size,
    )


async def get_connection(config: Optional[PostgresConnectionConfig] = None):
    if config is None:
        config = read_config(PostgresConnectionConfig)

    return await asyncpg.connect(
        user=config.user,
        password=config.password,
        database=config.dbname,
        host=config.host,
        port=config.port,
    )
