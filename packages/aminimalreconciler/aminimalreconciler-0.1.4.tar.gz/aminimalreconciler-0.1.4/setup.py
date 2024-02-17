
from setuptools import setup, find_packages

setup(
    name='aminimalreconciler',
    version='0.1.4',
    description='reconciler',
    url='https://github.com/muathendirangu/reconcile',
    author='muathendirangu',
    author_email='muathe.ndirangu@gmail.com',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'reconciler=reconciler.reconciler:main'
        ],
    },
    long_description_content_type='text/markdown'
)
