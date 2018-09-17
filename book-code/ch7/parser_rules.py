"""
A left-corner parser for simple clauses and relative clauses.
"""

import pyactr as actr
import simpy
import re
from nltk.stem.snowball import SnowballStemmer

import numpy as np
import pandas as pd

SENTENCES = "sentences.csv"
SEC_IN_YEAR = 365*24*3600
SEC_IN_TIME = 15*SEC_IN_YEAR

def load_file(lfile, index_col=None, sep=","):
    """
    Loads file as a list
    """
    csvfile = pd.read_csv(lfile, index_col=index_col, header=0, sep=sep)
    return csvfile

def get_freq_array(word_freq, real_freq=True):
    """
    Calculates the array of past uses of the word, based on the frequency of the word.

    Why it is calculated this way -> described in Brasoveanu and Dotlacil: An extensible framework for mechanistic processing models.
    """
    time_interval = SEC_IN_TIME / word_freq
    if real_freq:
        return np.arange(start=-time_interval, stop=-(time_interval*word_freq)-1, step=-time_interval)
    else:
        return np.array([0])

#load file for the experiment
stimuli_csv = load_file(SENTENCES, sep=",") #sentences with frequencies

#ACT-R model

environment = actr.Environment(focus_position=(320, 180))

actr.chunktype("parsing_goal",
               "task stack1 stack2 stack3 stack4\
                right_frontier_stack1 right_frontier_stack2 \
                parsed_word gapped just_finished found")
actr.chunktype("parse_state",
               "node_cat mother daughter1 daughter2 daughter3 lex_head")
actr.chunktype("word", "form cat")

parser = actr.ACTRModel(environment, subsymbolic=True, retrieval_threshold=-20,
                        decay = 0.5, latency_factor=0.15, latency_exponent=1,
                        rule_firing=0.05, motor_prepared=True, automatic_visual_search=False)
temp_dm = {}

words = stimuli_csv.groupby('word', sort=False)

for name, group in words:

    freq = group.iloc[0]['freq']
    word = group.iloc[0]['word']
    function = group.iloc[0]['function']

    #temp_dm is the lexical memory (memory of all the words used in the
    #experiment)

    temp_dm[actr.chunkstring(string="""
    isa  word
    form """+str(word)+"""
    cat  """+str(function)+"""
    """)] = get_freq_array(freq)

parser.decmems = {}
parser.set_decmem(temp_dm) #we store lexical knowledge in the parser's
#declarative memory

#below are rules -- production knowledge of the parser

parser.productionstring(name="find first word", string="""
    =g>
    isa             parsing_goal
    task            reading_word
    ?visual_location>
    buffer          empty
    ==>
    ?visual_location>
    attended False
    +visual_location>
    isa _visuallocation
    screen_x lowest
    """)

parser.productionstring(name="encode word", string="""
    =g>
    isa             parsing_goal
    task            reading_word
    =visual_location>
    isa    _visuallocation
    ?visual>
    state   free
    ==>
    =g>
    isa             parsing_goal
    task            reading_word
    +visual>
    isa     _visual
    cmd     move_attention
    screen_pos =visual_location""", utility=-5) #move attention to a located word

parser.productionstring(name="retrieve word", string="""
    =g>
    isa             parsing_goal
    task            reading_word
    ?visual>
    buffer  full
    =visual>
    isa     _visual
    value   =w
    value   ~___
    ?retrieval>
    state      free
    ==>
    =g>
    isa             parsing_goal
    task            shifting_word
    parsed_word     =w
    +retrieval>
    isa             word
    form            =w
""")

parser.productionstring(name="shift and project word", string="""
    =g>
    isa             parsing_goal
    task            shifting_word
    ?retrieval>
    state           free
    buffer          full
    =retrieval>
    isa             word
    form            =w
    cat             =c
    ==>
    =g>
    isa             parsing_goal
    task            parsing
    found           =c
    +imaginal>
    isa             parse_state
    node_cat        =c
    daughter1       =w
    ~visual>
""")

