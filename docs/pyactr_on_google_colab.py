#!/usr/bin/env python
# coding: utf-8

# In[2]:


get_ipython().system('pip3 install pyactr')


# In[ ]:


import pyactr as actr


# In[5]:


actr.chunktype("word", "meaning, category, number, synfunction")
actr.chunktype("goal_lexeme", "task, category, number")

carLexeme = actr.makechunk(
    nameofchunk="car",
    typename="word",
    meaning="[[car]]",
    category="noun",
    number="sg",
    synfunction="subject")

agreement = actr.ACTRModel()

dm = agreement.decmem
dm.add(carLexeme)

agreement.goal.add(actr.chunkstring(string="""
    isa goal_lexeme
    task agree
    category verb"""))

agreement.productionstring(name="retrieve", string="""
    =g>
    isa goal_lexeme
    category verb
    task agree
    ?retrieval>
    buffer empty
    ==>
    =g>
    isa goal_lexeme
    task trigger_agreement
    category verb
    +retrieval>
    isa word
    category noun
    synfunction subject
    """)

agreement.productionstring(name="agree", string="""
    =g>
    isa goal_lexeme
    task trigger_agreement
    category verb
    =retrieval>
    isa word
    category noun
    synfunction subject
    number =x
    ==>
    =g>
    isa goal_lexeme
    category verb
    number =x
    task done
    """)

agreement.productionstring(name="done", string="""
    =g>
    isa goal_lexeme
    task done
    ==>
    ~g>""")


# In[6]:


agreement_sim = agreement.simulation()
agreement_sim.run()
print("\nDeclarative memory at the end of the simulation:")
print(dm)


# In[ ]:




