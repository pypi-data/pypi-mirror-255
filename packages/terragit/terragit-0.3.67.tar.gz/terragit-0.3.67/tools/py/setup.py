from setuptools import setup
import semver


# Read the current version from the VERSION file
with open('VERSION', 'r') as f:
    current_version_string = f.read().strip()
    print(type(current_version_string))
# Strip the decimal point before parsing as an integer 
current_version = semver.Version.parse(current_version_string)
print("currrent version ",current_version)



# Increment the patch version
new_version = current_version.bump_patch()

with open('VERSION', 'w') as f:
    f.write(str(new_version))
print("new version ",new_version)

"""
setup(
    name='my-project',
    version=str(new_version),
    description='My awesome project',
    author='Your Name',
    author_email='youremail@example.com',
    url='https://github.com/your-username/my-project',
    packages=['my_project'],
)
"""
