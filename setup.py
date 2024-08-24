from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='maxsmart',
    version='2.0.0-beta1',
    author='Akim Sissaoui',
    author_email='superkikim@sissaoui.com',
    description='A Python module for operating network connected power strips',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/superkikim/maxsmart',
    packages=find_packages(),  # Automatically find packages
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',  # Change to 5 - Production/Stable when you are ready
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.6',  # Optional: Specify compatible Python versions
)
