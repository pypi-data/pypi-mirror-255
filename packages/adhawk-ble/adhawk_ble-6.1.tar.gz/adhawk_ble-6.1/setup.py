
import setuptools

setuptools.setup(
    name='adhawk_ble',
    version='6.1',
    description='AdHawk Microsystems SDK',
    url='http://www.adhawkmicrosystems.com/',
    author='AdHawk Microsystems',
    author_email='info@adhawkmicrosystems.com',
    packages=['adhawkapi.frontend_ble'],
    license="Proprietary",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=[
        'adhawk>=6.1',
        'bleak'
    ],
)
