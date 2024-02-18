from setuptools import find_packages, setup 

setup(
    name="binance_info",
    version="2.0",
    packages=find_packages(),
    install_requires=["requests", "qrcode", "pyotp"]
)