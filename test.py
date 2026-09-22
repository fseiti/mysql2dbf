import pandas as pd
import dbf

csv_file = r"C:\Projects\MS\Tabnet\pnsab_202609211443.csv"
dbf_file = "output.dbf"

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
    "v0022": "N(2,0)",
    "v0026": "C(1)",
    "v0031": "C(1)",
    "v0025a": "C(1)",
    "v0025b": "C(1)",
    "a001": "C(1)",
    "a002010": "C(1)",
    "a003010": "C(1)",
    "a004010": "C(1)",
    "a01001": "N(2,0)",
    "a011": "N(2,0)",
    "a005010": "C(1)",
    "a005012": "C(1)",
    "a00601": "C(1)",
    "a009010": "C(1)",
    "a01401": "N(2,0)",
    "a01402": "N(2,0)",
    "a01403": "C(1)",
    "a01501": "C(1)",
    "a016010": "C(1)",
    "a018011": "C(1)",
    "a018012": "N(2,0)",
    "a018013": "C(1)",
    "a018014": "N(2,0)",
    "a018015": "C(1)",
    "a018016": "N(2,0)",
    "a018017": "C(1)",
    "a018018": "N(2,0)",
    "a018019": "C(1)",
    "a018020": "N(2,0)",
    "a018021": "C(1)",
    "a018022": "N(2,0)",
    "a018023": "C(1)",
    "a018024": "N(2,0)",
    "a018025": "C(1)",
    "a018026": "N(2,0)",
    "a018027": "C(1)",
    "a018028": "N(2,0)",
    "a01901": "C(1)",
    "a02101": "C(1)",
    "a02102": "N(2,0)",
    "a02201": "C(1)",
    "a02305": "N(2,0)",
    "a02306": "N(2,0)",
    "a02307": "N(2,0)",
    "a02308": "N(2,0)",
    "a02401": "N(2,0)",
    "a02402": "N(2,0)",
    "b001": "C(1)",
    "b002": "C(1)",
    "b003": "C(1)",
    "b004": "C(1)",
    "v0028": "N(15,8)",
    "v0029": "N(15,8)",
    "v0030": "N(18,8)",
    "v00281": "N(15,8)",
    "v00291": "N(15,8)",
    "v00301": "N(18,8)",
    "v00282": "N(9,0)",
    "v00292": "N(18,8)",
    "v00302": "N(18,8)",
    "v00283": "C(3)",
    "v00293": "C(5)",
    "v00303": "C(2)",
    "vdc001": "N(2,0)",
    "vdc003": "N(2,0)",
    "vdd004a": "C(1)",
    "vde001": "C(1)",
    "vde002": "C(1)",
    "vde014": "C(2)",
    "vdf002": "N(8,0)",
    "vdf003": "N(8,0)",
    "vdf004": "C(1)",
    "vdl001": "N(2,0)",
    "vdm001": "C(1)",
    "vdp001": "C(1)",
    "vdr001": "C(1)",
    "vddata": "C(8)",
    "estupa": "C(20)",
    "estupa_seq": "N(5,0)",
    "chavedom": "N(1,0)",
    "domicilios": "N(15,8)",
    "moradores": "N(15,8)",
    "comodos": "N(15,8)",
    "comoddorm": "N(15,8)",
    "domaguacan": "N(15,8)",
    "pesaguacan": "N(15,8)",
    "domesgsan": "N(15,8)",
    "pesesgsan": "N(15,8)",
    "domlixlimp": "N(15,8)",
    "peslixlimp": "N(15,8)",
    "domeletric": "N(15,8)",
    "peseletric": "N(15,8)",
    "domcachor": "N(15,8)",
    "pescachor": "N(15,8)",
    "domgatos": "N(15,8)",
    "pesgatos": "N(15,8)",
    "domraiva": "N(15,8)",
    "pesraiva": "N(15,8)",
    "domcachgat": "N(15,8)",
    "pescachgat": "N(15,8)",
    "domcadusf": "N(15,8)",
    "pescadusf": "N(15,8)",
    "domcad1a": "N(15,8)",
    "pescad1a": "N(15,8)",
    "domvisacs": "N(15,8)",
    "pesvisacs": "N(15,8)",
    "domsvisacs": "N(15,8)",
    "pessvisacs": "N(15,8)",
    "domvisend": "N(15,8)",
    "pesvisend": "N(15,8)",
    "pontosbr": "N(1,0)"
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