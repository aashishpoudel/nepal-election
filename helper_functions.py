
def to_number(x):
    """Safely convert age to int; return None if not possible."""
    import pandas as pd
    if pd.isna(x):
        return None
    s = str(x).strip()
    if not s:
        return None
    # Extract first number if the cell contains extra text
    m = pd.to_numeric(s, errors="coerce")
    if pd.notna(m):
        return int(m)
    # fallback: regex extract
    import re
    mm = re.search(r"\d+", s)
    return int(mm.group()) if mm else None

def filter_by_parties(df, party_column, parties_dict, output_path=None):
    """
    Filter rows where party_column contains any party name in parties_dict keys.

    Parameters
    ----------
    df : pd.DataFrame
        Original dataframe
    party_column : str
        Column name that contains party names
    parties_dict : dict
        PARTIES dictionary from nepal_election_constants
    output_path : str, optional
        If provided, saves filtered dataframe to Excel

    Returns
    -------
    pd.DataFrame
        Filtered dataframe
    """
    import re
    import pandas as pd

    if party_column not in df.columns:
        raise KeyError(f"Column '{party_column}' not found in dataframe")

    party_names = list(parties_dict.keys())

    # Create regex pattern for "contains any party"
    pattern = "|".join(re.escape(p) for p in party_names)

    mask = (
        df[party_column]
        .astype(str)
        .str.contains(pattern, regex=True, na=False)
    )

    df_filtered = df.loc[mask].copy()

    if output_path:
        df_filtered.to_excel(output_path, index=False)
        print(f"Filtered file saved: {output_path} (rows={len(df_filtered)})")

    return df_filtered