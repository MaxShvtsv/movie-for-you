from setuptools import setup, find_packages

setup(
    name='movie_for_you',
    version='1.0',
    description='Telegram bot for movie recommendations and statistics',
    author='Max Shevtsov, Koretz Oleksandr, Baida Oleksiy',
    author_email='max.shvtsv@gmail.com',
    url='https://github.com/MaxShvtsv/movie-for-you',
    packages=find_packages(),
    install_requires=[
        'pytelegrambotapi>=4.12.0',
        'matplotlib>=3.5.0',
        'python-dotenv==1.0.1',
        'bs4==0.0.2'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
    entry_points={
        'console_scripts': [
            'telebot-movie=your_bot_module:main',
        ]
    },
)
