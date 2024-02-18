import setuptools
setuptools.setup(
    name="pydiver",
    version="0.0.3",
    author="Almos Gero",
    author_email="almos.gero@gmail.com",
    description="A pydiver package",
    url="https://github.com/modules.py/pydiver",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
)