from setuptools import setup

setup(
    name="OTDHT",
    version="0.1.0",
	author="Thomas Churchman",
	packages=["dht", "hash", "krpc"],
    install_requires=[
        "twisted",
		"bencode"
    ]
)