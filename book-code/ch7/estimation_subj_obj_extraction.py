"""
Estimation of parameters for left-corner parser.

"""

import pyactr as actr
import simpy
import re
import sys
import warnings
warnings.filterwarnings("ignore")

import pymc3 as pm
from pymc3 import Gamma, Normal, HalfNormal, Deterministic, Uniform, find_MAP,\
                  Slice, sample, summary, Metropolis, traceplot, gelman_rubin
from pymc3.backends.base import merge_traces
from pymc3.backends import SQLite
from pymc3.backends.sqlite import load
import theano
import theano.tensor as tt
from theano.compile.ops import as_op

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from simpy.core import EmptySchedule

from parser_rules import parser, environment

SENTENCES = "sentences.csv"
DM = parser.decmem.copy()

subj_extraction = np.array(
        [(2, 360.2),
         (3, 349.8),
         (4, 354.8),
         (5, 334.3),
         (6, 384),
         (7, 346.5),
         (8, 318.4),
         (9, 403.6),
         (10, 404.6)], dtype=[('position', np.uint8), ('rt', np.float32)])
# subj_extraction['word']
# subj_extraction['rt']

obj_extraction = np.array(
        [(2, 373.1),
         (3, 343),
         (4, 348.1),
         (5, 357.6),
         (6, 422.1),
         (7, 375.8),
         (8, 338.6),
         (9, 482.9),
         (10, 401.1)], dtype=[('position', np.uint8), ('rt', np.float32)])
# obj_extraction['word']
# obj_extraction['rt']

def load_file(lfile, index_col=None, sep=","):
    """
    Loads file as a list
    """
    csvfile = pd.read_csv(lfile, index_col=index_col, header=0, sep=sep)
    return csvfile

def run_extraction_stimulus(sentence):
    """
    This runs one example of stimulus from the parser ACT-R model.
    """
    parser.set_decmem(DM)

    parser.retrievals = {}
    parser.set_retrieval("retrieval")
    parser.visbuffers = {}
    parser.goals = {}
    parser.set_goal("g")
    parser.set_goal(name="imaginal", delay=0)

    stimuli = [{} for i in range(len(sentence))]
    pos_word = 30
    environment.current_focus = (pos_word + 5*len(sentence.iloc[0]), 180)
    last_pos_word = 0
    for i, word in enumerate(sentence):
        pos_word += 5*len(word)
        for j in range(len(stimuli)):
            if j == i:
                stimuli[j].update({i: {'text': word, 'position': (pos_word, 180), 'vis_delay': len(word)}})
            else:
                stimuli[j].update({i: {'text': "___", 'position': (pos_word, 180), 'vis_delay': 3}})


        parser.productionstring(name="move eyes" + str(i), string="""
        =g>
        isa             parsing_goal
        task            move_eyes
        =visual_location>
        isa _visuallocation
        screen_y =ypos
        screen_x    """ + str(last_pos_word) + """
        ?manual>
        preparation       free
        processor       free
        ==>
        =g>
        isa     parsing_goal
        task   reading_word
        ?visual_location>
        attended False
        +visual_location>
        isa _visuallocation
        screen_x    """ + str(pos_word) + """
        screen_y =ypos
        ~visual>""")
        last_pos_word = pos_word
        pos_word += 5*len(word)

    parser.goals["g"].add(actr.chunkstring(string="""
        isa             parsing_goal
        task            reading_word
        stack1          'S'
        right_frontier_stack1  'S'
        right_frontier_stack2  None
    """))

    parser_sim = parser.simulation(realtime=False, gui=True, trace=False, environment_process=environment.environment_process, stimuli=stimuli, triggers='space', times=10)

    spacebar_press_times = []

    i = 0
    press_time = 0
    while True:
        try:
            parser_sim.step()
        except simpy.core.EmptySchedule:
            spacebar_press_times = [np.nan for _ in sentence] #if sth goes wrong, it's probably because it got stuck somewhere; in that case report time-out time per word (5 s) or nan
            break
        if parser_sim.show_time() > 20:
            spacebar_press_times = [np.nan for _ in sentence] #this takes care of looping - break if you loop (20 s should be definitely enough to move on)
            break
        if parser_sim.current_event.action == "KEY PRESSED: SPACE":
            spacebar_press_times.append(parser_sim.show_time() - press_time)
            press_time = parser_sim.show_time()
            i += 1
        if i > 9: #we ignore the words after the matrix verb, these are any words higher than 9
            break

    final_times = np.array(spacebar_press_times[1:])
    print("Simulated times for stimulus:")
    print(final_times)
    return final_times

def run_self_paced_task():
    subj_predicted_rt = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32)
    obj_predicted_rt = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32)

    subj_idx = 0
    obj_idx = 0
    for name, sentence in sentences:
        if np.isnan(run_extraction_stimulus(sentence['word'])).any():
            continue
        if (sentence['label'] == "subj_ext").all():
            subj_predicted_rt += 1000 * run_extraction_stimulus(sentence['word'])
            subj_idx += 1

        elif (sentence['label'] == "obj_ext").all():
            obj_predicted_rt += 1000 * run_extraction_stimulus(sentence['word'])
            obj_idx += 1
        else:
            raise NotImplementedError

    return [subj_predicted_rt/subj_idx, obj_predicted_rt/obj_idx]

@as_op(itypes=[tt.dscalar, tt.dscalar, tt.dscalar, tt.dscalar],
       otypes=[tt.dvector, tt.dvector])
def actrmodel_latency(lf, le, rf, emap):
    """
    This function specifies the estimated free parameters inside the act-r
    model and it envokes the model to record reaction times.       
    The simulated reaction times are returned.
    """
    parser.model_parameters["latency_factor"] = lf
    parser.model_parameters["latency_exponent"] = le
    parser.model_parameters["rule_firing"] = rf
    parser.model_parameters["eye_mvt_angle_parameter"] = emap
    predicted_rts = run_self_paced_task()
    return predicted_rts

stimuli_csv = load_file(SENTENCES, sep=",") #sentences with frequencies
sentences = stimuli_csv.groupby(['item', 'label'], sort=False)

parser_with_bayes = pm.Model()
with parser_with_bayes:
    lf = HalfNormal('lf', sd=0.3)
    le = HalfNormal('le', sd=0.5)
    rf = HalfNormal('rf', sd=0.05)
    emap = HalfNormal('emap', sd=1.0)
    # latency likelihood -- this is where pyactr is used
    pyactr_rt = actrmodel_latency(lf, le, rf, emap)
    subj_mu_rt = Deterministic('subj_mu_rt', pyactr_rt[0])
    subj_rt_observed = Normal('subj_rt_observed', mu=subj_mu_rt, sd=10, observed=subj_extraction['rt'])
    obj_mu_rt = Deterministic('obj_mu_rt', pyactr_rt[1])
    obj_rt_observed = Normal('obj_rt_observed', mu=obj_mu_rt, sd=10, observed=obj_extraction['rt'])
    # we start the sampling
    step = Metropolis()
    db = SQLite('subj_obj_extraction.sqlite')
    trace = sample(draws=100, trace=db, njobs=1, step=step, init='auto', tune=10)
    traceplot(trace)
    plt.savefig("subj_obj_extraction_posteriors.pdf")
    plt.savefig("subj_obj_extraction_posteriors.png")
