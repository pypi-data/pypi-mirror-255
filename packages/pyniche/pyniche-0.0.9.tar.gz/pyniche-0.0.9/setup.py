from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyniche",
    version="0.0.9",
    url="https://github.com/Niche-Squad/pyniche",
    author="James Chen",
    author_email="niche@vt.edu",
    description="An AI Library for Niche Squad",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        # data manipulation
        "pandas",
        "numpy",
        "scipy",
        "scikit-learn",
        "datasets",
        "supervision",
        # modeling
        "optuna",
        "albumentations",
        # deep learning frameworks
        "ultralytics",
        "lightning",
        "transformers",
        "torch",
        "torchvision",
        "torchaudio",
        # visualization
        "seaborn",
        "matplotlib",
    ],
    entry_points={"console_scripts": ["niche=pyniche.show:main"]},
)
