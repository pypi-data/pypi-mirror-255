from setuptools import setup, find_packages
import time

setup(
    name="moyanlib",
    version="1.5." + str(int(time.time())),
    description="莫颜的个人python函数包",
    author="MoYan",
    packages=find_packages(),
    install_requires=[
        # 添加你的依赖库
        "requests",
        "psutil",
        "click",
        "rsa",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    # 添加命令
    entry_points={"console_scripts": ["moyancli = moyanlib.cli:cli"]},
)
