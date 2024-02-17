from setuptools import setup, find_packages

setup(
    name='xgame',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        # 依赖列表
    ],
    author='Next',
    author_email='xinshouit@outlook.com',
    license='MIT',
    description='A question-answer app',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/potato47/qa',
    classifiers=[
        # 分类器列表
    ],
    python_requires='>=3.6',
)