from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='maxsmart',
    version='2.0.0',
    author='Akim Sissaoui',
    author_email='superkikim@sissaoui.com',
    description='A Python module for operating network connected power strips',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/superkikim/maxsmart',
    packages=find_packages(),  # Automatically find packages
    install_requires=[
        'aiohttp',  # Replaced requests with aiohttp for async support
        # Note: asyncio is built-in to Python 3.7+ so no need to specify it
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',  # Changed to Production/Stable
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',  # Updated minimum version for async support
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.7',  # Async/await requires Python 3.7+
    license='MIT',  # Specify the license type
)