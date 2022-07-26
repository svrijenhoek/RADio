import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path


class Visualize:

    @staticmethod
    def print_mean(df):
        print(df.groupby('type')['mean'].mean())
        print(df.groupby('type')['std'].mean())

    @staticmethod
    def plot(df, title):
        plt.figure(title)
        df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")
        df = df.sort_values('date', ascending=True)
        df.set_index('date', inplace=True)
        df.groupby('type')['mean'].plot(legend=True, title=title)
        plt.xticks(rotation='vertical')
        plt.draw()

    @staticmethod
    def violin_plot(df, output_folder):
        columns = list(df.columns)[2:8]
        fig, axs = plt.subplots(ncols=len(columns))
        for i, column in enumerate(columns):
            sns.violinplot(data=df, x=column, y="rec_type", inner="quart", split=True, ax=axs[i])
        plt.show(block=True)
        fig.savefig(Path(output_folder+'metrics.png'))

        columns = list(df.columns)[7:]
        fig, axs = plt.subplots(ncols=len(columns))
        for i, column in enumerate(columns):
            sns.violinplot(data=df, x=column, y="rec_type", inner="quart", split=True, ax=axs[i])
        plt.show(block=True)
        fig.savefig(Path(output_folder+'alternative_voices.png'))

    @staticmethod
    def boxplot(df):
        df.boxplot(column=list(df.columns)[2:8], by='rec_type', grid=False)
        df.boxplot(column=list(df.columns)[7:], by='rec_type', grid=False)
        # df['alternative_voices'] = df['alternative_voices'].where(df['alternative_voices'] <= 1, 1)
        plt.show(block=True)

    @staticmethod
    def violin_plot_per_distance(df, output_folder):
        pd.options.mode.chained_assignment = None
        columns = list(df.columns)[2:8]
        metrics = ['kl', 'kl_symm', 'jsd']
        for i, column in enumerate(columns):
            fig, axs = plt.subplots(ncols=len(metrics))
            fig.suptitle(column)
            df1 = df[['rec_type']]
            try:
                df1['kl'], df1['jsd'], df1['kl_symm'] = df[column].str
                print(column)
                print(df1.groupby('rec_type').mean())
                for a, metric in enumerate(metrics):
                    sns.violinplot(data=df1, x=metric, y="rec_type", inner="quart", split=True, ax=axs[a],
                                   title=column)
            except ValueError:
                pass
        plt.show(block=True)

    @staticmethod
    def violin_plot_on_jsd(df):
        df1 = df.copy()
        columns = list(df1.columns)[2:8]
        for i, column in enumerate(columns):
            _, df1[column], _ = df1[column].str

        f, axs = plt.subplots(nrows=2, ncols=3)
        sns.violinplot(data=df1, x='calibration_topic', y="rec_type", inner="quart", split=True, ax=axs[0][0])
        sns.violinplot(data=df1, x='calibration_complexity', y="rec_type", inner="quart", split=True, ax=axs[0][1])
        sns.violinplot(data=df1, x='fragmentation', y="rec_type", inner="quart", split=True, ax=axs[0][2])
        sns.violinplot(data=df1, x='affect', inner="quart", y="rec_type", split=True, ax=axs[1][0])
        sns.violinplot(data=df1, x='representation', y="rec_type", inner="quart", split=True, ax=axs[1][1])
        sns.violinplot(data=df1, x='alternative_voices', y="rec_type", inner="quart", split=True, ax=axs[1][2])
        plt.show()

    @staticmethod
    def visualize(df, cutoff, distance):
        df = df.loc[(df['cutoff'] == cutoff) & (df['distance'] == distance)]
        sns.catplot(x="rec_type", y="value",
                    hue="discount", col="metric",
                    data=df, kind="boxen",
                    height=4, aspect=.7, col_wrap=3)
        plt.show()
