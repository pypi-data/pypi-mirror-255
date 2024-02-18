from setuptools import setup, find_packages
def load_readme() -> str:
    with open("README.md",encoding="utf-8_sig") as fin:
        return fin.read()
setup(
    name='EAGM',
    version='1.0.0',
    keywords = ("discord","add member"),
    long_description=load_readme(),
    long_description_content_type="text/markdown",
    author='taka4602',
    author_email='shun4602@gmail.com',
    url='https://github.com/taka-4602/Discord-Easy-Add-Guild-Member',
    description='A simple API wrapper for Discord Add Guild Member',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)