"""
Syn/sem parser for fan experiment.
"""

import pyactr as actr
import simpy
import re
import itertools
from nltk.stem.snowball import SnowballStemmer


environment = actr.Environment(focus_position=(320, 180))

actr.chunktype("parsing_goal",
               "task stack1 stack2 stack3 stack4 arg_stack \
                expected1 expected2 expected3 parsed_word right_frontier\
                dref_peg")
actr.chunktype("parse_state",
               "node_cat mother daughter1 daughter2 lex_head")
actr.chunktype("word", "form cat pred")
actr.chunktype("drs",
               "dref pred arg1 arg2")

actr.chunktype("main_drs",
               "subdrs1 subdrs2 subdrs3")

parser = actr.ACTRModel(environment, subsymbolic=True,\
                        retrieval_threshold=-5, latency_factor=0.5,\
                        latency_exponent=0.5, emma_noise=False,\
                        rule_firing=0.1, buffer_spreading_activation={"g":2},\
                        strength_of_association=2)

dm = parser.decmem
parser.goal
parser.set_goal(name="imaginal", delay=0)
parser.set_goal(name="discourse_context", delay=0)

# stemmer to generate non-logical constants for word meaning representations
stemmer = SnowballStemmer("english")

for det in ['the', 'a']:
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(det)+"""
    cat  Det
    """))

for noun in ['doctor', 'hippie', 'lawyer', 'debutante','captain', 'fireman',\
             'cave', 'bank', 'park', 'church', 'town', 'shop']:
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(noun)+"""
    cat  N
    pred """+str(noun).upper()+"""
    """))

for prep in ['in']:
    predicate = stemmer.stem(prep)
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(prep)+"""
    cat  P
    pred """+str(predicate).upper()+"""
    """))

for copverb in ['is', 'was']:
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(copverb)+"""
    cat  Vcop
    """))

for chunk in dm:
     # we set high activation because the words are very frequent
     # (activation around 5 is common for high-frequency words)
    dm.activations[chunk] = 5

for word in ["park", "church", "town"]:
    hippie = actr.makechunk(typename="drs", arg1=1, dref=1, pred='HIPPIE')
    location = actr.makechunk(typename="drs", arg1=2, pred=word.upper())
    in_relation = actr.makechunk(typename="drs", arg1=1, arg2=2, dref=2,\
                                 pred='IN')
    dm.add(actr.makechunk(typename="main_drs", subdrs1=hippie,\
                          subdrs2=location, subdrs3=in_relation))

for word in ["park", "church"]:
    captain =actr.makechunk(typename="drs", arg1=1, dref=1, pred='CAPTAIN')
    location = actr.makechunk(typename="drs", arg1=2, pred=word.upper())
    in_relation = actr.makechunk(typename="drs", arg1=1, arg2=2, dref=2,\
                                 pred='IN')
    dm.add(actr.makechunk(typename="main_drs", subdrs1=captain,\
                          subdrs2=location, subdrs3=in_relation))

for word in ["bank", "shop"]:
    doctor =actr.makechunk(typename="drs", arg1=1, dref=1, pred='DOCTOR')
    location = actr.makechunk(typename="drs", arg1=2, pred=word.upper())
    in_relation = actr.makechunk(typename="drs", arg1=1, arg2=2, dref=2,\
                                 pred='IN')
    dm.add(actr.makechunk(typename="main_drs", subdrs1=doctor,\
                          subdrs2=location, subdrs3=in_relation))

fireman = actr.makechunk(typename="drs", arg1=1, dref=1, pred='FIREMAN')
park = actr.makechunk(typename="drs", arg1=2, pred='PARK')
in_relation = actr.makechunk(typename="drs", arg1=1, arg2=2, dref=2, pred='IN')
dm.add(actr.makechunk(typename="main_drs", subdrs1=fireman, subdrs2=park,\
                      subdrs3=in_relation))

debutante = actr.makechunk(typename="drs", arg1=1, dref=1, pred='DEBUTANTE')
bank = actr.makechunk(typename="drs", arg1=2, pred='BANK')
in_relation = actr.makechunk(typename="drs", arg1=1, arg2=2, dref=2, pred='IN')
dm.add(actr.makechunk(typename="main_drs", subdrs1=debutante, subdrs2=bank,\
                      subdrs3=in_relation))

lawyer = actr.makechunk(typename="drs", arg1=1, dref=1, pred='LAWYER')
cave = actr.makechunk(typename="drs", arg1=2, pred='CAVE')
in_relation = actr.makechunk(typename="drs", arg1=1, arg2=2, dref=2, pred='IN')
dm.add(actr.makechunk(typename="main_drs", subdrs1=lawyer, subdrs2=cave,\
                      subdrs3=in_relation))
