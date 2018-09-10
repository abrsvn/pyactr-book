"""
Simulation of left-corner syn/sem parser for fan experiment.
"""

import pyactr as actr
import simpy
import re
import sys
import numpy as np
import matplotlib as mpl
mpl.use("pgf")
pgf_with_pdflatex = {"text.usetex": True, "pgf.texsystem": "pdflatex",
                     "pgf.preamble": [r"\usepackage{mathpazo}",
                                      r"\usepackage[utf8x]{inputenc}",
                                      r"\usepackage[T1]{fontenc}"],
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

import pandas as pd

import pymc3 as pm
from pymc3 import Model, Gamma, Normal, HalfNormal, Deterministic,\
                  Uniform, find_MAP, Slice, sample, summary, Metropolis,\
                  traceplot, gelman_rubin
from pymc3.backends.base import merge_traces
from pymc3.backends import SQLite
from pymc3.backends.sqlite import load
import theano
import theano.tensor as tt
from theano.compile.ops import as_op
from mpi4py import MPI

import warnings
warnings.filterwarnings("ignore")

from parser_rules_fan import parser, recall_by_location
from parser_dm_fan import environment

NDRAWS = 5000

# person-location pairs: 3-3, 3-2, 3-1, 2-3, 2-2, 2-1, 1-3, 1-2; 1-1
# (from Anderson 1974, in ms)
RT = np.array([1.36, 1.22, 1.22, 1.23, 1.2,\
               1.17, 1.15, 1.17, 1.11]) * 1000
DM = parser.decmem

SENTENCES = ["a hippie is in a park", "a hippie is in a church",\
             "a hippie is in a town", "a captain is in a park",\
             "a captain is in a church", "a doctor is in a shop",\
             "a fireman is in a park", "a debutante is in a bank",\
             "a lawyer is in a cave"]

def run_fan_exp():
    """
    Run fan experiment.
    """
    sample = []

    for sentence in SENTENCES:
        sentence = sentence.split()
        run_time = 0
        for i in range(2):
            recall_by_location["utility"] = i #change utility so that the other way of recalling becomes active
            parser.goals["g"].add(actr.chunkstring(string="""
                isa             parsing_goal
                task            reading_word
                stack1          S
                right_frontier  S
                dref_peg        1
            """))
            parser.decmems = {}
            parser.decmems['decmem'] = DM.copy()
            parser.retrieval.finst = 5

            parser.set_goal

            environment.current_focus = (160, 180)
            stimuli = [{x: {'text': word, 'position': (160+x*40, 180)}\
                       for x, word in enumerate(sentence)}]
            parser.visualBuffer("visual", "visual_location",
                                parser.decmem, finst=80)
            parser_sim = parser.simulation(
            realtime=False,
            gui=True,
            environment_process=environment.environment_process,
            stimuli=stimuli,
            triggers='space', times=20)

            parser.model_parameters["motor_prepared"] = True

            while True:
                try:
                    parser_sim.step()
                    #print(parser_sim.current_event)
                except simpy.core.EmptySchedule:
                    break
                if re.search("^KEY PRESSED: J",\
                             str(parser_sim.current_event.action)):
                    parser.retrieval.pop()
                    # record time, use average of two runs if
                    # there is a previously recorded time
                    # to get average of recalling by person+location
                    if run_time:
                        run_time += parser_sim.show_time()
                        run_time = run_time/2
                    else:
                        run_time = parser_sim.show_time()
                        #print("RT", run_time)
                        #input()
                    break

        sample.append(run_time)

    return sample

@as_op(itypes=[tt.dscalar, tt.dscalar, tt.dscalar, tt.dscalar],
       otypes=[tt.dvector])
def actrmodel_latency(rule_firing, latency_factor, buffer_spreading_activation, strength_of_association):
    """
    ACT-R Model.
    """
    parser.model_parameters["buffer_spreading_activation"] = \
            {"g": buffer_spreading_activation}
    parser.model_parameters["strength_of_association"] = \
            strength_of_association
    parser.model_parameters["rule_firing"] = rule_firing
    parser.model_parameters["latency_factor"] = latency_factor

    sample = np.array(run_fan_exp(), dtype=np.dtype('f8')) * 1000

    #print("SAMPLE", sample)

    return sample

fan_model = Model()

with fan_model:
    # Priors
    buffer_spreading_activation = HalfNormal("bsa", sd=3)
    strength_of_association = HalfNormal("soa", sd=6)
    rule_firing = HalfNormal("rf", sd=0.04)
    latency_factor = HalfNormal("lf", sd=0.3)
    # Likelihood
    pyactr_rt = actrmodel_latency(rule_firing, latency_factor,\
                                  buffer_spreading_activation,\
                                  strength_of_association)
    mu_rt = Deterministic('mu_rt', pyactr_rt)
    rt_observed = Normal('rt_observed', mu=mu_rt, sd=30, observed=RT)
    # Compute posteriors
    step = Metropolis(fan_model.vars)
    db = SQLite('fan_chain_5000_draws.sqlite')
    #trace = sample(NDRAWS, step=step, trace=db, njobs=1, init='auto', tune=500)

with fan_model:
    trace = load('./fan_chain_5000_draws.sqlite')
    trace = trace[500:]

traceplot(trace)
plt.savefig('fan_chain_5000_draws.png')
plt.savefig('fan_chain_5000_draws.pgf')
plt.savefig('fan_chain_5000_draws.pdf')

mu_rt = pd.DataFrame(trace['mu_rt'])
yerr_rt = [(mu_rt.mean()-mu_rt.quantile(0.025)),\
           (mu_rt.quantile(0.975)-mu_rt.mean())]

def generate_fan_model_figure():
    fig, ax1 = plt.subplots(ncols=1, nrows=1)
    fig.set_size_inches(5.5, 3.5)
    # plot 1: RTs
    ax1.errorbar(RT, mu_rt.mean(), yerr=yerr_rt, marker='o', linestyle='')
    ax1.plot(np.linspace(1100, 1400, 10), np.linspace(1100, 1400, 10),\
             color='red', linestyle=':')
    #ax1.set_title('Fan model: Observed vs. predicted RTs')
    ax1.set_title('')
    ax1.set_xlabel('Observed RTs (ms)')
    ax1.set_ylabel('Predicted RTs (ms)')
    ax1.grid(b=True, which='minor', color='w', linewidth=1.0)
    # clean up and save
    plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=0.7)
    plt.savefig('../../figures/fan_model_figure.pgf')
    plt.savefig('../../figures/fan_model_figure.pdf')

generate_fan_model_figure()

pm.plot_posterior(trace, varnames=["bsa", "soa", "rf", "lf"],\
                  figsize=(5.5, 3.5), text_size=10)
plt.savefig('../../figures/fan_model_estimates.pgf')
plt.savefig('../../figures/fan_model_estimates.pdf')

