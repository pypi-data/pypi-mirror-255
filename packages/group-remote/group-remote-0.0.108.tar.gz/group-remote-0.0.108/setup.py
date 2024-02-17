import setuptools

PACKAGE_NAME = "group-remote"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0.108',  # https://pypi.org/project/group-remote/
    author="Circles",
    author_email="info@circlez.ai",
    description="PyPI Package for Circles Group-Remote Python",
    long_description="PyPI Package for Circles Group-Remote Python",
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
        'logger-local',
        'url-remote',
        'user-context-remote',
        'python-sdk-remote'
    ],
)
