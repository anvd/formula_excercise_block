"""Setup for formula_exercise_block XBlock."""

import os
from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='Formula Exercise XBlock',
    version='0.2',
    description='Formula Exercise XBlock',
    license='LGPL-3.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='xblock open edx formula exercise',
    author='Vo Duc An',
    author_email='voducanvn@gmail.com',
    packages=[
        'formula_exercise_block',
    ],
    install_requires=[
        'XBlock',
        'xblock-utils',
        'cexprtk',
        'mysql-connector==2.1.4'
    ],
    entry_points={
        'xblock.v1': [
            'formula_exercise_block = formula_exercise_block:FormulaExerciseXBlock',
        ]
    },
    package_data=package_data("formula_exercise_block", ["static", "public"]),
)
