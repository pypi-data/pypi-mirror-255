import setuptools

with open("README.md", "r", encoding="UTF-8") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name="BusProjectUW_KO",
	version="0.0.1",
	author="Kuba Ornatek",
	author_email="kuba.ornatek@gmail.com",
	description="A package for the University of Warsaw Python Course",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/Ometek16/UW_Python_Course",
	packages=setuptools.find_packages(),
	package_data={'BUS_PROJECT_UW_KO': ['src/*.json', 'src/*.geojson']},
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires=">=3.6", 
)
