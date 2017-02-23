from distutils.core import setup

setup(
    name='magnet-table',
    version='1.0',
    packages=[''],
    url='https://github.com/VELA-CLARA-software/Software/tree/master/magnet-table',
    license='',
    author='Ben Shepherd',
    author_email='ben.shepherd@stfc.ac.uk',
    description='Magnet Table app for VELA/CLARA',
    install_requires=[
        'PyQt4',
        'numpy',
        'scipy',
        'VELA_CLARA_MagnetControl']
)