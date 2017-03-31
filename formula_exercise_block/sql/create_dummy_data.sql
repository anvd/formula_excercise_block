INSERT INTO edxapp.question_template (xblock_id, question_template) VALUES (?, ?)


INSERT INTO edxapp.variable (xblock_id, name, type, min_value, max_value, accuracy) VALUES (?, a, int, 0, 10, 2)
INSERT INTO edxapp.variable (xblock_id, name, type, min_value, max_value, accuracy) VALUES (?, b, int, 10, 100, 2)


INSERT INTO edxapp.expression (xblock_id, name, formula, accuracy) VALUES (?, Tong, a+b, accuracy)
INSERT INTO edxapp.expression (xblock_id, name, formula, accuracy) VALUES (?, Hieu, a-b, accuracy)
