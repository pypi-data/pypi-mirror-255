from setuptools import Extension, setup 
from setuptools.command.build_ext import build_ext
from os import system

def Make():
    system('make -C bulgogi lib/libyaml.a')

class MakeBuildExt(build_ext):
    def run(self) -> None:
        Make()
        super().run()

setup(
    cmdclass={
        'build_ext': MakeBuildExt,
    },
    ext_modules=[
        Extension(
            name="bulgogi",
            sources=[
                "bulmodule.c", 
                "bulgogi/src/dot_bul.c", 
                "bulgogi/src/engine.c",
                "bulgogi/src/fs.c",
                "bulgogi/src/yaml_ext.c",
            ],
            include_dirs=["bulgogi/inc"],
            library_dirs=["bulgogi/lib"],
            libraries=["yaml"],
        ),
    ]
)
