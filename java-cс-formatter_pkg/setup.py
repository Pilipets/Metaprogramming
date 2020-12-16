from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='java-cc-formatter',
    version='0.1.6',
    description='Package for Python to SQL object relationship mapping',
    long_description_content_type="text/markdown",
    long_description=README,
    license='MIT',
    packages=find_packages(),
    author='Hlib Pylypets',
    keywords=['Java', 'CodeConvention', 'Formatter'],
    url='https://github.com/Pilipets/Metaprogramming/tree/main/TasksSolution/CodeConventionModifier(Java)'
)

if __name__ == '__main__':
    setup(**setup_args)