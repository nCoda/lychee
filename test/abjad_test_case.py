from abjad.tools.abctools.AbjadObject import AbjadObject
import unittest

#are the objects of the same class?
#if so, are their formatted strings equal?

SAME_CLASS_ERROR = "The two arguments aren't instances of the same class."
STRING_FORMAT_ERROR = "The objects are instances of the same class but their strings aren't equal."

class AbjadTestCase(unittest.TestCase):
    
    def assertEqual(self,first,second,msg=None):
        if isinstance(first,AbjadObject):
            if type(first) != type(second):
                raise AssertionError(SAME_CLASS_ERROR)
            elif format(first) != format(second):
                raise AssertionError(STRING_FORMAT_ERROR)
        else:
            super(AbjadTestCase,self).assertEqual(first,second,msg)
