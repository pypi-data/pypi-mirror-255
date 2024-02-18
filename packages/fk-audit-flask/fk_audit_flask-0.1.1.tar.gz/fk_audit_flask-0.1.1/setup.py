from setuptools import setup, find_packages


VERSION = '0.1.1'
PACKAGE_NAME = 'fk_audit_flask'
AUTHOR = 'José Luis Rosales Meza'
AUTHOR_EMAIL = 'jrosalesmeza@gmail.com'
URL = 'https://gitlab.com/f3315/team-back-end/cross/packages/package_audit_flask'

LICENSE = 'MIT'
DESCRIPTION = 'Library for auditing models made with SQLAlchemy and Mongoengine'
LONG_DESCRIPTION = DESCRIPTION
LONG_DESC_TYPE = 'text/markdown'

INSTALL_REQUIRES = [
    'flask',
    'mongoengine',
    'blinker',
    'sqlalchemy'
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    license=LICENSE,
    packages=find_packages(),
    include_package_data=True
)
