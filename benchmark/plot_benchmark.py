import os

from matplotlib import pyplot

from run_benchmark import benchmarks, REPO_PATH, DB_PATH

PLOT_DIR = os.path.join(REPO_PATH, 'tmp', 'plot')


def main():
    if not os.path.isdir(PLOT_DIR):
        os.makedirs(PLOT_DIR)

    for bm in benchmarks:
        fig = pyplot.figure()
        bm.plot(DB_PATH, ax=pyplot.gca())
        figpath = os.path.join(PLOT_DIR, '{0}.png'.format(bm.name))
        fig.savefig(figpath, bbox_inches='tight')


if __name__ == '__main__':
    main()
