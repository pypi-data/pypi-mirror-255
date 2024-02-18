from setuptools import setup
from pathlib import Path

desc = (Path(__file__).parent / "README.md").read_text()

setup(
    name='latex2readme',
    version='0.0.2',
    py_modules=["latex2readme"],
    description="Convert LaTeX documents to README.md files",
    long_description=desc,
    long_description_content_type='text/markdown',
    url="https://github.com/leon-h-a/latex2readme",
    license="MIT",
    install_requires=[
        "natsort==8.4.0",
        "pdf2image==1.16.3",
        "pillow==10.2.0",
        "pdflatex"
    ],
    entry_points={
        'console_scripts': [
            'ttr = latex2readme:run',
        ]
    }
)
