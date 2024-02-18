#  Copyright (C) 2023 Y Hsu <yh202109@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public license as published by
#  the Free software Foundation, either version 3 of the License, or
#  any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details
#
#  You should have received a copy of the GNU General Public license
#  along with this program. If not, see <https://www.gnu.org/license/>

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def plot_ridge_logx(df, group_col, y_col, x_scale_base=10):
    """
    Plot ridge plots with logarithmic x-axis.

    Args:
        df (pandas.DataFrame): The input DataFrame.
        group_col (str): The column name used for grouping the data.
        y_col (str): The column name used for the y-axis values.
        x_scale_base (int, optional): The base value for the logarithmic x-axis scale. Defaults to 10.

    Returns:
        matplotlib.pyplot: The resulting plot.

    """
    df = df.sort_values(group_col).reset_index()
    sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})

    # Initialize the FacetGrid object
    pal = sns.cubehelix_palette(10, rot=-.25, light=.7)
    g = sns.FacetGrid(df, row=group_col, hue=group_col, aspect=15, height=0.5, palette=pal)

    # Draw the densities in a few steps
    g.map(sns.kdeplot, y_col,
        bw_adjust=.5, clip_on=False,
        fill=True, alpha=0.7, linewidth=1.5)
    g.map(sns.kdeplot, y_col, clip_on=False, color="w", lw=2, bw_adjust=.5)

    # passing color=None to refline() uses the hue mapping
    g.refline(y=0, linewidth=2, linestyle="-", color=None, clip_on=False)

    # Define and use a simple function to label the plot in axes coordinates
    def label(x, color, label):
        ax = plt.gca()
        ax.text(0, .2, label, fontweight="bold", color=color,
                ha="left", va="center", transform=ax.transAxes)

    g.map(label, y_col)

    # Set the subplots to overlap
    g.figure.subplots_adjust(hspace=-.25)

    # Remove axes details that don't play well with overlap
    g.set_titles("")
    g.set(yticks=[], ylabel="")
    g.despine(bottom=True, left=True)
    if x_scale_base > 0:
        plt.xscale('log', base=x_scale_base)

    group_counts = df.groupby(group_col, dropna=True).size()
    geometric_means = df.groupby(group_col)[y_col].apply(lambda x: np.exp(np.mean(np.log(x))))
    combined_data = pd.concat([group_counts, geometric_means], axis=1)
    combined_data.columns = ['Group_Count', 'Geometric_Mean']
    combined_data.reset_index(inplace=True)
    print(combined_data.head())

    for i in range(len(combined_data)):
        count = combined_data['Group_Count'][i]
        mean = combined_data['Geometric_Mean'][i]
        group = combined_data[group_col][i]
        nan_percentage = df[df[group_col] == combined_data[group_col][i]][y_col].isna().mean() * 100
        g.axes[i, -1].text(1.02, 0.5, f'N({group}): {count}\nGM: {mean:.2f}\n%NaN: {nan_percentage:.2f}', transform=g.axes[i, -1].transAxes, va='center')

    return plt


def plot_hbox_logx(df, group_col, y_col, fn_x=0.5, fn_y=0.01, pt_size=5, x_scale_base=10, title=""):
    """
    Plot a horizontal boxplot with logarithmic x-axis.

    Parameters:
    - df: DataFrame
        The input DataFrame containing the data to be plotted.
    - group_col: str
        The column name in the DataFrame to group the data by.
    - y_col: str
        The column name in the DataFrame representing the y-axis values.
    - fn_x: float, optional
        The x-coordinate of the text annotation.
    - fn_y: float, optional
        The y-coordinate of the text annotation.
    - pt_size: int, optional
        The size of the points in the stripplot.
    - x_scale_base: int, optional
        The base value for the logarithmic x-axis scale.


    Returns:
    None
    """
    # reference: https://seaborn.pydata.org/examples/horizontal_boxplot.html

    sns.set_theme(style="ticks")
    f, ax = plt.subplots(figsize=(7, 6))
    df = df.sort_values(group_col).reset_index()
    if x_scale_base > 0:
        ax.set_xscale("log", base=x_scale_base)

    # Plot the orbital period with horizontal boxes
    sns.boxplot(df, x=y_col, y=group_col, hue=group_col, whis=[0, 100], width=.6, palette="vlag")

    # Add in points to show each observation
    sns.stripplot(df, x=y_col, y=group_col, size=pt_size, color=".3", alpha=0.3)
    #plt.text(fn_x, fn_y, "Whiskers: range. Box: inter-quartile range (IQR).", transform=ax.transAxes, ha='center')

    group_counts = df.groupby(group_col, dropna=True).size()
    geometric_means = df.groupby(group_col)[y_col].apply(lambda x: np.exp(np.mean(np.log(x))))
    nan_percentage = df.groupby(group_col)[y_col].isna().mean()*100
    combined_data = pd.concat([group_counts, geometric_means, nan_percentage], axis=1)
    combined_data.columns = ['Group_Count', 'Geometric_Mean', 'Nan_Percentage']
    combined_data.reset_index(inplace=True)


    for i in range(len(combined_data)):
        mean = combined_data['Geometric_Mean'][i]
        count = combined_data['Group_Count'][i]
        group = combined_data[group_col][i]
        pctnan = combined_data['Nan_Percentage'][i]
        ax.text(ax.get_xlim()[1], i, f'N: {count}\nGM: {mean:.2f}\nNaN: {pctnan:.2f}%', va='center', ha='left')

    plt.tight_layout()

    # Tweak the visual presentation

    ax.set_title(title)
    ax.xaxis.grid(True)
    ax.set(ylabel="")
    sns.despine(trim=False, left=True)

    plt.show()

if __name__ == "__main__": 
    # Example usage of plot_density function 
    group = np.random.choice(['A', 'B', 'C','D','E'], size=100)
    value = np.random.normal(0, 1, size=100)
    df = pd.DataFrame({'Group': group, 'Value': value})
    df.loc[df['Group'] == 'B', 'Value'] += 2
    df.loc[df['Group'] == 'C', 'Value'] += 3
    df['Value'] = np.exp(np.abs(df['Value'])+2)
    

    df = df.sort_values('Group')
    plt = plot_hbox_logx(df, 'Group', 'Value', x_scale_base=5)
    #plt = plot_ridge_logx(df, 'Group', 'Value', x_scale_base=2)
    #plt.show()