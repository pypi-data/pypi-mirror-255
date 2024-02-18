from setuptools import setup, find_packages

setup(
    name='VSGenerator',
    version='0.0.1',
    description="Dynamic Virtual Space generation neural Network.",
    long_description=open('README.md', encoding='utf-8').read(),
    include_package_data=True,
    author='CaoBin',
    author_email='binjacobcao@gmail.com',
    maintainer='CaoBin',
    maintainer_email='binjacobcao@gmail.com',
    license='MIT License',
    url='https://github.com/Bin-Cao/Bgolearn',
    packages=find_packages(),  # Automatically include all Python modules
    package_data={'VSGenerator': ['_BgoVAE/*','_VSGNN/*']},  # Specify non-Python files to include
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.5',
    install_requires=[ 'tensorflow', 'pandas', 'numpy',],
    entry_points={
        'console_scripts': [
            '',
        ],
    },
)
