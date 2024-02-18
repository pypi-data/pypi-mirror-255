from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='auto_duo',
    version='1.0.0',
    author='Tiancheng Jiao',
    author_email='jtc1246@outlook.com',
    url='https://github.com/jtc1246/auto-duo',
    description='Autotamically pass each duo push, no need to click on cellphone.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['auto_duo'],
    install_requires=['myBasics'],
    python_requires='>=3.9',
    platforms=["all"],
    license='GPL-2.0 License'
)
