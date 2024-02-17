import asyncio
import importlib
import json
from threading import Thread

from fastapi import FastAPI, WebSocket, status
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from starlette.websockets import WebSocketState
from uvicorn import run

from lapa_database.configuration import (
    config_bool_create_schema,
    config_int_db_port,
    config_int_host_port,
    config_str_database_module_name,
    config_str_db_ip,
    config_str_db_password,
    config_str_db_username,
    config_str_host_ip,
    global_object_square_logger,
    config_str_module_name,
)
from lapa_database.create_database import create_database_and_tables
from lapa_database.pydantic_models.pydantic_models import (
    DeleteRows,
    EditRows,
    GetRows,
    InsertRows,
)
from lapa_database.utils.CommonOperations import snake_to_capital_camel
from lapa_database.web_socket.Trigger import create_trigger_in_db
from lapa_database.web_socket.WebsocketOperation import run_listen_for_changes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/insert_rows", status_code=status.HTTP_201_CREATED)
@global_object_square_logger.async_auto_logger
async def insert_rows(insert_rows_model: InsertRows):
    try:
        local_str_database_url = (
            f"postgresql://{config_str_db_username}:{config_str_db_password}@"
            f"{config_str_db_ip}:{str(config_int_db_port)}/{insert_rows_model.database_name.value}"
        )
        database_engine = create_engine(local_str_database_url)

        # Connect to database
        with database_engine.connect() as database_connection:
            # ===========================================
            try:
                # Connect to schema
                database_connection.execute(
                    text(f"SET search_path TO {insert_rows_model.schema_name.value}")
                )
                # ===========================================
            except OperationalError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect schema name.",
                )
            try:
                table_class_name = snake_to_capital_camel(
                    insert_rows_model.table_name.value
                )
                table_module_path = (
                    f"{config_str_database_module_name}.{insert_rows_model.database_name.value}"
                    f".{insert_rows_model.schema_name.value}.tables"
                )
                table_module = importlib.import_module(table_module_path)
                table_class = getattr(table_module, table_class_name)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect table name.",
                )
            local_object_session = sessionmaker(bind=database_engine)
            session = local_object_session()
            try:
                data_to_insert = [
                    table_class(**row_dict) for row_dict in insert_rows_model.data
                ]
                session.add_all(data_to_insert)
                session.commit()
                for ele in data_to_insert:
                    session.refresh(ele)
                return_this = [
                    {
                        key: value
                        for key, value in new_row.__dict__.items()
                        if not key.startswith("_")
                    }
                    for new_row in data_to_insert
                ]
                session.close()
                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content=json.loads(json.dumps(return_this, default=str)),
                )
            except Exception as e:
                session.rollback()
                session.close()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                )
    except HTTPException:
        raise
    except OperationalError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="incorrect database name."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/get_rows", status_code=status.HTTP_200_OK)
@global_object_square_logger.async_auto_logger
async def get_rows(get_rows_model: GetRows):
    try:
        local_str_database_url = (
            f"postgresql://{config_str_db_username}:{config_str_db_password}@"
            f"{config_str_db_ip}:{str(config_int_db_port)}/{get_rows_model.database_name.value}"
        )
        database_engine = create_engine(local_str_database_url)
        # Connect to database
        with database_engine.connect() as database_connection:
            # ===========================================
            try:
                # Connect to schema
                database_connection.execute(
                    text(f"SET search_path TO {get_rows_model.schema_name.value}")
                )
                # ===========================================

            except OperationalError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect schema name.",
                )
            try:
                table_class_name = snake_to_capital_camel(
                    get_rows_model.table_name.value
                )
                table_module_path = (
                    f"{config_str_database_module_name}.{get_rows_model.database_name.value}"
                    f".{get_rows_model.schema_name.value}.tables"
                )
                table_module = importlib.import_module(table_module_path)
                table_class = getattr(table_module, table_class_name)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect table name.",
                )
            local_object_session = sessionmaker(bind=database_engine)
            session = local_object_session()
            try:
                # get rows
                if get_rows_model.ignore_filters_and_get_all:
                    query = session.query(table_class)
                    filtered_rows = query.all()
                else:
                    if not get_rows_model.filters:
                        query = None
                        filtered_rows = []
                    else:
                        query = session.query(table_class)
                        for key, value in get_rows_model.filters.items():
                            query = query.filter(getattr(table_class, key) == value)

                        filtered_rows = query.all()
                # ===========================================
                local_list_filtered_rows = [
                    {
                        key: value
                        for key, value in x.__dict__.items()
                        if not key.startswith("_")
                    }
                    for x in filtered_rows
                ]

                session.close()
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=json.loads(
                        json.dumps(local_list_filtered_rows, default=str)
                    ),
                )
            except Exception as e:
                session.close()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                )
    except HTTPException:
        raise
    except OperationalError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="incorrect database name."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.put("/edit_rows", status_code=status.HTTP_200_OK)
