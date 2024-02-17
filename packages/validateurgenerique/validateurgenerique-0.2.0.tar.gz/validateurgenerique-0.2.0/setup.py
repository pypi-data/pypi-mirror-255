from setuptools import setup, find_packages

with open ('README.txt','r') as f:
    ldescription=f.read()

setup(
    name='validateurgenerique',
    version='0.2.0', 
    author='Garbi Youssef',
    author_email='gharbiyoussef884@gmail.com',
    description="A tool for validating, transforming, and controlling data.",
    long_description=ldescription,
    long_description_content_type='text/markdown',
    url="https://gitlab.com/gharbiyoussef884/pythonvalidatorpackage", 
    license="MIT",
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "jsonschema>=3.0.0", 
        "flask>=1.0.0",  
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
        ]
    },
    project_urls={
        "Source": "https://gitlab.com/gharbiyoussef884/pythonvalidatorpackage",
        "Bug Reports": "https://gitlab.com/gharbiyoussef884/pythonvalidatorpackage/-/issues",
    },
)