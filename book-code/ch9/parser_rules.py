"""
Procedural memory related components of:

Eager left-corner syn/sem parser for the interaction of
pronominal/presuppositional cataphora and conjunctions/conditionals.

Models self-paced reading (left-to-right moving window paradigm).
Also models eye movements.
Instantiates a form of "parallel reader": key press commands are issued as soon
as lexical retrieval is completed; further processing (construction of
appropriate syn/sem structures etc.) is done in parallel to the motor module
actions.
"""

from parser_dm import parser

parser = parser

# AGAIN is a right-adjoined adjunct, and these adjuncts are parsed completely
# bottom-up (i.e., the generalized left-corner announce point is only after the
# adjunct is parsed). So a syntactic search for the VP to which AGAIN needs to
# be adjoined has to be triggered.

# Separately from this, AGAIN triggers a presupposition that is anaphorically
# resolved or, if that fails, cataphorically resolved.
# The search is based on the structure of the discourse context (the DRS
# embedding level where the anaphora/cataphora originates)
# The retrieval request for the antecedent is conditioned on:
# -- the gender of the pronouns for pronominal anaphora / cataphora
# -- the verbal predicate to which AGAIN attaches for presuppositional anaphora
# / cataphora
# If the anaphoric search of an antecedent fails, a cataphoric search will be
# triggered after every NP for pronominal cataphora, and after every verb for
# AGAIN

# move peg rules

for i in range(1, 20):
    parser.productionstring(name="move entity/individual dref peg to x" + str(i+1), string="""
    =g>
    isa               parsing_goal
    task              move_dref_peg
    dref_peg          x"""+str(i)+"""
    ==>
    =g>
    isa               parsing_goal
    task              parsing
    dref_peg          x"""+str(i+1))

for i in range(1, 20):
    parser.productionstring(name="move event dref peg to e" + str(i+1), string="""
    =g>
    isa               parsing_goal
    task              move_event_peg
    event_peg         e"""+str(i)+"""
    ==>
    =g>
    isa               parsing_goal
    task              parsing
    event_peg         e"""+str(i+1))

for i in range(1, 20):
    parser.productionstring(name="move event dref peg to e" + str(i+1) + " and wait for retrieval", string="""
    =g>
    isa               parsing_goal
    task              move_event_peg_and_wait_for_retrieval
    event_peg         e"""+str(i)+"""
    ==>
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_AGAIN
    event_peg         e"""+str(i+1))

for i in range(1, 20):
    parser.productionstring(name="move DRS/propositional dref peg to d" + str(i+1), string="""
    =g>
    isa               parsing_goal
    task              move_drs_peg
    drs_peg           d"""+str(i)+"""
    drs_peg           =drs_peg
    ==>
    =g>
    isa               parsing_goal
    task              parsing
    prev_drs_peg      =drs_peg
    drs_peg           d"""+str(i+1)+"""
""")


# word related rules

parser.productionstring(name="encode word", string="""
    =g>
    isa               parsing_goal
    task              ~move_dref_peg
    task              ~move_event_peg
    task              ~move_event_peg_and_wait_for_retrieval
    task              ~move_drs_peg
    task              ~attempting_to_resolve_PRO
    task              ~attempting_to_resolve_AGAIN
    task              ~attempting_to_resolve_cataphoric_PRO
    task              ~attempting_to_resolve_cataphoric_AGAIN
    task              ~if_reanalysis
    task              ~stop_resolution_attempt_PRO
    task              ~stop_resolution_attempt_AGAIN
    found             None
    parsed_word       None
    =visual>
    isa               _visual
    value             =val
    ==>
    =g>
    isa               parsing_goal
    task              encoding_word
    parsed_word       =val
    ~visual>
    ~retrieval>
""", utility=-1)

parser.productionstring(name="encode word after failed resolution", string="""
    =g>
    isa               parsing_goal
    task              ~move_dref_peg
    task              ~move_event_peg
    task              ~move_event_peg_and_wait_for_retrieval
    task              ~move_drs_peg
    task              ~attempting_to_resolve_PRO
    task              ~attempting_to_resolve_AGAIN
    task              ~attempting_to_resolve_cataphoric_PRO
    task              ~attempting_to_resolve_cataphoric_AGAIN
    task              ~if_reanalysis
    task              ~stop_resolution_attempt_PRO
    task              ~stop_resolution_attempt_AGAIN
    found             no_antecedent
    parsed_word       None
    =visual>
    isa               _visual
    value             =val
    ==>
    =g>
    isa               parsing_goal
    task              encoding_word
    parsed_word       =val
    ~visual>
    ~retrieval>
""", utility=-1)

parser.productionstring(name="retrieve word", string="""
    =g>
    isa               parsing_goal
    task              encoding_word
    parsed_word       =w
    ==>
    +retrieval >
    isa               word
    form              =w
    =g>
    isa               parsing_goal
    task              retrieving_word
""")

parser.productionstring(name="shift and project word (not N)", string="""
    =g>
    isa               parsing_goal
    task              retrieving_word
    =retrieval>
    isa               word
    form              =w
    cat               =c
    cat               ~N
    ==>
    =g>
    isa               parsing_goal
    task              key_press
    found             =c
    +imaginal>
    isa               parse_state
    node_cat          =c
    daughter1         =w
""")

parser.productionstring(name="shift and project N", string="""
    =g>
    isa               parsing_goal
    task              retrieving_word
    =retrieval>
    isa               word
    form              =w
    cat               N
    cat               =c
    ?imaginal>
    buffer            full
    ==>
    =g>
    isa               parsing_goal
    task              key_press
    found             =c
    =imaginal>
    isa               parse_state
    daughter2         =c
    lex_head          =w
    +imaginal>
    isa               parse_state
    node_cat          =c
    daughter1         =w
""")

parser.productionstring(name="press spacebar", string="""
    =g>
    isa               parsing_goal
    task              key_press
    ?manual>
    state             free
    ?retrieval>
    state             free
    ==>
    =g>
    isa               parsing_goal
    task              parsing
    +manual>
    isa               _manual
    cmd               press_key
    key               'space'
""")

parser.productionstring(name="finished: no visual input", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            None
    ?visual>
    state             free
    buffer            empty
    ?manual>
    state             free
    buffer            empty
    ==>
    ~g>
    ~imaginal>
    ~discourse_context>
    ~unresolved_discourse>
""")


# phrase structure rules

parser.productionstring(name="project: NP ==> Det N", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            S
    arg_stack1        =a1
    right_edge_stack1 =re1
    right_edge_stack2 =re2
    parsed_word       =w
    found             Det
    dref_peg          =dref_peg
    drs_peg           =drs_peg
    embedding_level   =el
    =retrieval>
    isa               word
    pred1             =p1
    pred2             =p2
    ==>
    =g>
    isa               parsing_goal
    task              move_dref_peg
    stack1            N
    stack2            NP
    stack3            S
    found             None
    parsed_word       None
    arg_stack1        =dref_peg
    arg_stack2        =a1
    +imaginal>
    isa               parse_state
    node_cat          NP
    daughter1         Det
    daughter2         N
    mother            =re1
    mother_of_mother  =re2
    +discourse_context>
    isa               drs
    dref              =dref_peg
    arg1              =dref_peg
    drs               =drs_peg
    embedding_level   =el
    discourse_status  at_issue
    ~retrieval>
""")

