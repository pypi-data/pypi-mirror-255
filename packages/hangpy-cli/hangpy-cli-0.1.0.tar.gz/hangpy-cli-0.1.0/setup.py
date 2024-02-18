import setuptools
from hangpy import __version__


with open("README.md", "r", encoding="utf-8") as f:
    README = f.read()


setuptools.setup(
    name="hangpy-cli",
    version=__version__,
    author="Renzo Valentin",
    author_email="renzofbn@gmail.com",
    description="CLI program to play the hangman game suporting multiple languages, ideal for learning new words",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/renzofbn/hangpy",
    include_package_data = True,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment :: Puzzle Games",
    ],
    keywords="hangpy, hangman, game, cli, command-line, hangman-game",
    python_requires='>=3.6',
    # cmdclass={
    #     'install': PostInstallHook,  # type: ignore
    # },
    entry_points={
        "console_scripts": ["hangpy=hangpy.__main__:main"],
    },
)