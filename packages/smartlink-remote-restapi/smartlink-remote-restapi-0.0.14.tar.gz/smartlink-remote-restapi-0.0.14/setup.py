import setuptools

PACKAGE_NAME = "smartlink-remote-restapi"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0.14',  # https://pypi.org/project/smartlink-remote-restapi/
    author="Circles",
    author_email="info@circlez.ai",
    description="PyPI Package for Circles smartlink-remote-restapi Python",
    long_description="PyPI Package for Circles smartlink-remote-restapi Python",
    long_description_content_type='text/markdown',
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    # packages=setuptools.find_packages(),
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests',
        'user-context-remote',
        'python-sdk-local',
        'python-dotenv',
        'logger-local',
        'url-remote',
        'smartlink-local'
    ],
)
