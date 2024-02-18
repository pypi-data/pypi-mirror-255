import argparse
import subprocess
import yaml

def install_package(package):
    subprocess.run(["apt-get", "install", "-y", package])

def enable_service(service):
    subprocess.run(["systemctl", "enable", service])
    subprocess.run(["systemctl", "start", service])

def read_spoink_file(file_path):
    with open(file_path, 'r') as file:
        spoink_data = yaml.safe_load(file)
        packages = spoink_data.get('packages', [])
        services = spoink_data.get('services', [])

        for package in packages:
            install_package(package)

        for service in services:
            enable_service(service)

def main():
    parser = argparse.ArgumentParser(description='Spoink - Custom Linux configuration tool')
    parser.add_argument('-i', '--input', help='Specify the path to the .spoink file', required=True)
    args = parser.parse_args()

    spoink_file = args.input
    read_spoink_file(spoink_file)

if __name__ == "__main__":
    main()
