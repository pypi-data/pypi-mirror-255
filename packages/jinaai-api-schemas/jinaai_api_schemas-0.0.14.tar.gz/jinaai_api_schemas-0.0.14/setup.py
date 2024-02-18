from os import path
from setuptools import find_packages, setup

# package version
try:
    pkg_name = 'api_schemas'
    libinfo_py = path.join(pkg_name, '__init__.py')
    libinfo_content = open(libinfo_py, 'r', encoding='utf-8').readlines()
    version_line = [l.strip() for l in libinfo_content if l.startswith('__version__')][
        0
    ]
    exec(version_line)  # gives __version__
except FileNotFoundError:
    __version__ = '0.0.0'


def get_requiments():
    with open(f'requirements.txt') as f:
        lines = [
            line.strip()
            for line in f.read().splitlines()
            if not line.strip().startswith('#')
        ]
        return lines


_name = 'api_schemas'

_dependencies = get_requiments()
_description = 'The schemas for the Jina Serving API'
_long_description = ''

if __name__ == '__main__':
    setup(
        name=f'jinaai_{_name}',
        packages=find_packages(),
        version=__version__,
        include_package_data=True,
        description=_description,
        author='Jina AI',
        author_email='hello@jina.ai',
        license='Proprietary',
        download_url='https://github.com/jina-ai/embedding-api-schemas/tags',
        long_description=_long_description,
        long_description_content_type='text/markdown',
        zip_safe=False,
        setup_requires=['setuptools>=18.0', 'wheel'],
        install_requires=_dependencies,
        python_requires='>=3.8.0',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Environment :: Console',
            'Operating System :: OS Independent',
            'Topic :: Scientific/Engineering :: Artificial Intelligence',
        ],
        project_urls={
            'Source': 'https://github.com/jina-ai/embedding-api-schemas.fit/',
            'Tracker': 'https://github.com/jina-ai/embedding-api-schemas/issues',
        },
    )
