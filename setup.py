"""
Flask-Mail
----------

A Flask extension for sending email messages.

Please refer to the online documentation for details.

Links
`````

* `documentation <http://packages.python.org/Flask-Mail>`_
* `development version
  <http://bitbucket.org/danjac/flask-mail/get/tip.gz#egg=Flask-Mail-dev>`_
"""
from setuptools import setup


setup(
    name='Flask-Mail',
    version='0.7.0',
    url='http://bitbucket.org/danjac/flask-mail',
    license='BSD',
    author='Dan Jacob',
    author_email='danjac354@gmail.com',
    description='Flask extension for sending email',
    long_description=__doc__,
    py_modules=[
        'flask_mail'
    ],
    test_suite='nose.collector',
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'blinker',
    ],
    tests_require=[
        'nose',
        'blinker',
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
