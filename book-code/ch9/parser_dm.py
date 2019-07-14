"""
Declarative memory related components of:

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
from nltk.stem.snowball import SnowballStemmer

import numpy as np

# stemmer to generate non-logical constants for word meaning representations
stemmer = SnowballStemmer("english")

environment = actr.Environment(focus_position=(320, 180))

# we have a discourse_status feature in goal chunks, initialized to the value
# at_issue (as opposed to presupposed or unresolved DRSs)

actr.chunktype("parsing_goal",
               "task stack1 stack2 stack3 \
                arg_stack1 arg_stack2 \
                right_edge_stack1 right_edge_stack2 \
                right_edge_stack3 right_edge_stack4 \
                parsed_word found discourse_status \
                dref_peg event_peg drs_peg prev_drs_peg embedding_level\
                entity_cataphora event_cataphora if_conseq_pred")
actr.chunktype("parse_state",
               "node_cat daughter1 daughter2 daughter3 \
                mother mother_of_mother lex_head")
actr.chunktype("word", "form cat pred1 pred2")
actr.chunktype("pred", "constant_name arity")
actr.chunktype("drs",
               "dref pred1 pred2 event_arg arg1 arg2 \
                discourse_status drs embedding_level")

parser = actr.ACTRModel(environment, subsymbolic=True,
                        #activation_trace=False,
                        motor_prepared=True,
                        retrieval_threshold=-4,
                        latency_factor=0.15,
                        latency_exponent=0.05,
                        emma_noise=False,
                        rule_firing=0.011,
                        buffer_spreading_activation={"discourse_context":2,
                                                     "unresolved_discourse":2},
                        strength_of_association=4)

dm = parser.decmem
parser.goal
parser.set_goal(name="imaginal", delay=0)
parser.set_goal(name="discourse_context", delay=0)
parser.set_goal(name="unresolved_discourse", delay=0)

actr.chunkstring(name="EQUALS", string="""
    isa  pred
    constant_name _equals_
    arity         2
""")

actr.chunkstring(name="MALE", string="""
    isa  pred
    constant_name _male_
    arity         1
""")

actr.chunkstring(name="FEMALE", string="""
    isa  pred
    constant_name _female_
    arity         1
""")

actr.chunkstring(name="NONHUMAN", string="""
    isa  pred
    constant_name _nonhuman_
    arity         1
""")

actr.chunkstring(name="PRECEDES", string="""
    isa  pred
    constant_name _precedes_
    arity         2
""")

for propernoun in ['Jeffrey', 'John', 'Bill']:
    actr.chunkstring(name=str(propernoun).upper(), string="""
    isa  pred
    constant_name _"""+str(propernoun).lower()+"""_
    arity         1
    """)
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(propernoun)+"""
    cat  ProperN
    pred1 """+str(propernoun).upper()+"""
    pred2 MALE
    """))

for propernoun in ['Danielle', 'Mary']:
    actr.chunkstring(name=str(propernoun).upper(), string="""
    isa  pred
    constant_name _"""+str(propernoun).lower()+"""_
    arity         1
    """)
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(propernoun)+"""
    cat  ProperN
    pred1 """+str(propernoun).upper()+"""
    pred2 FEMALE
    """))

for det in ['A', 'The']:
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(det)+"""
    cat  Det
    """))
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(det).lower()+"""
    cat  Det
    """))

for pronoun in ['He', 'Him']:
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(pronoun)+"""
    cat  PRO
    pred1 EQUALS
    pred2 MALE
    """))
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(pronoun).lower()+"""
    cat  PRO
    pred1 EQUALS
    pred2 MALE
    """))

for pronoun in ['She', 'Her']:
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(pronoun)+"""
    cat  PRO
    pred1 EQUALS
    pred2 FEMALE
    """))
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(pronoun).lower()+"""
    cat  PRO
    pred1 EQUALS
    pred2 FEMALE
    """))

for pronoun in ['It']:
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(pronoun)+"""
    cat  PRO
    pred1 EQUALS
    pred2 NONHUMAN
    """))
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(pronoun).lower()+"""
    cat  PRO
    pred1 EQUALS
    pred2 NONHUMAN
    """))

for adverb in ['again']:
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(adverb)+"""
    cat  Adv
