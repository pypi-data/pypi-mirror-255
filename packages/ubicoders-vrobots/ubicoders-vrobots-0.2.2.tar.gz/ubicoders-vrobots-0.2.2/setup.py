from setuptools import setup, find_packages

setup(
    name="ubicoders-vrobots",
    version="0.2.2",
    license="GPLv3",
    author="Elliot Lee",
    author_email="info@airnh.ca",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    url="https://github.com/ubicoders0/vrobots",
    keywords="ubicoders virtual robots",
    install_requires=["websockets", "websocket-client", "numpy", "flatbuffers", "fastapi", "uvicorn"],
)
