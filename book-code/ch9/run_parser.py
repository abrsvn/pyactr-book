"""
File to running / simulate:

Eager left-corner syn/sem parser for the interaction of
pronominal/presuppositional cataphora and conjunctions/conditionals.

Models self-paced reading (left-to-right moving window paradigm).
Also models eye movements.
Instantiates a form of "parallel reader": key press commands are issued as soon
as lexical retrieval is completed; further processing (construction of
appropriate syn/sem structures etc.) is done in parallel to the motor module
actions.
"""

import pyactr as actr
import simpy
import re

import numpy as np

# import warnings
# warnings.filterwarnings("ignore")

from parser_rules import parser
from parser_dm import environment


def reading(sentence, dm):
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
        gui=False,
        environment_process=environment.environment_process,
        stimuli=stimuli,
        triggers='space',
        times=100)

    elapsed_time = 0

    while True:
        try:
            parser_sim.step()
        except simpy.core.EmptySchedule:
            break

        if re.search("^KEY PRESSED: SPACE", str(parser_sim.current_event.action)) and\
                (environment.stimulus[1]["text"] == "argued" or environment.stimulus[1]["text"] == "played") and not elapsed_time:
                    elapsed_time = parser_sim.show_time()
        elif re.search("^KEY PRESSED: SPACE", str(parser_sim.current_event.action)) and\
                elapsed_time:
                    elapsed_time = parser_sim.show_time() - elapsed_time
                    break

    sortedDM = sorted(([item[0], time] for item in parser.decmem.items()\
                       for time in item[1]),\
                       key=lambda item: item[1])

    return elapsed_time, sortedDM



if __name__ == "__main__":

    # sentences = ["John smiled"]
    # sentences = ["John wont smile"]
    # sentences = ["John will smile"]
    # sentences = ["He smiled"]
    # sentences = ["John saw Mary"]
    # sentences = ["John saw a woman"]
    # sentences = ["He saw her"]
    # sentences = ["A woman smiled"]
    # sentences = ["A woman ate a hamburger"]
    # sentences = ["Mary wont eat a hamburger"]
    # sentences = ["A hamburger is overcooked"]
    # sentences = ["John smiled and Mary laughed"]
    # sentences = ["A boy bought a horse and a woman ate a hamburger"]
    # sentences = ["John smiled and he laughed"]
    # sentences = ["John smiled and she laughed"]
    # sentences = ["A woman smiled and she left"]
    # sentences = ["A woman smiled and he left"]
    # sentences = ["John smiled and Bill laughed and he left"]
    # sentences = ["John left and Mary followed him"]
    # sentences = ["John left and Mary followed her"]
    # sentences = ["John greeted Mary and she greeted him"]
    # sentences = ["John smiled if Mary laughed"]
    # sentences = ["John smiled if Mary smiled"]
    # sentences = ["John followed her if Mary left"]
    # sentences = ["John followed her and Mary left"]
    # sentences = ["John follows her if John sees Mary"]
    # sentences = ["John followed Mary if she left"]
    # sentences = ["John followed her if a woman left"]
    # sentences = ["John wont eat it if a hamburger is overcooked"]
    # sentences = ["John wont eat it and a hamburger is overcooked"]

    # sentences = ["Jeffrey will argue with Danielle"]
    # sentences = ["Jeffrey will play with Danielle"]

    # sentences = ["Jeffrey will argue with Danielle and Jeffrey will argue with Danielle"]
    # sentences = ["Jeffrey will argue with Danielle if Jeffrey will argue with Danielle"]
    # sentences = ["Jeffrey will argue with Danielle and Jeffrey will play with Danielle"]
    # sentences = ["Jeffrey will argue with Danielle if Jeffrey will play with Danielle"]


    # sentences = ["Jeffrey will argue with Danielle and he will play with her"]
    # sentences = ["Jeffrey will argue with Danielle if he will play with her"]

    # sentences = ["Jeffrey will argue with Danielle and he will argue with her again"]
    # sentences = ["Jeffrey will argue with Danielle and he will play with her again"]

    # sentences = ["Jeffrey played with Danielle"]
    # sentences = ["Jeffrey will argue with Danielle and he argued with her"]



    # sentences = ["Jeffrey will argue with Danielle and he argued with her"]
    sentences = ["Jeffrey will argue with Danielle if he argued with her"]
    # sentences = ["Jeffrey will argue with Danielle again and he argued with her"]
    # sentences = ["Jeffrey will argue with Danielle again if he argued with her"]
    # sentences = ["Jeffrey will argue with Danielle and he played with her"]
    # sentences = ["Jeffrey will argue with Danielle if he played with her"]
    # sentences = ["Jeffrey will argue with Danielle again and he played with her"]
    # sentences = ["Jeffrey will argue with Danielle again if he played with her"]

    dm = parser.decmem.copy()

    for sentence in sentences:
        print("\nNow parsing:\t", sentence, "\n")
        time, sortedDM = reading(sentence, dm)
        print("\nTime to read preposition:", time)
        print("\nParse states in declarative memory at the end of the simulation",
            "\nordered by time of (re)activation:")
        for chunk in sortedDM:
            if chunk[0].typename == "parse_state":
                print(chunk[1], "\t", chunk[0])
        print("\nDRSs in declarative memory at the end of the simulation",
            "\nordered by time of (re)activation:")
        for chunk in sortedDM:
            if chunk[0].typename == "drs":
                print(chunk[1], "\t", chunk[0])
        print("\n")
        print("\nJust finished parsing:\t", sentence)
        print("\n\nPress any key to continue.\n")
        input()