@global_object_square_logger.async_auto_logger
async def edit_rows(edit_rows_model: EditRows):
    try:
        local_str_database_url = (
            f"postgresql://{config_str_db_username}:{config_str_db_password}@"
            f"{config_str_db_ip}:{str(config_int_db_port)}/{edit_rows_model.database_name.value}"
        )
        database_engine = create_engine(local_str_database_url)
        # Connect to database
        with database_engine.connect() as database_connection:
            # ===========================================
            try:
                # Connect to schema
                database_connection.execute(
                    text(f"SET search_path TO {edit_rows_model.schema_name.value}")
                )
                # ===========================================

            except OperationalError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect schema name.",
                )
            try:
                table_class_name = snake_to_capital_camel(
                    edit_rows_model.table_name.value
                )
                table_module_path = (
                    f"{config_str_database_module_name}.{edit_rows_model.database_name.value}"
                    f".{edit_rows_model.schema_name.value}.tables"
                )
                table_module = importlib.import_module(table_module_path)
                table_class = getattr(table_module, table_class_name)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect table name.",
                )
            local_object_session = sessionmaker(bind=database_engine)
            session = local_object_session()
            try:
                # Get rows from filters
                if edit_rows_model.ignore_filters_and_edit_all:
                    query = session.query(table_class)
                    filtered_rows = query.all()
                else:
                    if not edit_rows_model.filters:
                        query = None
                        filtered_rows = []
                    else:
                        query = session.query(table_class)
                        for key, value in edit_rows_model.filters.items():
                            query = query.filter(getattr(table_class, key) == value)

                        filtered_rows = query.all()
                # ===========================================
                for row in filtered_rows:
                    for key, value in edit_rows_model.data.items():
                        # edit rows
                        setattr(row, key, value)
                        # ===========================================
                session.commit()
                for row in filtered_rows:
                    session.refresh(row)
                local_list_filtered_rows = [
                    {
                        key: value
                        for key, value in x.__dict__.items()
                        if not key.startswith("_")
                    }
                    for x in filtered_rows
                ]
                session.close()
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=json.loads(
                        json.dumps(local_list_filtered_rows, default=str)
                    ),
                )
            except Exception as e:
                session.rollback()
                session.close()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                )
    except HTTPException:
        raise
    except OperationalError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="incorrect database name."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.delete("/delete_rows", status_code=status.HTTP_200_OK)
@global_object_square_logger.async_auto_logger
async def delete_rows(delete_rows_model: DeleteRows):
    try:
        local_str_database_url = (
            f"postgresql://{config_str_db_username}:{config_str_db_password}@"
            f"{config_str_db_ip}:{str(config_int_db_port)}/{delete_rows_model.database_name.value}"
        )
        database_engine = create_engine(local_str_database_url)
        # Connect to database
        with database_engine.connect() as database_connection:
            # ===========================================
            try:
                # Connect to schema
                database_connection.execute(
                    text(f"SET search_path TO {delete_rows_model.schema_name.value}")
                )
                # ===========================================

            except OperationalError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect schema name.",
                )
            try:
                table_class_name = snake_to_capital_camel(
                    delete_rows_model.table_name.value
                )
                table_module_path = (
                    f"{config_str_database_module_name}.{delete_rows_model.database_name.value}"
                    f".{delete_rows_model.schema_name.value}.tables"
                )
                table_module = importlib.import_module(table_module_path)
                table_class = getattr(table_module, table_class_name)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect table name.",
                )
            local_object_session = sessionmaker(bind=database_engine)
            session = local_object_session()
            try:
                # get rows from filters
                if delete_rows_model.ignore_filters_and_delete_all:
                    query = session.query(table_class)
                    filtered_rows = query.all()
                else:
                    if not delete_rows_model.filters:
                        query = None
                        filtered_rows = []
                    else:
                        query = session.query(table_class)
                        for key, value in delete_rows_model.filters.items():
                            query = query.filter(getattr(table_class, key) == value)

                        filtered_rows = query.all()
                # ===========================================
                local_list_filtered_rows = [
                    {
                        key: value
                        for key, value in x.__dict__.items()
                        if not key.startswith("_")
                    }
                    for x in filtered_rows
                ]
                # delete all rows at once
                if query:
                    query.delete()
                # ===========================================
                session.commit()
                session.close()
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=json.loads(
                        json.dumps(local_list_filtered_rows, default=str)
                    ),
                )
            except Exception as e:
                # no need for this but kept it anyway :/
                session.rollback()
                session.close()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                )

    except HTTPException:
        raise
    except OperationalError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="incorrect database name."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/")
