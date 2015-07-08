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
    
    def assertAttribsEqual(self, with_id_dict, without_id_dict):
        with_id_dict = dict(with_id_dict)
        without_id_dict = dict(without_id_dict)
        if isinstance(with_id_dict, dict):
            if type(with_id_dict) != type(without_id_dict):
                raise AssertionError(SAME_CLASS_ERROR)
            elif not with_id_dict['{http://www.w3.org/XML/1998/namespace}id']:
                raise AssertionError("First Element lacks an xml id.")
        with_id_copy = with_id_dict.copy()
        del(with_id_copy['{http://www.w3.org/XML/1998/namespace}id'])
        self.assertEqual(with_id_copy, without_id_dict)
            
            
