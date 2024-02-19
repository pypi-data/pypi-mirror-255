import re

import setuptools

version = ""
requirements = []
with open("papertools/__init__.py") as f:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        f.read(),
        re.MULTILINE,
    ).group(1)

if not version:
    raise RuntimeError("version is not set")

if version.endswith(("a", "b", "rc")):
    # append version identifier based on commit count
    try:
        import subprocess

        p = subprocess.Popen(
            ["git", "rev-list", "--count", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        if out:
            version += out.decode("utf-8").strip()
        p = subprocess.Popen(
            ["git", "rev-parse", "--short", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        if out:
            version += "+g" + out.decode("utf-8").strip()
    except Exception:
        pass

with open("README.md", "r") as f:
    readme = f.read()

setuptools.setup(
    name="papertools",
    author="aiokev",
    version=version,
    url="https://github.com/paper-devs/papertools",
    packages=setuptools.find_packages(),
    license="GPL-3.0",
    description="A module which offers tons of usefull features for discord.py bots.",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    python_requires=">=3.9",
    keywords=["python", "discord.py", "utilities"],
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
)
