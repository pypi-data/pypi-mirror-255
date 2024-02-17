import setuptools

PACKAGE_NAME = "google-contact-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name='google-contact-local',
    version='0.0.9',  # https://pypi.org/project/google-contact-local
    author="Circles",
    author_email="valeria.e@circ.zone",
    description="PyPI Package for Circles google-contact-local Python",
    long_description="PyPI Package for Circles google-contact-local Python",
    long_description_content_type="text/markdown",
    url="https://github.com/circles-zone/google-contact-local-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'user-context-remote>=0.0.17',
        'python-sdk-remote>=0.0.27',
        'importer-local>=0.0.36',
        'entity-type-local>=0.0.13',
        'url-remote>=0.0.65',
        'internet-domain-local>=0.0.1',
        'api-management-local>=0.0.54',
        'database-infrastructure-local>=0.0.22',
        'user-external-local>=0.0.36',
        'contact-local>=0.0.19',
        'contact-email-address-local>=0.0.3',
        'contact-persons-local>=0.0.3',
        'contact-group-local>=0.0.7',
        'contact-notes-local>=0.0.1',
        'contact-phones-local>=0.0.2',
        'contact-profiles-local>=0.0.2',
        'contact-user-externals-local>=0.0.1',
        'contact-locations-local>=0.0.1',
        'user-external-local>=0.0.36',
        'phone-local>=0.0.15',
        'email-address-local>=0.0.29',
        'location-local>=0.0.6',
        'entity-type-local>=0.0.13',
        'group-remote>=0.0.97'
    ]
 )
