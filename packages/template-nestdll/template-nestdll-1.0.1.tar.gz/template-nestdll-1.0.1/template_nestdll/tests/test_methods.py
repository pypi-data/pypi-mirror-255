import unittest, prepare
from nest import Nest

class TestMethods(unittest.TestCase):

    def setUp(self):
        self.nest = Nest({})
        self.methods = {
            'string' : [
                'template_ext',
                'template_dir',
                'template_label'
            ],
            'bool': [
                'show_labels',
                'fixed_indent',
                'error_on_bad_params'
            ],
            'char': [
                'escape_char',
                'defaults_namespace_char',
            ],
            'delims': [
                'token_delims',
                'comment_delims'
            ],
            'dict': [
                'defaults'
            ]
        }

    def test_string_methods(self):

        for method in self.methods['string']:
            default = getattr( self.nest, method )
            self.assertIsInstance( default, str, 'method "'+method+'" returns a default value, which is string' )
            text = 'hello'
            setattr( self.nest, method, text )
            result = getattr( self.nest, method )
            self.assertEqual( result, text, 'Get/set as expected for method '+method )

    def test_bool_methods(self):

        for method in self.methods['bool']:
            default = getattr( self.nest, method )
            self.assertIsInstance( default, bool, 'method "'+method+'" returns a default value, which is a bool' )
            vals = [False, True]
            for val in vals:
                setattr( self.nest, method, val )
                result = getattr( self.nest, method )
                self.assertEqual( result, val, 'method "'+method+'": get/set for boolean input' )

                value_error = False
                try:
                    setattr( self.nest, method, 2 );
                except ValueError:
                    value_error = True

                self.assertTrue(value_error, 'method "'+method+'": Attempt to set non-boolean value returns a ValueError')

    def test_char_methods(self):

        for method in self.methods['char']:
            default = getattr( self.nest, method )
            self.assertIsInstance( default, str, 'method "'+method+'": default value is a string' )
            self.assertEqual( len( default ), 1, 'method "'+method+'": default value is a single char' )

            for val in ['A','$','4']:
                setattr( self.nest, method, val )
                self.assertEqual( getattr( self.nest, method ), val, 'method "'+method+'": get/set for single char input' )

            for val in [1, 'tree', True]:
                value_error = False
                try:
                    setattr( self.nest, method, val )
                except ValueError:
                    value_error = True
                self.assertTrue(value_error, 'method %s: Attempt to set to type %s returns a ValueError' % ( method, type(val) ) )

    def test_delims_methods(self):

        for method in self.methods['delims']:
            default = getattr( self.nest, method )
            self.assertIsInstance( default, list, 'method %s: default value is a list' % method )
            self.assertEqual( len( default ), 2, 'method %s: default has 2 elements' % method )
            self.assertIsInstance( default[0], str, 'method %s: first delim is a string' % method )
            self.assertIsInstance( default[1], str, 'method %s: second delim is a string' % method )
            self.assertTrue( len(default[0]) > 0 , 'method %s: first delim has non-zero length' % method )

            for val in [ [ '<%', '%>' ], [ 'AAA','BBB' ], ['#','#'] ]:
                setattr( self.nest, method, val )
                res = getattr( self.nest, method )
                self.assertIsInstance( res, list, 'method %s: set/get returns a list' % method )
                self.assertEqual( len( res ), 2, 'method %s: set/get list has 2 elements' % method )

                for i in [0,1]:
                    self.assertEqual( res[ i ], val[ i ], 'method %s: set/get correct delim %s %s ' % ( method, i, val[i] ) )

            for val in [ True, 34, [ 'A', 1 ], [ 'XX', 'YY', 'ZZ' ], [ 'One' ] ]:
                value_error = False
                try:
                    setattr( self.nest, method, val )
                except ValueError:
                    value_error = True

                self.assertTrue( value_error, 'method %s: attempt to set to invalid value raises ValueError' % method )

    def test_dict_methods(self):
        for method in self.methods['dict']:
            default = getattr( self.nest, method )
            self.assertIsInstance( default, dict, 'method %s: default is a dict' % method )
            for val in [ {}, { 'config': 'some text' } ]:
                setattr( self.nest, method, val )
                res = getattr( self.nest, method )
                self.assertDictEqual( res, val, 'method %s: set/get returns the correct dict' % method )




#    def test
#        ext = '.txt'
#        self.nest.template_ext = ext
#        self.assertEqual( self.nest.template_ext, ext )
