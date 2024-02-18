import unittest, os, prepare
from nest import Nest


class TestMethods(unittest.TestCase):

    def setUp(self):
        template_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
        self.nest = Nest({
            "template_dir": template_dir,
            "token_delims": [ "<!--%","%-->" ]
        })

        self.templates = {
            'table': [ "rows" ],
            'tr': [ 'cols' ],
            'td': [ 'contents' ],
            'tr_default': [ 'col1', 'cols' ],
            'nested_default_outer': [
                  'config.default2',
                  'config.nested.iexist',
                  'contents'
            ],
            'nested_default_contents': [
                  'config.default1',
                  'config.default2',
                  'config.nested.idontexist',
                  'config.nested.iexist',
                  'non_config_var',
                  'ordinary_default'
            ]
        }

    def test_params(self):
        for name in self.templates:
            self.assertEqual( self.nest.params( name ), sorted( self.templates[ name ] ) )
