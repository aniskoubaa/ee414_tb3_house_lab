from glob import glob

from setuptools import setup

package_name = 'ee414_house_lab'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/worlds', glob('worlds/*.sdf')),
        ('share/' + package_name + '/rviz', glob('rviz/*.rviz')),
        ('share/' + package_name + '/config', glob('config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Anis Koubaa',
    maintainer_email='anis.koubaa@gmail.com',
    description='EE 414 hands-on lab: TurtleBot3 in the House world.',
    license='MIT',
    entry_points={
        'console_scripts': [
            # Lab 1 -- the laser scanner and a robot that wanders safely
            'l1_scan_reader = ee414_house_lab.l1_scan_reader:main',
            'l1_wander = ee414_house_lab.l1_wander:main',
            # Lab 2 -- TF2: where is that object?
            'l2_object_finder = ee414_house_lab.l2_object_finder:main',
            # Lab 3 -- go to a goal, then the Bug algorithm
            'l3_go_to_goal = ee414_house_lab.l3_go_to_goal:main',
            'l3_bug = ee414_house_lab.l3_bug:main',
            # Tools you do not edit
            'lab_monitor = ee414_house_lab.lab_monitor:main',
            'l2_check = ee414_house_lab.l2_check:main',
        ],
    },
)
