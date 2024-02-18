from setuptools import setup, find_packages

setup(
    name='datalibro_utils',
    version='2.2.6',
    packages=find_packages(),
    install_requires=[
        'tablemaster',
        'pandas',
        'streamlit',
        'plotly',
    ],
    author='DesignLibro',
    author_email='livid.su@gmail.com',
    description='For Datalibro.',
    url='https://github.com/DesignLibro/datalibro_utils'
)
