import setuptools

PACKAGE_NAME = "contact-notes-local"
package_dir = PACKAGE_NAME.replace("-", "_")


setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0.7',  # update only the minor version each time # https://pypi.org/project/contact-notes-local/
    author="Circles",
    author_email="info@circlez.ai",
    description="PyPI Package for Circles contact-notes-local Python",
    long_description="PyPI Package for Circles contact-notes-local Python",
    long_description_content_type='text/markdown',
    url="https://github.com/circles-zone/contact-note-local-python-package",  # https://pypi.org/project/contact-notes-local/
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'PyMySQL>=1.0.2',
        'pytest>=7.4.0',
        'mysql-connector>=2.2.9',
        'logzio-python-handler>= 4.1.0',
        'database-infrastructure-local>=0.0.20',
        'text-block-local>=0.0.9',
        'contact-group-local>=0.0.7'
    ],
)
