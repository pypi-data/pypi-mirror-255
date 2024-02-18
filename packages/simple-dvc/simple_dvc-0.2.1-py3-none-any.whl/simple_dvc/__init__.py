"""
Simple DVC
==========

+-----------------+-------------------------------------------------------+
| Read the Docs   | http://simple-dvc.readthedocs.io/en/latest/           |
+-----------------+-------------------------------------------------------+
| Gitlab (main)   | https://gitlab.kitware.com/computer-vision/simple_dvc |
+-----------------+-------------------------------------------------------+
| Pypi            | https://pypi.org/project/simple_dvc                   |
+-----------------+-------------------------------------------------------+

"""
__version__ = '0.2.1'
__author__ = 'Jon Crall'
__author_email__ = 'jon.crall@kitware.com'
__url__ = 'https://gitlab.kitware.com/computer-vision/simple_dvc'

__mkinit__ = """
mkinit /home/joncrall/code/simple_dvc/simple_dvc/__init__.py --lazy
"""


__submodules__ = {
    'api': ['SimpleDVC'],
    'registery': None,
}

from .api import SimpleDVC

__all__ = ['SimpleDVC']
