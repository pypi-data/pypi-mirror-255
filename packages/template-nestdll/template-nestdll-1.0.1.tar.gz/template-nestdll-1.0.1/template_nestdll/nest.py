import re

import json
import os
import  ctypes
import platform
class Nest:

    def __init__(self, args):

        # defaults
        self.opt = {
            'template_ext': '.html',
            'template_dir': '.',
            'views_module': '',
            'token_delims': [ '<%','%>' ],
            'comment_delims': [ '<!--','-->' ],
            'template_label': 'TEMPLATE',
            'view_label': 'VIEW',
            'show_labels': False,
            'defaults': {},
            'defaults_namespace_char': '.',
            'fixed_indent': False,
            'error_on_bad_params': True,
            'escape_char': '\\'
        }

        if args is not None:
            for key in args:
                setattr(self,key,args[key])
        this_dir = os.path.abspath(os.path.dirname(__file__))
        if platform.system()=='Windows':
            self.lib = ctypes.cdll.LoadLibrary(os.path.join(this_dir, 'templatenest.dll'))
        if platform.system() == 'Linux':
            self.lib = ctypes.cdll.LoadLibrary(os.path.join(this_dir, 'templatenest.so'))

        self.class_pointer = ctypes.c_void_p()
        self.lib.templatenest_init(ctypes.byref(self.class_pointer))


    @property
    def template_dir(self):
        return self.opt['template_dir']

    @template_dir.setter
    def template_dir(self,template_dir):
        self.opt['template_dir'] = template_dir

    @property
    def views_module(self):
        return self.opt['views_module']

    @views_module.setter
    def views_module(self,views_module):
        self.opt['views_module'] = views_module

    @property
    def template_ext(self):
        return self.opt['template_ext']

    @template_ext.setter
    def template_ext(self,template_ext):
        self.opt['template_ext'] = template_ext

    @property
    def token_delims(self):
        return self.opt['token_delims']

    @token_delims.setter
    def token_delims(self,token_delims):
        if not isinstance( token_delims, list ):
            raise ValueError("'token_delims' should be a list. Instead got a %s with value %s" \
                % ( type( token_delims ), token_delims ) )
        if len( token_delims ) != 2:
            raise ValueError("'token_delims' should be a 2 element list. Instead got a list with %s elements" \
                % len( token_delims ) )
        if not isinstance( token_delims[0], str ):
            raise ValueError("First 'token_delim' should be of type 'str' instead got '%s' with value %s " \
                % ( type( token_delims[0] ), token_delims[0] ) )
        if not isinstance( token_delims[1], str ):
            raise ValueError("Second 'token_delim' should be of type 'str' instead got '%s' with value %s " \
                % ( type( token_delims[1] ), token_delims[1] ) )
        if len( token_delims[0] ) < 1:
            raise ValueError("First token_delim cannot be an empty string")
        if len( token_delims[1] ) < 1:
            raise ValueError("Second token_delim cannot be an empty string")


        self.opt['token_delims'] = token_delims


    @property
    def comment_delims(self):
        return self.opt['comment_delims']

    @comment_delims.setter
    def comment_delims(self,comment_delims):
        if not isinstance( comment_delims, list ):
            raise ValueError("'comment_delims' should be a list. Instead got a %s with value %s" \
                % ( type( comment_delims ), comment_delims ) )
        if len( comment_delims ) != 2:
            raise ValueError("'token_delims' should be a 2 element list. Instead got a list with %s elements" \
                % len( comment_delims ) )
        if not isinstance( comment_delims[0], str ):
            raise ValueError("First 'comment_delim' should be of type 'str' instead got '%s' with value %s " \
                % ( type( comment_delims[0] ), comment_delims[0] ) )
        if not isinstance( comment_delims[1], str ):
            raise ValueError("Second 'comment_delim' should be of type 'str' instead got '%s' with value %s " \
                % ( type( comment_delims[1] ), comment_delims[1] ) )
        if len( comment_delims[0] ) < 1:
            raise ValueError("First comment_delim cannot be an empty string")
        self.opt['comment_delims'] = comment_delims


    @property
    def template_label(self):
        return self.opt['template_label']

    @template_label.setter
    def template_label(self,template_label):
        self.opt['template_label'] = template_label

    @property
    def show_labels(self):
        return self.opt['show_labels']

    @show_labels.setter
    def show_labels(self,show_labels):
        if ( not isinstance( show_labels, bool ) ):
            raise ValueError("'show_labels' expects a boolean, instead got a %s with value %s" \
                % ( type(show_labels), show_labels ))
        self.opt['show_labels'] = show_labels

    @property
    def defaults(self):
        return self.opt['defaults']

    @defaults.setter
    def defaults(self,defaults):
        self.opt['defaults'] = defaults

    @property
    def defaults_namespace_char(self):
        return self.opt['defaults_namespace_char']

    @defaults_namespace_char.setter
    def defaults_namespace_char(self,defaults_namespace_char):
        if not isinstance( defaults_namespace_char, str ):
            raise ValueError("'defaults_namespace_char' expects a single char, instead got a %s with value %s" \
                % ( type( defaults_namespace_char ), defaults_namespace_char ) )
        if len(defaults_namespace_char) != 1:
            raise ValueError("'defaults_namespace_char' expects a single char, instead got string '%s' of length %s" \
                % ( defaults_namespace_char, len(defaults_namespace_char) ) )
        self.opt['defaults_namespace_char'] = defaults_namespace_char

    @property
    def fixed_indent(self):
        return self.opt['fixed_indent']

    @fixed_indent.setter
    def fixed_indent(self,fixed_indent):
        if ( not isinstance( fixed_indent, bool ) ):
            raise ValueError("'fixed_indent' expects a boolean, instead got a %s with value %s" \
                % ( type(fixed_indent), fixed_indent ))
        self.opt['fixed_indent'] = fixed_indent

    @property
    def error_on_bad_params(self):
        return self.opt['error_on_bad_params']

    @error_on_bad_params.setter
    def error_on_bad_params(self,error_on_bad_params):
        if ( not isinstance( error_on_bad_params, bool ) ):
            raise ValueError("'show_labels' expects a boolean, instead got a %s with value %s" \
                % ( type(error_on_bad_params), error_on_bad_params ))
        self.opt['error_on_bad_params'] = error_on_bad_params

    @property
    def escape_char(self):
        return self.opt['escape_char']

    @escape_char.setter
    def escape_char(self,escape_char):
        if not isinstance( escape_char, str ):
            raise ValueError("'escape_char' expects a single char, instead got a %s with value %s" \
                % ( type( escape_char ), escape_char ) )
        if len(escape_char) > 1:
            raise ValueError("'escape_char' expects a single char, instead got string '%s' of length %s" \
                % ( escape_char, len(escape_char) ) )
        self.opt['escape_char'] = escape_char

