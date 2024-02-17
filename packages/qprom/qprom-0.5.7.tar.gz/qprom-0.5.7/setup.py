from setuptools import setup, find_packages


def readme():
    with open('README.md', "r", encoding='utf-8') as f:
        return f.read()


setup(name='qprom',
      version='0.5.7',
      description='A Python-based CLI tool to quickly interact with OpenAIs GPT models instead of relying on the web interface.',
      long_description=readme(),
      long_description_content_type='text/markdown',
      entry_points={
          'console_scripts': [
              'qprom=qprom.main:main'
          ]
      },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Operating System :: OS Independent'
      ],
      url='https://github.com/MartinWie/qprom',
      author='MartinWiechmann',
      author_email='donotsuspend@googlegroups.com',
      keywords='GPT-4 CLI GPT-3 OpenAI',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'tiktoken',
          'openai',
          'argparse'
      ],
      include_package_data=True,
      zip_safe=False)
