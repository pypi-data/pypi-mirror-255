from setuptools import setup

setup(
    name='auto_duo',
    version='0.9.1',
    author='Tiancheng Jiao',
    author_email='jtc1246@outlook.com',
    url='https://github.com/jtc1246/auto-duo',
    description='Autotamically pass each duo push, no need to click on cellphone.',
    packages=['auto_duo'],
    install_requires=['myBasics'],
    python_requires='>=3',
    platforms=["all"],
    license='GPL-2.0 License'
)
