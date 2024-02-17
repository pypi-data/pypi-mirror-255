from setuptools import setup

setup(
    name='webloc2html',
    version='0.1.0',
    py_modules=['webloc2html'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'webloc2html = webloc2html:convert_all',
        ],
    },
)
