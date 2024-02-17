from setuptools import setup, find_packages

setup(
	name='granloader',
    version='2.4.33',
	packages=find_packages(),
	install_requires=[
		'yt-dlp==2023.12.30',
		'ffmpeg-python==0.2.0',
		'ffmpeg==1.4'
	],
	entry_points={
        'console_scripts': [
            'granloader-play=granloader:play_all'
		]
	}
)