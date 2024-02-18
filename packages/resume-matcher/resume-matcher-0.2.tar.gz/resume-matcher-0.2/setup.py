from setuptools import setup, find_packages

setup(
    name='resume-matcher',
    version='0.2',
    description='A Python library for matching resumes with job descriptions',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
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