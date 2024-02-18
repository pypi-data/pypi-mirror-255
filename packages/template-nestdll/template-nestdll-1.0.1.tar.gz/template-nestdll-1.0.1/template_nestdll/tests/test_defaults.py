import unittest, os, prepare
from nest import Nest


class TestMethods(unittest.TestCase):

    def setUp(self):
        template_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
        self.nest = Nest({
            "template_dir": template_dir,
            "token_delims": [ "<!--%","%-->" ],
            "template_label": "NAME"
        })

        self.x = {
            "table_default": {
                "NAME": "table",
                "rows": [{
                    "NAME": "tr_default",
                    "cols": {
                        "NAME": "td",
                        "contents": 1
                    }
                }, {
                    "NAME": "tr_default",
                    "cols": {
                        "NAME": "td",
                        "contents": 2
                    }
                }]
            },
            "table_default_ns": {
                "NAME": "table",
                "rows": [{
                    "NAME": "tr_default_ns",
                    "cols": {
                        "NAME": "td",
                        "contents": 1
                    }
                }, {
                    "NAME": "tr_default_ns",
                    "cols": {
                        "NAME": "td",
                        "contents": 2
                    }
                }]
            }
        }

    def test_non_namespaced(self):
        self.nest.defaults = { 'col1': 'default' }

        html = self.nest.render( self.x[ "table_default" ] )
        html = ''.join( html.split() )

        self.assertEqual( html, '<table><tr><td>default</td><td>1</td></tr><tr><td>default</td><td>2</td></tr></table>' )

    def test_namespaced_no_defaults(self):
        self.nest.defaults_namespace_char = '.'

        html = self.nest.render( self.x[ "table_default_ns" ] )
        html = ''.join( html.split() )

        self.assertEqual( html, '<table><tr><td></td><td>1</td></tr><tr><td></td><td>2</td></tr></table>' )


    def test_namespaced_with_defaults(self):
        self.nest.defaults_namespace_char = '.'

        self.nest.defaults = { "default": { "col1": "default" } }

        html = self.nest.render( self.x[ "table_default_ns" ] )
        html = ''.join( html.split() )

        self.assertEqual( html, "<table><tr><td>default</td><td>1</td></tr><tr><td>default</td><td>2</td></tr></table>" )

    def test_complex_defaults(self):
        self.nest.defaults = {
            "ordinary_default": 'ORD',
            "config": {
                "default1": 'CONF1',
                "default2": 'CONF2',
                "default3": 'CONF3',
                "nested": {
                    "iexist": 'NEST1',
                    "metoo": 'NEST2'
                }
            }
        }

        page = {
            "NAME": 'nested_default_outer',
            "contents": {
                "NAME": 'nested_default_contents',
                "non_config_var": 'NONCONF'
            }
        }


        html = self.nest.render( page );
        html = ''.join( html.split() )

        self.assertEqual( html, "<div>CONF2<span><h1>ORD</h1><div>CONF1</div><h4>NONCONF</h4><span>CONF2</span><h2>NEST1</h2><h3></h3></span><div>NEST1</div></div>" )
