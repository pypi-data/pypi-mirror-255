from setuptools import setup



from setuptools import setup, find_packages

setup(
    name='taowa',
    version='1.0.5',
    description='建议使用python3.9版本,高版本可能需要自己提前安装一些模块',
    long_description_content_type='text/markdown',
    author='陈炳强',
    author_email='99396686@qq.com',
    packages=find_packages(),
    package_data={
        'taowa': ['Skin/*'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    # 如果有依赖包，可以在此处添加
    install_requires=[
        'wxPython',
        'web3',
        'requests',
        'PyExecjs',
        'pywin32',
    ],
)