from setuptools import setup, find_packages

setup(
    name="rigid_body_segmentation",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "MDAnalysis>=2.7.0",
        "numpy>=1.26.3",
        "scikit-learn>=1.4.0",
        "rich>=13.7.0"
    ]
)
