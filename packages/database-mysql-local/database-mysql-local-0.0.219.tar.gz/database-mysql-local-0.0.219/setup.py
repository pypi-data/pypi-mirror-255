import setuptools

PACKAGE_NAME = "database-mysql-local"
package_dir = PACKAGE_NAME.replace("-", "_")
# TODO: we are migrating from circles_local_database_python to database_mysql_local
#  but in the meantime we want to keep both names
old_name = "circles_local_database_python"

setuptools.setup(
    name=PACKAGE_NAME,  # https://pypi.org/project/database-mysql-local
    version='0.0.219',
    author="Circles",
    author_email="info@circles.life",
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    packages=[package_dir, old_name],
    package_dir={package_dir: f'{package_dir}/src', old_name: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    long_description="Database MySQL Local",
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "mysql-connector-python>=8.3.0",  # https://pypi.org/project/mysql-connector-python/
        "url_remote>=0.0.68",  # https://pypi.org/project/url-remote/
        "logger-local>=0.0.102",  # https://pypi.org/project/logger-local/
        "database-infrastructure-local>=0.0.19",  # https://pypi.org/project/database-infrastructure-local/
        "language-remote>=0.0.8",  # https://pypi.org/project/language-local/
        "sql-to-code-local>=0.0.2"  # https://pypi.org/project/sql-to-code-local/
    ]
)
