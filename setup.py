from setuptools import setup

setup(
    name='SIMLR Portal',
    packages=['simlrportal'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_sqlalchemy'
    ],
)
