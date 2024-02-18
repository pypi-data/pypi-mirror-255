from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='gerenciamento_software',
    version='2.0.1',
    license='MIT License',
    author='George Júnior',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='ctt.georgejr@gmail.com',
    keywords='gerenciamento de software',
    description=u'Conjunto De Ferramentas Para Gerenciar Um Software',
    packages=['gerenciamento_software'],
    install_requires=['mysql-connector-python','colorama','psutil',],)
