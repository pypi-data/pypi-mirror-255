import pandas as pd


def reset_column_name_indices(df: pd.DataFrame):
    """Resets the suffix indices of dataframe columns;
    s.t. `name.1` becomes `name` if there is only one."""

    def __get_real_name(col: str) -> str:
        return col.split(".")[0]

    columns = df.columns
    unique_cols = set([__get_real_name(col) for col in columns])
    appearances = {col: 0 for col in unique_cols}
    new_cols = []
    for col in columns:
        real_name = __get_real_name(col)
        if appearances[real_name] == 0:
            new_cols.append(real_name)
        else:
            new_name = f"{real_name}.{appearances[real_name]}"
            new_cols.append(new_name)
        appearances[real_name] += 1

    was_updated = any(old != new for old, new in zip(df.columns, new_cols))
    if was_updated:
        print(f"Updated df columns to: {new_cols}")

    df.columns = new_cols
