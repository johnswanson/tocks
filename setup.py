from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='tocks',
    version='0.0.0',
    description='Tock thing',
    long_description=readme,
    author='John Swanson',
    author_email='tocks@agh.io',
    url='https://github.com/johnswanson/tocks',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    entry_points={
        'console_scripts': [
            'tock=tocks.main:main'
        ]
    }
)