parser.productionstring(name="project and complete: wh", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          =s1
    stack2          =s2
    stack3          =s3
    right_frontier_stack1  =rf1
    parsed_word     =w
    found           'wh'
    just_finished   NP
    ==>
    =g>
    isa             parsing_goal
    task            fillgap
    stack1          'VP'
    stack2          =s1
    stack3          =s2
    stack4          =s3
    parsed_word     None
    right_frontier_stack1  'S'
    right_frontier_stack2  =rf1
    just_finished   'wh-DP'
    +imaginal>
    isa             parse_state
    node_cat        'CP'
    daughter1       'NP'
    daughter2       'S'
    lex_head        wh
    mother          'NP'
""")

parser.productionstring(name="reanalyse: subject wh", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          'VP'
    stack1          =s1
    gapped          True
    found           ~'Vt'
    found           ~'Vi'
    found           ~'Vd'
    found           ~'Vp'
    found           ~'Vcop'
    found           ~None
    ==>
    =g>
    isa             parsing_goal
    stack1          'S'
    stack2          'VP'
    stack3          =s1
    gapped          filling
""")

parser.productionstring(name="project and complete: subj wh-gap", string="""
    =g>
    isa             parsing_goal
    task            fillgap
    found           'wh'
    stack1          'VP'
    gapped          ~filling
    parsed_word     =w
    ==>
    =g>
    isa             parsing_goal
    gapped          True
    found           None
    just_finished   NP
    +imaginal>
    isa             parse_state
    node_cat        'NP'
    daughter1       'gap'
    lex_head        =w
    mother          'S'
""")

parser.productionstring(name="recall wh", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          'VP'
    parsed_word     =w
    parsed_word     ~None
    gapped          filling
    ?retrieval>
    state           free
    =retrieval>
    isa             parse_state
    lex_head        ~wh
    ==>
    +retrieval>
    isa             parse_state
    daughter1       'NP'
    lex_head        wh
    """)

parser.productionstring(name="project: NP ==> Det N", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          S
    stack2          =s2
    right_frontier_stack1  =rf1
    parsed_word     =w
    found           Det
    ==>
    =g>
    isa             parsing_goal
    stack1          N
    stack2          NP
    stack3          S
    stack4          =s2
    found           None
    parsed_word     None
    just_finished   Det
    +imaginal>
    isa             parse_state
    node_cat        NP
    daughter1       Det
    daughter2       N
    mother          =rf1
    ~retrieval>
""")

parser.productionstring(name="project and complete: N", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          N
    stack2          =s2
    stack3          =s3
    stack4          =s4
    parsed_word     =w
    found           N
    ==>
    =g>
    isa             parsing_goal
    stack1          =s2
    stack2          =s3
    stack3          =s4
    stack4          None
    found           None
    parsed_word     None
    just_finished   N
    +imaginal>
    isa             parse_state
    node_cat        'NP'
    daughter1       'Det'
    daughter2       'N'
    lex_head        =w
    mother          'NP'
""")

parser.productionstring(name="project: NP ==> ProperN", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          'S'
    stack2          =s2
    stack3          =s3
    right_frontier_stack1  =rf1
    parsed_word     =w
    found           'ProperN'
    ==>
    =g>
    isa             parsing_goal
    stack1          'NP'
    stack2          'S'
    stack3          =s2
    stack4          =s3
    found           None
    just_finished   ProperN
    +imaginal>
    isa             parse_state
    node_cat        'NP'
    daughter1       'ProperN'
    mother          =rf1
    lex_head        =w
""")

parser.productionstring(name="project: NP ==> PRO", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          'S'
    stack2          =s2
    stack3          =s3
    right_frontier_stack1  =rf1
    parsed_word     =w
    found           'PRO'
    ==>
    =g>
    isa             parsing_goal
    stack1          'NP'
    stack2          'S'
    stack3          =s2
    stack4          =s3
    found           None
    just_finished   PRO
    +imaginal>
    isa             parse_state
    node_cat        'NP'
    daughter1       'PRO'
    mother          =rf1
    lex_head        =w
""")

parser.productionstring(name="project adjunction and complete: PP ==> P NP", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          =s1
    stack2          =s2
    stack3          =s3
    parsed_word     =w
    just_finished   NP
    found          'P'
    ==>
    =g>
    isa             parsing_goal
    stack1          NP
    stack2          =s1
    stack3          =s2
    stack4          =s3
    found           None
    just_finished   P
    right_frontier_stack1  PP
    right_frontier_stack2  NP
    +imaginal>
    isa             parse_state
    node_cat        'PP'
    daughter1       'P'
    mother          NP
""")

