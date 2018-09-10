"""
Syn/sem parser for fan experiment (continued).
"""

from parser_dm_fan import parser

parser = parser

# these rules advance the current peg / stack position
# to make new drefs available
for i in range(1,10):
    parser.productionstring(name="move peg" + str(i), string="""
    =g>
    isa             parsing_goal
    task            move_peg
    dref_peg    """+str(i)+"""
    ==>
    =g>
    isa             parsing_goal
    task            parsing
    dref_peg    """+str(i+1))

parser.productionstring(name="move eyes", string="""
    =g>
    isa             parsing_goal
    task            ~reading_word
    task            ~finish_match_drs
    ?retrieval>
    state           free
    =visual_location>
    isa             _visuallocation
    screen_x        =x
    screen_y        =ypos
    ==>
    =g>
    isa             parsing_goal
    task            attending_word
    ?visual_location>
    attended        False
    +visual_location>
    isa             _visuallocation
    screen_x        lowest
    screen_y        =ypos
""", utility=-5)

parser.productionstring(name="attend word", string="""
        =g>
        isa     parsing_goal
        task    attending_word
        =visual_location>
        isa    _visuallocation
        ?visual>
        state   free
        buffer  empty
        ==>
        =g>
        isa     parsing_goal
        task    reading_word
        +visual>
        isa     _visual
        cmd     move_attention
        screen_pos =visual_location
""")

parser.productionstring(name="encode word", string="""
    =g>
    isa             parsing_goal
    task            reading_word
    =visual>
    isa             _visual
    value           =w
    ==>
    =g>
    isa             parsing_goal
    task            encoding_word
    parsed_word     =w
    ~visual>
    ~retrieval>
""")

parser.productionstring(name="retrieve word", string="""
    =g>
    isa             parsing_goal
    task            encoding_word
    parsed_word     =w
    ==>
    +retrieval>
    isa             word
    form            =w
    =g>
    isa             parsing_goal
    task            retrieving_word
""")

parser.productionstring(name="shift and project word", string="""
    =g>
    isa             parsing_goal
    task            retrieving_word
    =retrieval>
    isa             word
    form            =w
    cat             =c
    ==>
    =g>
    isa             parsing_goal
    task            parsing
    +imaginal>
    isa             parse_state
    node_cat        =c
    daughter1       =w
""")

parser.productionstring(name="project: NP ==> Det N", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          S
    stack2          =s2
    right_frontier  =rf
    parsed_word     =w
    dref_peg    =peg
    =retrieval>
    isa             word
    cat            Det
    ==>
    =g>
    isa             parsing_goal
    task            move_peg
    stack1          N
    stack2          NP
    stack3          S
    stack4          =s2
    +imaginal>
    isa             parse_state
    node_cat        NP
    daughter1       Det
    mother          =rf
    lex_head        =w
    +discourse_context>
    isa             drs
    dref            =peg
    arg1            =peg
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
    right_frontier  =rf
    parsed_word     =w
    =retrieval>
    isa             word
    cat             N
    pred           =p
    ?discourse_context>
    buffer          full
    ==>
    =g>
    isa             parsing_goal
    stack1          =s2
    stack2          =s3
    stack3          =s4
    stack4          None
    +imaginal>
    isa             parse_state
    node_cat        NP
    daughter1       Det
    daughter2       N
    lex_head        =w
    mother          =rf
    =discourse_context>
    isa             drs
    pred           =p
    ~retrieval>
""")

parser.productionstring(name="project and complete: NP ==> Det N", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          NP
    right_frontier  =rf
    parsed_word     =w
    dref_peg        =peg
    =retrieval>
    isa             word
    cat             Det
    ?discourse_context>
    buffer          full
    ==>
    =g>
    isa             parsing_goal
    task            move_peg
    stack1          N
    +imaginal>
    isa             parse_state
    node_cat        NP
    daughter1       Det
    mother          =rf
    lex_head        =w
    =discourse_context>
    isa             drs
    dref            =peg
    arg2            =peg
    +discourse_context>
    isa             drs
    arg1            =peg
    ~retrieval>
""")

