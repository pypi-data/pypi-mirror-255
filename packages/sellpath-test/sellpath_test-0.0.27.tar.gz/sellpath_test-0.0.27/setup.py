from setuptools import setup, find_packages

setup(
    name="sellpath_test",
    version="0.0.27",
    description="test_description",
    author="bigbowltakestime",
    author_email="bigbowltakestime@gmail.com",
    install_requires=["simple-salesforce", "apollo", "prefect", "cryptography", "shortuuid"],
    packages=find_packages(exclude=[]),
    keywords=["sellpath", "sellpath_test"],
    python_requires=">=3.11",
    package_data={},
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3.11",
    ],
)
