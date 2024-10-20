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
- Basic familiarity with the command line on Linux.

## Installation

1. **Download the Script**

   Clone this repository or download the `bluetooth-dual-boot.py` script directly:

   ```bash
   wget https://raw.githubusercontent.com/nbanks/bluetooth-dualboot/refs/heads/main/bluetooth-dualboot.py
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

#### Using `chntpw` on Linux

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
   cd <DeviceMAC>   # Replace with your device's MAC address (e.g., for a mouse or keyboard)
   hex LTK
   hex KeyLength
   hex ERand
   hex EDIV
   hex IRK
   hex CSRK
   hex CSRKInbound
   ```

   *Note: If `ControlSet001` does not exist, try `CurrentControlSet`.*

   Record the output of each `hex` command; you will need this information when running the script.

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
   - CSRKInbound (optional)

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
This script helps convert Bluetooth keys from Windows to Linux format.

It will not modify any files, but will provide output for you to copy and paste.

# Example: How to extract Bluetooth keys from the Windows registry using 'chntpw'
# Use the hex value with spaces as shown in Windows registry (e.g. 'C1 22 E9 8B 71 DA 90 C9 45 0E EC 40 52 94 DE 49')

sudo chntpw -e /win/Windows/System32/config/SYSTEM
cd \ControlSet001\Services\BTHPORT\Parameters\Keys
ls
cd <AdapterMAC>  # Replace with your adapter's MAC address
cd <DeviceMAC>  # Replace with your device's MAC address (e.g., for a mouse or keyboard)
hex <DeviceMAC>

# Extract values for the following keys:
hex LTK
hex KeyLength
hex ERand
hex EDIV
hex IRK
hex CSRK
hex CSRKInbound

Enter the device's MAC address (hexadecimal, no separators, e.g., '60abd2916ef6'):
> d11b1261da93
Formatted MAC address for use in directory: D0:1B:12:61:DA:93
Please enter the following keys as extracted from the Windows registry.
If a key is not available or not required, just press Enter to skip.

Enter LTK (or LinkKey from hex <DeviceMAC>):
> C9 96 D4 9E B2 D7 8C E9 A4 69 94 BF E3 5A 71 18
Enter KeyLength (DWORD in hex, e.g., '10 00 00 00' for 16):
> 10
Enter ERand (QWORD in hex, 8 bytes):
> 3C C0 BE 45 CC 73 1F F0
Enter EDIV (DWORD in hex, 4 bytes):
> 5B 6B 00 00
Enter IRK:
> 24 48 7C 1F 86 98 48 E3 9E 1B F2 59 96 CF FA 9B
Enter CSRK:
> 6D 1F A4 42 06 25 7B BE A1 C3 DB A0 8D 47 E4 59
Enter CSRKInbound (optional, press Enter to skip):
> 30 29 53 11 DB F9 57 2C FA 8F FD E0 4B 36 F1 E9
Warning: Expected 4 bytes, got 1 bytes.

Processing values...

You can try the following outputs in your 'info' file:
-----------------------------------------------------

=== Standard Processing ===

[IdentityResolvingKey]
Key=24487C1F869848E39E1BF25996CFFA9B

[LongTermKey]
Key=C996D49EB2D78CE9A46994BFE35A7118
EncSize=16
EDiv=27483
Rand=17302675614561386556
Authenticated=0

[LocalSignatureKey]
Key=6D1FA44206257BBEA1C3DBA08D47E459
Counter=0
Authenticated=false

[RemoteSignatureKey]
Key=30295311DBF9572CFA8FFDE04B36F1E9
Counter=0
Authenticated=false

=== Alternative Processing (Reversed Octets) ===

[IdentityResolvingKey]
Key=9BFACF9659F21B9EE34898861F7C4824

-----------------------------------------------------

Info file: /var/lib/bluetooth/*/D1:1B:12:61:DA:93/info

Remember to restart the Bluetooth service after updating the 'info' file:
sudo systemctl restart bluetooth
```

## Notes

- **Compatibility**: This script should work with most Python 3 versions.
- **Safety**: The script does not modify any system files automatically; you need to manually copy the output to your `info` file.
- **Backup**: Always back up your existing `info` files before making changes.
- **Permissions**: You might need to run the script and edit files with `sudo` to have the necessary permissions.
- **Restart Required**: Remember to restart the Bluetooth service after updating the `info` file.

## References
- [Arch Linux Wiki: Bluetooth - Dual Boot Pairing](https://wiki.archlinux.org/title/Bluetooth#Dual_boot_pairing)
- [StackExchange Thread: Bluetooth pairing on dual-boot of Windows & Linux Mint/Ubuntu: Stop having to pair each time](https://unix.stackexchange.com/questions/255509/bluetooth-pairing-on-dual-boot-of-windows-linux-mint-ubuntu-stop-having-to-p)
- [bt-dualboot GitHub repository (does not support LE)](https://github.com/x2es/bt-dualboot)

## License

This project is licensed under the GNU General Public License v3.0.

This script aims to simplify maintaining Bluetooth device pairings across dual-boot systems. By following the instructions and using the script, you should be able to avoid the hassle of re-pairing your devices every time you switch between Windows and Linux.

If you encounter issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

### Note to Users
- Ensure that you comply with the licensing and usage terms of any third-party tools (like `chntpw`) used in this process.
- Be cautious when handling system files and the Windows registry to avoid unintentional damage to your system.
