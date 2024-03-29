from setuptools import find_packages, setup

setup(
    name='souspi',
    version='0.0.1',
    license='MIT',
    packages=find_packages(exclude=["bluepy"]),
    description='A web app that runs on a RaspberryPi and starts/stops an Anova Precision Cooker.',
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask', 'bluepy'
    ],
    extra_requires={
        'test': [
            'pytest',
            'freezegun',
            'coverage'
        ]
    }
)
