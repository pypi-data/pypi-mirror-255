import pathlib
from setuptools import setup, Extension
import setuptools
from setuptools.command.build_ext import build_ext
import sys
import os

import platform

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

ext_modules = [
    Extension(
        'templatenest',
        ['TemplateNestCpp/TemplateNestDll/connector.cpp',
         'TemplateNestCpp/ConsoleApplication1/TemplateNestClass.cpp'],
        include_dirs=[
            'TemplateNestCpp/ConsoleApplication1/'
        ],
        language='c++'
    ),
]

def has_flag(compiler, flagname):
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        try:
            compiler.compile([f.name], extra_postargs=[flagname])
        except setuptools.distutils.errors.CompileError:
            return False
    return True

def cpp_flag(compiler):
    if has_flag(compiler, '-std=c++17'):
        return '-std=c++17'
    else:
        raise RuntimeError('Unsupported compiler -- at least C++17 support is needed!')


class CTypes:
    pass


class BuildExt(build_ext,CTypes):
    """A custom build extension for adding compiler-specific options."""
    c_opts = {
        'msvc': ['/EHsc'],
        'unix': [],
    }

    if sys.platform == 'darwin':
        c_opts['unix'] += ['-stdlib=libc++', '-mmacosx-version-min=10.7']

   # def build_extension(self, ext):
   #     self._ctypes = isinstance(ext, CTypes)
   #     return super().build_extension(ext)

    def get_export_symbols(self, ext):
        if 1:
            return ext.export_symbols
        return super().get_export_symbols(ext)

    def get_ext_filename(self, ext_name):

        if platform.system()=='Windows':
            so_ext = '.dll'
        else:
            so_ext = '.so'


        return os.path.join("template_nestdll",ext_name + so_ext)



    def build_extensions(self):

        ct = self.compiler.compiler_type

        opts = self.c_opts.get(ct, [])

        # extra compiler options
        if ct == 'msvc':
            opts += [ "/std:c++17",'/O2' , '/D "TEMPLATENESTDLL_EXPORTS"']
        else:
            opts += [
                '-O3',
                '-fPIC',
                '-march=native',
                '-lstdc++fs'
            ]





        if ct == 'unix':
            opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
            opts.append(cpp_flag(self.compiler))
           # if has_flag(self.compiler, '-fvisibility=hidden'):
           #     opts.append('-fvisibility=hidden')
        elif ct == 'msvc':
            opts.append('/DVERSION_INFO=\\"%s\\"' % self.distribution.get_version())
        for ext in self.extensions:
            ext.extra_compile_args = opts
            ext.extra_link_args.append('-lstdc++fs')

        build_ext.build_extensions(self)


setup(
    name="template-nestdll",
    version="1.0.1",
    description="Represent a nested structure of templates in a dict",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Tom Gracey",
    author_email="tomgracey@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=["template_nestdll"],
    include_package_data=True,
    tests_require=['pytest'],
    install_requires=[],
    ext_modules=ext_modules,
    cmdclass={'build_ext': BuildExt}

)

