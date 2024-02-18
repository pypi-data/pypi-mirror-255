from setuptools import setup, find_packages

setup(
    name='autopipeline',
    version='0.1.136',
    packages=find_packages(),
    package_data={
        # Include files from the "data" directory in the "autopipeline" package
        'autopipeline': ['data/*'],
    },
    include_package_data=True,
    license='LICENSE',
    install_requires=[
        'openai==0.28',
        'pandas',
        'PyMuPDF',
        'pytesseract',
        'textstat',
        'Pillow',
        'gensim',
        'nltk',
        'bert-extractive-summarizer', # This may be the package for summarizer, make sure to find the correct one.
        'flair',
        'textblob',
        'scikit-learn',
        'pandasql'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
