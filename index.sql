CREATE TABLE files (
	id INTEGER PRIMARY KEY,
	dir_rel TEXT,
	name TEXT,
	radar TEXT,
	ftype TEXT,
	angle FLOAT,
	ts DATETIME,
	quantities TEXT,
	ts_extra DATETIME,
	source_id INTEGER NOT NULL,
	FOREIGN KEY(source_id) REFERENCES sources(id)
);
CREATE TABLE sources (
	id INTEGER PRIMARY KEY,
	name TEXT,
	ts DATETIME
);
CREATE INDEX idx_files_ts ON files(ts);
CREATE INDEX idx_files_radar ON files(radar);
