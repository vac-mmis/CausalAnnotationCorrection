CONFIG_NAME = "config.toml"
DEFAULT_CONFIG = {
    "Annotation": {
        "regex_expression_structure": r"[a-zA-Z0-9]+(_[a-zA-Z0-9]+)*(-[a-zA-Z0-9]+(_[a-zA-Z-0-9]+)*)*",
        "regex_characters": r"[^a-zA-Z0-9,_-]",
        "regex_time": r"[^0-9.-]",

        "lang": "en_US",
        "whitespace_divider": "_",
        "term_divider": "-",
        "csv_delimiter": ",",
        "csv_quotechar": "|",
        "csv_columns": 2,
        "csv_sniffer_size": 1024,
    },

    "SpellCheck": {
        "candidates": 3,
    },
    "Validator": {
        "path": "",
        "timeout": 5
    },
    "DomainProblemCheck": {
        "timeout": 5
    }
}
ERROR_FILE_NAME = "errors.json"
GROUP_FILE_NAME = "groups.json"
GROUP_DOMAIN_FILE_NAME = "groups_d.json"
GROUP_PROBLEM_FILE_NAME = "groups_p.json"
OUTPUT = "output"
PERSONAL_EXCLUDE_LIST = "pel"
PERSONAL_WORD_LIST = "pwl"
PLAN_FILE_NAME = "plan.txt"
SIGNATURE_FILE = "sign.json"
STANDARD_PORT = 9000
THREADING_LOCK_TIMEOUT = 15
