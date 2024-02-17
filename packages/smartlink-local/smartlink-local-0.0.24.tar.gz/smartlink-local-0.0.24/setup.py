import setuptools

PACKAGE_NAME = "smartlink-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,  # https://pypi.org/project/smartlink-local/
    version='0.0.24',
    author="Circles",
    author_email="info@circlez.ai",
    description="PyPI Package for Circles smart link Python",
    long_description="PyPI Package for Circles smart link Python",
    long_description_content_type='text/markdown',
    # TODO Use PACKAG_NAME
    url="https://github.com/circles-zone/smartlink-local-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'logger-local>=0.0.76',
        'database-mysql-local>=0.0.107',
        'message-local>=0.0.47',
        'queue-worker-local'
    ],
)
