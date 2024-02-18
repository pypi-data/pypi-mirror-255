#!/usr/bin/env python

from setuptools import setup, find_packages
import versioneer

def unique_flatten_dict(d):
  return list(set(sum( d.values(), [] )))

core_requires = [
  'numpy',
  'pandas',
  'setuptools',
  'typing-extensions',
  'pyarrow>=0.15.0',
  'scikit-learn<=1.3.2',
  'psutil',
  'dirty-cat',  # only for pytest speed comparison
  'scipy',
#   'cuml', ## cannot test on github actions
#   'cudf',
#   'cupy'
]

stubs = [
  'pandas-stubs', 'types-requests', 'ipython', 'tqdm-stubs'
]

dev_extras = {
    'docs': ['sphinx==3.4.3', 'docutils==0.16', 'sphinx_autodoc_typehints==1.11.1', 'sphinx-rtd-theme==0.5.1', 'Jinja2<3.1'],
    'test': ['flake8>=5.0', 'mock', 'mypy', 'pytest'] + stubs,
    'testai': [
      'numba>=0.57.1'  # https://github.com/numba/numba/issues/8615
    ],
    'build': ['build']
}
extras_require = {

  **dev_extras,

    #kitchen sink for contributors, skips ai
    'dev': unique_flatten_dict(dev_extras),

}
# if __name__ == "__main__":
setup(
    name='cu-cat',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages = find_packages(),
    platforms='any',
    description = 'An end-to-end gpu Python library that encodes categorical variables into machine-learnable numerics',
    long_description=open("./README.md").read(),
    long_description_content_type='text/markdown',
    url='https://github.com/graphistry/cu-cat',
    download_url= 'https://github.com/graphistry/cu-cat',
    python_requires='>=3.9',
    author='The Graphistry Team',
    author_email='pygraphistry@graphistry.com',
    install_requires=core_requires,
    extras_require=extras_require,
    license='BSD',
    # dependency_links=['https://pypi.nvidia.com'],
    keywords=['cudf', 'cuml', 'GPU', 'Rapids']
)
