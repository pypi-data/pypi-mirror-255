from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="ffxivcalc",  # Required
    version="0.8.900",  # Required
    description="DPS simulator for Final Fantasy XIV.",
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    url="https://github.com/IAmPythagoras/FFXIV-Combat-Simulator",  # Optiona
    author="Anthony Desrochers",
    author_email="anthony.desrochers17@gmail.com",
    classifiers=[  # Optional
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10"
    ],
    keywords="ffxiv, xiv, dps, simulator, ffxiv-combat-simulator",
    package_dir={"": "src"},  # Optional,
    packages=find_packages(where="src"),  # Required
    python_requires=">=3.10",
    install_requires=[  "contourpy",
                        "cycler",
                        "fonttools",
                        "kiwisolver",
                        "matplotlib",
                        "numpy",
                        "packaging",
                        "Pillow",
                        "pyparsing",
                        "python-dateutil",
                        "six",
                        "coreapi"],  # Optional
    project_urls={  # Optional
        "Source": "https://github.com/IAmPythagoras/FFXIV-Combat-Simulator",
        "Site": "https://ffxivdpscalc.azurewebsites.net/simulate/",
        "Documentation": "https://iampythagoras.github.io/index.html"
    },
)