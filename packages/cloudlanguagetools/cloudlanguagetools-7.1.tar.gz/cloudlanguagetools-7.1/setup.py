from setuptools import setup
from setuptools.command.install import install

# build instructions
# python setup.py sdist
# twine upload dist/*

setup(name='cloudlanguagetools',
      version='7.1',
      description='Interface with various cloud APIs for language processing such as translation, text to speech',
      long_description=open('README.rst', encoding='utf-8').read(),
      url='https://github.com/Language-Tools/cloud-language-tools-core',
      author='Luc',
      author_email='languagetools@mailc.net',
      classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Text Processing :: Linguistic',
      ],      
      license='GPL',
      packages=['cloudlanguagetools'],
      install_requires=[
          'clt_wenlin>=1.0',
          'clt_requirements>=1.3',
          'pinyin_jyutping>=0.9',
      ],
      )
