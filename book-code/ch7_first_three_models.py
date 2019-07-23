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
import numpy as np
import pandas as pd
import pymc3 as pm
from pymc3.backends import Text
from pymc3.backends.text import load

freq = np.array([242, 92.8, 57.7, 40.5, 30.6, 23.4, 19,\
                 16, 13.4, 11.5, 10, 9, 7, 5, 3, 1])
rt = np.array([542, 555, 566, 562, 570, 569, 577, 587,\
               592, 605, 603, 575, 620, 607, 622, 674])/1000
accuracy = np.array([97.22, 95.56, 95.56, 96.3, 96.11, 94.26,\
                     95, 92.41, 91.67, 93.52, 91.85, 93.52,\
                     91.48, 90.93, 84.44, 74.63])/100



log_freq_model = pm.Model()
with log_freq_model:
    # priors
    intercept = pm.Normal('intercept', mu=0, sd=300)
    slope = pm.Normal('slope', mu=0, sd=300)
    sigma = pm.HalfNormal('sigma', sd=300)
    # likelihood
    mu = pm.Deterministic('mu', intercept + slope*np.log(freq))
    observed_rt = pm.Normal('observed_rt', mu=mu, sd=sigma,\
                            observed=rt)

#with log_freq_model:
    #db = Text('./data/log_freq_model_trace')
    #trace = pm.sample(draws=5000, trace=db, tune=15000,\
                      #n_init=200000, njobs=4)

with log_freq_model:
    trace = load('./data/log_freq_model_trace')

mu = trace["mu"]
def generate_log_freq_figure():
    fig, (ax1, ax2) = plt.subplots(ncols=1, nrows=2)
    fig.set_size_inches(5.5, 5.5)
    # plot 1
    ax1.plot(freq, rt, marker='o', linestyle='')
    ax1.plot(freq, mu.mean(axis=0), color='red', linestyle='-')
    ax1.set_title('Observed (blue) \& predicted (red) RTs\
                   against log frequency')
    ax1.set_xlabel('Log frequency (log of \# tokens/1 million words)')
    ax1.set_xscale('log', basex=10)
    ax1.set_ylabel('RTs (s)')
    ax1.grid(b=True, which='minor', color='w', linewidth=1.0)
    # plot 2
    yerr=[mu.mean(axis=0)-pm.hpd(mu)[:,0],\
          pm.hpd(mu)[:,1]-mu.mean(axis=0)]
    ax2.errorbar(rt, mu.mean(axis=0), yerr=yerr,\
                 marker='o', linestyle='')
    ax2.plot(np.linspace(0.5, 0.7, 10), np.linspace(0.5, 0.7, 10),
            color='red', linestyle=':')
    ax2.set_title('Log frequency model: Observed vs. predicted RTs')
    ax2.set_xlabel('Observed RTs (s)')
    ax2.set_ylabel('Predicted RTs (s)')
    ax2.grid(b=True, which='minor', color='w', linewidth=1.0)
    # clean up and save
    plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=1.9)
    plt.savefig('./figures/log_freq_model_figure.eps')
    plt.savefig('./figures/log_freq_model_figure.png')
    plt.savefig('./figures/log_freq_model_figure.pdf')

generate_log_freq_figure()


SEC_IN_YEAR = 365*24*3600
SEC_IN_TIME = 15*SEC_IN_YEAR
def time_freq(freq):
    max_idx = np.int(np.max(freq) * 112.5)
    rehearsals = np.zeros((max_idx, len(freq)))
    for i in np.arange(len(freq)):
        temp = np.arange(np.int((freq[i]*112.5)))
        temp = temp * np.int(SEC_IN_TIME/(freq[i]*112.5))
        rehearsals[:len(temp),i] = temp
    return(rehearsals.T)


import theano
import theano.tensor as tt
time = theano.shared(time_freq(freq), 'time')