"""))

for noun in ['boy', 'man', 'husband']:
    pred = stemmer.stem(noun)
    actr.chunkstring(name=str(pred).upper(), string="""
    isa  pred
    constant_name _"""+str(pred).lower()+"""_
    arity         1
    """)
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(noun)+"""
    cat  N
    pred1 """+str(pred).upper()+"""
    pred2 MALE
    """))

for noun in ['girl', 'woman', 'wife']:
    pred = stemmer.stem(noun)
    actr.chunkstring(name=str(pred).upper(), string="""
    isa  pred
    constant_name _"""+str(pred).lower()+"""_
    arity         1
    """)
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(noun)+"""
    cat  N
    pred1 """+str(pred).upper()+"""
    pred2 FEMALE
    """))

for noun in ['hamburger', 'car', 'horse']:
    pred = stemmer.stem(noun)
    actr.chunkstring(name=str(pred).upper(), string="""
    isa  pred
    constant_name _"""+str(pred).lower()+"""_
    arity         1
    """)
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(noun)+"""
    cat  N
    pred1 """+str(pred).upper()+"""
    pred2 NONHUMAN
    """))

for intransverb in ['smiled', 'left', 'laughed', 'smile']:
    pred = stemmer.stem(intransverb)
    actr.chunkstring(name=str(pred).upper(), string="""
    isa  pred
    constant_name _"""+str(pred).lower()+"""_
    arity         event_plus_1
    """)
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(intransverb)+"""
    cat  Vi
    pred1 """+str(pred).upper()+"""
    """))

for transverb in ['like', 'likes', 'liked', \
                  'eat', 'eats', 'ate', \
                  'see', 'sees', 'saw', \
                  'buy', 'buys', 'bought', \
                  'follow', 'follows', 'followed', \
                  'greet', 'greets', 'greeted', \
                  'ask', 'asks', 'asked']:
    pred = stemmer.stem(transverb)
    actr.chunkstring(name=str(pred).upper(), string="""
    isa  pred
    constant_name _"""+str(pred).lower()+"""_
    arity         event_plus_2
    """)
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(transverb)+"""
    cat  Vt
    pred1 """+str(pred).upper()+"""
    """))

for prepverb in ['argue', 'argues', 'argued', 'play', 'plays', 'played']:
    pred = stemmer.stem(prepverb)
    actr.chunkstring(name=str(pred).upper(), string="""
    isa  pred
    constant_name _"""+str(pred).lower()+"""_
    arity         event_plus_2
    """)
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(prepverb)+"""
    cat  VtPP
    pred1 """+str(pred).upper()+"""
    """))

for prep in ['with', 'in', 'on', 'to']:
    pred = stemmer.stem(prep)
    actr.chunkstring(name=str(pred).upper(), string="""
    isa  pred
    constant_name _"""+str(pred).lower()+"""_
    arity         2
    """)
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(prep)+"""
    cat  P
    pred1 """+str(pred).upper()+"""
    """))

for copverb in ['is', 'was']:
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(copverb)+"""
    cat  Vcop
    """))

for adjective in ['overcooked', 'happy', 'hungry']:
    pred = stemmer.stem(adjective)
    actr.chunkstring(name=str(pred).upper(), string="""
    isa  pred
    constant_name _"""+str(pred).lower()+"""_
    arity         1
    """)
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(adjective)+"""
    cat  A
    pred1 """+str(pred).upper()+"""
    """))

for conj in ['and', 'or']:
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(conj)+"""
    cat  Conj
    """))

for comp in ['if', 'because', 'when']:
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(comp)+"""
    cat  C
    """))

for auxverbneg in ['wont', 'doesnt']:
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(auxverbneg)+"""
    cat  VauxNeg
    """))

for auxverb in ['will']:
    dm.add(actr.chunkstring(string="""
    isa  word
    form """+str(auxverb)+"""
    cat  Vaux
    """))
