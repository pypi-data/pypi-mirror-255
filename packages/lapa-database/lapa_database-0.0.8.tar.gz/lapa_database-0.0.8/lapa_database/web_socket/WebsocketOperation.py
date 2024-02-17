import asyncio
import importlib
import json
import select

import psycopg2
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from lapa_database.configuration import (
    config_int_db_port,
    config_str_database_module_name,
    config_str_db_ip,
    config_str_db_password,
    config_str_db_username,
    global_object_square_logger,
)
from lapa_database.utils.CommonOperations import snake_to_capital_camel


def run_listen_for_changes(
    table_name: str,
    database_name: str,
    schema_name: str,
    result_queue: asyncio.Queue,
    loop,
):
    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            listen_for_changes(table_name, database_name, schema_name, result_queue)
        )

    except Exception:
        raise


async def listen_for_changes(
    table_name: str, database_name: str, schema_name: str, result_queue: asyncio.Queue
):
    """
    Author: Lav Sharma
    Description: This function continuously listens to the table_name with the help of LISTEN mechanism provided in
    postgres database. If any new rows are added/deleted/updated it will retrieve all the rows from the database
    and send it on the websocket connection.

    :param database_name: name of the database to which the table_name belongs
    :param table_name: name of the table which is present inside the database
    :param schema_name: under which schema the table_name is present
    :return: rows from the database
    """
    try:
        ldict_db_params = {
            "dbname": database_name,
            "user": config_str_db_username,
            "password": config_str_db_password,
            "host": config_str_db_ip,
            "port": str(config_int_db_port),
        }
        # ================================================================
        # Listen for changes using PostgreSQL LISTEN
        # ================================================================
        lobj_connection = psycopg2.connect(**ldict_db_params)
        lobj_connection.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
        )
        lobj_cursor = lobj_connection.cursor()

        # ================================================================
        # Use the table name as the channel name
        # ================================================================
        lstr_channel_name = f"{table_name}_channel"
        lobj_cursor.execute(f"LISTEN {lstr_channel_name}")

        try:
            while True:
                # ================================================================
                # Wait for notification from the database
                # ================================================================
                if select.select([lobj_connection], [], [], 1) == ([], [], []):
                    continue

                lobj_connection.poll()
                while lobj_connection.notifies:
                    lobj_notify = lobj_connection.notifies.pop()
                    if lobj_notify.channel == lstr_channel_name:
                        # ================================================================
                        # Notify the client about the update
                        # ================================================================
                        local_str_database_url = (
                            f"postgresql://{config_str_db_username}:{config_str_db_password}@"
                            f"{config_str_db_ip}:{str(config_int_db_port)}/{database_name}"
                        )
                        database_engine = create_engine(local_str_database_url)

                        with database_engine.connect() as database_connection:
                            try:
                                database_connection.execute(
                                    text(f"SET search_path TO {schema_name}")
                                )
                            except OperationalError:
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="incorrect schema name.",
                                )

                            try:
                                table_class_name = snake_to_capital_camel(table_name)
                                table_module_path = (
                                    f"{config_str_database_module_name}.{database_name}"
                                    f".{schema_name}.tables"
                                )
                                table_module = importlib.import_module(
                                    table_module_path
                                )
                                table_class = getattr(table_module, table_class_name)
                            except Exception:
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="incorrect table name.",
                                )

                            local_object_session = sessionmaker(bind=database_engine)
                            session = local_object_session()

                            try:
                                # ================================================================
                                # Get all rows
                                # ================================================================
                                query = session.query(table_class)
                                filtered_rows = query.all()

                                local_list_filtered_rows = [
                                    {
                                        key: value
                                        for key, value in x.__dict__.items()
                                        if not key.startswith("_")
                                    }
                                    for x in filtered_rows
                                ]
                            except Exception as e:
                                session.close()
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=str(e),
                                )
                            finally:
                                session.close()

                        update_data = local_list_filtered_rows

                        # ================================================================
                        # Manually serialize the update message using dumps
                        # ================================================================
                        update_message = json.dumps(
                            {"type": "updated", "data": update_data}, default=str
                        )
                        global_object_square_logger.logger.debug(
                            f"Updated message - {str(update_message)}"
                        )

                        # ================================================================
                        # Add the message to the queue
                        # ================================================================
                        await result_queue.put(update_message)

        except Exception:
            raise

        finally:
            lobj_cursor.close()
            lobj_connection.close()

    except Exception:
        raise
