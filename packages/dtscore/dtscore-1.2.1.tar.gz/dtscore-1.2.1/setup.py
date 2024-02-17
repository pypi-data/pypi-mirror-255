from setuptools import setup

#
# to install:
#   update the version number below
#   at cmd prompt :
#       python setup.py sdist
#       python setup.py bdist_wheel  <- this is deprecated, check alternatives
#       twine upload dist/*
#
#
setup(
    name='dtscore',
    version='1.2.1',    
    description='DTS core',
    long_description='The constants library for DTS Python routines.',
    long_description_content_type='text/x-rst',
    url='',
    author='D Smith',
    author_email='',
    license='BSD 2-clause',
    packages=['dtscore'],
    install_requires=[],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows :: Windows 11',
        'Programming Language :: Python :: 3.10',
    ],
)