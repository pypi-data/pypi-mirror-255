from setuptools import setup, find_packages

with open("README.md", "r") as o:
    long_description = o.read()

DATA01 = "clintonabrahamc@gmail.com"

DATA02 = ['Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules']

setup(
    name='blockporn',
    license='MIT',
    zip_safe=False,
    version='0.1.1',
    classifiers=DATA02,
    author_email=DATA01,
    python_requires='~=3.7',
    packages=find_packages(),
    author='Clinton-Abraham',
    long_description=long_description,
    description='block pornography sites',
    keywords=['python', 'block', 'blocker'],
    long_description_content_type="text/markdown",
    package_data={'Blockporn': ['RECORDED/*.txt']},
    url='https://github.com/Clinton-Abraham/PORN-X-BLOCKER',)
