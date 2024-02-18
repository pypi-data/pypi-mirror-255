from setuptools import setup, find_packages

setup(
    name='slack_error_notification',
    version='0.1.1',    
    description='A Slack notification handler that send error messages to a Slack channel',
    author='Gordon Oh',
    author_email='gordonoh@yahoo.com.sg',
    license='BSD 2-clause',
    packages=find_packages(),
    install_requires=['slack_sdk', 'Flask==2.0.1', 'Flask-Log-Request-ID'],
    url ="",
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)