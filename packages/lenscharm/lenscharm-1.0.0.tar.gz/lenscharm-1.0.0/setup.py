from setuptools import setup

setup(
    name='lenscharm',
    version='1.0.0',
    author='Matteo Guardiani',
    author_email='matteo.guardiani@gmail.com',
    description='A Charming, Bayesian, Strong Lensing Framework',
    packages=['charm_lensing', 'charm_lensing.models'],
    # package_data={
    #     'module_name': ['config/rules.yml'],
    # },
    # include_package_data=True,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'numpy',
        'jax',
        'jaxlib',
        'nifty',
        'matplotlib',
        'scipy',
        'astropy',
    ],
    url='https://gitlab.mpcdf.mpg.de/ift/lenscharm'
)
