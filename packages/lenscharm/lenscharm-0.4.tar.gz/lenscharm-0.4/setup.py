from setuptools import setup, find_packages

setup(
    name='lenscharm',
    version='0.4',
    author='Matteo Guardiani',
    author_email='matteo.guardiani@gmail.com',
    description='A Charming, Bayesian, Strong Lensing Framework',
    packages=find_packages(include=["charm_lensing", "charm_lensing.*"]),
    # package_data={
    #     'module_name': ['config/rules.yml'],
    # },
    # include_package_data=True,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3.10',
    install_requires=[
        'numpy',
        'typing-extensions',
        'jax',
        'jaxlib',
        # 'nifty8',
        'matplotlib',
        'scipy',
        'astropy',
    ],
    url='https://gitlab.mpcdf.mpg.de/ift/lenscharm'
)
