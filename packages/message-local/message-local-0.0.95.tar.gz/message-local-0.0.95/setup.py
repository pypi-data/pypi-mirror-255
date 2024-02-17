import setuptools

PACKAGE_NAME = "message-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,  # https://pypi.org/project/message-local
    version='0.0.95',
    author="Circles",
    author_email="info@circles.life",
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    long_description="message-local",
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=["item-local>=0.0.4",  # https://pypi.org/project/item-local/
                      "api-management-local>=0.0.39",  # https://pypi.org/project/api-management-local/
                      "language-local",
                      "variable-local",
                      "logger-local",
                      "database-mysql-local>=0.0.199",
                      "star-local",
                      "profiles-local>=0.0.50",
                      ]
)
