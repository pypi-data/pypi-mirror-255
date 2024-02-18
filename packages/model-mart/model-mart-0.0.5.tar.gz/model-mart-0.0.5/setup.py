import setuptools

with open("README.md", "r") as fh:
    long_description = None

setuptools.setup(
    name="model-mart",  # Replace with your own name
    version="0.0.5",
    author="SoutherLea",
    author_email="lizhengnan@stonewise.cn",
    description="sdk help users to use model market",
    long_description="sdk help users to use model market",
    long_description_content_type="text/markdown",
    url="https://gitlab.stonewise.cn/mlsys/model-mart.git",
    install_requires=[
        'minio>=7.1.16',
        'Requests>=2.31.0',
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
