import setuptools
 
with open("README.md", 'r', encoding="utf8") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name="HDLRTool",
    version="0.1.1",
    author="hdlr",
    author_email="1079489986@qq.com",
    description="寒冬利刃的工具箱 handongliren(hdlr)'s toolbox",
    #long_description="寒冬利刃的工具箱\nhandongliren(hdlr)'s toolbox",
    long_description=long_description,
    # long_description_content_type="text/reStructuredText",
    url="https://gitee.com/handongliren",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",  # 3 - Alpha, 4 - Beta, 5 - Production/Stable
        
        "Topic :: Software Development :: Build Tools",
        
        "Programming Language :: Python :: 3.8",
        
        "License :: OSI Approved :: MIT License",
        
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
    py_modules=['program', 'web', 'pip_install'],
    install_requires = ['requests']
)