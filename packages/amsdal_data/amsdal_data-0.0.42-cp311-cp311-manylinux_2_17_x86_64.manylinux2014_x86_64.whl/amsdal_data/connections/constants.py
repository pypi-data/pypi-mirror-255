ICEBERG_ALIAS = 'iceberg'
SQLITE_ALIAS = 'sqlite'
SQLITE_STATE_ALIAS = 'sqlite-state'
SQLITE_HISTORICAL_ALIAS = 'sqlite-historical'
POSTGRES_HISTORICAL_ALIAS = 'postgres-historical'

CONNECTION_BACKEND_ALIASES: dict[str, str] = {
    ICEBERG_ALIAS: 'amsdal_data.connections.implementations.iceberg_history.IcebergHistoricalConnection',
    SQLITE_ALIAS: 'amsdal_data.connections.implementations.sqlite_state.SqliteStateConnection',
    SQLITE_STATE_ALIAS: 'amsdal_data.connections.implementations.sqlite_state.SqliteStateConnection',
    SQLITE_HISTORICAL_ALIAS: 'amsdal_data.connections.implementations.sqlite_history.SqliteHistoricalConnection',
    POSTGRES_HISTORICAL_ALIAS: (
        'amsdal_data.connections.implementations.postgresql_history.PostgresHistoricalConnection'
    ),
}
