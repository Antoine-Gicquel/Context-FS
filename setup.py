from setuptools import setup

name="Context FS"
version="1.0"
scripts=["ctxfs.py"]
install_requires=["fusepy"]

setup(	name=name,
	version=version,
	scripts=scripts,
	install_requires=install_requires
)
