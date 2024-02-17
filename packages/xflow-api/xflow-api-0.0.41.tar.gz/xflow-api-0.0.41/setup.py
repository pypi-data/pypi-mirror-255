from setuptools import setup, find_packages

setup(
    name='xflow-api',
    version='0.0.41',
    description='python package for xflow',
    author='kyon',
    author_email='originky2@gmail.com',
    install_requires=['ipython', 'pydantic', 'requests', 'tqdm', 'ray',],
    packages=find_packages(exclude=[]),
    python_requires='>=3.10',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.11',
    ],
)


# python setup.py sdist bdist_wheel
# python -m twine upload dist/*