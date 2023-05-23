from setuptools import setup, find_packages

setup(
    name='maxsmart',
    version='0.1.1',
    author='Akim Sissaoui',
    author_email='superkikim@sissaoui.com',
    description='A Python module for operating network connected power strips',
    long_description='''A Python module for operating network connected power strips.
                        It provides functionality to turn on/off sockets, check their state, and retrieve power consumption data.''',
    url='https://github.com/superkikim/maxsmart',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
