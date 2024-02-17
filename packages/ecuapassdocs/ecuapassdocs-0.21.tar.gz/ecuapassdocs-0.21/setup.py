from setuptools import setup, find_packages

setup(
    name='ecuapassdocs',  # Package name
    version='0.21',  # Package version
    url="https://github.com/lgarreta/ecuapassdocs",
    author='Luis Garreta',
    author_email='lgarreta@gmail.com',
    description='Utils for creating PDFs, loading resources and extracting info from fields in ECUAPASS docs: cartaportes, manifiestos, declaraciones',
    packages=find_packages(),  # Automatically finds packages within the directory
	include_package_data=True, 
	package_data={"ecuapassdocs": ["resources/images/*", 
	                               "resources/data-cartaportes/*",
	                               "resources/data-manifiestos/*",
	                               "resources/data-declaracion/*",
	                               "resources/docs/*"]},
	# List any dependencies here
    install_requires = [
		"PyPDF2==3.0.1",
		"reportlab==4.0.8",
		"Pillow==10.1.0"
	], 
)
