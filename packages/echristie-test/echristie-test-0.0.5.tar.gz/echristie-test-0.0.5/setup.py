import setuptools
from distutils.core import setup
from pathlib import Path

HERE = Path(__file__).resolve().parent
setup(
    name="echristie-test",
    packages=["print_numbers"],
    version="0.0.5",
    author="Edwin",
    long_description=(HERE / "README.md").read_text(),
    long_description_content_type="text/markdown",
    description="Temp Package",
    python_requires=">=3.6",

)
