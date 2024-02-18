import pathlib
import setuptools

setuptools.setup(
    name="enigma_ai", 
    version="0.2.0",
    description="Tools for simple and efficient training of LLMs for code generation",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://www.enigma-ai.com/", 
    author="Enigma AI",
    license="MIT",
    project_urls={
        "Source": "https://github.com/ammarnasr/Customizable-Code-Assistant",
        "Documentation": "https://enigma-ai.readthedocs.io/",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",  
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.7",
    install_requires=[
    ],  
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "enigma_ai=enigma_ai.__main__:main"
        ]
    },
)