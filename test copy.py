import pandas as pd
import dbf

csv_file = r"C:\Projects\MS\Tabnet\scripts\csv\pnsn.csv"
dbf_file = "pnsn.dbf"

# ---------------------------------------------------------
# Read everything as string to preserve leading zeros
# ---------------------------------------------------------

df = pd.read_csv(
    csv_file,
    sep=",",
    dtype=str,
    low_memory=False
)

# ---------------------------------------------------------
# Clean column names
# ---------------------------------------------------------

df.columns = df.columns.str.strip().str.lower()

# ---------------------------------------------------------
# Schema: column -> DBF type
# ---------------------------------------------------------

schema = {
    "v0001": "C(2)",
    "v0024": "C(7)",
    "upa_pns": "C(9)",
    "v0006_pns": "C(4)",
    "v0015": "C(2)",
    "v0020": "C(4)",
    "v0022": "N(3,0)",
    "v0026": "C(1)",
    "v0031": "C(1)",
    "v0025a": "C(1)",
    "v0025b": "C(1)",
    "g059": "C(1)",
    "n001": "C(1)",
    "n00101": "C(1)",
    "n004": "C(1)",
    "n005": "C(1)",
    "n006": "C(1)",
    "n00701": "C(1)",
    "n008": "C(1)",
    "n010": "C(1)",
    "n011": "C(1)",
    "n012": "C(1)",
    "n013": "C(1)",
    "n014": "C(1)",
    "n015": "C(1)",
    "n016": "C(1)",
    "n017": "C(1)",
    "n018": "C(1)",
    "v0028": "N(15,8)",
    "v0029": "N(15,8)",
    "v0030": "N(18,8)",
    "v00281": "N(15,8)",
    "v00291": "N(15,8)",
    "v00301": "N(18,8)",
    "v00282": "N(10,0)",
    "v00292": "N(18,8)",
    "v00302": "N(18,8)",
    "v00283": "C(3)",
    "v00293": "C(5)",
    "v00303": "C(2)",
    "vdc001": "N(3,0)",
    "vdc003": "N(3,0)",
    "vdd004a": "C(1)",
    "vde001": "C(1)",
    "vde002": "C(1)",
    "vde014": "C(2)",
    "vdf002": "N(9,0)",
    "vdf003": "N(9,0)",
    "vdf004": "C(1)",
    "vdl001": "N(3,0)",
    "vdm001": "C(1)",
    "vdp001": "C(1)",
    "vdr001": "C(1)",
    "vddata": "C(8)",
    "estupa": "C(20)",
    "estupa_seq": "N(6,0)",
    "denmodn": "N(15,8)",
    "numaval": "N(15,8)",
    "numloco1": "N(15,8)",
    "numloco2": "N(15,8)",
    "numloco3": "N(15,8)",
    "denangina": "N(15,9)",
    "numangina2": "N(15,8)",
    "numangina1": "N(15,8)"
}

# ---------------------------------------------------------
# Check CSV and schema
# ---------------------------------------------------------

missing = set(schema) - set(df.columns)
extra = set(df.columns) - set(schema)

if missing:
    print("Missing columns:")
    for col in sorted(missing):
        print(f"  - {col}")

    raise ValueError(
        "CSV is missing columns required by the schema."
    )

if extra:
    print("Extra columns in CSV (will be ignored):")
    for col in sorted(extra):
        print(f"  - {col}")

# Keep only schema columns and in schema order
df = df[list(schema.keys())]

# ---------------------------------------------------------
# Validate character field lengths
# ---------------------------------------------------------

for column, dbf_type in schema.items():

    if dbf_type.startswith("C"):

        max_length = int(
            dbf_type.split("(")[1].split(")")[0]
        )

        values = df[column].dropna().astype(str)

        too_long = values[
            values.str.len() > max_length
        ]

        if len(too_long) > 0:

            print(
                f"WARNING: {column} contains "
                f"{len(too_long)} value(s) longer "
                f"than {max_length} characters."
            )

            print(too_long.head())

# ---------------------------------------------------------
# Create DBF
# ---------------------------------------------------------

field_specs = [
    f"{column} {dbf_type}"
    for column, dbf_type in schema.items()
]

table = dbf.Table(
    dbf_file,
    "; ".join(field_specs)
)

table.open(dbf.READ_WRITE)

# ---------------------------------------------------------
# Insert data
# ---------------------------------------------------------

for row in df.itertuples(index=False, name=None):

    values = []

    for value, (column, dbf_type) in zip(
        row,
        schema.items()
    ):

        # Missing value
        if pd.isna(value) or str(value).strip() == "":
            values.append(None)
            continue

        # Character
        if dbf_type.startswith("C"):
            values.append(str(value))

        # Numeric
        elif dbf_type.startswith("N"):

            try:
                values.append(float(value))

            except ValueError:

                raise ValueError(
                    f"Invalid numeric value '{value}' "
                    f"in column '{column}'"
                )

        else:
            values.append(value)

    table.append(tuple(values))

table.close()

print(f"Created: {dbf_file}")
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")