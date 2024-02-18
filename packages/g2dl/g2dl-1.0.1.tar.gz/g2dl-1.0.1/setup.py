from setuptools import setup, find_packages
import g2dl

requirements = [
    'torch==2.2.0',
    'torchvision==0.17.0'
]

setup(
    name='g2dl',
    version=g2dl.__version__,
    python_requires='>=3.8',
    author='chenlh',
    author_email='gavnlhchen@gmail.com',
    url='https://github.com/chenlehua/network',
    description="Gavin's Deep Learning functions",
    license='MIT',
    packages=find_packages(),
    zip_safe=True,
    install_requires=requirements,
)
