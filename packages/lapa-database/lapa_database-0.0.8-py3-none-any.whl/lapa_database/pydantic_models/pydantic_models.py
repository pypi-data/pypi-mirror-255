from typing import List

from pydantic import BaseModel

from lapa_database.configuration import database_structure_main_file


class InsertRows(BaseModel):
    database_name: database_structure_main_file.DatabasesEnum
    table_name: database_structure_main_file.TablesEnum
    schema_name: database_structure_main_file.SchemaEnum
    data: List[dict]


class GetRows(BaseModel):
    database_name: database_structure_main_file.DatabasesEnum
    table_name: database_structure_main_file.TablesEnum
    schema_name: database_structure_main_file.SchemaEnum
    filters: dict
    ignore_filters_and_get_all: bool = False


class EditRows(BaseModel):
    database_name: database_structure_main_file.DatabasesEnum
    table_name: database_structure_main_file.TablesEnum
    schema_name: database_structure_main_file.SchemaEnum
    filters: dict
    data: dict
    ignore_filters_and_edit_all: bool = False


class DeleteRows(BaseModel):
    database_name: database_structure_main_file.DatabasesEnum
    table_name: database_structure_main_file.TablesEnum
    schema_name: database_structure_main_file.SchemaEnum
    filters: dict
    ignore_filters_and_delete_all: bool = False
