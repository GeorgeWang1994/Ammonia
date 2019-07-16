from setuptools import setup, find_packages

requirements = [
    'alembic==1.0.10',
    'amqp==2.4.2',
    'Click==7.0',
    'decorator==4.4.0',
    'itsdangerous==1.1.0',
    'kombu==4.5.0',
    'pbr==5.2.0',
    'six==1.12.0',
    'SQLAlchemy==1.3.3',
    'SQLAlchemy-Utils==0.34.0',
    'sqlparse==0.3.0',
    'Tempita==0.5.2',
    'vine==1.3.0',
    'PyMySQL==0.9.3',
    'redis==3.2.1',
]

setup(
    name="Ammonia",
    version="0.0.13",
    description="task queue",
    author="george wang",
    author_email="georgewang1994@163.com",
    url="https://github.com/GeorgeWang1994/Ammonia",
    install_requires=requirements,
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    entry_points={
        'console_scripts': [
            'ammonia=ammonia.command.start:start',
        ],
    },
)
