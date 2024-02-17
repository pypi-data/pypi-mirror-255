from setuptools import setup


setup(
    name='salure_helpers_salure_functions',
    version='2.2.2',
    description='Helpful functions from Salure',
    long_description='Helpful functions from Salure',
    author='D&A Salure',
    author_email='support@salureconnnect.com',
    packages=["salure_helpers.salure_functions"],
    license='Salure License',
    install_requires=[
        'pandas>=1,<3',
        'requests>=2,<=3',
        'pyarrow>=10,<11'
    ],
    zip_safe=False,
)