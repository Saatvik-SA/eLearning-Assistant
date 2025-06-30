import pkg_resources

# Load the requirements file
with open("requirements.txt") as f:
    required = pkg_resources.parse_requirements(f)
    required_packages = [str(req) for req in required]

# Get all currently installed packages
installed_packages = {pkg.key for pkg in pkg_resources.working_set}

# Check each required package
missing_packages = []
for pkg in required_packages:
    pkg_name = pkg.split("==")[0] if "==" in pkg else pkg.lower()
    if pkg_name.lower() not in installed_packages:
        missing_packages.append(pkg)

if missing_packages:
    print("❌ Missing packages:")
    for pkg in missing_packages:
        print(" -", pkg)
else:
    print("✅ All packages are installed!")
