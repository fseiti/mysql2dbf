import os
import re
import dbf
import mysql.connector
import pandas as pd


# Configure these values for the database and table to export.
DB_CONFIG = {
	"host": os.getenv("MYSQL_HOST", "localhost"),
	"port": int(os.getenv("MYSQL_PORT", "3306")),
	"user": os.getenv("MYSQL_USER", "root"),
	"password": os.getenv("MYSQL_PASSWORD", ""),
	"database": os.getenv("MYSQL_DATABASE", "test"),
}
TABLE_SCHEMA = "test"
TABLE_NAME = "pnsn"
DBF_FILE = "output.dbf"


def make_field_names(columns):
	"""Return unique DBF field names (DBF names are limited to 10 characters)."""
	names = []
	used = set()

	for column in columns:
		base = re.sub(r"[^A-Za-z0-9_]", "_", str(column)).upper()[:10] or "FIELD"
		name = base
		suffix = 1
		while name in used:
			suffix_text = str(suffix)
			name = f"{base[:10 - len(suffix_text)]}{suffix_text}"
			suffix += 1
		names.append(name)
		used.add(name)

	return names


def dbf_type_from_mysql(column_type):
	"""Convert MySQL COLUMN_TYPE to a DBF field definition."""
	type_name = column_type.lower()
	match = re.match(r"([a-z]+)(?:\((\d+)(?:,(\d+))?\))?", type_name)
	if not match:
		raise ValueError(f"Unsupported MySQL COLUMN_TYPE: {column_type}")

	base_type, first_size, second_size = match.groups()

	if base_type in {"char", "varchar"}:
		return f"C({min(int(first_size), 254)})"
	if base_type in {"tinyint", "smallint", "mediumint", "int", "integer", "bigint"}:
		default_widths = {
			"tinyint": 3,
			"smallint": 5,
			"mediumint": 8,
			"int": 10,
			"integer": 10,
			"bigint": 19,
		}
		width = int(first_size or default_widths[base_type])
		return f"N({min(max(width, 1), 20)},0)"
	if base_type in {"decimal", "numeric"}:
		precision = min(int(first_size or 18) + 1, 20)
		scale = min(int(second_size or 0), precision - 1)
		return f"N({precision},{scale})"
	if base_type in {"float", "double", "real"}:
		# Leave enough room for large integer portions in DBF numeric fields.
		return "N(20,6)"
	if base_type == "date":
		return "D"

	# DBF character fields cannot exceed 254 bytes.
	return "C(254)"


def export_select_to_dbf():
	connection = mysql.connector.connect(**DB_CONFIG)

	try:
		cursor = connection.cursor()
		cursor.execute(
			"""
			SELECT COLUMN_NAME, COLUMN_TYPE
			FROM INFORMATION_SCHEMA.COLUMNS
			WHERE TABLE_SCHEMA = %s
			  AND TABLE_NAME = %s
			ORDER BY ORDINAL_POSITION
			""",
			(TABLE_SCHEMA, TABLE_NAME),
		)
		metadata = cursor.fetchall()
		if not metadata:
			raise ValueError(f"Table not found: {TABLE_SCHEMA}.{TABLE_NAME}")

		columns = [column_name for column_name, _ in metadata]
		field_types = [
			dbf_type_from_mysql(column_type)
			for _, column_type in metadata
		]

		cursor.execute(
			f"SELECT * FROM `{TABLE_SCHEMA}`.`{TABLE_NAME}`"
		)
		rows = cursor.fetchall()
	finally:
		cursor.close()
		connection.close()

	dataframe = pd.DataFrame(rows, columns=columns)
	field_names = make_field_names(columns)

	table = dbf.Table(
		DBF_FILE,
		"; ".join(
			f"{field_name} {field_type}"
			for field_name, field_type in zip(field_names, field_types)
		),
	)

	try:
		table.open(dbf.READ_WRITE)
		for row in dataframe.itertuples(index=False, name=None):
			converted = []
			for value, field_type in zip(row, field_types):
				if value is None or pd.isna(value) or str(value).strip() == "":
					converted.append(None)
				elif field_type.startswith("N"):
					converted.append(float(value))
				elif field_type == "D":
					converted.append(value)
				else:
					converted.append(str(value))
			table.append(tuple(converted))
	finally:
		table.close()

	print(f"Created: {DBF_FILE}")
	print(f"Rows: {len(dataframe):,}")
	print(f"Columns: {len(columns)}")


if __name__ == "__main__":
	export_select_to_dbf()
