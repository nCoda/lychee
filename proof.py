from abjad import *

# This works:
s = Voice("a''4 r4 <a'' b''> b'' a''4. r4.")
a = Voice("d' d' d' d' d' cs' d' d'")
top = Staff([s, a])
top.is_simultaneous = True
t = Voice("fs''  fs''8 g'' a''4  g''8 fs''  e'' d'' e''4  d'' d''")
b = Voice("d'4 b' fs' g' a' a' d' d'")
bottom = Staff([t,b])
bottom.is_simultaneous = True
group = StaffGroup([top,bottom])
tuba = Staff("c''''1 r c''''")
score = Score([group,tuba])
#conversion goes here.