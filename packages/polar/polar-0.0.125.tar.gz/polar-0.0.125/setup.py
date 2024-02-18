import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="polar",
    version="0.0.125",
    author="Piotr Parkitny",
    author_email="pparkitn@gmail.com",
    description="Data Science Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/polar/",
    packages=['polar'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
	install_requires=['pandas','numpy','scipy','statsmodels','scikit-learn','seaborn','cryptography','nltk','python-pptx','imblearn'],
    python_requires='>=3.5',
)
