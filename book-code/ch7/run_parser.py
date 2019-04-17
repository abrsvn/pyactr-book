"""
Simulation of left-corner parser.

Run simulation by calling the file + one argument, which is either 0 (stepwise simulation) or 1
(realtime simulation).
"""

import pyactr as actr
import simpy
import re
import sys

import pandas as pd

# import warnings
# warnings.filterwarnings("ignore")

from parser_rules import parser, environment

SENTENCES = "sentences.csv"
dm = parser.decmem.copy()

def load_file(lfile, index_col=None, sep=","):
    """
    Loads file as a list
    """
    csvfile = pd.read_csv(lfile, index_col=index_col, header=0, sep=sep)
    return csvfile

if __name__ == "__main__":

    try:
        simulate = int(sys.argv[1])
    except IndexError:
        simulate = 1

    stimuli_csv = load_file(SENTENCES, sep=",") #sentences with frequencies

    subset_stimuli = stimuli_csv[stimuli_csv.label.isin(['obj_ext'])]
    sentence = subset_stimuli[subset_stimuli.item.isin([1])].word

    parser.set_decmem(dm)

    parser.retrievals = {}
    parser.set_retrieval("retrieval")
    parser.visbuffers = {}
    parser.goals = {}
    parser.set_goal("g")
    parser.set_goal(name="imaginal", delay=0)

    lensen = len(sentence)

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

    #parser.productionstring(name="finished: no visual input", string="""
    #=g>
    #isa             parsing_goal
    #task            reading_word
    #=visual_location>
    #isa _visuallocation
    #screen_y =ypos
    #screen_x    """ + str(last_pos_word) + """
    #==>
    #~g>
    #~imaginal>""")
    parser.goals["g"].add(actr.chunkstring(string="""
        isa             parsing_goal
        task            reading_word
        stack1          'S'
        right_frontier_stack1  'S'
        right_frontier_stack2  None
    """))

    if simulate:
        parser_sim = parser.simulation(
        realtime=True,
        gui=True,
        environment_process=environment.environment_process,
        stimuli=stimuli,
        triggers='space', times=10)
    else:
        parser_sim = parser.simulation(
        realtime=False,
        gui=False,
        environment_process=environment.environment_process,
        stimuli=stimuli,
        triggers='space', times=10)

    recorded = ["sent", "saw"]
    dict_recorded = {key: [0, 0] for key in recorded}
    recorded_word = None

    if simulate:
        parser_sim.run(10)
    else:
        while True:
            try:
                parser_sim.step()
            except simpy.core.EmptySchedule:
                break

            # when debugging, maybe add: re.search("^NO RULE FOUND", str(parser_sim.current_event.action)) or\
            if re.search("^RULE FIRED: press spacebar", str(parser_sim.current_event.action)):
                print("\ngoal buffer:\n--> ", parser.goals["g"])
                print("\nimaginal:\n--> ", parser.goals["imaginal"])
                print("\nretrieval buffer:\n--> ", parser.retrieval)
                print("\n")
                input()
