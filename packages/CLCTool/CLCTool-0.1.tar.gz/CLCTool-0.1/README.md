---

# CLCTool Documentation

## Introduction

Welcome to CLCTool, a powerful and customizable Linux configuration tool designed for flexible system setup and deployment.

### Features

- Modular architecture for maximum scalability and customization.
- Dynamic loading of user-defined modules.
- User-defined functions (UDFs) for encapsulating complex logic.
- Conditional task execution and interactive prompts.
- Seamless integration with the Unlicense license.

## Installation

### Prerequisites

- Python 3.6 or higher

### Instructions

1. Clone the CLCTool repository:

    ```bash
    git clone https://github.com/SpoinkOSDevs/CLCTool.git
    ```

2. Install requirements

    ```bash
    sudo pip install -r ./requirements.txt --break-system-packages
    ```

4. Change into the CLCTool directory:

    ```bash
    cd CLCTool
    ```

5. Run CLCTool with your desired configuration:

    ```bash
    sudo python clctool.py -m path/to/modules -o module1,module2 -p your_profile -v your_version
    ```

    Replace `path/to/modules` with the path to your module files, `module1,module2` with the desired execution order, `your_profile` with the chosen profile, and `your_version` with the desired version.

## Usage

CLCTool provides a simple command-line interface for running your customized installation process. The tool supports various commands and options to tailor the deployment according to your needs.

```bash
 sudo python clctool.py -m path/to/modules -o module1,module2 -p your_profile -v your_version
```

- `-m` or `--modules`: Specify the paths to module .spoink files separated by a comma.
- `-o` or `--order`: Specify the order in which modules should be executed, separated by a comma.
- `-p` or `--profile`: Specify the profile to use.
- `-v` or `--version`: Specify the version.

## Configuration

### Module Configuration

Modules are the building blocks of CLCTool. Each module is defined in a `.spoink` file containing tasks, UDFs, and configurations.

```yaml
tasks:
  - command: echo "Running pre-install commands for {profile} version {version}"
  - install_package: nginx
  - enable_service: nginx
  - configure_firewall:
      - "{profile}_port/tcp"
      - "443/tcp"
  - prompt: "Enter the domain for the website: "
    parameter: "domain"
  - udf: custom_udf
  - command: echo "Running post-install commands for {profile} with domain {domain}"
```

### User-Defined Functions (UDFs)

UDFs allow encapsulating complex logic and reusing it across different parts of the installation process.

```python
def custom_udf(parameters):
    print(f"Running a custom UDF with parameters: {parameters}")
```

## License

CLCTool is released under the Unlicense license. See the [LICENSE](https://SpoinkOSDevs/CLCTool/LICENSE.md) file for more details.

## Issue Tracker Link

- GitHub Issues: [CLCTool Issues](https://github.com/SpoinkOSDevs/CLCTool/issues)

---
