# """ See:
# https://github.com/mix1009/sdwebuiapi
# """

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")


setup(
    name="cross-border-mover",
    version="0.1.2",
    description="A Cross-border E-commerce Mover",
    # url="https://github.com/mix1009/sdwebuiapi",
    author="Zilu Chen",
    author_email="2822459649@qq.com",
    keywords="E-commercei, Amazon, stable-diffusion",
    packages=["cross_border_mover"],
    #packages=find_packages(),
    python_requires=">=3.11, <4",
    install_requires=[
                      'Pillow',
                      'boto3',
                      'webuiapi',
                      'numpy',
                      'pandas',
                      'selenium',
                      'amazon_mws',
                      'deep_translator',
                      'chromedriver_autoinstaller',
                      ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="MIT",
)
