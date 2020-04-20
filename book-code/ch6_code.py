"""
Chapter 6 code.
"""

# loading the data
import pandas as pd
ebbinghaus_data = pd.read_csv('./data/ebbinghaus_retention_data.csv')
ebbinghaus_data


ebbinghaus_data.describe()

# settings for data visualization
import matplotlib as mpl
# mpl.use("pgf")
pgf_with_pdflatex = {"text.usetex": True, "pgf.texsystem": "pdflatex",
                     "pgf.preamble": [r"\usepackage{mathpazo}",
                                      r"\usepackage[utf8x]{inputenc}",
                                      r"\usepackage[T1]{fontenc}",
                                      r"\usepackage{amsmath}"],
                     "axes.labelsize": 8,
                     "font.family": "serif",
                     "font.serif":["Palatino"],
                     "font.size": 8,
                     "legend.fontsize": 8,
                     "xtick.labelsize": 8,
                     "ytick.labelsize": 8}
mpl.rcParams.update(pgf_with_pdflatex)
import matplotlib.pyplot as plt
plt.style.use('seaborn')
import seaborn as sns
sns.set_style({"font.family":"serif", "font.serif":["Palatino"]})

def generate_ebbinghaus_data_figure():
    fig, (ax1, ax2, ax3) = plt.subplots(ncols=1, nrows=3)
    fig.set_size_inches(5.5, 6.3)
    # plot 1
    ax1.plot(ebbinghaus_data['delay_in_hours'],
            ebbinghaus_data['percent_savings'],
            marker='o', linestyle='--')
    ax1.set_title('a. Non-transformed data')
    ax1.set_xlabel('Delay (hours)')
    ax1.set_ylabel('Savings (\\%)')
    # plot 2
    ax2.plot(ebbinghaus_data['delay_in_hours'],
            ebbinghaus_data['percent_savings'],
            marker='o', linestyle='--')
    ax2.set_title('b. Log performance (log percent savings), base 10')
    ax2.set_xlabel('Delay (hours)')
    ax2.set_ylabel('Savings (log \\%)')
    ax2.set_yscale('log', basey=10)
    ax2.grid(b=True, which='minor', color='w', linewidth=1.0)
    # plot 3
    ax3.plot(ebbinghaus_data['delay_in_hours'],
            ebbinghaus_data['percent_savings'],
            marker='o', linestyle='--')
    ax3.set_title('c. Log-log (log delay, log percent savings), base 10')
    ax3.set_xlabel('Delay (log hours)')
    ax3.set_xscale('log', basex=10)
    ax3.set_ylabel('Savings (log \\%)')
    ax3.set_yscale('log', basey=10)
    ax3.grid(b=True, which='minor', color='w', linewidth=1.0)
    # clean up and save
    plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=0.7)
    plt.savefig('./figures/ebbinghaus_data.eps')
    plt.savefig('./figures/ebbinghaus_data.png')
    plt.savefig('./figures/ebbinghaus_data.pdf')

generate_ebbinghaus_data_figure()


import numpy as np

np.log(4) - np.log(2)
np.log(14) - np.log(12)

def generate_log_figure():
    fig, ax = plt.subplots(ncols=1, nrows=1)
    fig.set_size_inches(5.5, 3)
    x = np.arange(1, 15, 0.01)
    ax.plot(x, np.log(x), linestyle='-')
    #ax.set_xlim(left=1)
    ax.set_xlabel(r'$x$')
    ax.set_ylabel(r'$\log(x)$')
    plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=0.7)
    plt.savefig('./figures/log_plot.eps')
    plt.savefig('./figures/log_plot.png')
    plt.savefig('./figures/log_plot.pdf')

generate_log_figure()


import pymc3 as pm
from pymc3.backends import Text
from pymc3.backends.text import load

delay = ebbinghaus_data['delay_in_hours']
savings = ebbinghaus_data['percent_savings']

exponential_model = pm.Model()
with exponential_model:
    # priors
    intercept = pm.Normal('intercept', mu=0, sd=100)
    slope = pm.Normal('slope', mu=0, sd=100)
    sigma = pm.HalfNormal('sigma', sd=100)
    # likelihood
    mu = pm.Deterministic('mu', intercept + slope*delay)
    log_savings = pm.Normal('log_savings', mu=mu, sd=sigma,
                            observed=np.log(savings))

