from setuptools import setup, find_packages

setup(
    name="rdaensemble",
    version="1.3.1",
    description="Redistricting ensembles",
    url="https://github.com/rdatools/rdaensemble",
    author="alecramsay",
    author_email="a73cram5ay@gmail.com",
    license="MIT",
    packages=[
        "rdaensemble",
        "rdaensemble.general",
        "rdaensemble.mcmc",
        "rdaensemble.rmfrsp",
        "rdaensemble.rmfrst",
        "rdaensemble.smc",
        "rdaensemble.ust",
    ],
    install_requires=["rdabase", "rdascore", "rdadccvt", "gerrychain"],
    zip_safe=False,
)
