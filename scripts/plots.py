import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

from utils import LATEST_DATA


mpl.rcParams['svg.hashsalt'] = 'trending-header'


def plot_header_img():
    import matplotlib as mpl
    mpl.rcParams['axes.spines.left'] = False
    mpl.rcParams['axes.spines.right'] = False
    mpl.rcParams['axes.spines.top'] = False
    mpl.rcParams['axes.spines.bottom'] = False

    df = pd.read_csv(LATEST_DATA)
    df['query_date'] = pd.to_datetime(df['query_date'])
    df = df.query_date.groupby(df.query_date.dt.year).agg('count')

    fig, ax = plt.subplots(1, figsize=(12, 3))

    ax.plot(df.index, df.values, color='#FF053E', linewidth=4)
    ax.plot(df.index[-1], df.values[-1],
            'o-', linewidth=4,
            markerfacecolor='#FAF82E', markeredgewidth=3,
            markersize=12, color='#FF053E')

    ax.set_xticks(df.index)
    ax.tick_params(colors='#777')
    plt.savefig('imgs/year_mails_count.svg',
                transparent=True, metadata={'Date': None})


if __name__ == '__main__':
    plot_header_img()
