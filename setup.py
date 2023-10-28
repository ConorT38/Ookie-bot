from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

setup(
    name="ookiebot",
    version="1.0.0",
    packages=find_packages(),
    entry_points={"console_scripts": ["ookiebot = ookiebot.__main__:main"]},
    install_requires=install_requires,
)