parser.productionstring(name="project and complete: N", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            N
    stack2            =s2
    stack3            =s3
    found             N
    =retrieval>
    isa               word
    pred1             =p1
    pred2             =p2
    ?discourse_context>
    buffer            full
    ==>
    =g>
    isa               parsing_goal
    stack1            =s2
    stack2            =s3
    stack3            None
    found             None
    parsed_word       None
    =discourse_context>
    isa               drs
    pred1             =p1
    pred2             =p2
    ~retrieval>
    ~imaginal>
""")

parser.productionstring(name="project: NP ==> ProperN", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            S
    stack2            =s2
    arg_stack1        =a1
    right_edge_stack1 =re1
    right_edge_stack2 =re2
    parsed_word       =w
    found             ProperN
    dref_peg          =dref_peg
    drs_peg           =drs_peg
    embedding_level   =el
    =retrieval>
    isa               word
    pred1             =p1
    pred2             =p2
    ==>
    =g>
    isa               parsing_goal
    task              move_dref_peg
    stack1            NP
    stack2            S
    stack3            =s2
    arg_stack1        =dref_peg
    arg_stack2        =a1
    found             None
    +imaginal>
    isa               parse_state
    node_cat          NP
    daughter1         ProperN
    mother            =re1
    mother_of_mother  =re2
    lex_head          =w
    +discourse_context>
    isa               drs
    dref              =dref_peg
    arg1              =dref_peg
    pred1             =p1
    pred2             =p2
    drs               =drs_peg
    embedding_level   =el
    discourse_status  at_issue
    ~retrieval>
    ~imaginal>
    ~discourse_context>
""")

parser.productionstring(name="project: NP ==> PRO", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            S
    stack2            =s2
    arg_stack1        =a1
    right_edge_stack1 =re1
    right_edge_stack2 =re2
    parsed_word       =w
    found             PRO
    dref_peg          =dref_peg
    drs_peg           =drs_peg
    embedding_level   =el
    =retrieval>
    isa               word
    pred1             =p1
    pred2             =p2
    ==>
    =g>
    isa               parsing_goal
    task              move_dref_peg
    stack1            NP
    stack2            S
    stack3            =s2
    arg_stack1        =dref_peg
    arg_stack2        =a1
    found             None
    +imaginal>
    isa               parse_state
    node_cat          NP
    daughter1         PRO
    mother            =re1
    mother_of_mother  =re2
    lex_head          =w
    +discourse_context>
    isa               drs
    dref              =dref_peg
    arg1              =dref_peg
    pred1             =p2
    drs               =drs_peg
    embedding_level   =el
    discourse_status  at_issue
    +unresolved_discourse>
    isa               drs
    arg1              =dref_peg
    arg2              UNKNOWN
    pred1             =p1
    pred2             =p2
    drs               =drs_peg
    embedding_level   =el
    discourse_status  unresolved
    ~retrieval>
    ~imaginal>
    ~discourse_context>
""")

parser.productionstring(name="project and complete: NP ==> Det N", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            NP
    right_edge_stack1 =re1
    right_edge_stack2 =re2
    right_edge_stack3 =re3
    right_edge_stack4 =re4
    parsed_word       =w
    found             Det
    dref_peg          =dref_peg
    drs_peg           =drs_peg
    embedding_level   =el
    =retrieval>
    isa               word
    pred1             =p1
    pred2             =p2
    ?discourse_context>
    buffer            full
    ==>
    =g>
    isa               parsing_goal
    task              move_dref_peg
    stack1            N
    found             None
    parsed_word       None
    right_edge_stack1 =re2
    right_edge_stack2 =re3
    right_edge_stack3 =re4
    right_edge_stack4 None
    +imaginal>
    isa               parse_state
    node_cat          NP
    daughter1         Det
    mother            =re1
    mother_of_mother  =re2
    =discourse_context>
    isa               drs
    arg2              =dref_peg
    +discourse_context>
    isa               drs
    dref              =dref_peg
    arg1              =dref_peg
    pred1             =p1
    pred2             =p2
    drs               =drs_peg
    embedding_level   =el
    discourse_status  at_issue
    ~retrieval>
""")

parser.productionstring(name="project and complete: NP ==> ProperN", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            NP
    stack2            =s2
    stack3            =s3
    parsed_word       =w
    found             ProperN
    right_edge_stack1 =re1
    right_edge_stack2 =re2
    right_edge_stack3 =re3
    right_edge_stack4 =re4
    dref_peg          =dref_peg
    drs_peg           =drs_peg
    embedding_level   =el
    =retrieval>
    isa               word
    pred1             =p1
    pred2             =p2
    ?discourse_context>
    buffer            full
    ==>
    =g>
    isa               parsing_goal
    task              move_dref_peg
    stack1            =s2
    stack2            =s3
    stack3            None
    found             None
    parsed_word       None
    right_edge_stack1 =re2
    right_edge_stack2 =re3
    right_edge_stack3 =re4
    right_edge_stack4 None
    +imaginal>
    isa               parse_state
    node_cat          NP
    daughter1         ProperN
    mother            =re1
    mother_of_mother  =re2
    lex_head          =w
    =discourse_context>
    isa               drs
    arg2              =dref_peg
    +discourse_context>
    isa               drs
    dref              =dref_peg
    arg1              =dref_peg
    pred1             =p1
    pred2             =p2
    drs               =drs_peg
    embedding_level   =el
    discourse_status  at_issue
    ~retrieval>
    ~imaginal>
    ~discourse_context>
""")

parser.productionstring(name="project and complete: NP ==> PRO", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            NP
    stack2            =s2
    stack3            =s3
    parsed_word       =w
    found             PRO
    right_edge_stack1 =re1
    right_edge_stack2 =re2
    right_edge_stack3 =re3
    right_edge_stack4 =re4
    dref_peg          =dref_peg
    drs_peg           =drs_peg
    embedding_level   =el
    =retrieval>
    isa               word
    pred1             =p1
    pred2             =p2
    ?discourse_context>
    buffer            full
    ==>
    =g>
    isa               parsing_goal
    task              move_dref_peg
    stack1            =s2
    stack2            =s3
    stack3            None
    found             None
    parsed_word       None
    right_edge_stack1 =re2
    right_edge_stack2 =re3
    right_edge_stack3 =re4
    right_edge_stack4 None
    +imaginal>
    isa               parse_state
    node_cat          NP
    daughter1         PRO
    mother            =re1
    mother_of_mother  =re2
    lex_head          =w
    =discourse_context>
    isa               drs
    arg2              =dref_peg
    +discourse_context>
    isa               drs
    dref              =dref_peg
    arg1              =dref_peg
    pred1             =p2
    drs               =drs_peg
    embedding_level   =el
    discourse_status  at_issue
    +unresolved_discourse>
    isa               drs
    arg1              =dref_peg
    arg2              UNKNOWN
    pred1             =p1
    pred2             =p2
    drs               =drs_peg
    embedding_level   =el
    discourse_status  unresolved
    ~retrieval>
    ~imaginal>
    ~discourse_context>
""")