#with exponential_model:
    #db = Text('./data/exponential_model_trace')
    #trace = pm.sample(draws=5000, trace=db, n_init=50000, njobs=4)

with exponential_model:
    trace = load('./data/exponential_model_trace')


mu = trace["mu"]

def generate_ebbinghaus_data_figure_2():
    fig, (ax1, ax2) = plt.subplots(ncols=1, nrows=2)
    fig.set_size_inches(5.5, 4.5)
    # plot 1
    ax1.plot(delay, savings, marker='o', linestyle='--')
    ax1.plot(delay, np.median(np.exp(mu), axis=0), color='red', linestyle='-')
    ax1.set_title('b. Log performance (blue) and exponential model estimates (red)')
    ax1.set_xlabel('Delay (hours)')
    ax1.set_ylabel('Savings (log \\%)')
    ax1.set_yscale('log', basey=10)
    ax1.grid(b=True, which='minor', color='w', linewidth=1.0)
    # plot 2
    yerr=[np.median(np.exp(mu), axis=0)-pm.hpd(np.exp(mu))[:,0],
          pm.hpd(np.exp(mu))[:,1]-np.median(np.exp(mu), axis=0)]
    ax2.errorbar(savings, np.median(np.exp(mu), axis=0), yerr=yerr,
                 marker='o', linestyle='')
    ax2.plot(np.linspace(0, 100, 10), np.linspace(0, 100, 10),
            color='red', linestyle=':')
    ax2.set_title('Exponential model: Observed vs. predicted savings')
    ax2.set_xlabel('Observed savings (\\%)')
    ax2.set_ylabel('Predicted savings (\\%)')
    ax2.grid(b=True, which='minor', color='w', linewidth=1.0)
    # clean up and save
    plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=0.7)
    plt.savefig('./figures/ebbinghaus_data_2.eps')
    plt.savefig('./figures/ebbinghaus_data_2.png')
    plt.savefig('./figures/ebbinghaus_data_2.pdf')

generate_ebbinghaus_data_figure_2()


power_law_model = pm.Model()
with power_law_model:
    # priors
    intercept = pm.Normal('intercept', mu=0, sd=100)
    slope = pm.Normal('slope', mu=0, sd=100)
    sigma = pm.HalfNormal('sigma', sd=100)
    # likelihood
    mu = pm.Deterministic('mu', intercept + slope*np.log(delay))
    log_savings = pm.Normal('log_savings', mu=mu, sd=sigma,
                            observed=np.log(savings))

#with power_law_model:
    #db = Text('./data/power_law_model_trace')
    #trace = pm.sample(draws=5000, trace=db, n_init=50000, njobs=4)

with power_law_model:
    trace = load('./data/power_law_model_trace')


mu = trace["mu"]
def generate_ebbinghaus_data_figure_3():
    fig, (ax1, ax2) = plt.subplots(ncols=1, nrows=2)
    fig.set_size_inches(5.5, 4.5)
    # plot 1
    ax1.plot(delay, savings, marker='o', linestyle='--')
    ax1.plot(delay, np.median(np.exp(mu), axis=0), color='red', linestyle='-')
    ax1.set_title('c. Log-log plot (blue) and power law model estimates (red)')
    ax1.set_xlabel('Delay (log hours)')
    ax1.set_xscale('log', basex=10)
    ax1.set_ylabel('Savings (log \\%)')
    ax1.set_yscale('log', basey=10)
    ax1.grid(b=True, which='minor', color='w', linewidth=1.0)
    # plot 2
    yerr=[np.median(np.exp(mu), axis=0)-pm.hpd(np.exp(mu))[:,0],
          pm.hpd(np.exp(mu))[:,1]-np.median(np.exp(mu), axis=0)]
    ax2.errorbar(savings, np.median(np.exp(mu), axis=0), yerr=yerr,
                 marker='o', linestyle='')
    ax2.plot(np.linspace(0, 100, 10), np.linspace(0, 100, 10),
             color='red', linestyle=':')
    ax2.set_title('Power law model: Observed vs. predicted savings')
    ax2.set_xlabel('Observed savings (\\%)')
    ax2.set_ylabel('Predicted savings (\\%)')
    ax2.grid(b=True, which='minor', color='w', linewidth=1.0)
    # clean up and save
    plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=0.7)
    plt.savefig('./figures/ebbinghaus_data_3.eps')
    plt.savefig('./figures/ebbinghaus_data_3.png')
    plt.savefig('./figures/ebbinghaus_data_3.pdf')

