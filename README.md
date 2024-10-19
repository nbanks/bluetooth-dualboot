# Bluetooth Dual Boot Pairing Helper

A Python script to transfer Bluetooth pairing keys from Windows to Linux, enabling seamless Bluetooth device usage when dual-booting between Windows and Linux. This script supports both Bluetooth Low Energy (LE) and classic Bluetooth devices.

## Table of Contents
- [Background](#background)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Notes](#notes)
- [References](#references)
- [License](#license)

## Background

When dual-booting Windows and Linux, you might find that you need to re-pair your Bluetooth devices every time you switch operating systems. This occurs because each OS maintains its own set of Bluetooth pairing keys, making it impossible for devices to recognize both systems simultaneously.

This script simplifies the process of transferring Bluetooth pairing keys from Windows to Linux, allowing your devices to stay paired across both operating systems without the need for re-pairing.

The solution draws inspiration from the StackExchange thread:

- Bluetooth pairing on dual-boot of Windows & Linux Mint/Ubuntu: Stop having to pair each time

## Features

- Supports both Bluetooth LE and classic Bluetooth devices.
- Extracts Bluetooth pairing keys from the Windows registry.
- Converts keys into the format required by the Linux Bluetooth stack.
- Provides step-by-step instructions for key extraction and script usage.
- Outputs ready-to-use configuration sections for the Linux Bluetooth info file.
- Designed to be cut-and-paste friendly, minimizing errors and streamlining the process.
- Compatible with most Python versions (Python 3 recommended).

## Prerequisites

- Python 3 installed on your Linux system.
- Access to the Windows registry files (from a Windows installation on the same machine).
- The `chntpw` utility installed on Linux to read the Windows registry:

  ```bash
  sudo apt-get install chntpw  # Ubuntu/Debian
  sudo pacman -S chntpw        # Arch Linux
  ```
- Basic familiarity with the command line on both Windows and Linux.

## Installation

1. **Download the Script**

   Clone this repository or download the `bluetooth-dual-boot.py` script directly:

   ```bash
   wget https://raw.githubusercontent.com/yourusername/yourrepository/main/bluetooth-dual-boot.py
   ```

2. **Make the Script Executable**

   ```bash
   chmod +x bluetooth-dual-boot.py
   ```

3. **(Optional) Place the Script in Your PATH**

   To make it easier to run, you can place the script in a directory in your PATH, such as `/usr/local/bin`:

   ```bash
   sudo mv bluetooth-dual-boot.py /usr/local/bin/
   ```

## Usage

### Step 1: Extract Bluetooth Keys from Windows Registry

#### Option A: Using `chntpw` on Linux (Recommended)

1. **Mount Your Windows Partition**

   Identify your Windows system partition:

   ```bash
   sudo fdisk -l
   ```

   Create a mount point and mount the partition (replace `/dev/sdX` with your partition identifier):

   ```bash
   sudo mkdir /mnt/windows
   sudo mount -t ntfs-3g -o ro /dev/sdX /mnt/windows
   ```

2. **Navigate to the Windows Registry System Hive**

   ```bash
   cd /mnt/windows/Windows/System32/config
   ```

3. **Open the Windows Registry with `chntpw`**

   ```bash
   sudo chntpw -e SYSTEM
   ```

4. **Extract the Required Keys**

   In the `chntpw` interactive console, run the following commands:

   ```
   cd ControlSet001\Services\BTHPORT\Parameters\Keys
   ls
   cd <AdapterMAC>  # Replace with your adapter's MAC address
   ls
   cd <DeviceMAC>   # Replace with your device's MAC address
   ls
   hex LTK
   hex KeyLength
   hex ERand
   hex EDIV
   hex IRK
   hex CSRK
   ```

   *Note: If `ControlSet001` does not exist, try `CurrentControlSet`.*

   Record the output of each `hex` command; you will need this information when running the script.

#### Option B: Using Windows (Alternative)

1. **Boot into Windows**
2. **Use `regedit` or `psexec` to Access the Registry**

   - Download `psexec` from Microsoft Sysinternals.
   - Open a command prompt as Administrator.
   - Run `psexec -s -i regedit.exe`.

3. **Navigate to the Keys**

   Go to `HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Services\BTHPORT\Parameters\Keys`.

4. **Export the Necessary Keys**

   Locate the keys associated with your Bluetooth adapter and device and note down the values of the following:
   - LTK
   - KeyLength
   - ERand
   - EDIV
   - IRK
   - CSRK

### Step 2: Run the Script and Input the Keys

1. **Run the Script**

   ```bash
   ./bluetooth-dual-boot.py
   ```

2. **Follow the Prompts**

   The script will guide you through entering the extracted keys. It will ask for:
   - Device's MAC address (no separators, e.g., `D01B1261DA93`)
   - LTK
   - KeyLength
   - ERand
   - EDIV
   - IRK
   - CSRK

3. **Copy the Output**

   The script will generate the sections you need to add to your Linux Bluetooth info file, which is typically located at:

   ```bash
   /var/lib/bluetooth/<AdapterMAC>/<DeviceMAC>/info
   ```

### Step 3: Update the `info` File

1. **Backup the Existing `info` File**

   ```bash
   sudo cp /var/lib/bluetooth/<AdapterMAC>/<DeviceMAC>/info /var/lib/bluetooth/<AdapterMAC>/<DeviceMAC>/info.backup
   ```

2. **Edit the `info` File**

   ```bash
   sudo nano /var/lib/bluetooth/<AdapterMAC>/<DeviceMAC>/info
   ```

3. **Paste the Output from the Script**

   Replace or add the sections provided by the script into the `info` file.

4. **Save and Exit**

### Step 4: Restart the Bluetooth Service

```bash
sudo systemctl restart bluetooth
```

### Step 5: Test the Device

Your Bluetooth device should now work seamlessly on Linux without needing to re-pair every time you switch from Windows.

## Examples

Example Run:

```bash
$ ./bluetooth-dual-boot.py
This script will help you convert Bluetooth keys from Windows registry to Linux format.

Enter the device's MAC address (hexadecimal, no separators, e.g., '60abd2916ef6'):
> C0B51234ABCD
Formatted MAC address for use in directory: C0:B5:12:34:AB:CD
Info file: /var/lib/bluetooth/*/C0:B5:12:34:AB:CD/info

Please enter the following keys as extracted from the Windows registry.
Only the LinkKey is required for some devices.

If a key is not available or not required, just press Enter to skip.

Enter LTK (or LinkKey from hex <DeviceMAC>):
> 9A B7 41 6E F3 A1 C9 2E 7F 22 11 0C 4D 5B 63 27
Enter KeyLength (DWORD in hex, e.g., '10 00 00 00' for 16):
> 10 00 00 00
Enter ERand (QWORD in hex, 8 bytes):
> A9 C4 F3 12 77 65 AB 90
Enter EDIV (DWORD in hex, 4 bytes):
> 3D 8A 00 00
Enter IRK:
> 87 A4 32 1F 45 68 73 A3 92 1C F5 49 71 CF FA 9B
Enter CSRK:
> 5D 1B 94 62 09 25 7B BE 91 C3 DB A2 8D 77 E4 59
```

## Notes

- **Compatibility**: This script should work with most Python 3 versions.
- **Safety**: The script does not modify any system files automatically; you need to manually copy the output to your `info` file.
- **Backup**: Always back up your existing `info` files before making changes.
- **Permissions**: You might need to run the script and edit files with `sudo` to have the necessary permissions.
- **Restart Required**: Remember to restart the Bluetooth service after updating the `info` file.

## References
- StackExchange Thread: Bluetooth pairing on dual-boot of Windows & Linux Mint/Ubuntu: Stop having to pair each time
- Arch Linux Wiki: Bluetooth - Dual Boot Pairing
- `chntpw` Documentation: CHNTPW Registry Editor

## License

This project is licensed under the GNU General Public License v3.0.

This script aims to simplify maintaining Bluetooth device pairings across dual-boot systems. By following the instructions and using the script, you should be able to avoid the hassle of re-pairing your devices every time you switch between Windows and Linux.

If you encounter issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

### Note to Users
- Ensure that you comply with the licensing and usage terms of any third-party tools (like `chntpw` or `psexec`) used in this process.
- Be cautious when handling system files and the Windows registry to avoid unintentional damage to your system.
