from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()


setup(
    name='OmnicommSun',
    version='0.0.23',
    author='SeAllexUnder',
    author_email='sun5038@yandex.ru',
    description='test',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/SeAllexUnder/OmnicommSun',
    packages=find_packages(),
    install_requires=['requests>=2.25.1'],
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='omnicomm',
    project_urls={
        'GitHub': 'https://github.com/SeAllexUnder/OmnicommSun'
    },
    python_requires='>=3.6'
)