parser.productionstring(name="project and complete: PP ==> P NP", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          'PP'
    right_frontier_stack1  =rf1
    parsed_word     =w
    found          'P'
    ==>
    =g>
    isa             parsing_goal
    stack1          NP
    found           None
    just_finished   P
    +imaginal>
    isa             parse_state
    node_cat        'PP'
    daughter1       'P'
    mother          =rf1
""")

parser.productionstring(name="project and complete: NP ==> Det N", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          'NP'
    right_frontier_stack1  =rf1
    right_frontier_stack2  =rf2
    parsed_word     =w
    found          'Det'
    ==>
    =g>
    isa             parsing_goal
    stack1          'N'
    found           None
    right_frontier_stack1  =rf2
    right_frontier_stack2  None
    just_finished   Det
    +imaginal>
    isa             parse_state
    node_cat        'NP'
    daughter1       'Det'
    mother          =rf1
""")

parser.productionstring(name="project and complete: NP ==> ProperN", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          'NP'
    stack2          =s2
    stack3          =s3
    stack4          =s4
    parsed_word     =w
    found           'ProperN'
    right_frontier_stack1  =rf1
    right_frontier_stack2  =rf2
    ==>
    =g>
    isa             parsing_goal
    stack1          =s2
    stack2          =s3
    stack3          =s4
    stack4          None
    found           None
    parsed_word     None
    right_frontier_stack1  =rf2
    right_frontier_stack2  None
    just_finished   NP
    +imaginal>
    isa             parse_state
    node_cat        'NP'
    daughter1       'ProperN'
    mother          =rf1
    lex_head        =w
""")

parser.productionstring(name="project and complete: NP ==> PRO", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          'NP'
    stack2          =s2
    stack3          =s3
    stack4          =s4
    parsed_word     =w
    found           'PRO'
    right_frontier_stack1  =rf1
    right_frontier_stack2  =rf2
    ==>
    =g>
    isa             parsing_goal
    stack1          =s2
    stack2          =s3
    stack3          =s4
    stack4          None
    found           None
    parsed_word     None
    right_frontier_stack1  =rf2
    right_frontier_stack2  None
    just_finished   NP
    +imaginal>
    isa             parse_state
    node_cat        'NP'
    daughter1       'PRO'
    mother          =rf1
    lex_head        =w
""")

parser.productionstring(name="recall subject", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          'VP'
    parsed_word     ~None
    just_finished   ~NP
    ?retrieval>
    state           free
    =retrieval>
    isa             word
    cat             ~None
    ==>
    =g>
    isa             parsing_goal
    task            parsing
    +retrieval>
    isa             parse_state
    node_cat        S
    daughter1       NP
    """, utility=5)

parser.productionstring(name="project and complete: VP ==> Vi", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          'VP'
    stack2          =s2
    stack3          =s3
    stack4          =s4
    found           'Vi'
    parsed_word     =w
    right_frontier_stack1  'VP'
    right_frontier_stack2  =rf2
    ==>
    =g>
    isa             parsing_goal
    stack1          =s2
    stack2          =s3
    stack3          =s4
    stack4          None
    found           None
    parsed_word     None
    right_frontier_stack1  =rf2
    right_frontier_stack2  None
    just_finished   VP
    +imaginal>
    isa             parse_state
    mother          'S'
    node_cat        'VP'
    daughter1       'Vi'
    lex_head        =w
""")

parser.productionstring(name="project and complete: VP ==> Vt NP", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          'VP'
    found           'Vt'
    parsed_word     =w
    gapped          ~filling
    ==>
    =g>
    isa             parsing_goal
    stack1          'NP'
    found           None
    parsed_word     None
    just_finished   Vt
    +imaginal>
    isa             parse_state
    mother          'S'
    node_cat        'VP'
    daughter1       'Vt'
    daughter2       'NP'
    lex_head        =w
""")

parser.productionstring(name="project and complete: VP ==> Vp PP", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          'VP'
    found           'Vp'
    parsed_word     =w
    gapped          ~filling
    ==>
    =g>
    isa             parsing_goal
    stack1          'PP'
    found           None
    parsed_word     None
    just_finished   Vp
    +imaginal>
    isa             parse_state
    mother          'S'
    node_cat        'VP'
    daughter1       'Vp'
    daughter2       'NP'
    lex_head        =w
""")

