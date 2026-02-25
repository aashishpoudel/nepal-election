import pandas as pd
import sqlite3
from pathlib import Path
from typing import Optional, Sequence, Any



class NepalElectionDataProcessor:
    """
    A class to handle the processing of Nepal election candidate data.
    This includes importing from Excel, storing in SQLite, and running queries.
    """

    def get_all_columns(
            self,
            db_path: Path,
            table_name: str,
            include_types: bool = True
    ) -> pd.DataFrame:
        """
        Returns metadata about all columns in a table.

        Parameters:
            include_types: If True, includes datatype and constraints
        """

        query = f"PRAGMA table_info({table_name});"

        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query(query, conn)

        # Rename SQLite default columns for clarity
        df = df.rename(columns={
            "cid": "column_id",
            "name": "column_name",
            "type": "data_type",
            "notnull": "not_null",
            "dflt_value": "default_value",
            "pk": "is_primary_key"
        })

        if not include_types:
            df = df[["column_name"]]

        return df

    def print_all_columns(
            self,
            db_path: Path,
            table_name: str,
            include_types: bool = True
    ) -> None:

        df = self.get_all_columns(
            db_path=db_path,
            table_name=table_name,
            include_types=include_types
        )

        print(f"\n--- Columns in table: {table_name} ---")
        self.print_df_as_table(df)

    def get_unique_values(
            self,
            db_path: Path,
            table_name: str,
            column_name: str,
            include_counts: bool = False,
            sort: bool = True
    ) -> pd.DataFrame:
        """
        Returns unique values of a column.

        Parameters:
            column_name: Name of column (exact DB column name)
            include_counts: If True, also returns frequency count
            sort: Sort alphabetically (or by count if include_counts=True)
        """

        if include_counts:
            query = f"""
                SELECT "{column_name}" AS value,
                       COUNT(*) AS count
                FROM {table_name}
                GROUP BY "{column_name}"
            """
            if sort:
                query += " ORDER BY count DESC;"
        else:
            query = f"""
                SELECT DISTINCT "{column_name}" AS value
                FROM {table_name}
            """
            if sort:
                query += " ORDER BY value;"

        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query(query, conn)

        return df

    def print_unique_values(
            self,
            db_path: Path,
            table_name: str,
            column_name: str,
            include_counts: bool = False
    ) -> None:
        df = self.get_unique_values(
            db_path=db_path,
            table_name=table_name,
            column_name=column_name,
            include_counts=include_counts
        )

        print(f"\n--- Unique values for column: {column_name} ---")
        self.print_df_as_table(df)

    def import_excel_to_sqlite(self, excel_path: Path, db_path: Path, table_name: str) -> None:
        # Read Excel
        df = pd.read_excel(excel_path)

        # (Optional) Basic cleanup: strip whitespace from column names and string cells
        df.columns = [str(c).strip() for c in df.columns]
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].astype(str).str.strip().replace({"nan": None})

        # Write to SQLite
        with sqlite3.connect(db_path) as conn:
            # Replace the table if it exists
            df.to_sql(table_name, conn, if_exists="replace", index=False)

            # Helpful indexes for faster queries (optional)
            conn.execute(f'CREATE INDEX IF NOT EXISTS idx_province ON {table_name}("प्रदेश");')
            conn.execute(f'CREATE INDEX IF NOT EXISTS idx_gender ON {table_name}("लिङ्ग");')
            conn.execute(f'CREATE INDEX IF NOT EXISTS idx_party ON {table_name}("राजनीतिक दल / स्वतन्त्र");')

    def print_sample_filtered_records(self, db_path: Path, table_name: str) -> None:
        query = f"""
        SELECT
            "प्रदेश" AS province,
            "जिल्ला" AS district,
            "प्रतिनिधि सभा निर्वाचन क्षेत्र" AS constituency,
            "उम्मेदवारको नाम" AS candidate_name,
            "लिङ्ग" AS gender,
            "राजनीतिक दल / स्वतन्त्र" AS party_or_independent,
            "चुनाव चिन्ह" AS symbol,
            "उमेर" AS age,
            "शैक्षिक योग्यता (माथिल्लो शैक्षिक योग्यता)" AS education,
            "अनुभव" AS experience
        FROM {table_name}
        WHERE "प्रदेश" = ?
          AND "लिङ्ग" = ?
          AND "राजनीतिक दल / स्वतन्त्र" = ?
        LIMIT 20;
        """

        params = ("बागमती प्रदेश", "महिला", "नेपाली काँग्रेस")
        df = self.query_to_df(db_path, query, params=params)

        print("\n--- Sample filtered records (tabular) ---")
        self.print_df_as_table(df, max_rows=20)

    def add_age_group_processing_in_sql(self, db_path: Path, table_name: str) -> None:
        """
        Example "processing": create a view with an age_group derived from उमेर.
        Keeps the original table unchanged.
        """
        create_view_sql = f"""
        CREATE VIEW IF NOT EXISTS candidates_with_age_group AS
        SELECT
            *,
            CASE
                WHEN CAST("उमेर" AS INTEGER) < 30 THEN "<30"
                WHEN CAST("उमेर" AS INTEGER) BETWEEN 30 AND 39 THEN "30-39"
                WHEN CAST("उमेर" AS INTEGER) BETWEEN 40 AND 49 THEN "40-49"
                WHEN CAST("उमेर" AS INTEGER) BETWEEN 50 AND 59 THEN "50-59"
                WHEN CAST("उमेर" AS INTEGER) >= 60 THEN "60+"
                ELSE "Unknown"
            END AS age_group
        FROM {table_name};
        """

        sample_group_query = """
        SELECT age_group, COUNT(*) AS cnt
        FROM candidates_with_age_group
        GROUP BY age_group
        ORDER BY cnt DESC;
        """

        with sqlite3.connect(db_path) as conn:
            conn.execute(create_view_sql)
            rows = conn.execute(sample_group_query).fetchall()

        print("\n--- Age group counts (from SQL view) ---")
        for age_group, cnt in rows:
            print(f"{age_group:>7}: {cnt}")

    def query_to_df(self, db_path: Path, query: str, params: Optional[Sequence[Any]] = None) -> pd.DataFrame:
        with sqlite3.connect(db_path) as conn:
            return pd.read_sql_query(query, conn, params=params)

    def print_df_as_table(self, df: pd.DataFrame, max_rows: int = 706) -> None:
        """
        Prints a DataFrame as a readable table in the console.
        Requires: pip install tabulate
        """
        if df.empty:
            print("No rows to display.")
            return

        df_show = df.head(max_rows).copy()

        try:
            from tabulate import tabulate
            print(tabulate(df_show, headers="keys", tablefmt="github", showindex=False))
            if len(df) > max_rows:
                print(f"\n(showing first {max_rows} of {len(df)} rows)")
        except ImportError:
            # Fallback (no extra dependency)
            print(df_show.to_string(index=False))
            if len(df) > max_rows:
                print(f"\n(showing first {max_rows} of {len(df)} rows)")

        

