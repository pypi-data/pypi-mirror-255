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

    def test_unspecified(self):

        table = {
            "NAME": 'table',
            "rows": [{
                "NAME": 'tr',
                "cols": {
                    "NAME": 'td'
                }
            },{
                "NAME": 'tr',
                "cols": {
                    "NAME": 'td'
                }
            }]
        }

        html = self.nest.render( table )

        html = ''.join( html.split() )

        self.assertEqual( html, '<table><tr><td></td></tr><tr><td></td></tr></table>' )


    def test_specified(self):

        table = {
            "NAME": 'table',
            "rows": [{
                "NAME": 'tr',
                "cols": {
                    "NAME": 'td',
                    "contents": '1'
                }
            },{
                "NAME": 'tr',
                "cols": {
                    "NAME": 'td',
                    "contents": '2'
                }
            }]
        }

        html = self.nest.render( table )

        html = ''.join( html.split() )

        self.assertEqual( html, '<table><tr><td>1</td></tr><tr><td>2</td></tr></table>' )


    def test_comment_labels( self ):

        table = {
            "NAME": 'table',
            "rows": [{
                "NAME": 'tr',
                "cols": {
                    "NAME": 'td',
                    "contents": '1'
                }
            },{
                "NAME": 'tr',
                "cols": {
                    "NAME": 'td',
                    "contents": '2'
                }
            }]
        }

        self.nest.comment_delims = ['<!--','-->']
        self.nest.show_labels = True
        html = self.nest.render( table )

        html = ''.join( html.split() )

        x_html = "<!--BEGINtable--><table><!--BEGINtr--><tr><!--BEGINtd--><td>1</td><!--ENDtd--></tr><!--ENDtr--><!--BEGINtr--><tr><!--BEGINtd--><td>2</td><!--ENDtd--></tr><!--ENDtr--></table><!--ENDtable-->"

        self.assertEqual( html, x_html )
