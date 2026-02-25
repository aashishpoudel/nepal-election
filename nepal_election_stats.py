from nepal_election_base import *

nepal_election_processor = NepalElectionDataProcessor()
EXCEL_PATH = Path("/Users/aashishpoudel/Downloads/2022_nepal_house_candidates_enriched.xlsx")  # <-- your file
DB_PATH = Path("nepal_candidates.db")
TABLE_NAME = "candidates"

def main():
    nepal_election_processor.import_excel_to_sqlite(EXCEL_PATH, DB_PATH, TABLE_NAME)
    print(f"Imported Excel into SQLite DB: {DB_PATH.resolve()} (table: {TABLE_NAME})")

    nepal_election_processor.print_all_columns(DB_PATH, TABLE_NAME)

    nepal_election_processor.print_sample_filtered_records(DB_PATH, TABLE_NAME)
    nepal_election_processor.add_age_group_processing_in_sql(DB_PATH, TABLE_NAME)

    nepal_election_processor.print_unique_values(
        DB_PATH,
        TABLE_NAME,
        column_name="शैक्षिक योग्यता (माथिल्लो शैक्षिक योग्यता)",
        include_counts=False
    )



if __name__ == "__main__":
    main()