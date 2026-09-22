import json
import logging
import re
import sys
from pathlib import Path
import dbf
import mysql.connector
import pandas as pd


BASE_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"
LOG_FILE = BASE_DIR / "Mysql2dbf.log"

logging.basicConfig(
	filename=LOG_FILE,
	level=logging.INFO,
	format="%(asctime)s [%(levelname)s] %(message)s",
	encoding="utf-8",
)
LOGGER = logging.getLogger(__name__)


def load_config():
	LOGGER.info("Loading configuration from %s", CONFIG_FILE)
	try:
		with CONFIG_FILE.open(encoding="utf-8") as file:
			config = json.load(file)
	except FileNotFoundError as error:
		raise FileNotFoundError(
			f"Configuration file not found: {CONFIG_FILE}"
		) from error

	db_config = config["db"]
	return {
		"db": {
			"host": db_config["host"],
			"port": int(db_config["port"]),
			"user": db_config["user"],
			"password": db_config["password"],
			"database": db_config["database"],
		},
		"table_name": config["table_name"],
		"dbf_file": str(BASE_DIR / config["dbf_file"]),
	}


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


def export_select_to_dbf(config):
	LOGGER.info(
		"Starting export: %s.%s -> %s",
		config["db"]["database"],
		config["table_name"],
		config["dbf_file"],
	)
	connection_options = {
		**config["db"],
		"connection_timeout": 10,
		"use_pure": True,
	}
	print(f"Conversão iniciada: {config['db']['database']}.{config['table_name']} -> {config['dbf_file']}")
	try:
		connection = mysql.connector.connect(**connection_options)
	except Exception as error:
		LOGGER.exception(
			"MySQL connection failed for %s:%s/%s",
			config["db"]["host"],
			config["db"]["port"],
			config["db"]["database"],
		)
		db = config["db"]
		raise ConnectionError(
			"Could not connect to MySQL at "
			f"{db['host']}:{db['port']} "
			f"using database '{db['database']}'. "
			f"Check that MySQL is running and verify host, port, user, "
			f"password, and database in {CONFIG_FILE}. MySQL error: {error}"
		) from error

	try:
		cursor = connection.cursor()
		cursor.execute(
			"""
			SELECT COLUMN_NAME, COLUMN_TYPE
			FROM INFORMATION_SCHEMA.COLUMNS
			WHERE TABLE_NAME = %s
			ORDER BY ORDINAL_POSITION
			""",
			(config["db"]["database"], config["table_name"]),
		)
		metadata = cursor.fetchall()
		if not metadata:
			LOGGER.error(
				"Table not found: %s.%s",
				config["db"]["database"],
				config["table_name"],
			)
			raise ValueError(
				f"Table not found: {config['db']['database']}.{config['table_name']}"
			)

		columns = [column_name for column_name, _ in metadata]
		field_types = [
			dbf_type_from_mysql(column_type)
			for _, column_type in metadata
		]

		cursor.execute(
			f"SELECT * FROM `{config['db']['database']}`.`{config['table_name']}`"
		)
		rows = cursor.fetchall()
		LOGGER.info("Read %s rows and %s columns", len(rows), len(columns))
	finally:
		cursor.close()
		connection.close()

	dataframe = pd.DataFrame(rows, columns=columns)
	field_names = make_field_names(columns)

	table = dbf.Table(
		config["dbf_file"],
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

	print(f"Criado: {config['dbf_file']}")
	print(f"Linhas: {len(dataframe):,}")
	print(f"Colunas: {len(columns)}")
	LOGGER.info("Export completed: %s rows and %s columns", len(dataframe), len(columns))


if __name__ == "__main__":
	try:
		export_select_to_dbf(load_config())
	except Exception as error:
		LOGGER.exception("Export failed")
		print(f"ERROR: {error}")
		print(f"Detalhes em: {LOG_FILE}")
		sys.exit(1)
