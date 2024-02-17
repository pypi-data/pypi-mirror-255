import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xml-generator-seobaeksol",  # Replace with your own username
    version="0.5.0",
    author="seobaeksol",
    author_email="suyoung154@example.com",
    description="Comprehensive XML generator for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seobaeksol/xml-generator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
