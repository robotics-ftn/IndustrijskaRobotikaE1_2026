from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'robot_move'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        # Launch
        (os.path.join("share", package_name, "launch"), glob(os.path.join("launch", "*.launch.py"))),

        # Config
        (os.path.join("share", package_name, "config"), glob(os.path.join("config", "*.yaml"))),

    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dexter',
    maintainer_email='lazarmilic2@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'robot_move = robot_move.robot_move:main'
        ],
    },
)
