import argparse
import sys
import semver


parser = argparse.ArgumentParser()
parser.add_argument("-m", "--minor", dest="minor", type=bool)
parser.add_argument("-p", "--patch", dest="patch", type=bool)
args = parser.parse_args()

filePath = f"VERSION"

# Read the current version from the VERSION file
with open(filePath, "r") as f:
    version = f.read().strip()
    version = semver.Version.parse(version)
    print("currrent version ", version)

# Increment the patch version
if args.patch:
    new_version = version.bump_patch()
    with open(filePath, "w") as f:
        f.write(str(new_version))
        print("new patch version ", new_version)

# Increment the miner version
if args.minor:
    new_version = version.bump_minor()
    with open(filePath, "w") as f:
        f.write(str(new_version))
        print("new minor version ", new_version)
