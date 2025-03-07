from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="video-generator",
    version="0.1.0",
    author="Christian Mueller",
    author_email="christian.mueller@vr-worlds.de",
    description="Sample YouTube video generator created with AI assistance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/smoki99/ClineClaudeMCPTesting",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "Programming Language :: Python :: 3.10",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'pytest-mock>=3.11.1',
            'black>=23.3.0',
            'pylint>=2.17.4',
            'mypy>=1.4.1',
            'ipython>=8.14.0',
            'jupyter>=1.0.0',
            'memory-profiler>=0.61.0',
            'sphinx>=7.0.1',
            'sphinx-rtd-theme>=1.2.2',
            'pre-commit>=3.3.3',
        ]
    },
    entry_points={
        'console_scripts': [
            'videogen=src.cli:main',
        ],
    },
)
