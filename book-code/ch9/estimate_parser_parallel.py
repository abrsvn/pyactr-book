"""
Simulation of left-corner syn/sem parser for the AGAIN and IF/AND experiment.
"""

import pyactr as actr
import simpy
import re
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import pandas as pd

import pymc3 as pm
from pymc3 import Model, Gamma, Normal, HalfNormal, Deterministic,\
                  Uniform, find_MAP, Slice, sample, summary, Metropolis,\
                  traceplot, gelman_rubin
from pymc3.backends.base import merge_traces
from pymc3.backends import Text
from pymc3.backends.text import load
from pymc3.backends.text import dump
import theano
import theano.tensor as tt
from theano.compile.ops import as_op
from mpi4py import MPI

import warnings
warnings.filterwarnings("ignore")

from parser_rules import parser
from parser_dm import environment

NDRAWS = 1500

# Order of mean RTs below is:
# (match, nothing, and), (match, nothing, if), (match, cataphora, and), (match, cataphora, if), (mismatch, cataphora, and), (mismatch, cataphora, if)
RT = np.array([364.05, 429.01, 390.13, 378.83, 374.28, 387.72])

DM = parser.decmem.copy()

SENTENCES = ["Jeffrey will argue with Danielle and he argued with her",\
             "Jeffrey will argue with Danielle if he argued with her",\
             "Jeffrey will argue with Danielle again and he argued with her",\
             "Jeffrey will argue with Danielle again if he argued with her",\
             "Jeffrey will argue with Danielle again and he played with her",\
             "Jeffrey will argue with Danielle again if he played with her"]


def reading_stim(sentence, dm):
    parser.goals["g"].add(actr.chunkstring(string="""
    isa               parsing_goal
    task              reading_word
    stack1            S
    right_edge_stack1 S
    right_edge_stack2 None
    discourse_status  at_issue
    dref_peg          x1
    drs_peg           d1
    event_peg         e1
    embedding_level   0
    """))

    parser.goals["imaginal"].add(actr.chunkstring(string="""
    isa             parse_state
    """))

    parser.goals["unresolved_discourse"].add(actr.chunkstring(string="isa drs"))

    sentence = sentence.split()

    parser.set_decmem(data={x: dm[x] for x in dm})

    parser.retrieval.finst = 5

    stimuli = []
    for word in sentence:
        stimuli.append({1: {'text': word, 'position': (320, 180)}})
    parser_sim = parser.simulation(
        realtime=False,
        gui=True,
        environment_process=environment.environment_process,
        stimuli=stimuli,
        triggers='space',
        times=500)

    elapsed_time = 0

    while True:
        try:
            parser_sim.step()
            #print(parser_sim.current_event)
        except simpy.core.EmptySchedule:
            break

        if parser_sim.show_time() > 500:
            break

        if re.search("^KEY PRESSED: SPACE", str(parser_sim.current_event.action)) and\
                (environment.stimulus[1]["text"] == "argued" or environment.stimulus[1]["text"] == "played") and not elapsed_time:
                    elapsed_time = parser_sim.show_time()
        elif re.search("^KEY PRESSED: SPACE", str(parser_sim.current_event.action)) and\
                elapsed_time:
                    elapsed_time = parser_sim.show_time() - elapsed_time
                    break

    return elapsed_time

def run_exp(rank):
    """
    Run experiment.
    """

    while True:

        received_list = np.empty(1, dtype=np.float)
        comm.Recv([received_list, MPI.FLOAT], 0, rank)
        if received_list[0] == -1:
            break
        parser.model_parameters["latency_exponent"] = received_list[0]
        # print(received_list[0])

        run_time_in_s = reading_stim(SENTENCES[rank-1], DM) #run_time - time between key presses on the preposition "with"
        # print(run_time_in_s)
        comm.Send([np.array([run_time_in_s]), MPI.FLOAT], dest=0, tag=1)


@as_op(itypes=[tt.dscalar],
       otypes=[tt.dvector])
def actrmodel_latency(latency_exponent):
    """
    ACT-R Model.
    """
    predicted_ms = np.array([0, 0, 0, 0, 0, 0], dtype=np.float)

    sent_list = np.array([latency_exponent], dtype = np.float)

    # print("param values sent:", sent_list)

    #get slaves to work
    for i in range(1, N_GROUPS):
        comm.Send([sent_list, MPI.FLOAT], dest=i, tag=i)

    for i in range(1, N_GROUPS):
        #receive list one by one from slaves
        received_list = np.empty(1, dtype=np.float)
        comm.Recv([received_list, MPI.FLOAT], i, 1)
        predicted_ms[i-1] = 1000 * received_list[0]

    # print("predicted RTs:", predicted_ms)

    return predicted_ms


comm = MPI.COMM_WORLD
rank = comm.Get_rank()

N_GROUPS = comm.Get_size() #Groups used for simulation


if rank == 0: #master
    parser_model = Model()
    with parser_model:
        # Priors
        latency_exponent = HalfNormal('le', sd=0.3)
        # Likelihood
        pyactr_rt = actrmodel_latency(latency_exponent)
        mu_rt = Deterministic('mu_rt', pyactr_rt)
        rt_observed = Normal('rt_observed', mu=mu_rt, sd=30, observed=RT)
        # Compute posteriors
        #step = pm.SMC()
        #trace = sample(draws=NDRAWS, step=step, njobs=1)
else:
    run_exp(rank)

#dump('parser_model_'+str(NDRAWS)+'_iterations', trace)

with parser_model:
    trace = load('../../data/parser_model_'+str(NDRAWS)+'_iterations')

pm.diagnostics.gelman_rubin(trace)
traceplot(trace)
plt.savefig('../../figures/parser_'+str(NDRAWS)+'_trace.eps')
plt.savefig('../../figures/parser_'+str(NDRAWS)+'_trace.png')
plt.savefig('../../figures/parser_'+str(NDRAWS)+'_trace.pdf')
#plt.show()

mu_rt = pd.DataFrame(trace['mu_rt'])
yerr_rt = [(mu_rt.mean()-mu_rt.quantile(0.025)),\
        (mu_rt.quantile(0.975)-mu_rt.mean())]

def generate_parser_model_figure():
    fig, ax1 = plt.subplots(ncols=1, nrows=1)
    fig.set_size_inches(5.5, 3.5)
    # plot 1: RTs
    ax1.errorbar(RT, mu_rt.mean(), yerr=yerr_rt, marker='o', linestyle='')
    ax1.plot(np.linspace(300, 500, 10), np.linspace(300, 500, 10),\
             color='red', linestyle=':')
    #ax1.set_title('Fan model: Observed vs. predicted RTs')
    ax1.set_title('')
    ax1.set_xlabel('Observed RTs (ms)')
    ax1.set_ylabel('Predicted RTs (ms)')
    ax1.grid(b=True, which='minor', color='w', linewidth=1.0)
    # clean up and save
    plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=0.7)
    plt.savefig('../../figures/parser_model_figure.eps')
    plt.savefig('../../figures/parser_model_figure.png')
    plt.savefig('../../figures/parser_model_figure.pdf')
    #plt.show()

generate_parser_model_figure()

pm.plot_posterior(trace, varnames=["le", "mu_rt"],
                  figsize=(11.5, 8.5), text_size=10)
plt.savefig('../../figures/parser_model_estimates.eps')
plt.savefig('../../figures/parser_model_estimates.png')
plt.savefig('../../figures/parser_model_estimates.pdf')
#plt.show()
