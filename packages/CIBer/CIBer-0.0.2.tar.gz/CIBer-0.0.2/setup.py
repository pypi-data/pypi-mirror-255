from setuptools import setup, find_packages
  
with open("README.md", "r") as fh: 
    description_long = fh.read() 
  
setup( 
    name="CIBer", 
    version="0.0.2", 
    author="Kaiser & Ross", 
    author_email="rosscooper@link.cuhk.edu.hk", 
    packages=find_packages(),
    description="A Comonotone-Independence Bayesian Classifier", 
    long_description=description_long, 
    long_description_content_type="text/markdown", 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
        ],
    url="https://github.com/ross1456/CIBer-Package.git", 
    license='MIT', 
    python_requires='>=3.8', 
    install_requires=["numpy","pandas","scipy","scikit-learn"] 
)