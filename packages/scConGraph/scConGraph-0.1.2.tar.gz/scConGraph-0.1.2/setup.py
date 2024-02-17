from setuptools import setup, find_packages

setup(
    name='scConGraph',  # 包名
    version='0.1.2',  # 版本
    description="a package for sc-RNA",  # 包简介
    long_description=open('README.md').read(),  # 读取文件中介绍包的详细内容
    include_package_data=True,  # 是否允许上传资源文件
    author='XinQi Li',  # 作者
    author_email='lxq19@mails.tsinghua.edu.cn',  # 作者邮件
    maintainer='XinQi Li',  # 维护者
    maintainer_email='lxq19@mails.tsinghua.edu.cn',  # 维护者邮件
    license='MIT License',  # 协议
    url='',  # github或者自己的网站地址
    packages=find_packages('scConGraph'),  # 包的目录
    package_dir={'': 'scConGraph'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',  # 设置编写时的python版本
    ],
    python_requires='>=3.7',  # 设置python版本要求
    install_requires=['networkx','matplotlib','numpy','pandas','seaborn','scipy','scanpy','time'],  # 安装所需要的库
   # entry_points={
   #    'console_scripts': [
   #         ''],
   #},  # 设置命令行工具(可不使用就可以注释掉)

)