#void templatenest_set_parameters(void* object, char * template_dir,char * template_ext,char * defaults_namespace_char,
        #   char** comment_delims,
		#   char** token_delims,int64_t show_labels, char * name_label,
    #   int64_t fixed_indent, int64_t die_on_bad_params, char * escape_char)
#
    def render(self,comp):

        comment_delims = [bytes(self.opt['comment_delims'][0], 'utf-8'),bytes(self.opt['comment_delims'][1], 'utf-8')]
        arr = (ctypes.c_char_p * len(comment_delims))()
        arr[:] = comment_delims

        token_delims = [bytes(self.opt['token_delims'][0], 'utf-8'), bytes(self.opt['token_delims'][1], 'utf-8')]
        arr2 = (ctypes.c_char_p * len(token_delims))()
        arr2[:] = token_delims
        self.lib.templatenest_set_jsonparameters(self.class_pointer, json.dumps(self.opt['defaults']).encode('utf8'),
                                            ctypes.c_char_p(  self.opt['template_dir'].encode('utf-8')),
                                            ctypes.c_char_p( self.opt['template_ext'].encode('utf-8')),
                                            ctypes.c_char_p(self.opt['defaults_namespace_char'].encode('utf-8')),
                                             arr,
                                             arr2,
                                             ctypes.c_int64(self.opt['show_labels']),
                                             ctypes.c_char_p(self.opt['template_label'].encode('utf-8')),
                                             ctypes.c_int64(self.opt['fixed_indent']),
                                             ctypes.c_int64(self.opt['error_on_bad_params']),
                                             ctypes.c_char_p(self.opt['escape_char'].encode('utf-8')))

        args = json.dumps(comp).encode('utf8')
        html =  ctypes.c_char_p()
        err =ctypes.c_char_p()
        #print(args)
        self.lib.templatenest_jsonrender(self.class_pointer,ctypes.c_char_p(args),ctypes.byref(html),ctypes.byref(err))
        result = html.value.decode('utf-8')
        if result=="":
            err2 = ctypes.c_char_p()
            self.lib.get_error(self.class_pointer, ctypes.byref(err2))
            err2value = err2.value.decode("utf-8")
            if err2value!="":
                raise Exception("there is an error during execution:"+err2value)
        return result

    def __del__(self):
        self.lib.templatenest_destroy(self.class_pointer)


    def _get_template(self,name):

        import os
        path = os.path.join(self.opt['template_dir'],name + self.opt['template_ext'])
        f = open(path,"r")
        text = f.read().rstrip()
        f.close()
        #raise Exception("text: "+text)
        return text

    def _params_in( self, text ):

        esc = self.opt['escape_char']
        tda = self.token_delims[0]
        tdb = self.token_delims[1]

        if esc:
            rem = re.findall( '(?<!' + re.escape( esc ) + ')' + tda + \
                r'\s+(.*?)\s+' +tdb, text)
        else:
            rem = re.findall( tda + r'\s+(.*?)\s+' + tdb, text )

        remd = {}
        for name in rem:
            remd[name] = 1

        return remd.keys()


    def params(self,template_name):

        esc = self.opt['escape_char']
        template = self._get_template( template_name )
        frags = re.split( re.escape( esc + esc ), template )

        rem = {}
        for frag in frags:
            params = self._params_in( frag )
            for param in params:
                rem[ param ] = 1

        return sorted( rem.keys() )






    def _get_default_val(self,ref,parts):
        if len(parts) == 1:
            if parts[0] in ref:
                return ref[ parts[0] ]
            else:
                return ''
        else:
            ref_name = parts.pop(0)
            if ref_name not in ref:
                return ''

            return self._get_default_val( ref[ ref_name ], parts )
