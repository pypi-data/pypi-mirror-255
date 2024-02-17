from setuptools import setup, find_packages

setup(
    name='ERTool',
    version='0.2.4',
    author='Tongyue Shi',
    author_email='tyshipku@gmail.com',
    packages=find_packages(),
    description='A Python package for simple and efficient implementation of Evidential Reasoning (ER) methods.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        "numpy",
        "matplotlib",
        "pandas",
        # 其他依赖
    ],
    classifiers=[
        # 分类器
    ],
)
