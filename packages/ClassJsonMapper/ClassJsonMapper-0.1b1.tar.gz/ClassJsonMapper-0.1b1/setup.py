from setuptools import setup, find_packages

# 项目元数据
metadata = {
    'name': 'ClassJsonMapper',  # 项目名称
    'version': '0.1b1',         # 版本号
    'description': 'ClassJsonMapper 是一个易于使用的Python库，旨在简化JSON数据与类对象之间的映射和转换过程。通过自定义类方法，它使得处理JSON文件变得直观、安全且高效。' + 
    "\nClassJsonMapper is an easy-to-use Python library designed to simplify the mapping and transformation process between JSON data and class objects. By using custom class methods, it makes handling JSON files intuitive, secure, and efficient.",  # 简短描述
    'long_description': open('README.md', encoding='utf-8').read(),  # 可以读取 README 文件内容作为详细描述
    'long_description_content_type': 'text/markdown',  # 如果使用 Markdown 格式的 README
    'author': 'PYmili',      # 作者姓名
    'author_email': 'mc2005wj@163.com',   # 作者邮箱
    'url': 'https://github.com/PYmili/ClassJsonMapper',  # 项目主页
    'license': 'MIT',           # 许可证类型
    'classifiers': [            # 类别列表，用于PyPI展示
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    'keywords': ['json', 'mapping', 'data serialization', 'object mapping'],  # 关键字列表
    'packages': find_packages(exclude=['tests', 'docs', 'venv']),  # 自动查找包含__init__.py的子目录作为包
    'install_requires': [],# 项目依赖项列表
    'extras_require': {            # 可选依赖项
        # 'dev': [
        #     'pytest>=6.0',
        #     'flake8',
        # ],
        # 'docs': [
        #     'sphinx',
        #     'recommonmark',
        # ],
    },
}

# 执行 setup 函数来定义项目结构和生成所需的打包命令
setup(**metadata)