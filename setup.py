from setuptools import setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="essentials-configuration",
    version="0.0.1",
    description=(
        "Implementation of key-value pair based "
        "configuration for Python applications."
    ),
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/Neoteroi/essentials-configuration",
    author="RobertoPrevato",
    author_email="roberto.prevato@gmail.com",
    keywords="configuration root core yaml ini json environment",
    license="MIT",
    packages=["configuration"],
    install_requires=[],
    extras_require={
        "yaml": [
            "PyYAML==5.4.1",
        ]
    },
    include_package_data=True,
    zip_safe=False,
)
