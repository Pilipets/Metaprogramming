from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='py2sql_orm',
    version='0.1.2',
    description='Tool for fixing renamings, documentation in accordance with java code convention',
    long_description_content_type="text/markdown",
    long_description=README,
    license='MIT',
    packages=find_packages(),
    author='Hlib Pylypets',
    keywords=['SQL', 'Python', 'ORM'],
    install_requires=["cx_Oracle"],
    url='https://github.com/Pilipets/Metaprogramming/tree/main/TasksSolution/Py2SqlOrm'
)

if __name__ == '__main__':
    setup(**setup_args)