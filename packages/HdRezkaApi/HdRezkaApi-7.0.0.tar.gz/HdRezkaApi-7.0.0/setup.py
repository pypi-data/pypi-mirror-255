import setuptools
with open(r'C:\Users\rost\Downloads\README.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='HdRezkaApi',
	version='7.0.0',
	author='Super_Zombi',
	author_email='super.zombi.yt@gmail.com',
	description='',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/SuperZombi/HdRezkaApi',
	packages=['HdRezkaApi'],
	install_requires=["beautifulsoup4"],
	include_package_data=True,
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)