parser.productionstring(name="project and complete: VP ==> Vi", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            VP
    found             Vi
    parsed_word       =w
    right_edge_stack1 VP
    right_edge_stack2 =re2
    right_edge_stack3 =re3
    right_edge_stack4 =re4
    arg_stack1        =a1
    drs_peg           =drs_peg
    event_peg         =ev_peg
    embedding_level   =el
    =retrieval>
    isa               word
    pred1             =p1
    ==>
    =g>
    isa               parsing_goal
    task              move_event_peg
    stack1            None
    found             None
    parsed_word       None
    right_edge_stack1 =re2
    right_edge_stack2 =re3
    right_edge_stack3 =re4
    right_edge_stack4 None
    +imaginal>
    isa               parse_state
    mother            =re2
    mother_of_mother  =re3
    node_cat          VP
    daughter1         Vi
    lex_head          =w
    +discourse_context>
    isa               drs
    dref              =ev_peg
    event_arg         =ev_peg
    arg1              =a1
    pred1             =p1
    drs               =drs_peg
    embedding_level   =el
    discourse_status  at_issue
    ~retrieval>
    ~imaginal>
    ~discourse_context>
""")

parser.productionstring(name="project and complete: VP ==> Vt NP", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            VP
    found             Vt
    parsed_word       =w
    arg_stack1        =a1
    right_edge_stack1 VP
    right_edge_stack2 =re2
    right_edge_stack3 =re3
    right_edge_stack4 =re4
    drs_peg           =drs_peg
    event_peg         =ev_peg
    embedding_level   =el
    =retrieval>
    isa               word
    pred1             =p1
    ==>
    =g>
    isa               parsing_goal
    task              move_event_peg
    stack1            NP
    found             None
    parsed_word       None
    +imaginal>
    isa               parse_state
    mother            =re2
    mother_of_mother  =re3
    node_cat          VP
    daughter1         Vt
    daughter2         NP
    lex_head          =w
    +discourse_context>
    isa               drs
    dref              =ev_peg
    event_arg         =ev_peg
    arg1              =a1
    pred1             =p1
    drs               =drs_peg
    embedding_level   =el
    discourse_status  at_issue
    ~retrieval>
    ~imaginal>
""")

parser.productionstring(name="project and complete: VP ==> Vt PP (no if_conseq_pred present)", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            VP
    found             VtPP
    parsed_word       =w
    arg_stack1        =a1
    right_edge_stack1 VP
    right_edge_stack1 =re1
    right_edge_stack2 =re2
    right_edge_stack3 =re3
    right_edge_stack4 =re4
    event_peg         =ev_peg
    drs_peg           =drs_peg
    embedding_level   =el
    if_conseq_pred    None
    =retrieval>
    isa               word
    pred1             =p1
    ==>
    =g>
    isa               parsing_goal
    task              move_event_peg
    stack1            PP
    found             None
    parsed_word       None
    right_edge_stack1 PP
    right_edge_stack2 =re1
    right_edge_stack3 =re2
    right_edge_stack4 =re3
    +imaginal>
    isa               parse_state
    mother            =re2
    mother_of_mother  =re3
    node_cat          VP
    daughter1         VtPP
    daughter2         PP
    lex_head          =w
    +discourse_context>
    isa               drs
    dref              =ev_peg
    event_arg         =ev_peg
    arg1              =a1
    pred1             =p1
    drs               =drs_peg
    embedding_level   =el
    discourse_status  at_issue
    ~retrieval>
    ~imaginal>
""")

parser.productionstring(name="project and complete: VP ==> Vt PP (if_conseq_pred present, but also event cataphora)", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            VP
    found             VtPP
    parsed_word       =w
    arg_stack1        =a1
    right_edge_stack1 VP
    right_edge_stack1 =re1
    right_edge_stack2 =re2
    right_edge_stack3 =re3
    right_edge_stack4 =re4
    event_peg         =ev_peg
    drs_peg           =drs_peg
    embedding_level   =el
    if_conseq_pred    ~None
    event_cataphora   True
    =retrieval>
    isa               word
    pred1             =p1
    ==>
    =g>
    isa               parsing_goal
    task              move_event_peg
    stack1            PP
    found             None
    parsed_word       None
    right_edge_stack1 PP
    right_edge_stack2 =re1
    right_edge_stack3 =re2
    right_edge_stack4 =re3
    +imaginal>
    isa               parse_state
    mother            =re2
    mother_of_mother  =re3
    node_cat          VP
    daughter1         VtPP
    daughter2         PP
    lex_head          =w
    +discourse_context>
    isa               drs
    dref              =ev_peg
    event_arg         =ev_peg
    arg1              =a1
    pred1             =p1
    drs               =drs_peg
    embedding_level   =el
    discourse_status  at_issue
    ~retrieval>
    ~imaginal>
""")

