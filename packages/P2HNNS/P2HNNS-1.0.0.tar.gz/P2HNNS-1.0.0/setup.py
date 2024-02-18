from distutils.core import setup
setup(
  name = 'P2HNNS',
  packages = ['P2HNNS'],
  version = '1.0.0',
  license='MIT',
  description = 'A Python library for efficient Point-to-hyperplane nearest neighbours search (P2HNNS)',
  author = 'Petros Demetrakopoulos',
  author_email = 'petrosdem@gmail.com',
  url = 'https://github.com/petrosDemetrakopoulos/P2HNNS',
  download_url = 'https://github.com/petrosDemetrakopoulos/P2HNNS/archive/refs/tags/1.0.0.tar.gz',    # I explain this later on
  keywords = ['KNN', 'similarity', 'search','hyperplance','point','nearest','neighbours'],
  install_requires=[
          'numpy',
          'tqdm',
      ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
