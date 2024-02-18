from setuptools import setup, find_packages

setup(
    name='resume-matcher',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'resume-matcher=resume_matcher.matching:main',
        ],
    },
    install_requires=[
        'docx2txt',
        'scikit-learn'
    ],
)