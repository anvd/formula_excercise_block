INSERT INTO edxapp.question_template (xblock_id, question_template) VALUES (?, ?)


INSERT INTO edxapp.variable (xblock_id, name, type, min_value, max_value, decimal_places) VALUES (?, a, int, 0, 10, 2)
INSERT INTO edxapp.variable (xblock_id, name, type, min_value, max_value, decimal_places) VALUES (?, b, int, 10, 100, 2)


INSERT INTO edxapp.expression (xblock_id, name, formula, decimal_places) VALUES (?, Tong, float, a+b, decimal_places)
INSERT INTO edxapp.expression (xblock_id, name, formula, decimal_places) VALUES (?, Hieu, float, a-b, decimal_places)
