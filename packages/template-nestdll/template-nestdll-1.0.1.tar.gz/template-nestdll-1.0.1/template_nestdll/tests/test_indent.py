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


    def test_no_fixed_indent(self):

        self.nest.fixed_indent = False

        x_html = '''<table>
    <tr>
    <td>
    1
</td>
</tr><tr>
    <td>
    2
</td>
</tr>
</table>'''

        self.assertEqual( x_html, self.nest.render( self.table ) )



    def test_fixed_indent(self):

        self.nest.fixed_indent = True

        x_html = '''<table>
    <tr>
        <td>
            1
        </td>
    </tr><tr>
        <td>
            2
        </td>
    </tr>
</table>'''

        self.assertEqual( x_html, self.nest.render( self.table ) )
