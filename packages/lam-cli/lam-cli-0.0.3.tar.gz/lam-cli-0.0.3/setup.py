from setuptools import find_packages, setup

setup(
    name='lam-cli',
    version='0.0.3',
    packages=find_packages(),
    install_requires=[
        'click',
        'posthog',
    ],
    entry_points={
        'console_scripts': [
            'lam=lam.lam:lam',
        ],
    },
    license='GPLv3',
    # Include additional metadata about your package
    author='Laminar Run, Inc.',
    author_email='connect@laminar.run',
    description='Laminar data transformation tool',
    url='https://github.com/laminar-run/lam',
    long_description="""
    Laminar is a platform that makes building and maintaining API integrations faster.
    """
)
