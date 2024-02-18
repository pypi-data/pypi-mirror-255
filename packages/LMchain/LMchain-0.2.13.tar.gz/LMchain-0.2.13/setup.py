import setuptools
# with open("README.md", "r") as fh:
#     long_description = fh.read()
setuptools.setup(
    name="lmchain",
    version="0.2.13",
    author="xiaohuaWang",
    author_email="5847713@qq.com",
    description="LMchain package",
    long_description="A large chinese freelanguage chain tools,you can get free API from:open.bigmodel.cn",
    #long_description_content_type="text/markdown",
    url="https://github.com/virgo777/lmchain/",
    include_package_data=True,

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires=[
        'uvicorn>= 0.23.2',
        'fastapi>=0.108.0',
        'zhipuai>=2.0.1',
        "gradio", "requests","numpy"
    ],
    python_requires='>=3',
)
