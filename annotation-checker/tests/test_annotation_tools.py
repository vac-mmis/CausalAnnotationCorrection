from os.path import join
from acheck.utils.annotationhelper import read_annotation


def test_parse_read_annotation(test_dir):
	with open(join(test_dir, "example.csv")) as f:
		expected = f.read()
	anno_as_list = read_annotation(join(test_dir, "example.csv"),-1)
	string_to_test = ("\n".join(anno_as_list))

	assert string_to_test == expected

