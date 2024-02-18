import pandas as pd
from maisaedu_utilities_prefect import get_dsn
from .document_handling import (
    document_handling,
    delete_docs,
)
from maisaedu_utilities_prefect.database.postgres import (
    connect,
    select,
    execute,
    insert_batch
)

class Extractor():
    def __init__(self, prefect_flow_name):
        self.prefect_flow_name = prefect_flow_name
        self.__get_file_infos()
        self.__get_tables_info()
        self.__get_columns_info()
        self.__get_documents()

    def __get_file_infos(self):
        files_info = []
        conn = connect(get_dsn())
        result = select(
            conn,
            f"""
                select 
                    id, name, url 
                from 
                    meta.one_drive_docs 
                where 
                    prefect_flow_name = '{self.prefect_flow_name}' 
                    and is_active
            """
        )
        for r in result:
            files_info.append(
                {
                    "id": r[0],
                    "name": r[1],
                    "url": r[2]
                }
            )
        self.files_info = files_info
        conn.close()

    def __get_tables_info(self):
        tables_info = []
        conn = connect(get_dsn())
        result = select(
            conn,
            f"""
                select 
                     oddt.id, oddt.table_name, spreadsheet_tab_name, deletion_clause 
                from 
                    meta.one_drive_docs_tables oddt
                join 
                    meta.one_drive_docs as odc on odc.id = oddt.doc_id
                where 
                    odc.is_active 
                    and oddt.is_active 
                    and odc.prefect_flow_name = '{self.prefect_flow_name}'
            """
        )
        for r in result:
            tables_info.append(
                {
                    "id": r[0],
                    "name": r[1],
                    "spreadsheet_tab_name": r[2],
                    "deletion_clause": r[3]
                }
            )
        self.tables_info = tables_info
        conn.close()

    def __get_columns_info(self):
        conn = connect(get_dsn())

        for idx, t in enumerate(self.tables_info):
            columns = []
            result = select(
                conn,
                f"""
                    select 
                        column_name, "position", type_cast 
                    from 
                        meta.one_drive_docs_tables_columns 
                    where 
                        doc_table_id = {t['id']}
                """
            )

            for r in result:
                columns.append(
                    {
                        "column_name": r[0],
                        "position": r[1],
                        "type_cast": r[2]
                    }
                )
            t['columns'] = columns

            self.tables_info[idx] = t

        conn.close()

    def __get_documents(self):
        file_sheet_names = [str(t['spreadsheet_tab_name']) for t in self.tables_info]
        documents_names, documents_list = document_handling(
            files_info={
                "docs" : self.files_info
            }, 
            sheet_name = file_sheet_names
        )
        self.documents_names = documents_names
        self.documents_list = documents_list
        delete_docs(documents_names)

    def __convert_types(self, documents_list, columns):
        for column in columns:
            if column['type_cast'] is not None:

                if column['type_cast'] == 'string':
                    documents_list.iloc[:, column['position']] = documents_list.iloc[:, column['position']].astype(str)

                if column['type_cast'] == 'string and remove dots':
                    documents_list.iloc[:, column['position']] = documents_list.iloc[:, column['position']].astype(str)
                    documents_list.iloc[:, column['position']] = documents_list.iloc[:, column['position']].astype(str).replace('\.0', '', regex=True)

        documents_list.replace({pd.NA: None}, inplace=True)
        documents_list.replace({"nan": None}, inplace=True)

        return documents_list

    def __save_records(self, conn, table_name, spreadsheet_tab_name, columns):
        documents_list = self.documents_list[0][spreadsheet_tab_name]

        records = []
        documents_list = self.__convert_types(documents_list, columns)

        for record in documents_list.values:
            data = {}

            for column in columns:
                data[column['column_name']] = record[column['position']]

            records.append(data)

            if len(records) >= 1000:
                insert_batch(
                    conn,
                    records,
                    table_name,
                    onconflict="",
                    page_size=1000,
                    default_commit=False,
                )
                records = []

        if len(records) > 0:
            insert_batch(
                conn,
                records,
                table_name,
                onconflict="",
                page_size=1000,
                default_commit=False,
            )

    def save_data(self):
        for table_info in self.tables_info:
            conn = connect(get_dsn())

            if table_info['deletion_clause'] is None:
                deletion_clause = '1=1'
            else:
                deletion_clause = table_info['deletion_clause']

            execute(
                conn,
                f"""
                    delete from {table_info['name']}
                    where {deletion_clause}
                """,
                default_commit=False,
            )

            self.__save_records(
                conn = conn,
                table_name = table_info['name'], 
                spreadsheet_tab_name = table_info['spreadsheet_tab_name'],
                columns = table_info['columns']
            )

            conn.commit()