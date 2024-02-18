import os

from setuptools import find_packages, setup

basedir = os.path.abspath(os.path.dirname(__file__))
requirements_path = os.path.join(basedir, "requirements.txt")


def get_requirements():
    """Get package requirements from a requirements file (ex: requirements.txt)."""
    with open(requirements_path, "r") as f:
        return f.read().splitlines()


def get_extras_require():
    extras_require = {
        "aws": [
            "awscli==1.32.36",
            "botocore==1.34.36",
            "rsa==4.7.2",
            "s3transfer==0.10.0",
        ],
        "dev": [
            "black==22.12.0",
            "isort>=5.10.1",
            "flake8>=4.0.1",
            "pytest>=7.4.4",
            "pre-commit==3.6.0",
        ],
    }

    extras_require.update({"all": [i[0] for i in extras_require.values()]})
    return extras_require


setup(
    name="yvestest",
    version="0.1.3",
    packages=find_packages(),
    author="Dataverse Team",
    author_email="77601251@daum.net",
    description="An open-source simplifies ETL workflow with Python based on Spark",
    license="MIT",
    include_package_data=True,
    install_requires=get_requirements(),
    extras_require=get_extras_require(),
    entry_points={"console_scripts": ["dataverse = dataverse.api.cli:main"]},
    python_requires=">=3.10, <=3.11",
)