lex_dec_model = pm.Model()
with lex_dec_model:
    # prior for base activation
    decay = pm.Uniform('decay', lower=0, upper=1)
    # priors for latency
    intercept = pm.Uniform('intercept', lower=0, upper=2)
    latency_factor = pm.Uniform('latency_factor', lower=0, upper=5)
    # priors for accuracy
    noise = pm.Uniform('noise', lower=0, upper=5)
    threshold = pm.Normal('threshold', mu=0, sd=10)
    # compute activation
    scaled_time = time ** (-decay)
    def compute_activation(scaled_time_vector):
        compare = tt.isinf(scaled_time_vector)
        subvector = scaled_time_vector[(1-compare).nonzero()]
        activation_from_time = tt.log(subvector.sum())
        return activation_from_time
    activation_from_time, _ = theano.scan(fn=compute_activation,\
                                          sequences=scaled_time)
    # latency likelihood
    mu_rt = pm.Deterministic('mu_rt', intercept +\
                          latency_factor*tt.exp(-activation_from_time))
    rt_observed = pm.Normal('rt_observed', mu=mu_rt, sd=0.01,\
                            observed=rt)
    # accuracy likelihood
    odds_reciprocal = tt.exp(-(activation_from_time - threshold)/noise)
    mu_prob = pm.Deterministic('mu_prob', 1/(1 + odds_reciprocal))
    prob_observed = pm.Normal('prob_observed', mu=mu_prob, sd=0.01,\
                              observed=accuracy)

#with lex_dec_model:
    #db = Text('./data/lex_dec_model_trace')
    #trace = pm.sample(draws=10000, trace=db,\
                      #n_init=200000, njobs=6)

with lex_dec_model:
    trace = load('./data/lex_dec_model_trace')


trace = trace[2000:]
mu_rt = pd.DataFrame(trace['mu_rt'])
yerr_rt = [(mu_rt.mean()-mu_rt.quantile(0.025))*1000,\
           (mu_rt.quantile(0.975)-mu_rt.mean())*1000]

mu_prob = pd.DataFrame(trace['mu_prob'])
yerr_prob = [(mu_prob.mean()-mu_prob.quantile(0.025)),\
             (mu_prob.quantile(0.975)-mu_prob.mean())]

def generate_lex_dec_model_figure():
    fig, (ax1, ax2) = plt.subplots(ncols=1, nrows=2)
    fig.set_size_inches(5.5, 5.5)
    # plot 1: RTs
    ax1.errorbar(rt*1000, mu_rt.mean()*1000, yerr=yerr_rt, marker='o',\
                 linestyle='')
    ax1.plot(np.linspace(500, 800, 10), np.linspace(500, 800, 10),\
             color='red', linestyle=':')
    ax1.set_title('Lexical decision model:\
                   Observed vs. predicted RTs')
    ax1.set_xlabel('Observed RTs (ms)')
    ax1.set_ylabel('Predicted RTs (ms)')
    ax1.grid(b=True, which='minor', color='w', linewidth=1.0)
    # plot 2: probabilities
    ax2.errorbar(accuracy, mu_prob.mean(), yerr=yerr_prob, marker='o',\
                 linestyle='')
    ax2.plot(np.linspace(50, 100, 10)/100,\
                         np.linspace(50, 100, 10)/100,\
                         color='red', linestyle=':')
    ax2.set_title('Lexical decision model:\
                   Observed vs. predicted probabilities')
    ax2.set_xlabel('Observed probabilities')
    ax2.set_ylabel('Predicted probabilities')
    ax2.grid(b=True, which='minor', color='w', linewidth=1.0)
    # clean up and save
    plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=0.7)
    plt.savefig('./figures/lex_dec_model_figure.eps')
    plt.savefig('./figures/lex_dec_model_figure.png')
    plt.savefig('./figures/lex_dec_model_figure.pdf')

generate_lex_dec_model_figure()


from pymc3.backends.text import dump

