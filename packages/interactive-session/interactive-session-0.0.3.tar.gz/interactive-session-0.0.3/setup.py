# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup, find_packages
from version import __version__

# The main interface is through Pybind11Extension.
# * You can add cxx_std=11/14/17, and then build_ext can be removed.
# * You can set include_pybind11=false to add the include directory yourself,
#   say from a submodule.
#
# Note:
#   Sort input source files if you glob sources to ensure bit-for-bit
#   reproducible builds (https://github.com/pybind/python_example/pull/53)

ext_modules = [
    Pybind11Extension(
        "interactive_session",
        ["src/main.cxx", "src/session.cxx"],
        # Example: passing in the version to the compiled code
        define_macros=[("VERSION_INFO", __version__)],
    ),
]

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Read the contents of README.md
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="interactive-session",
    version=__version__,
    author="Bo Chen",
    author_email="bochen0909@gmail.com",
    url="https://github.com/bochen0909/interactive-session",
    description="A shell session project using pybind11",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=requirements,
    ext_modules=ext_modules,
    extras_require={"test": "pytest"},
    # Currently, build_ext only provides an optional "highest supported C++
    # level" feature, but in the future it may provide more features.
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.8",
)
