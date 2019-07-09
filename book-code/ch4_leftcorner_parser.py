"""
A left-corner parser.
"""

import pyactr as actr

environment = actr.Environment(focus_position=(320, 180))

actr.chunktype("parsing_goal",
               "task stack_top stack_bottom parsed_word right_frontier")
actr.chunktype("parse_state",
               "node_cat mother daughter1 daughter2 lex_head")
actr.chunktype("word", "form cat")

parser = actr.ACTRModel(environment, motor_prepared=True)
dm = parser.decmem
g = parser.goal
imaginal = parser.set_goal(name="imaginal", delay=0)

dm.add(actr.chunkstring(string="""
    isa  word
    form Mary
    cat  ProperN
"""))
dm.add(actr.chunkstring(string="""
    isa  word
    form Bill
    cat  ProperN
"""))
dm.add(actr.chunkstring(string="""
    isa  word
    form likes
    cat  V
"""))
g.add(actr.chunkstring(string="""
    isa             parsing_goal
    task            read_word
    stack_top       S
    right_frontier  S
"""))


parser.productionstring(name="press spacebar", string="""
    =g>
    isa             parsing_goal
    task            read_word
    stack_top       ~None
    ?manual>
    state           free
    ==>
    =g>
    isa             parsing_goal
    task            encode_word
    +manual>
    isa             _manual
    cmd             press_key
    key             'space'
""")

parser.productionstring(name="encode word", string="""
    =g>
    isa             parsing_goal
    task            encode_word
    =visual>
    isa             _visual
    value           =val
    ==>
    =g>
    isa             parsing_goal
    task            get_word_cat
    parsed_word    =val
    ~visual>
""")

parser.productionstring(name="retrieve category", string="""
    =g>
    isa             parsing_goal
    task            get_word_cat
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
    stack_top       =t
    stack_bottom    None
    =retrieval>
    isa             word
    form            =w
    cat             =c
    ==>
    =g>
    isa             parsing_goal
    task            parsing
    stack_top       =c
    stack_bottom    =t
    +imaginal>
    isa             parse_state
    node_cat        =c
    daughter1       =w
    ~retrieval>
""")

parser.productionstring(name="project: NP ==> ProperN", string="""
    =g>
    isa             parsing_goal
    stack_top       ProperN
    stack_bottom    ~NP
    right_frontier  =rf
    parsed_word     =w
    ==>
    =g>
    isa             parsing_goal
    stack_top       NP
    +imaginal>
    isa             parse_state
    node_cat        NP
    daughter1       ProperN
    mother          =rf
    lex_head        =w
""")

parser.productionstring(name="project and complete: NP ==> ProperN", string="""
    =g>
    isa             parsing_goal
    stack_top       ProperN
    stack_bottom    NP
    right_frontier  =rf
    parsed_word     =w
    ==>
    =g>
    isa             parsing_goal
    task            read_word
    stack_top       None
    stack_bottom    None
    +imaginal>
    isa             parse_state
    node_cat        NP
    daughter1       ProperN
    mother          =rf
    lex_head        =w
""")

parser.productionstring(name="project and complete: S ==> NP VP", string="""
    =g>
    isa             parsing_goal
    stack_top       NP
    stack_bottom    S
    ==>
    =g>
    isa             parsing_goal
    task            read_word
    stack_top       VP
    stack_bottom    None
    right_frontier  VP
    +imaginal>
    isa             parse_state
    node_cat        S
    daughter1       NP
    daughter2       VP
""")

parser.productionstring(name="project and complete: VP ==> V NP", string="""
    =g>
    isa             parsing_goal
    task            parsing
    stack_top       V
    stack_bottom    VP
    ==>
    =g>
    isa             parsing_goal
    task            read_word
    stack_top       NP
    stack_bottom    None
    +imaginal>
    isa             parse_state
    node_cat        VP
    daughter1       V
    daughter2       NP
""")

parser.productionstring(name="finished", string="""
    =g>
    isa             parsing_goal
    task            read_word
    stack_top       None
    ==>
    ~g>
    ~imaginal>
""")

if __name__ == "__main__":
    stimuli = [{1: {'text': 'Mary', 'position': (320, 180)}},
               {1: {'text': 'likes', 'position': (320, 180)}},
               {1: {'text': 'Bill', 'position': (320, 180)}}]
    parser_sim = parser.simulation(
        realtime=True,
        gui=False,
        environment_process=environment.environment_process,
        stimuli=stimuli,
        triggers='space')
    parser_sim.run(1.5)

    sortedDM = sorted(([item[0], time] for item in dm.items()\
                                       for time in item[1]),\
                      key=lambda item: item[1])
    print("\nParse states in declarative memory at the end of the simulation",
          "\nordered by time of (re)activation:")
    for chunk in sortedDM:
        if chunk[0].typename == "parse_state":
            print(chunk[1], "\t", chunk[0])
    print("\nWords in declarative memory at the end of the simulation",
          "\nordered by time of (re)activation:")
    for chunk in sortedDM:
        if chunk[0].typename == "word":
            print(chunk[1], "\t", chunk[0])