parser.productionstring(name="project and complete: VP ==> Vt NP gapped", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          'VP'
    stack2          =s2
    stack3          =s3
    stack4          =s4
    found           'Vt'
    gapped          filling
    =retrieval>
    isa             parse_state
    lex_head        'wh'
    ==>
    =g>
    isa             parsing_goal
    stack1          =s2
    stack2          =s3
    stack3          =s4
    stack4          None
    found           None
    parsed_word     None
    gapped          True
    just_finished   Vt
    +imaginal>
    isa             parse_state
    mother          'S'
    node_cat        'VP'
    daughter1       'V'
    daughter2       'NP'
""")

parser.productionstring(name="project and complete: VP ==> Vd NP PP", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          'VP'
    stack2          =s2
    stack3          =s3
    found           'Vd'
    parsed_word     =w
    gapped          ~filling
    ==>
    =g>
    isa             parsing_goal
    stack1          'NP'
    stack2          'PP'
    stack3          =s2
    stack4          =s3
    found           None
    parsed_word     None
    just_finished   Vd
    +imaginal>
    isa             parse_state
    mother          'S'
    node_cat        'VP'
    daughter1       'Vd'
    daughter2       'NP'
    lex_head        =w
""")

parser.productionstring(name="project and complete: VP ==> Vd NP PP gapped", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          'VP'
    found           'Vd'
    parsed_word     =w
    gapped          filling
    =retrieval>
    isa             parse_state
    lex_head        'wh'
    ==>
    =g>
    isa             parsing_goal
    stack1          'PP'
    found           None
    parsed_word     None
    gapped          True
    just_finished   Vd
    +imaginal>
    isa             parse_state
    mother          'S'
    node_cat        'VP'
    daughter1       'Vd'
    daughter2       'NP'
    lex_head        =w
""")

parser.productionstring(name="project and complete: S ==> NP VP", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          NP
    stack2          S
    stack3          =s3
    stack4          =s4
    right_frontier_stack1  =rf1
    ==>
    =g>
    isa             parsing_goal
    stack1          VP
    stack2          =s3
    stack3          =s4
    stack4          None
    right_frontier_stack1  VP
    right_frontier_stack2  =rf1
    found           None
    parsed_word     None
    just_finished   NP
    +imaginal>
    isa             parse_state
    node_cat        S
    daughter1       NP
    daughter2       VP
    ~retrieval>
    ~imaginal>
""")

parser.productionstring(name="project and complete: AP ==> A", string="""
    =g>
    isa             parsing_goal
    task            parsing
    found           A
    stack1          AP
    stack2          =s2
    stack3          =s3
    stack4          =s4
    parsed_word     =w
    right_frontier_stack1  =rf1
    right_frontier_stack2  =rf2
    ==>
    =g>
    isa             parsing_goal
    stack1          =s2
    stack2          =s3
    stack3          =s4
    stack4          None
    found           None
    parsed_word     None
    right_frontier_stack1  =rf2
    right_frontier_stack2  None
    just_finished   AP
    =imaginal>
    isa             parse_state
    lex_head        =w
    +imaginal>
    isa             parse_state
    node_cat        AP
    daughter1       A
    mother          =rf1
    lex_head        =w
""")

parser.productionstring(name="project and complete: VP ==> Vcop PP", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          VP
    found           Vcop
    parsed_word     =w
    ==>
    =g>
    isa             parsing_goal
    stack1          PP
    found           None
    parsed_word     None
    just_finished   Vcop
    +imaginal>
    isa             parse_state
    mother          S
    node_cat        VP
    daughter1       Vcop
    daughter2       PP
""")

parser.productionstring(name="project and complete: VP ==> Vaux VP", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          VP
    found           Vaux
    parsed_word     =w
    ==>
    =g>
    isa             parsing_goal
    found           None
    parsed_word     None
    just_finished   Vaux
    +imaginal>
    isa             parse_state
    mother          S
    node_cat        VP
    daughter1       Vaux
    daughter2       VP
    lex_head        =w
""")

parser.productionstring(name="project and complete: VP ==> VauxNeg VP", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          VP
    found           VauxNeg
    parsed_word     =w
    ==>
    =g>
    isa              parsing_goal
    found            None
    parsed_word      None
    just_finished   VauxNeg
    +imaginal>
    isa              parse_state
    mother           S
    node_cat         VP
    daughter1        VauxNeg
    daughter2        VP
    lex_head         =w
""")

parser.productionstring(name="press spacebar", string="""
    =g>
    isa             parsing_goal
    task            ~reading_word
    task            ~move_eyes
    ?manual>
    state           free
    ?retrieval>
    state           free
    ==>
    =g>
    isa             parsing_goal
    task            move_eyes
    +manual>
    isa             _manual
    cmd             'press_key'
    key             'space'
""", utility=-5)
