import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


def _clean_version():
    """
    This function was required because scm was generating developer versions on
    GitHub Action.
    """
    def get_version(version):
        return str(version.tag)
    def empty(version):
        return ''

    return {'local_scheme': get_version, 'version_scheme': empty}


setuptools.setup(
    name="pollination-streamlit-io",
    use_scm_version=_clean_version,
    setup_requires=['setuptools_scm'],
    author="Ladybug Tools",
    author_email="info@ladybug.tools",
    description="Pollination input/output components for Streamlit",
    long_description="Pollination input/output components for Streamlit to use with pollination apps",
    long_description_content_type="text/plain",
    url="https://github.com/pollination/pollination-streamlit-io",
    packages=setuptools.find_packages(exclude=["examples/*"]),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=requirements,
    classifiers=[],
    license="Apache-2.0 License"
)
