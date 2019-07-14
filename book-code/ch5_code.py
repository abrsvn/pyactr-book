"""
Chapter 5 code.
"""


import numpy as np

import matplotlib as mpl
# mpl.use("pgf")
# pgf_with_pdflatex = {"text.usetex": True, "pgf.texsystem": "pdflatex",
                     # "pgf.preamble": [r"\usepackage{mathpazo}",
                                      # r"\usepackage[utf8x]{inputenc}",
                                      # r"\usepackage[T1]{fontenc}",
                                      # r"\usepackage{amsmath}"],
                     # "axes.labelsize": 8,
                     # "font.family": "serif",
                     # "font.serif":["Palatino"],
                     # "font.size": 8,
                     # "legend.fontsize": 8,
                     # "xtick.labelsize": 8,
                     # "ytick.labelsize": 8}
# mpl.rcParams.update(pgf_with_pdflatex)
import matplotlib.pyplot as plt
plt.style.use('seaborn')
import seaborn as sns
sns.set_style({"font.family":"serif", "font.serif":["Palatino"]})

import pandas as pd
import pymc3 as pm


every_each = pd.read_csv("./data/every_each.csv")
every_each["quant"] = every_each["quant"].astype('category')
every_each.shape
every_each.head(n=3)
every_each.iloc[[0, 8, 18, 31], :]


np.log(300)
np.log(600)
np.min(every_each["logRTresid"])
np.max(every_each["logRTresid"])


every_each_model = pm.Model()
with every_each_model:
    normal_density = pm.Normal('normal_density', mu=0, sd=10)

from pymc3.backends import Text
from pymc3.backends.text import load
#with every_each_model:
    #db = Text('./data/normal_trace')
    #trace = pm.sample(draws=5000, trace=db, n_init=500)

# we load the results / trace of previous run
with every_each_model:
    trace = load('./data/normal_trace')

def generate_normal_prior_figure():
    fig, ax = plt.subplots(ncols=1, nrows=1)
    fig.set_size_inches(5.5, 3.5)
    sns.distplot(trace['normal_density'], hist=True, ax=ax)
    ax.set_xlabel('Normal density, mean = 0, standard deviation = 10')
    plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=0.7)
    plt.savefig('./figures/normal_prior.eps')
    plt.savefig('./figures/normal_prior.png')
    plt.savefig('./figures/normal_prior.pdf')

generate_normal_prior_figure()


every_each["quant"].value_counts()

def generate_RTs_by_quant_figure():
    fig, ax = plt.subplots(ncols=1, nrows=1)
    fig.set_size_inches(5.5, 3.5)
    g = sns.stripplot(x="quant", y="logRTresid", data=every_each,\
                      jitter=True)
    g.set_xlabel("Quantifier")
    g.set_ylabel("Residualized log RTs")
    plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=0.7)
    plt.savefig('./figures/RTs_by_quant.eps')
    plt.savefig('./figures/RTs_by_quant.png')
    plt.savefig('./figures/RTs_by_quant.pdf')

generate_RTs_by_quant_figure()


every_each["dummy_quant"] = (every_each["quant"]=="each").astype("int")
every_each.head(n=6)


mean_every = -0.05
mean_difference = 0.1
quant = np.array(every_each["dummy_quant"])
synthetic_RT_means = mean_every + quant * mean_difference
synthetic_RT_means[:25]
sigma = 0.25
synthetic_RTs = np.random.normal(synthetic_RT_means, sigma)
synthetic_RTs.round(2)[:25]
# compare to the actual RTs in our dataset
RTs = np.array(every_each["logRTresid"])
RTs.round(2)[:25]
# repeat to generate a different sample of synthetic RTs
synthetic_RTs = np.random.normal(synthetic_RT_means, sigma)
synthetic_RTs.round(2)[:25]


every_each_model = pm.Model()
with every_each_model:
    half_normal_density = pm.HalfNormal('half_normal_density', sd=10)

from pymc3.backends import Text
from pymc3.backends.text import load
#with every_each_model:
    #db = Text('./data/half_normal_trace')
    #trace = pm.sample(draws=5000, trace=db, n_init=500)

# we load the results / trace of previous run
with every_each_model:
    trace = load('./data/half_normal_trace')

def generate_half_normal_prior_figure():
    fig, ax = plt.subplots(ncols=1, nrows=1)
    fig.set_size_inches(5.5, 3.5)
    sns.distplot(trace['half_normal_density'], hist=True, ax=ax)
    ax.set_xlabel('Half-normal density, standard deviation = 10')
    plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=0.7)
    plt.savefig('./figures/half_normal_prior.eps')
    plt.savefig('./figures/half_normal_prior.png')
    plt.savefig('./figures/half_normal_prior.pdf')

generate_half_normal_prior_figure()


every_each_model = pm.Model()
with every_each_model:
    # priors
    mean_every = pm.Normal('mean_every', mu=0, sd=10)
    mean_difference = pm.Normal('mean_difference', mu=0, sd=10)
    sigma = pm.HalfNormal('sigma', sd=10)
    # likelihood
    observed_RTs = pm.Normal('observed_RTs',
                   mu=mean_every + quant*mean_difference,
                   sd=sigma,
                   observed=RTs)

#with every_each_model:
    #db = Text('./data/every_each_model_trace')
    #trace = pm.sample(draws=5000, trace=db, n_init=50000, njobs=4)

with every_each_model:
    trace = load('./data/every_each_model_trace')


def generate_every_each_model_posteriors_figure():
    fig, (ax1, ax2) = plt.subplots(ncols=2, nrows=1)
    fig.set_size_inches(6, 4)
    plot1 = sns.distplot(trace['mean_every'], hist=True, bins=300,\
                         ax=ax1)
    plot1.set_xlim(-0.2, 0.1)
    ax1.set_xlabel(r"Mean RT `every'")
    plot2 = sns.distplot(trace['mean_difference'], hist=True,\
                         bins=300, ax=ax2)
    plot2.set_xlim(-0.1, 0.2)
    ax2.set_xlabel(r'Mean RT difference')
    plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=0.7)
    plt.savefig('./figures/every_each_model_posteriors.eps')
    plt.savefig('./figures/every_each_model_posteriors.png')
    plt.savefig('./figures/every_each_model_posteriors.pdf')

generate_every_each_model_posteriors_figure()


mean_difference = trace['mean_difference']
pm.hpd(mean_difference).round(2)


mean_difference.mean().round(2)
mean_difference.std().round(2)

mean_every = trace['mean_every']
mean_every.mean().round(2)
mean_every.std().round(2)
