from setuptools import setup, find_packages

VERSION = "0.0.1"
DESCRIPTION = "Communicate with the Onvo platform."
LONG_DESCRIPTION = "A gem to provide utilities to seamlessly communicate with the Onvo platform, allowing developers to integrate AI-powered dashboards into their products."

setup(
    # the name must match the folder name 'verysimplemodule'
    name="onvo",
    version=VERSION,
    author="Bryan Davis",
    author_email="bryandavis999.dev@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=["python", "onvo"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
