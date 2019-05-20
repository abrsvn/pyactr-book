"""
Counter automaton for the a^n b^n language.
"""

import pyactr as actr

counter = actr.ACTRModel()

actr.chunktype("countOrder", "first, second")
actr.chunktype("countFrom", ("start", "end", "count", "terminal"))

dm = counter.decmem
dm.add(actr.chunkstring(string="""
    isa         countOrder
    first       1
    second      2
"""))
dm.add(actr.chunkstring(string="""
    isa         countOrder
    first       2
    second      3
"""))
dm.add(actr.chunkstring(string="""
    isa         countOrder
    first       3
    second      4
"""))
dm.add(actr.chunkstring(string="""
    isa         countOrder
    first       4
    second      5
"""))

counter.goal.add(actr.chunkstring(string="""
    isa         countFrom
    start       1
    end         3
    terminal    'a'
"""))

counter.productionstring(name="start", string="""
    =g>
    isa         countFrom
    start       =x
    count       None
    ==>
    =g>
    isa         countFrom
    count       =x
    +retrieval>
    isa         countOrder
    first       =x
""")

counter.productionstring(name="increment", string="""
    =g>
    isa         countFrom
    count       =x
    end         ~=x
    =retrieval>
    isa         countOrder
    first       =x
    second      =y
    ==>
    !g>
    show        terminal
    =g>
    isa         countFrom
    count       =y
    +retrieval>
    isa         countOrder
    first       =y
""")

counter.productionstring(name="restart counting", string="""
    =g>
    isa         countFrom
    count       =x
    end         =x
    terminal    'a'
    ==>
    +g>
    isa         countFrom
    start       1
    end         =x
    terminal    'b'
""")

if __name__ == "__main__":
    counter_sim = counter.simulation(trace=False)
    counter_sim.run()