@global_object_square_logger.async_auto_logger
async def root():
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"text": config_str_module_name}
    )


@app.websocket("/ws/{database_name}/{table_name}/{schema_name}")
@global_object_square_logger.async_auto_logger
async def get_rows_using_websocket(
    websocket: WebSocket, database_name: str, table_name: str, schema_name: str
):
    """
    Author: Lav Sharma
    Description: This api endpoint is a websocket which is used to receive the initial data of a table-name.
    After which it will receive whenever the data is added/deleted/edited.

    :param database_name: name of the database to which the table_name belongs
    :param table_name: name of the table which is present inside the database
    :param schema_name: under which schema the table_name is present
    :return: rows from the database
    """
    await websocket.accept()
    try:
        global_object_square_logger.logger.info(
            "Websocket connected"
            f", Database name - {str(database_name)}"
            f", Table name - {str(table_name)}"
            f", Schema name - {str(schema_name)}"
        )
        # ================================================================
        # Create the trigger function and trigger for the table_name
        # ================================================================
        create_trigger_in_db(
            pstr_database_host=config_str_db_ip,
            pstr_database_port=str(config_int_db_port),
            pstr_database_name=database_name,
            pstr_database_username=config_str_db_username,
            pstr_database_password=config_str_db_password,
            pstr_table_name=table_name,
        )

        local_str_database_url = (
            f"postgresql://{config_str_db_username}:{config_str_db_password}@"
            f"{config_str_db_ip}:{str(config_int_db_port)}/{database_name}"
        )
        database_engine = create_engine(local_str_database_url)

        with database_engine.connect() as database_connection:
            try:
                database_connection.execute(text(f"SET search_path TO {schema_name}"))
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
                table_module = importlib.import_module(table_module_path)
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
                initial_message = json.dumps(
                    {"type": "initial", "data": local_list_filtered_rows}, default=str
                )
                await websocket.send_text(initial_message)

                """
                Run listen_for_changes on a separate thread, if we don't then due to postgres connection
                the message is not sent through websocket
                """
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                """
                Create a queue to communicate between threads. This is done so that any new message generated is 
                added into the queue and then the main code takes care of sending it through websocket.
                This is done because if we are passing the websocket object then the connection is showing as 
                'closed' even when the connection is 'open'.
                """
                result_queue = asyncio.Queue()
                listen_thread = Thread(
                    target=run_listen_for_changes,
                    args=(table_name, database_name, schema_name, result_queue, loop),
                )
                listen_thread.start()

                while True:
                    # ================================================================
                    # Retrieve results from the queue (this is a non-blocking call)
                    # ================================================================
                    try:
                        update_message = await result_queue.get()
                        if update_message is not None:
                            # ================================================================
                            # Process the result (send message, update data, etc.)
                            # ================================================================
                            global_object_square_logger.logger.debug(
                                f"Updated message - {str(update_message)}"
                            )

                            if websocket.client_state == WebSocketState.CONNECTED:
                                global_object_square_logger.logger.info(
                                    "Websocket connection is open"
                                )
                                try:
                                    await websocket.send_text(update_message)
                                except Exception as error:
                                    global_object_square_logger.logger.error(
                                        f"Exception - {str(error)}", exc_info=True
                                    )

                    except asyncio.QueueEmpty:
                        # ================================================================
                        # No result yet, do something else or sleep
                        # ================================================================
                        pass
            except Exception as e:
                session.close()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                )
            finally:
                session.close()
    except HTTPException:
        raise
    except OperationalError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="incorrect database name."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


if __name__ == "__main__":
    try:
        if config_bool_create_schema:
            create_database_and_tables()

        run(app, host=config_str_host_ip, port=config_int_host_port)

    except Exception as exc:
        global_object_square_logger.logger.critical(exc, exc_info=True)
