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

        self.table = {
            "NAME": 'table',
            "rows": [{
                "NAME": 'tr',
                "cols": {
                    "NAME": 'tr',
                    "bad_param": 'stuff'
                }
            },{
                "NAME": 'tr',
                "cols": {
                    "NAME": 'td',
                    #no contents
                }
            }]
        };

    def test_error_on_bad_params(self):

        import re
        ok = False

        try:
            self.nest.render( self.table )
            print("rendered!")

        except Exception as e:
            if re.search( 'bad_param.*?does not exist', str(e) ):
                ok = True

        self.assertEqual(ok, True)


    def test_dont_error_on_bad_params(self):

        self.nest.error_on_bad_params = False
        x_html = "<table><tr><tr></tr></tr><tr><td></td></tr></table>"
        html = self.nest.render( self.table )
        html = ''.join( html.split() )
        self.assertEqual( html, x_html )
