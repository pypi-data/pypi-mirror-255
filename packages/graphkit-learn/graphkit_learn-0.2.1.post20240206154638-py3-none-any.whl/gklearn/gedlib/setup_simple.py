from distutils.extension import Extension
from distutils.core import setup
from Cython.Build import cythonize

import os
import sys
import shutil
import subprocess
import platform

import numpy
import importlib


def parse_args():
	# @TODO: This may not work with bdist_wheel/PyPI installation.
	import argparse
	parser = argparse.ArgumentParser()

	parser.add_argument(
		'--use-existing-gedlib2',
		dest='use_existing_gedlib',
		type=str,
		choices=['true', 'false'],
		default='false',
		help='Whether to use an existing GEDLIB2 C++ library. This will avoid '
		     'downloading the library from GitHub and extracting it. If no library '
		     'is found, the installation will stop and an error will be raised. '
		     'Does not have effect when `--build-gedlibpy2` is set to `false`. It may help '
		     'when you have problem accessing GitHub or it takes too long time to '
		     'extract the file (which is my case on CentOS (I hate this system!)). '
	)

	parser.add_argument(
		'--build-gedlib2',
		dest='build_gedlib2',
		type=str,
		choices=['true', 'false'],
		default='true',
		help='Whether to build GEDLIB2 C++.'
	)

	parser.add_argument(
		'--develop-mode',
		dest='develop_mode',
		type=str,
		choices=['true', 'false'],
		default='true',
		help='Whether in development mode. If true, the include files in the `gedlibpy2` module will be deleted after installation.'
	)

	args, unknown = parser.parse_known_args()
	return args


def install(package):
	try:
		importlib.import_module(package)
	except ImportError:
		import subprocess
		cur_python = sys.executable
		subprocess.call([cur_python, '-m', 'pip', 'install', package])


def get_gedlib():
	install('tqdm')

	import urllib.request
	from tqdm import tqdm
	import zipfile

	print()
	# Delete previous GEDLIB installation if exists:
	path_gedlib = os.path.join(os.getcwd(), 'include/gedlib2/')
	if os.path.exists(path_gedlib):
		print('Deleting previous GEDLIB2 installation...')
		shutil.rmtree(path_gedlib)
		print('Done!')
		print()
	else:
		pass
		print('No previous installation of GEDLIB2.')

	print('Downloading and unpacking GEDLIB2 from GitHub...')

	url = 'https://github.com/jajupmochi/gedlib2/archive/refs/heads/master.zip'
	filename = 'gedlib2.zip'

	with tqdm(
			unit='B', unit_scale=True, unit_divisor=1024, miniters=1,
			desc=filename
	) as t:
		urllib.request.urlretrieve(
			url, filename=filename,
			reporthook=lambda blocknum, blocksize, totalsize: t.update(
				blocknum * blocksize - t.n
			)
		)

	with zipfile.ZipFile(filename, 'r') as zip_ref:
		for member in tqdm(zip_ref.infolist(), desc='Extracting'):
			try:
				zip_ref.extract(member, path='include/')
			except zipfile.error as e:
				pass

	# Delete the .zip file:
	os.remove(filename)
	print('The .zip file of GEDLIB2 is deleted.')

	print('Done!')
	print()


def check_gedlib():
	print()
	print('Checking if GEDLIB2 is already downloaded...')
	path_gedlib = os.path.join(os.getcwd(), 'include/gedlib2/')
	if not os.path.exists(path_gedlib):
		raise ModuleError(
			'The C++ library `GEDLIB2` is not found, which is required to build the '
			'`gedlibpy2` module. You have to install several ways to fix this error:'
			'\n-- 1. Download GEDLIB2 from '
			'`https://github.com/jajupmochi/gedlib2/archive/refs/heads/master.zip`, '
			'and extract it into `include/gedlib2/`.'
			'\n-- 2. Set `use-existing-gedlib2` to `false` or the default value.'
			'\n-- 3. Set `--build-gedlibpy2` to `false`. Notice, it '
			'is possible that the module would not work when it is incompatible '
			'with the system (libraries).'
		)
	print('Done!')
	print()


def install_gedlib():
	"""
	Notes
	-----
	The followings are done during this installation:
		- Build files in `ext/fann.2.2.0/lib/`;
		- Clean obj files in `ext/nomad.3.8.1/ext/sgtelib/src/`;
		- Build files in `ext/nomad.3.8.1/ext/sgtelib/lib/`;
		- Generate executable files in `ext/nomad.3.8.1/ext/sgtelib/bin/`;
		- Build files in `ext/nomad.3.8.1/lib/`;
		- Generate `ext/libsvm.3.22/libsvm.so`;
	"""
	print()
	print('Installing GEDLIB2...')
	import subprocess
	cur_python = sys.executable
	subprocess.call([cur_python, '--version'])
	subprocess.call(['which', cur_python])
	gedlib_dir = 'include/gedlib2/'
	subprocess.call(
		[cur_python, 'install.py'], cwd=gedlib_dir
	)
	print()


