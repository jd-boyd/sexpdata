"""
Plot benchmark result.

You need to run run_benchmark.py first to generate benchmark data.

"""

import os

from matplotlib import pyplot

from run_benchmark import benchmarks, REPO_PATH, DB_PATH

PLOT_DIR = os.path.join(REPO_PATH, "tmp", "plot")

html_template = """
<html>
<body>
{0}
</body>
</html>
"""

img_template = """
<img style="width-max: 100%;" src="{0}">
"""


def generate_html(fignames):
    return html_template.format("\n".join(map(img_template.format, fignames)))


def main():
    if not os.path.isdir(PLOT_DIR):
        os.makedirs(PLOT_DIR)

    figname_list = []
    for bm in benchmarks:
        fig = pyplot.figure()
        bm.plot(DB_PATH, ax=pyplot.gca())
        figname = "{0}.png".format(bm.name)
        figpath = os.path.join(PLOT_DIR, figname)
        fig.savefig(figpath, bbox_inches="tight")
        figname_list.append(figname)

    with open(os.path.join(PLOT_DIR, "index.html"), "w") as f:
        f.write(generate_html(figname_list))


if __name__ == "__main__":
    main()
