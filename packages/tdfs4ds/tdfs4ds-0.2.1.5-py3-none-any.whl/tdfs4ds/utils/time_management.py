import teradataml as tdml
import datetime
class TimeManager:
    """
    A class to manage time-related operations in a database table.

    Attributes:
        schema_name (str): Name of the schema in the database.
        table_name (str): Name of the table in the schema.
        data_type (str): Type of the date/time data, defaults to 'DATE'.
    """

    def __init__(self, table_name, schema_name, data_type='DATE'):
        """
        Initializes the TimeManager with a table name, schema name, and optionally a data type.

        If the table doesn't exist, it creates one with a BUSINESS_DATE column of the specified data type.

        Args:
            table_name (str): Name of the table.
            schema_name (str): Name of the schema.
            data_type (str, optional): Type of the date/time data. Defaults to 'DATE'.
        """
        self.schema_name = schema_name
        self.table_name = table_name
        if not self._exists():
            self.data_type = data_type
            self._create_table()
        else:
            df = tdml.DataFrame(tdml.in_schema(self.schema_name, self.table_name))
            d_ = {x[0]: x[1] for x in df._td_column_names_and_types}
            self.data_type = d_['BUSINESS_DATE']

    def _create_table(self):
        """
        Creates a table in the database with a BUSINESS_DATE column.
        """
        query = f"""
        CREATE TABLE {self.schema_name}.{self.table_name}
        (
            BUSINESS_DATE {self.data_type}
        )
        """
        tdml.execute_sql(query)

        if 'date' in self.data_type.lower():
            query = f"""
            INSERT INTO {self.schema_name}.{self.table_name} VALUES (CURRENT_DATE)
            """
        else:
            query = f"""
            INSERT INTO {self.schema_name}.{self.table_name} VALUES (CURRENT_TIME)
            """
        tdml.execute_sql(query)

    def _exists(self):
        """
        Checks if the table exists in the database.

        Returns:
            bool: True if the table exists, False otherwise.
        """

        return len([x for x in tdml.db_list_tables(schema_name=self.schema_name).TableName.values if
                    x.lower().replace('"', '') == self.table_name.lower()]) > 0

    def _drop(self):
        """
        Drops the table if it exists.
        """
        # Drop the table if it exists
        if self._exists():
            tdml.db_drop_table(schema_name=self.schema_name, table_name=self.table_name)

    def update(self, new_time=None):
        """
        Updates the BUSINESS_DATE in the table.

        Args:
            new_time (str, optional): The new time to update. If None, current date or time is used depending on the data type.
        """
        if self._exists():
            if new_time is None and 'date' in self.data_type.lower():
                query = f"""
                UPDATE {self.schema_name}.{self.table_name}
                SET BUSINESS_DATE = CURRENT_DATE
                """
            elif new_time is None:
                query = f"""
                UPDATE {self.schema_name}.{self.table_name}
                SET BUSINESS_DATE = CURRENT_TIME
                """
            else:
                query = f"""
                UPDATE {self.schema_name}.{self.table_name}
                SET BUSINESS_DATE = {self.data_type} '{new_time}'
                """
            tdml.execute_sql(query)

    def display(self):
        """
        Displays the table.

        Returns:
            DataFrame: The table data as a DataFrame.
        """
        return tdml.DataFrame(tdml.in_schema(self.schema_name, self.table_name))

    def get_date_in_the_past(self):
        # '9999-01-01 00:00:00'
        date_obj = self.display().to_pandas().reset_index().iloc[0,0]

        if isinstance(date_obj, datetime.datetime):
            # print("temp is a datetime.datetime object")
            datetime_obj = date_obj
        elif isinstance(date_obj, datetime.date):
            # print("temp is a datetime.date object")
            # Convert date object to a datetime object at midnight (00:00:00)
            datetime_obj = datetime.datetime.combine(date_obj, datetime.time.min)
        else:
            print("temp is neither a datetime.date nor a datetime.datetime object")
            return

        # Convert datetime object to string
        output_string = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")

        return output_string