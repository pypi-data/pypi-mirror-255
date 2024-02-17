from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))


def get_file_text(file_name):
    with open(os.path.join(here, file_name)) as in_file:
        return in_file.read()


setup(
    name="cleancourt",
    version="0.8.3",
    description="a library for cleaning court docket entries",
    author="Logan Pratico",
    author_email="praticol@lsc.gov",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    long_description=get_file_text("README.md"),
    long_description_content_type="text/markdown",
    keywords="name standardization, plaintiff names, court data, name cleaning",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9, <4",
    install_requires=[
        "scikit-learn",
        "loguru",
        "probablepeople",
        "rapidfuzz",
        "tqdm",
        "pandas",
        "sparse-dot-topn",
        "ftfy",
        "scipy",
        "numpy",
    ],
    project_urls={},
)
