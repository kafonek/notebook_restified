from setuptools import setup, find_packages

setup(name='notebook_restified',
      version='0.0.1',
      
      author='Matt Kafonek',
      author_email='kafonek@gmail.com',
      #url='https://github.com/kafonek/ipython_blocking',
            
      description='Separate Notebooks that deal with the model and view',
      long_description=open('README.md', encoding='utf-8').read(),
      long_description_content_type = 'text/markdown',
      
      packages=find_packages(),
      install_requires=['papermill', 'jinja2'],
      
      classifiers = [],
      license='BSD')