lex_dec_model_lat_exp = pm.Model()
with lex_dec_model_lat_exp:
    # prior for base activation
    decay = pm.Uniform('decay', lower=0, upper=1)
    # priors for latency
    intercept = pm.Uniform('intercept', lower=0, upper=2)
    latency_factor = pm.Uniform('latency_factor', lower=0, upper=5)
    latency_exponent = pm.HalfNormal('latency_exponent', sd=3)
    # priors for accuracy
    noise = pm.Uniform('noise', lower=0, upper=5)
    threshold = pm.Normal('threshold', mu=0, sd=10)
    # compute activation
    scaled_time = time ** (-decay)
    def compute_activation(scaled_time_vector):
        compare = tt.isinf(scaled_time_vector)
        subvector = scaled_time_vector[(1-compare).nonzero()]
        activation_from_time = tt.log(subvector.sum())
        return activation_from_time
    activation_from_time, _ = theano.scan(fn=compute_activation,\
                                          sequences=scaled_time)
    # latency likelihood
    mu_rt = pm.Deterministic('mu_rt', intercept +\
                             latency_factor*tt.exp(-latency_exponent*\
                             activation_from_time))
    rt_observed = pm.Normal('rt_observed', mu=mu_rt, sd=0.01,\
                            observed=rt)
    # accuracy likelihood
    odds_reciprocal = tt.exp(-(activation_from_time - threshold)/noise)
    mu_prob = pm.Deterministic('mu_prob', 1/(1 + odds_reciprocal))
    prob_observed = pm.Normal('prob_observed', mu=mu_prob, sd=0.01,\
                              observed=accuracy)

# run 4 times to obtain 4 chains
#with lex_dec_model_lat_exp:
    #step = pm.SMC()
    #trace = pm.sample(draws=20000, step=step, njobs=1)

#dump = Text('./data/lex_dec_model_lat_exp_trace', trace)

with lex_dec_model_lat_exp:
    trace = load('./data/lex_dec_model_lat_exp_trace')


mu_rt = pd.DataFrame(trace['mu_rt'])
yerr_rt = [(mu_rt.mean()-mu_rt.quantile(0.025))*1000,\
           (mu_rt.quantile(0.975)-mu_rt.mean())*1000]

mu_prob = pd.DataFrame(trace['mu_prob'])
yerr_prob = [(mu_prob.mean()-mu_prob.quantile(0.025)),\
             (mu_prob.quantile(0.975)-mu_prob.mean())]

def generate_lex_dec_model_lat_exp_figure():
    fig, (ax1, ax2) = plt.subplots(ncols=1, nrows=2)
    fig.set_size_inches(5.5, 5.5)
    # plot 1: RTs
    ax1.errorbar(rt*1000, mu_rt.mean()*1000, yerr=yerr_rt, marker='o', linestyle='')
    ax1.plot(np.linspace(500, 800, 10), np.linspace(500, 800, 10),\
             color='red', linestyle=':')
    ax1.set_title('Lex. dec. model with latency exponent:\
                   Observed vs. predicted RTs')
    ax1.set_xlabel('Observed RTs (ms)')
    ax1.set_ylabel('Predicted RTs (ms)')
    ax1.grid(b=True, which='minor', color='w', linewidth=1.0)
    # plot 2: probabilities
    ax2.errorbar(accuracy, mu_prob.mean(), yerr=yerr_prob, marker='o',\
                 linestyle='')
    ax2.plot(np.linspace(50, 100, 10)/100,\
             np.linspace(50, 100, 10)/100,\
             color='red', linestyle=':')
    ax2.set_title('Lex. dec. model with lat. exp.:\
                   Observed vs. predicted probabilities')
    ax2.set_xlabel('Observed probabilities')
    ax2.set_ylabel('Predicted probabilities')
    ax2.grid(b=True, which='minor', color='w', linewidth=1.0)
    # clean up and save
    plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=0.7)
    plt.savefig('./figures/lex_dec_model_lat_exp_figure.eps')
    plt.savefig('./figures/lex_dec_model_lat_exp_figure.png')
    plt.savefig('./figures/lex_dec_model_lat_exp_figure.pdf')

generate_lex_dec_model_lat_exp_figure()