parser.productionstring(name="project and complete: VP ==> Vt PP (if_conseq_pred present, mismatching pred)", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            VP
    found             VtPP
    parsed_word       =w
    arg_stack1        =a1
    right_edge_stack1 VP
    right_edge_stack1 =re1
    right_edge_stack2 =re2
    right_edge_stack3 =re3
    right_edge_stack4 =re4
    event_peg         =ev_peg
    drs_peg           =drs_peg
    embedding_level   =el
    if_conseq_pred    ~None
    if_conseq_pred    =verbal_pred
    event_cataphora   ~True
    =retrieval>
    isa               word
    pred1             =p1
    pred1             ~=verbal_pred
    ==>
    =g>
    isa               parsing_goal
    task              move_event_peg
    stack1            PP
    found             None
    parsed_word       None
    right_edge_stack1 PP
    right_edge_stack2 =re1
    right_edge_stack3 =re2
    right_edge_stack4 =re3
    +imaginal>
    isa               parse_state
    mother            =re2
    mother_of_mother  =re3
    node_cat          VP
    daughter1         VtPP
    daughter2         PP
    lex_head          =w
    +discourse_context>
    isa               drs
    dref              =ev_peg
    event_arg         =ev_peg
    arg1              =a1
    pred1             =p1
    drs               =drs_peg
    embedding_level   =el
    discourse_status  at_issue
    ~retrieval>
    ~imaginal>
""")

parser.productionstring(name="project and complete: VP ==> Vt PP (if_conseq_pred present, matching pred)", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            VP
    found             VtPP
    parsed_word       =w
    arg_stack1        =a1
    right_edge_stack1 VP
    right_edge_stack1 =re1
    right_edge_stack2 =re2
    right_edge_stack3 =re3
    right_edge_stack4 =re4
    event_peg         =ev_peg
    drs_peg           =drs_peg
    embedding_level   =el
    if_conseq_pred    ~None
    if_conseq_pred    =verbal_pred
    event_cataphora   ~True
    =retrieval>
    isa               word
    pred1             =verbal_pred
    ==>
    =g>
    isa               parsing_goal
    task              move_event_peg_and_wait_for_retrieval
    stack1            PP
    found             None
    parsed_word       None
    right_edge_stack1 PP
    right_edge_stack2 =re1
    right_edge_stack3 =re2
    right_edge_stack4 =re3
    +imaginal>
    isa               parse_state
    mother            =re2
    mother_of_mother  =re3
    node_cat          VP
    daughter1         VtPP
    daughter2         PP
    lex_head          =w
    +discourse_context>
    isa               drs
    dref              =ev_peg
    event_arg         =ev_peg
    arg1              =a1
    pred1             =verbal_pred
    drs               =drs_peg
    embedding_level   =el
    discourse_status  at_issue
    +retrieval>
    isa               drs
    dref              None
    arg1              UNKNOWN
    arg2              ~None
    pred1             ~None
    pred2             =verbal_pred
    drs               =drs_peg
    embedding_level   ~0
    discourse_status  unresolved
    ~imaginal>
    ~unresolved_discourse>
""")

parser.productionstring(name="project and complete: PP ==> P NP", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            PP
    found             P
    parsed_word       =w
    arg_stack1        =a1
    right_edge_stack1 PP
    right_edge_stack2 =re2
    right_edge_stack3 =re3
    right_edge_stack4 =re4
    drs_peg           =drs_peg
    embedding_level   =el
    =retrieval>
    isa               word
    pred1             =p1
    ==>
    =g>
    isa               parsing_goal
    stack1            NP
    found             None
    parsed_word       None
    +imaginal>
    isa               parse_state
    mother            =re2
    mother_of_mother  =re3
    node_cat          PP
    daughter1         P
    daughter2         NP
    lex_head          =w
    =discourse_context>
    isa               drs
    arg1              =a1
    pred2             =p1
    drs               =drs_peg
    embedding_level   =el
    discourse_status  at_issue
    ~retrieval>
    ~imaginal>
""")

parser.productionstring(name="project and complete: S ==> NP VP", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            NP
    stack2            S
    stack3            =s3
    right_edge_stack1 =re1
    right_edge_stack2 =re2
    right_edge_stack3 =re3
    right_edge_stack4 =re4
    ==>
    =g>
    isa               parsing_goal
    stack1            VP
    stack2            =s3
    stack3            None
    right_edge_stack1 VP
    right_edge_stack2 =re1
    right_edge_stack3 =re2
    right_edge_stack4 =re3
    found             None
    parsed_word       None
    +imaginal>
    isa               parse_state
    node_cat          S
    daughter1         NP
    daughter2         VP
    ~retrieval>
    ~imaginal>
    ~discourse_context>
""")

parser.productionstring(name="project and complete: AP ==> A", string="""
    =g>
    isa               parsing_goal
    task              parsing
    found             A
    stack1            AP
    stack2            =s2
    stack3            =s3
    parsed_word       =w
    right_edge_stack1 =re1
    right_edge_stack2 =re2
    right_edge_stack3 =re3
    right_edge_stack4 =re4
    arg_stack1        =a1
    drs_peg           =drs_peg
    embedding_level   =el
    =retrieval>
    isa               word
    pred1             =p1
    ==>
    =g>
    isa               parsing_goal
    stack1            =s2
    stack2            =s3
    stack3            None
    found             None
    parsed_word       None
    right_edge_stack1 =re2
    right_edge_stack2 =re3
    right_edge_stack3 =re4
    right_edge_stack4 None
    =imaginal>
    isa               parse_state
    lex_head          =w
    +imaginal>
    isa               parse_state
    node_cat          AP
    daughter1         A
    mother            =re1
    mother_of_mother  =re2
    lex_head          =w
    +discourse_context>
    isa               drs
    arg1              =a1
    pred1             =p1
    drs               =drs_peg
    embedding_level   =el
    discourse_status  at_issue
    ~retrieval>
    ~imaginal>
    ~discourse_context>
""")

parser.productionstring(name="project and complete: VP ==> Vcop AP", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            VP
    found             Vcop
    parsed_word       =w
    right_edge_stack1 VP
    right_edge_stack2 =re2
    right_edge_stack3 =re3
    ==>
    =g>
    isa               parsing_goal
    stack1            AP
    found             None
    parsed_word       None
    +imaginal>
    isa               parse_state
    mother            =re2
    mother_of_mother  =re3
    node_cat          VP
    daughter1         Vcop
    daughter2         AP
    ~retrieval>
    ~discourse_context>
""")

parser.productionstring(name="project and complete: VP ==> Vaux VP", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            VP
    found             Vaux
    parsed_word       =w
    right_edge_stack1 =re1
    right_edge_stack2 =re2
    right_edge_stack3 =re3
    right_edge_stack4 =re4
    ==>
    =g>
    isa               parsing_goal
    found             None
    parsed_word       None
    right_edge_stack1 VP
    right_edge_stack2 =re1
    right_edge_stack3 =re2
    right_edge_stack4 =re3
    +imaginal>
    isa               parse_state
    mother            =re2
    mother_of_mother  =re3
    node_cat          VP
    daughter1         Vaux
    daughter2         VP
    lex_head          =w
    ~retrieval>
    ~imaginal>
    ~discourse_context>
""")

