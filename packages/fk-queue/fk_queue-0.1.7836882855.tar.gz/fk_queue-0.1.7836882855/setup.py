from setuptools import setup, find_packages


VERSION = '0.1.7836882855'
PACKAGE_NAME = 'fk_queue'
AUTHOR = 'Steven Santacruz Garcia'
AUTHOR_EMAIL = 'stevengarcia1118@gmail.com'
URL = 'https://gitlab.com/f3315/team-back-end/cross/packages/package_queue'

LICENSE = 'MIT'
DESCRIPTION = """Libreria simplifica y centraliza el uso de Amazon Simple
                Queue Service (SQS) para gestionar registros, auditorías, bitácoras y
                comunicaciones en tus aplicaciones"""
LONG_DESCRIPTION = DESCRIPTION
LONG_DESC_TYPE = 'text/markdown'

INSTALL_REQUIRES = [
    'boto3'
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
