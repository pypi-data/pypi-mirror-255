#!/usr/bin/env python
# coding: utf-8

import re
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

modules_path = os.path.dirname(os.path.realpath(__file__))
modules_path = os.path.join(modules_path, 'modules')
sys.path.append(modules_path)

from multicellds import MultiCellDS



def main():

    color_dict = {"live": "g", "apoptotic": "r", "necrotic":"k"}

    instance_folder = sys.argv[1]

    output_data = instance_folder + 'output/'

    mcds = MultiCellDS(output_folder=output_data)

    df_time_course = mcds.get_cells_summary_frame()
    df_cell_variables = get_timeserie_mean(mcds)
    df_time_tnf = get_timeserie_density(mcds)

    df_time_course.to_csv(instance_folder + "time_course.tsv", sep="\t")
    df_cell_variables.to_csv(instance_folder + "cell_variables.tsv", sep="\t")
    df_time_tnf.to_csv(instance_folder + "tnf_time.tsv", sep="\t")

    fig, axes = plt.subplots(3, 1, figsize=(12,12), dpi=150, sharex=True)
    plot_cells(df_time_course, color_dict, axes[0])
    
    list_of_variables = ['bound_external_TNFR', 'unbound_external_TNFR', 'bound_internal_TNFR']
    plot_molecular_model(df_cell_variables, list_of_variables, axes[1])
    threshold = 0.5
    
    axes[1].hlines(threshold, 0, df_time_course.time.iloc[-1], label="Activation threshold")
    ax2 = axes[1].twinx()
    ax2.plot(df_time_tnf.time, df_time_tnf['tnf'], 'r', label="[TNF]")
    ax2.set_ylabel("[TNF]")
    ax2.set_ylim([0, 1000])
    axes[1].legend(loc="upper left")
    ax2.legend(loc="upper right")

    list_of_variables = ['tnf_node', 'nfkb_node', 'fadd_node']
    plot_molecular_model(df_cell_variables, list_of_variables, axes[2])
    axes[2].set_xlabel("time (min)")
    ax2 = axes[2].twinx()
    ax2.plot(df_time_tnf.time, df_time_tnf['tnf'], 'r', label="[TNF]")
    ax2.set_ylabel("[TNF]")
    ax2.set_ylim([0, 1000])
    axes[2].legend(loc="upper left")
    ax2.legend(loc="upper right")

    fig.tight_layout()
    fig.savefig(instance_folder + 'variables_vs_time.png')


