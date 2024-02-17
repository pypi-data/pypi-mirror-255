# python setup.py clean --all build_ext --build-lib win
# python -m build -wno dist

# .\Python\Scripts\pip.exe download -r .\wheels\requirements.txt -d .\wheels\
# .\Python\python.exe -m pip install --no-index --find-links=.\wheels -r .\wheels\requirements.txt


# packages=find_packages(exclude=['dev*', 'home*']),
# package_data={"": ["*.pyd", "*.so"]},
# include_package_data=True,


# from build.__main__ import main
# import sys

# main(sys.argv[1:], 'python -m build')

import argparse
import os
import subprocess
import sys

from Cython.Build import cythonize
from setuptools import find_packages, setup


def collect(path: str):  # = sys.argv[1]
    modules = []
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename.startswith('__init__'):
                continue
            filepath = os.path.join(dirpath, filename)
            if filepath.endswith('py'):
                # print(filepath)
                modules.append(filepath)

    return modules


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--update',
        type=str,
        nargs='?',
        default='all',
        help='update dependencies',
    )

    # parser.add_argument(
    #     'srcdir',
    #     type=str,
    #     nargs='?',
    #     default='src',
    #     help='source directory (defaults to current directory)',
    # )
    # parser.add_argument(
    #     '--outdir',
    #     '-o',
    #     type=str,
    #     help=f'output directory (defaults to {{srcdir}}{os.sep}dist)',
    #     metavar='PATH',
    # )
    args = parser.parse_args()
    # print(args)

    subprocess.run(f'{sys.executable} -m pip install -U vios quarkstudio'.split(' '))
    subprocess.run(f'quark update'.split(' '))

    # outdir = '.' if not args.outdir else args.outdir

    # setup(name="name",
    #       version='0.0.0',
    #       author="author",
    #       author_email="author_email",
    #       url="https://gitee.com/",
    #       license="MIT",
    #       keywords="keywords",
    #       description="description",
    #       long_description='long_description',
    #       long_description_content_type='text/markdown',
    #       ext_modules=cythonize(module_list=collect(args.srcdir),
    #                             exclude=[],
    #                             build_dir=f"build/src"),
    #       # 'bdist_wheel','--python-tag=cp3','--plat-name=win-amd64'], # sys.argv[1:]
    #       # options={"bdist_wheel": {"py_limited_api": "cp38"}},
    #       script_args=['clean', '--all', 'build_ext',
    #                    '-b', outdir, '-t', 'build/temp'],
    #       )
