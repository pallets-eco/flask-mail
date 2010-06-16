"""
flask-mail
----------

A Flask extension for sending email. 

Uses the Lamson mail framework.

"""
from setuptools import setup


setup(
    name='flask-mail',
    version='0.2',
    url='http://bitbucket.org/danjac/flask-mail',
    license='BSD',
    author='Dan Jacob',
    author_email='danjac354@gmail.com',
    description='Flask extension for sending email',
    long_description=__doc__,
    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'Lamson',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