parser.productionstring(name="project and complete: PP ==> P NP", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          PP
    parsed_word     =w
    arg_stack       =a
    right_frontier  =rf
    =retrieval>
    isa             word
    cat             P
    pred           =p
    ==>
    =g>
    isa             parsing_goal
    stack1          NP
    +imaginal>
    isa             parse_state
    mother          =rf
    node_cat        PP
    daughter1       P
    daughter2       NP
    lex_head        =w
    +discourse_context>
    isa             drs
    arg1            =a
    pred            =p
    ~retrieval>
""")

parser.productionstring(name="project and complete: VP ==> Vcop PP", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          VP
    parsed_word     =w
    right_frontier  =rf
    =retrieval>
    isa             word
    cat            Vcop
    ==>
    =g>
    isa             parsing_goal
    stack1          PP
    right_frontier  PP
    +imaginal>
    isa             parse_state
    mother          =rf
    node_cat        VP
    daughter1       Vcop
    daughter2       PP
    lex_head        =w
    ~retrieval>
""")

parser.productionstring(name="project and complete: S ==> NP VP", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          NP
    stack2          S
    stack3          =s3
    stack4          =s4
    =discourse_context>
    isa             drs
    dref            =d
    ==>
    =g>
    isa             parsing_goal
    stack1          VP
    stack2          =s3
    stack3          =s4
    right_frontier  VP
    arg_stack      =d
    +imaginal>
    isa             parse_state
    node_cat        S
    daughter1       NP
    daughter2       VP
""")

parser.productionstring(name="recall in_relation sub-DRS", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack1          None
    ?discourse_context>
    buffer          full
    ==>
    =g>
    isa             parsing_goal
    task            recall_person_subdrs
    +retrieval>
    isa             drs
    arg1            ~None
""")

parser.productionstring(name="recall person sub-DRS", string="""
    =g>
    isa             parsing_goal
    task            recall_person_subdrs
    stack1          None
    =retrieval>
    isa             drs
    ?discourse_context>
    buffer          full
    ==>
    =g>
    isa             parsing_goal
    task            match_subdrs
    expected3       =retrieval
    ?retrieval>
    recently_retrieved False
    +retrieval>
    isa             drs
    arg1            ~None
""")

parser.productionstring(name="recall main DRS by person sub-DRS", string="""
    =g>
    isa             parsing_goal
    task            match_subdrs
    =retrieval>
    isa             drs
    ?retrieval>
    state           free
    =discourse_context>
    isa             drs
    ==>
    =g>
    isa             parsing_goal
    task            match_main_drs
    expected1       =retrieval
    expected2       =discourse_context
    +retrieval>
    isa             main_drs
    subdrs1         =retrieval
""", utility=0.5)

recall_by_location = parser.productionstring(name="recall main DRS by location sub-DRS", string="""
    =g>
    isa             parsing_goal
    task            match_subdrs
    =retrieval>
    isa             drs
    ?retrieval>
    state           free
    =discourse_context>
    isa             drs
    ==>
    =g>
    isa             parsing_goal
    task            match_main_drs
    expected1       =retrieval
    expected2       =discourse_context
    +retrieval>
    isa             main_drs
    subdrs2         =discourse_context
""")

parser.productionstring(name="match found", string="""
    =g>
    isa             parsing_goal
    task            match_main_drs
    expected1       =e1
    expected2       =e2
    ?retrieval>
    state           free
    buffer          full
    =retrieval>
    isa             main_drs
    subdrs1           =e1
    subdrs2           =e2
    =discourse_context>
    isa             drs
    ==>
    ~g>
    +manual>
    isa             _manual
    cmd             'press_key'
    key             'J'
""")

parser.productionstring(name="mismatch in person found", string="""
    =g>
    isa             parsing_goal
    task            match_main_drs
    expected1       =e1
    expected2       =e2
    ?retrieval>
    state           free
    buffer          full
    =retrieval>
    isa             main_drs
    subdrs1           ~=e1
    subdrs2           =e2
    =discourse_context>
    isa             drs
    ==>
    ~g>
    +manual>
    isa             _manual
    cmd             'press_key'
    key             'F'
""")

parser.productionstring(name="mismatch in location found", string="""
    =g>
    isa             parsing_goal
    task            match_main_drs
    expected1       =e1
    expected2       =e2
    ?retrieval>
    state           free
    buffer          full
    =retrieval>
    isa             main_drs
    subdrs1           =e1
    subdrs2           ~=e2
    =discourse_context>
    isa             drs
    ==>
    ~g>
    +manual>
    isa             _manual
    cmd             'press_key'
    key             'F'
""")

parser.productionstring(name="failed retrieval", string="""
    =g>
    isa             parsing_goal
    task            match_main_drs
    ?retrieval>
    state           error
    ==>
    ~g>
    +manual>
    isa             _manual
    cmd             'press_key'
    key             'F'
""")
