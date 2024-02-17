import os

from setuptools import find_packages, setup


def get_version():
    basedir = os.path.dirname(__file__)
    try:
        with open(os.path.join(basedir, 'fcm_notifier/version.py')) as f:
            locals = {}
            exec(f.read(), locals)
            return locals['VERSION']
    except FileNotFoundError:
        raise RuntimeError('No version info found.')


def get_requirements():
    basedir = os.path.dirname(__file__)
    try:
        with open(os.path.join(basedir, 'requirements.txt')) as f:
            return f.readlines()
    except FileNotFoundError:
        raise RuntimeError('No requirements info found.')


def _read(file_path):
    with open(file_path, 'r') as infile:
        return infile.read()


setup(
    name='fcm-notifier',
    version=get_version(),
    license='MIT',
    author='BARS Group',
    description='Сервис отправки push-уведомлений через FCM',
    author_email='education_dev@bars-open.ru',
    packages=find_packages(exclude=('tests', 'tests.*')),
    install_requires=get_requirements(),
    long_description=_read('README.md'),
    long_description_content_type='text/markdown',
    zip_safe=False,
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'fcm-notifier = fcm_notifier.cli:main',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Russian',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
