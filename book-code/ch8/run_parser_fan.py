"""
Simulation of syn/sem parser for fan experiment.

Run simulation by calling the file + one argument:
which is either 0 (stepwise simulation) or 1 (realtime simulation).

example: python3 run_parser_fan.py 0
"""

import pyactr as actr
import simpy
import re
import sys

# import warnings
# warnings.filterwarnings("ignore")

from parser_rules_fan import parser
from parser_dm_fan import environment

parser.goals["g"].add(actr.chunkstring(string="""
    isa             parsing_goal
    task            reading_word
    stack1          S
    right_frontier  S
    dref_peg        1
"""))

if __name__ == "__main__":

    simulate = int(sys.argv[1])

    sentence = "a lawyer is in a cave"
    sentence = sentence.split()

    dm = parser.decmem

    parser.retrieval.finst = 5

    environment.current_focus = (160, 180)
    stimuli = [{x: {'text': word, 'position': (160+x*40, 180)}\
               for x, word in enumerate(sentence)}]
    parser.visualBuffer("visual", "visual_location", parser.decmem, finst=80)
    if simulate:
        parser_sim = parser.simulation(
        realtime=True,
        gui=True,
        environment_process=environment.environment_process,
        stimuli=stimuli,
        triggers='space')
    else:
        parser_sim = parser.simulation(
        realtime=False,
        gui=False,
        environment_process=environment.environment_process,
        stimuli=stimuli,
        triggers='space')

    if simulate:
        parser_sim.run(5)
    else:
        while True:
            try:
                parser_sim.step()
            except simpy.core.EmptySchedule:
                break
            if re.search("^RULE FIRED: move eyes",\
                         str(parser_sim.current_event.action)):
                print(parser.goals["g"])
                print(parser.goals["discourse_context"])
                input()

    sortedDM = sorted(([item[0], time] for item in dm.items()\
                        for time in item[1]),\
                      key=lambda item: item[1])
