-- Create custom tables for the testing
CREATE TABLE IF NOT EXISTS test_table(
	id INT,
    integer  INT,
	text_col TEXT,
	attribute_col TEXT,
	bool_col BOOL,

	PRIMARY KEY(id));

-- Insert dummy data into test_table
INSERT INTO test_table(
	id,
    integer,
	text_col,
	attribute_col,
	bool_col)
VALUES
(1, 1, 'first', 'attr_1', false),
(2, 2, 'second', null,  true),
(3, NULL, 'third', 'attr_1', false),
(4, 4, 'fourth', 'attr_3', true);
