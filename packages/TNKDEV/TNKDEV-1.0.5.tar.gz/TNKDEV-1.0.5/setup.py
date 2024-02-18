
from setuptools import setup, find_packages
import os, codecs, re

dirname = os.path.abspath(os.path.dirname(__file__))

name_pkg = 'TNKDEV'

with codecs.open(os.path.join(dirname, name_pkg, "__version__.py"), mode="r", encoding="utf-8") as fp:
    try:
        data = fp.read()
        version = re.findall(r"^__version__ = ['\"]([^'\"]*)['\"]", data, re.M)[0]
        email = re.findall(r"^__author_email__ = ['\"](.*?)['\"]", data, re.M)[0]
        author  = re.findall(r"^__author__ = ['\"]([^'\"]*)['\"]", data, re.M)[0]
    except Exception:
        raise RuntimeError("Unable to determine info")

description = 'Đây Là Contact Của TNKDEV'

setup(
    name=name_pkg,
    version=version,
    author=author,
    author_email=email,
    description=description,
    long_description=open(os.path.join(dirname, "README.md"), encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    url="https://github.com/tnk-admin/TNKDEV",
    packages=find_packages(),
    install_requires=[
        'pycryptodome',
    ],
    keywords=['python', 'GAUTRICKER', 'KHANH', 'TNKDEV', 'TNK', 'K07VN','GAU','TRUONGNGOCKHANH'],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