parser.productionstring(name="project and complete: VP ==> VauxNeg VP", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            VP
    found             VauxNeg
    parsed_word       =w
    right_edge_stack1 =re1
    right_edge_stack2 =re2
    right_edge_stack3 =re3
    right_edge_stack4 =re4
    drs_peg           =drs_peg
    embedding_level   =el
    ==>
    =g>
    isa                parsing_goal
    found              None
    parsed_word        None
    right_edge_stack1 VP
    right_edge_stack2 =re1
    right_edge_stack3 =re2
    right_edge_stack4 =re3
    +imaginal>
    isa                parse_state
    mother            =re2
    mother_of_mother  =re3
    node_cat           VP
    daughter1          VauxNeg
    daughter2          VP
    lex_head           =w
    +discourse_context>
    isa                drs
    pred1              NOT
    drs                =drs_peg
    embedding_level    =el
    discourse_status   at_issue
    ~retrieval>
    ~imaginal>
    ~discourse_context>
""")

parser.productionstring(name="project and complete: and", string="""
    =g>
    isa               parsing_goal
    task              parsing
    found             Conj
    parsed_word       and
    parsed_word       =w
    embedding_level   0
    ==>
    =g>
    isa               parsing_goal
    task              move_drs_peg
    stack1            S
    arg_stack1        None
    arg_stack2        None
    found             None
    parsed_word       None
    right_edge_stack1 S
    right_edge_stack2 ConjS
    right_edge_stack3 None
    right_edge_stack4 None
    embedding_level   1
    +imaginal>
    isa               parse_state
    daughter1         S
    daughter2         Conj
    daughter3         S
    node_cat          ConjS
    mother            None
    mother_of_mother  None
    lex_head          =w
    ~discourse_context>
""")

parser.productionstring(name="project and complete: and (following a previous Conj)", string="""
    =g>
    isa               parsing_goal
    task              parsing
    found             Conj
    parsed_word       and
    parsed_word       =w
    embedding_level   1
    ==>
    =g>
    isa               parsing_goal
    task              move_drs_peg
    stack1            S
    arg_stack1        None
    arg_stack2        None
    found             None
    parsed_word       None
    right_edge_stack1 S
    right_edge_stack2 ConjS
    right_edge_stack3 None
    right_edge_stack4 None
    embedding_level   2
    +imaginal>
    isa               parse_state
    daughter1         S
    daughter2         Conj
    daughter3         S
    node_cat          ConjS
    mother            None
    mother_of_mother  None
    lex_head          =w
    ~discourse_context>
""")

parser.productionstring(name="project and complete: sentence-final if", string="""
    =g>
    isa               parsing_goal
    task              parsing
    found             C
    parsed_word       if
    parsed_word       =w
    embedding_level   0
    ==>
    =g>
    isa               parsing_goal
    task              move_drs_peg
    stack1            S
    arg_stack1        None
    arg_stack2        None
    found             None
    parsed_word       None
    right_edge_stack1 S
    right_edge_stack2 CP
    right_edge_stack3 S
    right_edge_stack4 none
    embedding_level   1
    +imaginal>
    isa               parse_state
    daughter1         C
    daughter2         S
    node_cat          CP
    mother            S
    mother_of_mother  None
    lex_head          =w
    ~discourse_context>
""")#we create a [_CP [_C if] S] structure Chomsky-adjoined to the previous S, i.e., we need to set up a higher structure [_S [_S PREVIOUS_SENTENCE_GOES_HERE] [_CP [_C if] S]]; in this rule, we create the [_CP ...] structure and the new right edge (previously right frontier); the next rule ("start if-triggered reanalysis") adjoins it to the previous S

parser.productionstring(name="start if-triggered reanalysis (for sentence-final if)", string="""
    =g>
    isa               parsing_goal
    task              parsing
    found             None
    parsed_word       None
    right_edge_stack2 =re2
    right_edge_stack3 =re3
    drs_peg           =drs_peg
    prev_drs_peg      =prev_drs_peg
    =imaginal>
    isa               parse_state
    daughter1         C
    node_cat          CP
    lex_head          if
    lex_head          =w
    ==>
    =g>
    isa               parsing_goal
    task              if_reanalysis
    right_edge_stack4 None
    +imaginal>
    isa               parse_state
    daughter1         S
    daughter2         =re2
    node_cat          =re3
    mother            None
    lex_head          =w
    +retrieval>
    isa               drs
    drs               =prev_drs_peg
    embedding_level   0
""")

parser.productionstring(name="if-triggered reanalysis (no event recalled)", string="""
    =g>
    isa               parsing_goal
    task              if_reanalysis
    drs_peg           =drs_peg
    prev_drs_peg      =prev_drs_peg
    =retrieval>
    isa               drs
    drs               =drs
    discourse_status  =dstatus
    embedding_level   0
    dref              =dref
    pred1             =p1
    pred2             =p2
    dref              =dref
    drs               =drs
    event_arg         =ea
    event_arg         None
    arg1              =a1
    arg2              =a2
    ?retrieval>
    state             free
    ==>
    +discourse_context>
    isa               drs
    discourse_status  =dstatus
    drs               =drs
    embedding_level   2
    dref              =dref
    pred1             =p1
    pred2             =p2
    dref              =dref
    drs               =drs
    event_arg         =ea
    arg1              =a1
    arg2              =a2
    ?retrieval>
    recently_retrieved False
    +retrieval>
    isa               drs
    drs               =prev_drs_peg
    embedding_level   0
""")

parser.productionstring(name="if-triggered reanalysis (event recalled)", string="""
    =g>
    isa               parsing_goal
    task              if_reanalysis
    drs_peg           =drs_peg
    prev_drs_peg      =prev_drs_peg
    =retrieval>
    isa               drs
    drs               =drs
    discourse_status  =dstatus
    embedding_level   0
    dref              =dref
    pred1             =p1
    pred2             =p2
    dref              =dref
    drs               =drs
    event_arg         =ea
    event_arg         ~None
    arg1              =a1
    arg2              =a2
    ?retrieval>
    state             free
    ==>
    +discourse_context>
    isa               drs
    discourse_status  =dstatus
    drs               =drs
    embedding_level   2
    dref              =dref
    pred1             =p1
    pred2             =p2
    dref              =dref
    drs               =drs
    event_arg         =ea
    arg1              =a1
    arg2              =a2
    =g>
    isa               parsing_goal
    if_conseq_pred    =p1
    ?retrieval>
    recently_retrieved False
    +retrieval>
    isa               drs
    drs               =prev_drs_peg
    embedding_level   0
""")

parser.productionstring(name="stop if-triggered reanalysis", string="""
    =g>
    isa               parsing_goal
    task              if_reanalysis
    ?retrieval>
    state             error
    ?manual>
    state             free
    ==>
    =g>
    isa               parsing_goal
    task              reading_word
    found             None
    parsed_word       None
    ~retrieval>
    ~imaginal>
    ~discourse_context>
""")

parser.productionstring(name="recall S for adjoining adv. AGAIN", string="""
    =g>
    isa               parsing_goal
    task              parsing
    stack1            None
    found             Adv
    parsed_word       =w
    embedding_level   =el
    =retrieval>
    isa               word
    cat  Adv
    ==>
    =g>
    isa               parsing_goal
    task              recall_S
    +retrieval>
    isa               parse_state
    node_cat          S
    daughter1         NP
    daughter2         VP
    ~imaginal>
""")

parser.productionstring(name="build S adjunction and recall event for AGAIN", string="""
    =g>
    isa               parsing_goal
    task              recall_S
    stack1            None
    found             Adv
    drs_peg           =drs_peg
    =retrieval>
    isa               parse_state
    node_cat          S
    daughter1         NP
    daughter2         VP
    ==>
    =g>
    isa               parsing_goal
    task              recall_event
    +imaginal>
    isa               parse_state
    node_cat          S
    daughter1         NP
    daughter2         VP
    daughter3         Adv
    +retrieval>
    isa               drs
    dref              ~None
    event_arg         ~None
    drs               =drs_peg
""")

parser.productionstring(name="encode unresolved event presupposition for AGAIN", string="""
    =g>
    isa               parsing_goal
    task              recall_event
    stack1            None
    found             Adv
    drs_peg           =drs
    =retrieval>
    isa               drs
    event_arg         =ea
    pred1             =p1
    drs               =drs
    embedding_level   =el
    discourse_status  at_issue
    ==>
    =g>
    isa               parsing_goal
    task              parsing
    found             None
    parsed_word       None
    +unresolved_discourse>
    isa               drs
    arg1              UNKNOWN
    arg2              =ea
    pred1             PRECEDES
    pred2             =p1
    drs               =drs
    embedding_level   =el
    discourse_status  unresolved
    ~retrieval>
    ~imaginal>
""")

# anaphora / cataphora rules: PRO

parser.productionstring(name="attempting to resolve pronoun; pronoun at embedding level 0", string="""
    =g>
    isa               parsing_goal
    task              ~reading_word
    task              ~move_dref_peg
    task              ~move_event_peg
    task              ~attempting_to_resolve_PRO
    task              ~attempting_to_resolve_cataphoric_PRO
    task              ~stop_resolution_attempt_PRO
    task              ~if_reanalysis
    found             None
    ?retrieval>
    state             free
    =unresolved_discourse>
    isa               drs
    arg2              UNKNOWN
    pred2             =p2
    drs               =drs
    embedding_level   0
    discourse_status  unresolved
    ==>
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_PRO
    +retrieval>
    isa               drs
    dref              ~None
    event_arg         None
    drs               ~=drs
    embedding_level   0
    discourse_status  at_issue
""", utility=5)#event_arg None ensures that only entities, not events, will be considered as possible antecedents

parser.productionstring(name="attempting to resolve pronoun; pronoun at embedding level 1", string="""
    =g>
    isa               parsing_goal
    task              ~reading_word
    task              ~move_dref_peg
    task              ~move_event_peg
    task              ~attempting_to_resolve_PRO
    task              ~attempting_to_resolve_cataphoric_PRO
    task              ~stop_resolution_attempt_PRO
    task              ~if_reanalysis
    found             None
    ?retrieval>
    state             free
    =unresolved_discourse>
    isa               drs
    arg2              UNKNOWN
    pred2             =p2
    drs               =drs
    embedding_level   1
    discourse_status  unresolved
    ==>
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_PRO
    +retrieval>
    isa               drs
    dref              ~None
    event_arg         None
    drs               ~=drs
    embedding_level   ~2
    discourse_status  at_issue
""", utility=5)#event_arg None ensures that only entities, not events, will be considered as possible antecedents

parser.productionstring(name="attempting to resolve pronoun; pronoun at embedding level 2", string="""
    =g>
    isa               parsing_goal
    task              ~reading_word
    task              ~move_dref_peg
    task              ~move_event_peg
    task              ~attempting_to_resolve_PRO
    task              ~attempting_to_resolve_cataphoric_PRO
    task              ~stop_resolution_attempt_PRO
    task              ~if_reanalysis
    found             None
    ?retrieval>
    state             free
    =unresolved_discourse>
    isa               drs
    arg2              UNKNOWN
    pred2             =p2
    drs               =drs
    embedding_level   2
    discourse_status  unresolved
    ==>
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_PRO
    +retrieval>
    isa               drs
    dref              ~None
    event_arg         None
    drs               ~=drs
    discourse_status  at_issue
""", utility=5)#event_arg None ensures that only entities, not events, will be considered as possible antecedents

parser.productionstring(name="resolution of PRO succeeded", string="""
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_PRO
    embedding_level   =el
    =retrieval>
    isa               drs
    dref              ~None
    dref              =dref
    pred2             =p2
    =unresolved_discourse>
    isa               drs
    arg1              =a1
    arg2              UNKNOWN
    pred1             =p1
    pred2             =p2
    drs               =drs
    discourse_status  unresolved
    ==>
    =g>
    isa               parsing_goal
    task              parsing
    entity_cataphora  None
    +discourse_context>
    isa               drs
    arg1              =a1
    arg2              =dref
    pred1             =p1
    pred2             =p2
    drs               =drs
    embedding_level   =el
    discourse_status  presupposed
    ~retrieval>
    ~unresolved_discourse>
""")

parser.productionstring(name="resolution of PRO failed: no antecedent", string="""
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_PRO
    ?retrieval>
    state             error
    ?unresolved_discourse>
    buffer            full
    =unresolved_discourse>
    isa               drs
    arg2              UNKNOWN
    discourse_status  unresolved
    ==>
    =g>
    isa               parsing_goal
    task              parsing
    entity_cataphora  True
    found             no_antecedent
    ~unresolved_discourse>
    ~retrieval>
""")#we assume that when retrieval of entity failed, it's because the PROnoun is cataphoric

parser.productionstring(name="resolution of PRO failed: antecedent with non-matching gender", string="""
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_PRO
    ?unresolved_discourse>
    buffer            full
    =retrieval>
    isa               drs
    pred2             =p2
    =unresolved_discourse>
    isa               drs
    pred2             ~=p2
    discourse_status  unresolved
    ==>
    =g>
    isa               parsing_goal
    task              parsing
    entity_cataphora  True
    found             no_antecedent
    ~retrieval>
    ~unresolved_discourse>
""")#we assume that when retrieval of entity failed, it's because the PROnoun is cataphoric

parser.productionstring(name="attempting to resolve cataphoric pronoun; antecedent at embedding level 0", string="""
    =g>
    isa               parsing_goal
    task              ~reading_word
    task              ~move_dref_peg
    task              ~move_event_peg
    task              ~attempting_to_resolve_PRO
    task              ~attempting_to_resolve_cataphoric_PRO
    task              ~stop_resolution_attempt_PRO
    task              ~if_reanalysis
    found             None
    entity_cataphora  True
    ?retrieval>
    state             free
    =discourse_context>
    isa               drs
    dref              ~None
    dref              =dref
    event_arg         None
    pred2             ~None
    pred2             =p2
    drs               =drs
    embedding_level   0
    ==>
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_PRO
    +unresolved_discourse>
    isa               drs
    dref              =dref
    arg2              UNKNOWN
    pred2             =p2
    drs               =drs
    embedding_level   0
    discourse_status  unresolved
    +retrieval>
    isa               drs
    dref              None
    arg1              ~None
    arg2              UNKNOWN
    pred1              ~None
    drs               ~=drs
    discourse_status  unresolved
""", utility=5)

parser.productionstring(name="attempting to resolve cataphoric pronoun; antecedent at embedding level 1", string="""
    =g>
    isa               parsing_goal
    task              ~reading_word
    task              ~move_dref_peg
    task              ~move_event_peg
    task              ~attempting_to_resolve_PRO
    task              ~attempting_to_resolve_cataphoric_PRO
    task              ~stop_resolution_attempt_PRO
    task              ~if_reanalysis
    found             None
    entity_cataphora  True
    ?retrieval>
    state             free
    =discourse_context>
    isa               drs
    dref              ~None
    dref              =dref
    event_arg         None
    pred2             ~None
    pred2             =p2
    drs               =drs
    embedding_level   1
    ==>
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_PRO
    +unresolved_discourse>
    isa               drs
    dref              =dref
    arg2              UNKNOWN
    pred2             =p2
    drs               =drs
    embedding_level   1
    discourse_status  unresolved
    +retrieval>
    isa               drs
    dref              None
    arg1              ~None
    arg2              UNKNOWN
    pred1              ~None
    drs               ~=drs
    embedding_level   ~0
    discourse_status  unresolved
""", utility=5)

parser.productionstring(name="attempting to resolve cataphoric pronoun; antecedent at embedding level 2", string="""
    =g>
    isa               parsing_goal
    task              ~reading_word
    task              ~move_dref_peg
    task              ~move_event_peg
    task              ~attempting_to_resolve_PRO
    task              ~attempting_to_resolve_cataphoric_PRO
    task              ~stop_resolution_attempt_PRO
    task              ~if_reanalysis
    found             None
    entity_cataphora  True
    ?retrieval>
    state             free
    =discourse_context>
    isa               drs
    dref              ~None
    dref              =dref
    event_arg         None
    pred2             ~None
    pred2             =p2
    drs               =drs
    embedding_level   2
    ==>
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_PRO
    +unresolved_discourse>
    isa               drs
    dref              =dref
    arg2              UNKNOWN
    pred2             =p2
    drs               =drs
    embedding_level   2
    discourse_status  unresolved
    +retrieval>
    isa               drs
    dref              None
    arg1              ~None
    arg2              UNKNOWN
    pred1              ~None
    drs               ~=drs
    embedding_level   2
    discourse_status  unresolved
""", utility=5)

parser.productionstring(name="resolution of cataphoric PRO succeeded", string="""
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_PRO
    =retrieval>
    isa               drs
    dref              None
    arg1              ~None
    arg1              =a1
    arg2              UNKNOWN
    pred1             =p1
    pred2             =p2
    =unresolved_discourse>
    isa               drs
    dref              =dref
    pred2             =p2
    embedding_level   =el
    drs               =drs
    ==>
    =g>
    isa               parsing_goal
    task              parsing
    entity_cataphora  None
    +discourse_context>
    isa               drs
    arg1              =a1
    arg2              =dref
    pred1             =p1
    pred2             =p2
    drs               =drs
    embedding_level   =el
    discourse_status  presupposed
    ~unresolved_discourse>
    ~retrieval>
""")


# anaphora / cataphora rules: AGAIN

parser.productionstring(name="attempting to resolve event presupposition; presupposition at embedding level 0", string="""
    =g>
    isa               parsing_goal
    task              ~reading_word
    task              ~move_dref_peg
    task              ~move_event_peg
    task              ~attempting_to_resolve_AGAIN
    task              ~attempting_to_resolve_cataphoric_AGAIN
    task              ~stop_resolution_attempt_AGAIN
    task              ~move_event_peg_and_wait_for_retrieval
    task              ~if_reanalysis
    found             None
    ?retrieval>
    state             free
    =unresolved_discourse>
    isa               drs
    arg1              UNKNOWN
    arg2              =ea
    pred2             =p2
    drs               =drs
    embedding_level   0
    discourse_status  unresolved
    ==>
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_AGAIN
    +retrieval>
    isa               drs
    dref              ~None
    event_arg         ~None
    event_arg         ~=ea
    drs               ~=drs
    embedding_level   0
    discourse_status  at_issue
""", utility=5)# we search for a DRS with a DRS peg different from the DRS peg associated with again; given the presence of the pred2 feature =p2, we will get spreading activation to an antecedent with the same verbal predicate, if available

parser.productionstring(name="attempting to resolve event presupposition; presupposition at embedding level 1", string="""
    =g>
    isa               parsing_goal
    task              ~reading_word
    task              ~move_dref_peg
    task              ~move_event_peg
    task              ~attempting_to_resolve_AGAIN
    task              ~attempting_to_resolve_cataphoric_AGAIN
    task              ~stop_resolution_attempt_AGAIN
    task              ~move_event_peg_and_wait_for_retrieval
    task              ~if_reanalysis
    found             None
    ?retrieval>
    state             free
    =unresolved_discourse>
    isa               drs
    arg1              UNKNOWN
    arg2              =ea
    pred2             =p2
    drs               =drs
    embedding_level   1
    discourse_status  unresolved
    ==>
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_AGAIN
    +retrieval>
    isa               drs
    dref              ~None
    event_arg         ~None
    event_arg         ~=ea
    drs               ~=drs
    embedding_level   ~2
    discourse_status  at_issue
""", utility=5)

parser.productionstring(name="attempting to resolve event presupposition; presupposition at embedding level 2", string="""
    =g>
    isa               parsing_goal
    task              ~reading_word
    task              ~move_dref_peg
    task              ~move_event_peg
    task              ~attempting_to_resolve_AGAIN
    task              ~attempting_to_resolve_cataphoric_AGAIN
    task              ~stop_resolution_attempt_AGAIN
    task              ~move_event_peg_and_wait_for_retrieval
    task              ~if_reanalysis
    found             None
    ?retrieval>
    state             free
    =unresolved_discourse>
    isa               drs
    arg1              UNKNOWN
    arg2              =ea
    pred2             =p2
    drs               =drs
    embedding_level   2
    discourse_status  unresolved
    ==>
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_AGAIN
    +retrieval>
    isa               drs
    dref              ~None
    event_arg         ~None
    event_arg         ~=ea
    drs               ~=drs
    discourse_status  at_issue
""", utility=5)

parser.productionstring(name="resolution of AGAIN succeeded", string="""
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_AGAIN
    embedding_level   =el
    =retrieval>
    isa               drs
    dref              ~None
    dref              =ea
    event_arg         =ea
    pred1             =p2
    =unresolved_discourse>
    isa               drs
    arg1              UNKNOWN
    arg2              =ea2
    pred1             =p1
    pred2             =p2
    drs               =drs
    discourse_status  unresolved
    ==>
    =g>
    isa               parsing_goal
    task              parsing
    event_cataphora   None
    +discourse_context>
    isa               drs
    arg1              =ea
    arg2              =ea2
    pred1             =p1
    pred2             =p2
    drs               =drs
    embedding_level   =el
    discourse_status  presupposed
    ~retrieval>
    ~unresolved_discourse>
""")

parser.productionstring(name="resolution of AGAIN failed: no antecedent", string="""
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_AGAIN
    ?retrieval>
    state             error
    ?unresolved_discourse>
    buffer            full
    =unresolved_discourse>
    isa               drs
    arg1              UNKNOWN
    arg2              =ea2
    pred1             =p1
    pred2             =p2
    drs               =drs
    embedding_level   =el
    discourse_status  unresolved
    ==>
    =g>
    isa               parsing_goal
    task              parsing
    event_cataphora   True
    found             no_antecedent
    ~unresolved_discourse>
    ~retrieval>
""")#we assume that when retrieval of event failed, it's because the AGAIN presupposition is cataphoric


parser.productionstring(name="search for an unencoded AGAIN failed", string="""
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_AGAIN
    if_conseq_pred    ~None
    ?retrieval>
    state             error
    ?unresolved_discourse>
    buffer            empty
    ==>
    =g>
    isa               parsing_goal
    task              parsing
    ~retrieval>
""")#this is the end of the maximize presupposition resolution attempt


parser.productionstring(name="resolution of AGAIN failed: antecedent with non-matching verbal predicate", string="""
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_AGAIN
    ?unresolved_discourse>
    buffer            full
    =retrieval>
    isa               drs
    pred1             =p2
    =unresolved_discourse>
    isa               drs
    dref              None
    pred2             ~=p2
    discourse_status  unresolved
    ==>
    =g>
    isa               parsing_goal
    task              parsing
    event_cataphora   True
    found             no_antecedent
    ~retrieval>
    ~unresolved_discourse>
""")#we assume that when retrieval of event failed, it's because the AGAIN presupposition is cataphoric

parser.productionstring(name="attempting to resolve cataphoric event presupposition; antecedent at embedding level 0", string="""
    =g>
    isa               parsing_goal
    task              ~reading_word
    task              ~move_dref_peg
    task              ~move_event_peg
    task              ~attempting_to_resolve_AGAIN
    task              ~attempting_to_resolve_cataphoric_AGAIN
    task              ~stop_resolution_attempt_AGAIN
    task              ~if_reanalysis
    found             None
    event_cataphora   True
    =discourse_context>
    isa               drs
    dref              ~None
    dref              =ea
    arg1              ~None
    event_arg         =ea
    pred1             ~None
    pred1             ~None
    pred1             =p1
    pred2             None
    drs               =drs
    embedding_level   0
    ?retrieval>
    state             free
    ==>
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_AGAIN
    +unresolved_discourse>
    isa               drs
    dref              =ea
    arg1              UNKNOWN
    pred2             =p1
    drs               =drs
    embedding_level   0
    discourse_status  unresolved
    +retrieval>
    isa               drs
    dref              None
    arg1              UNKNOWN
    arg2              ~None
    pred1             ~None
    drs               ~=drs
    discourse_status  unresolved
""", utility=5)

parser.productionstring(name="attempting to resolve cataphoric event presupposition; antecedent at embedding level 1", string="""
    =g>
    isa               parsing_goal
    task              ~reading_word
    task              ~move_dref_peg
    task              ~move_event_peg
    task              ~attempting_to_resolve_AGAIN
    task              ~attempting_to_resolve_cataphoric_AGAIN
    task              ~stop_resolution_attempt_AGAIN
    task              ~if_reanalysis
    found             None
    event_cataphora   True
    =discourse_context>
    isa               drs
    dref              ~None
    dref              =ea
    arg1              ~None
    event_arg         =ea
    pred1             ~None
    pred1             ~None
    pred1             =p1
    pred2             None
    drs               =drs
    embedding_level   1
    ?retrieval>
    state             free
    ==>
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_AGAIN
    +unresolved_discourse>
    isa               drs
    dref              =ea
    arg1              UNKNOWN
    pred2             =p1
    drs               =drs
    embedding_level   1
    discourse_status  unresolved
    +retrieval>
    isa               drs
    dref              None
    arg1              UNKNOWN
    arg2              ~None
    pred1             ~None
    drs               ~=drs
    embedding_level   ~0
    discourse_status  unresolved
""", utility=5)

parser.productionstring(name="attempting to resolve cataphoric event presupposition; antecedent at embedding level 2", string="""
    =g>
    isa               parsing_goal
    task              ~reading_word
    task              ~move_dref_peg
    task              ~move_event_peg
    task              ~attempting_to_resolve_AGAIN
    task              ~attempting_to_resolve_cataphoric_AGAIN
    task              ~stop_resolution_attempt_AGAIN
    task              ~if_reanalysis
    found             None
    event_cataphora   True
    =discourse_context>
    isa               drs
    dref              ~None
    dref              =ea
    arg1              ~None
    event_arg         =ea
    pred1             ~None
    pred1             ~None
    pred1             =p1
    pred2             None
    drs               =drs
    embedding_level   2
    ?retrieval>
    state             free
    ==>
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_AGAIN
    +unresolved_discourse>
    isa               drs
    dref              =ea
    arg1              UNKNOWN
    pred2             =p1
    drs               =drs
    embedding_level   2
    discourse_status  unresolved
    +retrieval>
    isa               drs
    dref              None
    arg1              UNKNOWN
    arg2              ~None
    pred1             ~None
    drs               ~=drs
    embedding_level   2
    discourse_status  unresolved
""", utility=5)

parser.productionstring(name="resolution of cataphoric AGAIN succeeded", string="""
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_AGAIN
    =retrieval>
    isa               drs
    dref              None
    arg1              UNKNOWN
    arg2              ~None
    arg2              =a2
    pred1             =p1
    pred2             =p2
    =unresolved_discourse>
    isa               drs
    dref              =dref
    pred2             =p2
    embedding_level   =el
    drs               =drs
    ==>
    =g>
    isa               parsing_goal
    task              parsing
    event_cataphora  None
    +discourse_context>
    isa               drs
    arg1              =dref
    arg2              =a2
    pred1             =p1
    pred2             =p2
    drs               =drs
    embedding_level   =el
    discourse_status  presupposed
    ~unresolved_discourse>
    ~retrieval>
""")

parser.productionstring(name="resolution of cataphoric AGAIN failed: antecedent with non-matching verbal predicate", string="""
    =g>
    isa               parsing_goal
    task              stop_resolution_attempt_AGAIN
    ?unresolved_discourse>
    buffer            full
    =retrieval>
    isa               drs
    pred2             =p2
    =unresolved_discourse>
    isa               drs
    dref              ~None
    pred2             ~=p2
    discourse_status  unresolved
    ==>
    =g>
    isa               parsing_goal
    task              parsing
    event_cataphora   True
    found             no_antecedent
    ~retrieval>
    ~unresolved_discourse>
""")
