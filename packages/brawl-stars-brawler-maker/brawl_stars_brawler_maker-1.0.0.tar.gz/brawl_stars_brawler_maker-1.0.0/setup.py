from setuptools import setup, find_packages

setup(
    name='brawl_stars_brawler_maker',
    version='1.0.0',
    author='AngelFire',
    author_email='tinyangel@mail.com',
    description='A package to mod Brawl Stars game files for custom brawler creation.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AngelFireLA/Brawler-Maker-Python-Library',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'apk_signer',
        'mega.py',
    ],
)
