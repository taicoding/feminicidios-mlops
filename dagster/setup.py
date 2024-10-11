from setuptools import find_packages, setup

setup(
    name="etls",
    packages=find_packages(),
    install_requires=[
        "dagster",
        "dagster-cloud",
        "dagster-shell",
        "pymongo",
        "pandas",
        "joblib",
        "scikit-learn",
        "dagster-postgres",
    ],
    # "dagster-k8s",
    # "dagster-aws",
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
