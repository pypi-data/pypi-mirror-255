from setuptools import setup

setup(
    name='ict_szpu',
    version='1.0.7',
    authors='陈向学',
    description='深职院智能ict三维编程拓展组件',
    packages=["ict_szpu"],
    include_package_data=True,
    install_requires=[
        'websocket-client'
    ]
)