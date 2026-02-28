
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