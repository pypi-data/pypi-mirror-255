from setuptools import setup, find_packages


def parse_requirements() -> list[str]:
    reqs = []
    with open("requirements.txt") as f:
        for line in f.read().splitlines():
            line = line.split("#")[0].strip()
            if line:
                reqs.append(line)
    return reqs


setup(
    name="zonesmart-utils",
    version="0.5.3",
    author="Zonesmart",
    author_email="kamil@zonesmart.ru",
    packages=find_packages(include=["zs_utils", "zs_utils.*"]),
    install_requires=parse_requirements(),
)
