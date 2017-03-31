CREATE TABLE edxapp.question_template (
	id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
	xblock_id VARCHAR(255) NOT NULL UNIQUE,
	template VARCHAR(2048) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci AUTO_INCREMENT=40;

CREATE TABLE edxapp.variable (
	id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
	xblock_id VARCHAR(255) NOT NULL,
	name VARCHAR(32),
	type VARCHAR(32),
	min_value INT(6),
	max_value INT(6),
	accuracy INT(3),
	FOREIGN KEY (xblock_id) REFERENCES edxapp.question_template(xblock_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci AUTO_INCREMENT=40;

CREATE TABLE edxapp.expression (
	id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
	xblock_id VARCHAR(255) NOT NULL,
	name VARCHAR(32),
	formula VARCHAR(2048) NOT NULL,
	accuracy INT(3),
	FOREIGN KEY (xblock_id) REFERENCES edxapp.question_template(xblock_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci AUTO_INCREMENT=40;