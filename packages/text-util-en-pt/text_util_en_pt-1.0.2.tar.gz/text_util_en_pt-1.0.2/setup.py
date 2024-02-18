from setuptools import setup, find_packages

setup(
    name='text_util_en_pt',
    version='1.0.2',
    author='Carlo Moro',
    author_email='cnmoro@gmail.com',
    description="Python project for text cleaning. Some specifics for English and Portuguese languages.",
    packages=find_packages(),
    package_data={
        'text_util_en_pt': [
            'resources/english_nltk_tokenizer.pkl',
            'resources/portuguese_nltk_tokenizer.pkl'
        ]
    },
    include_package_data=True,
    install_requires=["langdetect"],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)