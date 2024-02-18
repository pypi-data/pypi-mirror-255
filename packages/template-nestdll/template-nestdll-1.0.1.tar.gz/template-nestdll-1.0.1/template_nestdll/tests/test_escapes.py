import unittest, os, prepare
from nest import Nest


class TestMethods(unittest.TestCase):

    def setUp(self):
        template_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
        self.nest = Nest({
            "template_dir": template_dir,
            "token_delims": [ "<%","%>" ],
            "template_label": "NAME"
        })

    def test_BS_BS_good(self):

        x_html = r'<div><%imescaped%></div><div></div><div>\</div>'
        html = self.nest.render({ "NAME": 'escapes'})
        html = ''.join( html.split() )

        self.assertEqual( html, x_html )

    def test_BS_BS_bad(self):

        import re
        ok = False

        try:
            self.nest.render({
                "NAME":  'escapes',
                "imescaped": '1',
                "imnotescaped": '2',
                "neitherami": '3'
            });
        except Exception as e:
            if re.search( 'imescaped.*?does not exist', str(e) ):
                ok = True

        self.assertEqual(ok, True)


    def test_BS_E_with_params(self):

        x_html = "<div>E1</div><div>2</div><div>EE3</div>"
        html = self.nest.render({
            "NAME": 'escapes_e',
            "imescaped": '1',
            "imnotescaped": '2',
            "neitherami": '3'
        });

        html = ''.join( html.split() )
        self.assertEqual( html, x_html )


    def test_E_E_no_params(self):

        x_html = '<div><%imescaped%></div><div></div><div>E</div>'
        html = self.nest.render({ "NAME": 'escapes_e'})


    def test_E_E_good_params(self):

        self.nest.escape_char = 'E'
        x_html = '<div><%imescaped%></div><div>2</div><div>E3</div>'
        html = self.nest.render({
            "NAME": 'escapes_e',
            "imnotescaped": '2',
            "neitherami": '3'
        })
        html = ''.join( html.split() )
        self.assertEqual( html, x_html )

    def test_E_E_bad_params(self):

        import re
        ok = False
        self.nest.escape_char = 'E'

        try:
            self.nest.render({
                "NAME":  'escapes_e',
                "imescaped": '1',
                "imnotescaped": '2',
                "neitherami": '3'
            });
        except Exception as e:
            if re.search( 'imescaped.*?does not exist', str(e) ):
                ok = True

        self.assertEqual(ok, True)

    def test_E_BS_with_params(self):

        x_html = "<div><%imescaped%></div><div>2</div><div>\\3</div>";
        html = self.nest.render({
            "NAME": 'escapes',
            "imnotescaped": '2',
            "neitherami": '3'
        })

        html = ''.join( html.split() )
        self.assertEqual( html, x_html )
