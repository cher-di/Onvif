import argparse

ZEEP_FIX = """import zeep
def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue
zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue
"""

CREDENTIALS = """IP = "172.18.212.17"  # Camera IP address
PORT = 80  # Port
USER = "laba2102"  # Username
PASS = "TMPpassword"  # Password
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert file for grader")
    parser.add_argument("source_filepath",
                        help="Path to file to convert")
    parser.add_argument("target_filepath",
                        help="Path to converted file")
    return parser.parse_args()


def convert(source_filepath: str, target_filepath: str) -> str:
    IMPORT_ZEEP_FIX = "import zeep_fix\n"
    IMPORT_CREDENTIALS = "from credentials import *\n"

    with open(source_filepath, "rt") as file:
        lines = file.readlines()
    for num, line in enumerate(lines):
        if line == IMPORT_ZEEP_FIX:
            lines[num] = ZEEP_FIX
        elif line == IMPORT_CREDENTIALS:
            lines[num] = CREDENTIALS
        else:
            pass

    with open(target_filepath, "wt") as file:
        file.writelines(lines)


if __name__ == '__main__':
    args = parse_args()
    try:
        convert(args.source_filepath, args.target_filepath)
    except Exception as e:
        print(e)
        exit(1)
