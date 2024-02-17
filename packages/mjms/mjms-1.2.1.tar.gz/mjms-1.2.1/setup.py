import setuptools

setuptools.setup(name="mjms",
    version="1.2.1",
    description="Python client for mailsrv.marcusj.org",
    long_description=open('README.md','r').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AgeOfMarcus/mjms",
    author="AgeOfMarcus",
    author_email="marcus@marcusweinberger.com",
    packages=setuptools.find_packages(),
    zip_safe=False,
    install_requires=[
        'requests',
    ],
)