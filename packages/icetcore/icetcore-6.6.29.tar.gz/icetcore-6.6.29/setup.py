# -*- coding: utf-8 -*-
__author__ = 'ICE Technology'

import setuptools
# try:
#     from wheel.bdist_wheel import bdist_wheel as _bdist_wheel, get_platform

#     class bdist_wheel(_bdist_wheel):

#         def finalize_options(self):
#             _bdist_wheel.finalize_options(self)
#             if self.plat_name != "any":
#                 self.root_is_pure = False
#                 #plat_name = (self.plat_name or get_platform()).replace('-', '_').replace('.', '_')

# except ImportError:
#     bdist_wheel = None
setuptools.setup(
    name='icetcore',
    version="6.6.29",
    description='icetcore python api',
    author='zxlee',
    author_email='zxlee@icetech.com.cn',
    url='https://www.algostars.com.cn/',
    platform_system='Windows',
    packages=setuptools.find_packages(exclude=["icetcore.sample.*"]),
    install_requires=["comtypes==1.2.0","pytz== 2023.3"],#"psutil>=5.9.5"
    # python_requires=">=3.6",
    # cmdclass={'bdist_wheel': bdist_wheel},
    classifiers=[
        "Environment :: Win32 (MS Windows)",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        #"Operating System :: Microsoft :: Windows",
    ],
    include_package_data=True
)