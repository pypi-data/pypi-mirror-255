import psycopg2

from lapa_database.configuration import global_object_square_logger


def is_trigger_exists(lobj_cursor, lstr_trigger_name: str):
    try:
        lobj_cursor.execute(
            """SELECT 1 FROM pg_trigger WHERE tgname = %s;""", (lstr_trigger_name,)
        )
        return lobj_cursor.fetchone() is not None

    except Exception:
        raise


def create_trigger_in_db(
    pstr_database_host: str,
    pstr_database_port: str,
    pstr_database_name: str,
    pstr_database_username: str,
    pstr_database_password: str,
    pstr_table_name: str,
):
    try:
        lstr_trigger_function_name = f"notify_{pstr_table_name}_changes"
        lstr_trigger_name = f"{pstr_table_name}_channel"

        # ================================================================
        # Replace the connection parameters with database connection details
        # ================================================================
        lobj_connection = psycopg2.connect(
            host=pstr_database_host,
            port=pstr_database_port,
            database=pstr_database_name,
            user=pstr_database_username,
            password=pstr_database_password,
        )

        try:
            with lobj_connection.cursor() as lobj_cursor:
                # ================================================================
                # Trigger function
                # ================================================================
                if not is_trigger_exists(lobj_cursor, lstr_trigger_function_name):
                    lobj_cursor.execute(
                        f"""
                            CREATE OR REPLACE FUNCTION {lstr_trigger_function_name}() RETURNS TRIGGER AS $$
                            DECLARE
                                payload JSONB;
                            BEGIN
                                -- Create a JSON object for column names and values
                                SELECT jsonb_object_agg(column_name, row_to_json(NEW)->>column_name)
                                INTO payload
                                FROM information_schema.columns
                                WHERE table_name = TG_TABLE_NAME;

                                -- Include the table name in the payload
                                payload := payload || jsonb_build_object('table_name', TG_TABLE_NAME);

                                PERFORM pg_notify('{lstr_trigger_name}', payload::TEXT);
                                RETURN NEW;
                            END;
                            $$ LANGUAGE plpgsql;
                        """
                    )
                    global_object_square_logger.logger.info(
                        f"Trigger function created successfully, trigger function name - {str(lstr_trigger_function_name)}"
                    )

                else:
                    global_object_square_logger.logger.warning(
                        f"Trigger function already exists, trigger function name - {str(lstr_trigger_function_name)}."
                        " Not creating the trigger function again."
                    )

                # ================================================================
                # Trigger
                # ================================================================
                if not is_trigger_exists(lobj_cursor, lstr_trigger_name):
                    lobj_cursor.execute(
                        f"""
                            CREATE TRIGGER {lstr_trigger_name}
                            AFTER INSERT OR UPDATE OR DELETE
                            ON {pstr_table_name}
                            FOR EACH ROW
                            EXECUTE FUNCTION {lstr_trigger_function_name}();
                        """
                    )
                    global_object_square_logger.logger.info(
                        f"Trigger created successfully, trigger name - {str(lstr_trigger_name)}"
                    )

                else:
                    global_object_square_logger.logger.warning(
                        f"Trigger already exists, trigger name - {str(lstr_trigger_name)}."
                        " Not creating the trigger again."
                    )

            lobj_connection.commit()

        finally:
            lobj_connection.close()

    except Exception:
        raise
