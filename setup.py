from setuptools import setup, Extension
import os
import glob
import shutil

levenshtein_c = Extension(
    'spell_check.levenshtein', sources=['spell_check/levenshtein.c'])

setup(
    name='spell_check',
    version='0.1.0',
    description='Spell check',
    author='Zachary Huff',
    author_email='zach.huff.386@gmail.com',
    packages=['spell_check'],
    ext_modules=[levenshtein_c],
)

spell_check_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
    'spell_check')
levenshtein_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
    'build', 'lib.*', 'spell_check', 'levenshtein.so')
levenshtein_path = glob.glob(levenshtein_path)

# Copy compiled c extension
if levenshtein_path:
    shutil.copy(levenshtein_path[0], spell_check_path)
