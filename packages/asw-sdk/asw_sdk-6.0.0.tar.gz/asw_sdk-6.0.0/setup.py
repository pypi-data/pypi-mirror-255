from distutils.core import setup

setup(
    name='asw_sdk',  # How you named your package folder (MyLib)
    packages=['asw_sdk'],  # Chose the same as "name"
    version='6.0.0',  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='Thotnr ML client to interact with Thotnr Projects',  # Give a short description about your library
    author='Thotnr',  # Type in your name
    author_email='npm-admin@thotnr.com',  # Type in your E-Mail

    download_url='https://github.com/user/reponame/archive/v_01.tar.gz',  # I explain this later on
    keywords=['thotnr', 'ml', 'client'],  # Keywords that define your package best
    install_requires=[  # I get to this in a second
        'backoff',
        'requests',
    ],
    python_requires=">=3.7",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',  # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
