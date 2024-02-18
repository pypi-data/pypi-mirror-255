import setuptools
PACKAGE_NAME = "dialog-workflow-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0.75', # https://pypi.org/project/dialog-workflow-local/
    author="Circles",
    author_email="info@circle.life",
    description="PyPI Package for dialog workflow",
    long_description="This is a package for running the dialog workflow",
    long_description_content_type="text/markdown",
    url="https://github.com/javatechy/dokr",
     packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    classifiers=[
        "Programming Language :: Python :: 3",
         "License :: Other/Proprietary License",
         "Operating System :: OS Independent",
    ],
        install_requires=["python-dotenv>=1.0.0",
"variable_local>=0.0.43"]
)
