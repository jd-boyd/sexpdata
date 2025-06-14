common_setup = """
import sexpdata
length = 10000
"""
do_loads = "sexpdata.loads(string)"

data = [
    {
        "code": do_loads,
        "setup": common_setup
        + r"""
string = '"{0}"'.format('x' * length)
""",
        "name": "Plain long string (plain:quote = 1:0)",
    },
    {
        "code": do_loads,
        "setup": common_setup
        + r"""
string = '"{0}"'.format(r'\"' * length)
""",
        "name": "Long string only with escaped quotes (plain:quote = 0:1)",
    },
    {
        "code": do_loads,
        "setup": common_setup
        + r"""
string = '"{0}"'.format(r'1\"' * length)
""",
        "name": "Long mixed string (plain:quote = 1:1)",
    },
    {
        "code": do_loads,
        "setup": common_setup
        + r"""
string = '"{0}"'.format(r'12345\"' * length)
""",
        "name": "Long mixed string (plain:quote = 5:1)",
    },
]