generate_ebbinghaus_data_figure_3()


def base_activation(pres_times, moments):
    base_act = np.zeros(len(moments))
    for idx in range(len(moments)):
        past_pres_times = pres_times[pres_times<moments[idx]]
        base_act[idx] = \
            np.sum(1/np.sqrt(moments[idx] - past_pres_times))
    non_zero_activations = np.not_equal(base_act, 0)
    base_act[non_zero_activations] = \
        np.log(base_act[non_zero_activations])
    return base_act

pres_times = np.linspace(0, 5000, 5)/1000
pres_times
moments = np.arange(10000)/1000
moments
base_act = base_activation(pres_times, moments)
base_act


def generate_base_activation_figure():
    fig, ax = plt.subplots(ncols=1, nrows=1)
    fig.set_size_inches(5.5, 3)
    ax.plot(moments, base_act, linestyle='-')
    ax.plot(pres_times, np.ones(5) * -0.3, 'ro')
    ax.set_title('Base activation (blue) and 5 presentations (red)')
    ax.set_xlabel('Time (s)')
    ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(1))
    ax.set_ylabel('Base activation (logits)')
    #plt.xticks(rotation=45)
    plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=0.7)
    plt.savefig('./figures/base_activation.eps')
    plt.savefig('./figures/base_activation.png')
    plt.savefig('./figures/base_activation.pdf')

generate_base_activation_figure()


s = 0.4
tau = 0.3
F = 0.47
f = 1
prob_retrieval = 1 / (1 + np.exp(-(base_act - tau)/s))
prob_retrieval
latency_retrieval = F * np.exp(-f*base_act)
# latency of retrieval in ms
(latency_retrieval * 1000).astype("int")
threshold_prob_scale = 1 / (1 + np.exp(-(tau-tau)/s)) # =1/(1+1)
# it's 1/2, i.e., 50% probability when activation is at threshold
threshold_prob_scale
threshold_latency_scale = F * np.exp(-tau)
# time to retrieve in ms when activation is at threshold
(threshold_latency_scale * 1000).astype("int")


def generate_prob_latency_figure():
    fig, (ax1, ax2, ax3) = plt.subplots(ncols=1, nrows=3, sharex=True)
    fig.set_size_inches(5.8, 8.3)
    # plot 1
    ax1.plot(moments, base_act, linestyle='-')
    ax1.plot(pres_times, np.ones(5) * -0.3, 'ro')
    ax1.plot(moments, np.ones(len(moments)) * tau,\
             linestyle='--', color='black')
    ax1.annotate('Threshold', xy=(8, tau - 0.26), size=10)
    ax1.set_title('Activation (blue),\
                   threshold (black) and 5 presentations (red)')
    ax1.set_ylabel('Activation (logits)')
    # plot 2
    ax2.plot(moments, prob_retrieval, linestyle='-')
    ax2.plot(pres_times, np.zeros(5), 'ro')
    ax2.plot(moments, np.ones(len(moments)) * threshold_prob_scale,\
            linestyle='--', color='black')
    ax2.annotate('Threshold', xy=(8, threshold_prob_scale - 0.067),\
                 size=10)
    ax2.set_title('Retrieval probability (blue), \
                   threshold (black) and 5 presentations (red)')
    ax2.set_ylabel('Probability of retrieval')
    # plot 3
    ax3.plot(moments, latency_retrieval, linestyle='-')
    ax3.plot(pres_times, np.ones(5) * -0.03, 'ro')
    ax3.plot(moments, np.ones(len(moments)) * threshold_latency_scale,\
            linestyle='--', color='black')
    ax3.annotate('Threshold', xy=(8, threshold_latency_scale - 0.037),\
                 size=10)
    ax3.set_title('Retrieval latency (blue), \
                   threshold (black) and 5 presentations (red)')
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Latency of retrieval (s)')
    # clean up and save
    plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=0.7)
    plt.savefig('./figures/prob_latency_figure.eps')
    plt.savefig('./figures/prob_latency_figure.png')
    plt.savefig('./figures/prob_latency_figure.pdf')

generate_prob_latency_figure()
