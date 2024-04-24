import mariadb

# **How to use the class**
# 1. Install MariaDB Connector/Python: `pip install mariadb`
# 2. Replace placeholders with your database credentials

class MariaDBClient:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

    def connect(self):
        try:
            conn = mariadb.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database
            )
            return conn
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            return None

    def close_connection(self, conn):
        if conn:
            conn.close()

    def upsert(self, table_name, data, primary_key):
        """
        Upserts data into the specified table.

        Args:
            table_name (str): Name of the table.
            data (dict): Dictionary containing column names and values.
            primary_key (str or list): Primary key column(s) of the table.
        """

        conn = self.connect()
        if conn:
            cursor = conn.cursor()

            columns = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            values = list(data.values())

            if isinstance(primary_key, str):  # Single primary key
                query = f"""
                    INSERT INTO {table_name} ({columns})
                    VALUES ({placeholders})
                    ON DUPLICATE KEY UPDATE {columns} = VALUES({columns})
                """
            else:  # Composite primary key
                update_assignments = ", ".join(
                    [f"{col} = VALUES({col})" for col in data.keys()])
                query = f"""
                    INSERT INTO {table_name} ({columns})
                    VALUES ({placeholders})
                    ON DUPLICATE KEY UPDATE {update_assignments}
                """

            try:
                cursor.execute(query, values)
                conn.commit()
            except mariadb.Error as e:
                print(f"Error during upsert: {e}")
            finally:
                self.close_connection(conn)

    def read(self, table_name, columns=None, where_clause=None, params=None):
        """
        Reads data from the specified table.

        Args:
            table_name (str): Name of the table.
            columns (list, optional): List of columns to select. Defaults to all.
            where_clause (str, optional): WHERE clause for filtering.
            params (list or tuple, optional): Parameters for the WHERE clause.
        """

        return self.execute(
            f"SELECT {','.join(columns) if columns else '*'} FROM {table_name}"
            + (f" WHERE {where_clause}" if where_clause else ""),
            params
        )


    def execute(self, query, params=None):
        """
        Executes a custom SQL query.

        Args:
            query (str): The SQL query to execute.
            params (list or tuple, optional): Parameters for the query, if any.
        """

        conn = self.connect()
        if conn:
            cursor = conn.cursor()

            try:
                cursor.execute(query, params)

                # Fetch results for SELECT queries
                if query.lower().startswith("select"):
                    raw_result = cursor.fetchall()
                    column_names = [column_desc[0] for column_desc in cursor.description]
                    result = [dict(zip(column_names, row)) for row in raw_result]
                else:
                    conn.commit()  # Commit changes for other query types
                    result = None  # No data to return for non-SELECT queries

            except mariadb.Error as e:
                print(f"Error executing custom query: {e}")
                result = None
            finally:
                self.close_connection(conn)

            return result