def copy_gedlib_includes_and_libs():
	def copy_paste_with_logs(src_path, dst_path):
		"""
		Authors
		-------
		Linlin Jia, ChatGPT 3.5 (2023.04.27)
		"""
		cur_dir = os.path.dirname(os.path.abspath(__file__))
		src_path = os.path.join(cur_dir, src_path)
		dst_path = os.path.join(cur_dir, dst_path)

		# if the source is a file, copy it and print the copied file name
		if os.path.isfile(src_path):
			shutil.copy(src_path, dst_path)
			print(f"Copied file {src_path} to {dst_path}.")

		# if the source is a directory, copy it and print the copied file names
		if os.path.isdir(src_path):
			shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
			print(f"Copied directory {src_path} to {dst_path}.")


	print()
	print(
		'Copying and pasting (generated) includes and libs files of GEDLIB2 into '
		'proper locations to build gedlibpy2...'
	)
	# Copy-paste includes:
	print('Copying includes...')
	copy_paste_with_logs(
		'include/gedlib2/ext/boost.1.69.0/', 'include/boost.1.69.0/'
	)
	copy_paste_with_logs(
		'include/gedlib2/ext/eigen.3.3.4/Eigen/',
		'include/eigen.3.3.4/Eigen/'
	)
	copy_paste_with_logs(
		'include/gedlib2/ext/nomad.3.8.1/src/', 'include/nomad.3.8.1/src/'
	)
	copy_paste_with_logs(
		'include/gedlib2/ext/nomad.3.8.1/ext/sgtelib/src/',
		'include/nomad.3.8.1/ext/sgtelib/src/'
	)
	copy_paste_with_logs(
		'include/gedlib2/ext/lsape.5/include/', 'include/lsape.5/include/'
	)
	copy_paste_with_logs(
		'include/gedlib2/ext/libsvm.3.22/', 'include/libsvm.3.22/'
	)
	copy_paste_with_logs(
		'include/gedlib2/ext/fann.2.2.0/include/',
		'include/fann.2.2.0/include/'
	)
	# Copy-paste libs:
	print('Copying includes...')
	copy_paste_with_logs(
		'include/gedlib2/ext/nomad.3.8.1/lib/', 'lib/nomad.3.8.1/'
	)
	copy_paste_with_logs(
		'include/gedlib2/ext/libsvm.3.22/', 'lib/libsvm.3.22/'
	)
	copy_paste_with_logs(
		'include/gedlib2/ext/fann.2.2.0/lib/', 'lib/fann.2.2.0/'
	)

	print('done!')
	print()


def clean_previous_build():
	# clean previous build
	print()
	print('Cleaning previous build...')
	for name in os.listdir():
		if (name.startswith('gedlibpy2') and not (
				name.endswith('.pyx') or name.endswith('.pxd'))):
			os.remove(name)
		if name == 'build':
			shutil.rmtree(name)
	print('Done!')
	print()


def get_extensions():
	exts = [
		Extension(
			"gedlibpy2",
			# sources=["gedlibpy.pyx", "src/GedLibBind2.cpp"],
			sources=["gedlibpy2.pyx"],
			include_dirs=[
				"src", "include", "include/lsape.5/include",
				"include/eigen.3.3.4/Eigen",
				"include/nomad.3.8.1/src",
				"include/nomad.3.8.1/ext/sgtelib/src",
				"include/libsvm.3.22",
				"include/fann.2.2.0/include", "include/boost.1.69.0"
			],
			library_dirs=[
				"lib/fann.2.2.0", "lib/libsvm.3.22",  # "lib/gedlib",
				"lib/nomad.3.8.1"
			],
			libraries=["doublefann", "sgtelib", "svm", "nomad"],
			language="c++",
   			extra_compile_args=["-std=c++11"],  # @TODO: Enable debug mode for C++ or not.
			# extra_compile_args=["-std=c++11", "-DDEBUG"],
			extra_link_args=["-std=c++11"]
		)
	]
	return exts


def remove_includes():
	print()
	print('Deleting includes...')
	name = os.path.join(os.getcwd(), 'include/')
	shutil.rmtree(name)
	print('Done!')
	print()


if __name__ == '__main__':
	# args = parse_args()
	# check_gedlib()
	# if args.build_gedlib2 == 'true':
	# 	# Install GEDLIB:
	# 	install_gedlib()
	# # Copy-Paste includes and libs of GEDLIB2:
	# copy_gedlib_includes_and_libs()

	# clean previous build:
	clean_previous_build()

	print()
	print('Start building...')
	# Build gedlibpy2:
	extensions = get_extensions()
	with open("README.rst", "r") as fh:
		long_description = fh.read()

	# Attention: setup function can not be put inside a function!
	setup(
		ext_modules=cythonize(
			extensions,
			compiler_directives={'language_level': '3'}
		),
		name="gedlibpy2",
		author="Lambert Natacha and Linlin Jia",
		author_email="linlin.jia@unibe.ch",
		description="A Python wrapper library for C++ library GEDLIB2 of graph edit distances",
		long_description=long_description,
		long_description_content_type="text/markdown",
		project_urls={
			# 'Documentation': 'https://graphkit-learn.readthedocs.io',
			'Source': 'https://github.com/jajupmochi/graphkit-learn/tree/master/gklearn/gedlib',
			'Tracker': 'https://github.com/jajupmochi/graphkit-learn/issues',
		},
		url="https://github.com/jajupmochi/graphkit-learn/tree/master/gklearn/gedlib",
		classifiers=[
			"Programming Language :: Python :: 3",
			"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
			"Operating System :: OS Independent",
			'Intended Audience :: Science/Research',
			'Intended Audience :: Developers',
		],
		include_dirs=[numpy.get_include()]
	)

	# List generated files:
	print()
	print('The following files are generated:')
	for name in os.listdir():
		if (name.startswith('gedlibpy2') and not (
				name.endswith('.pyx') or name.endswith('.pxd'))):
			print(name)

	print()
	print('Build completed!')
	print()

	# if args.develop_mode == 'false':
	# 	# Remove GEDLIB include files:
	# 	remove_includes()

# Commande Bash : python setup_simple.py build_ext --inplace
