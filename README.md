# Bluetooth Dual Boot Pairing Helper

A Python script to easily transfer Bluetooth pairing keys from Windows to Linux, enabling seamless device usage when dual-booting. Supports both Bluetooth Low Energy (LE) and classic Bluetooth. The script is safe to use as it does not modify any files directly.

## Table of Contents
- [Background](#background)
- [Quickstart](#quickstart)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Example Run](#example-run)
- [Notes](#notes)
- [References](#references)
- [License](#license)

## Background

When dual-booting Windows and Linux, you may need to re-pair Bluetooth devices each time you switch OS. This is due to both OSes having different sets of Bluetooth pairing keys. This script helps you transfer pairing keys from Windows to Linux, keeping devices paired across both systems.

## Quickstart

Run the script quickly with `curl` or `wget`:

```bash
curl -O https://raw.githubusercontent.com/nbanks/bluetooth-dualboot/refs/heads/main/bluetooth-dualboot.py
chmod +x bluetooth-dualboot.py
./bluetooth-dualboot.py
```

## Features

- Supports Bluetooth LE and classic devices.
- Extracts Bluetooth keys from Windows registry.
- Converts keys to Linux-compatible format.
- Provides step-by-step key extraction guidance.
- Outputs ready-to-use config for Linux Bluetooth info files.
- Python 3 recommended.

## Prerequisites

- Python 3 installed on Linux.
- Access to Windows registry files (from a Windows installation).
- `chntpw` to read Windows registry:
  
  ```bash
  sudo apt-get install chntpw  # Ubuntu/Debian
  sudo pacman -S chntpw        # Arch Linux
  ```

- Basic familiarity with Linux command line.

## Usage

### Step 1: Pair Device in Linux

1. **Boot into Linux** and pair your Bluetooth device as you normally would. This will generate the `/var/lib/bluetooth/<AdapterMAC>/<DeviceMAC>/info` file, which will be modified later.
2. Take Note of Adapter and Device MAC Addresses, though some devices change addresses whenever they're paired.  You need to find the correct info file and associate it with the MAC address from step 2.

### Step 2: Boot into Windows and Pair Device

1. **Boot into Windows** and pair the same Bluetooth device. This ensures that the device is properly registered in Windows and its pairing keys are stored in the registry.
2. To minimize confusion, you may keep other Bluetooth devices disabled or disconnected to easily locate the device in later steps.

### Step 3: Extract Bluetooth Keys from Windows Registry

#### Using `chntpw` on Linux

1. **Mount Windows Partition**

   ```bash
   sudo fdisk -l
   sudo mkdir /mnt/windows
   sudo mount -t ntfs-3g -o ro /dev/sdX /mnt/windows
   ```

2. **Navigate to Registry Hive**

   ```bash
   cd /mnt/windows/Windows/System32/config
   ```

3. **Open Registry with `chntpw`**

   ```bash
   sudo chntpw -e SYSTEM
   ```

4. **Extract Keys**

   Run commands to navigate to and extract Bluetooth keys. Leave this window open to cut-and-paste values:

   ```
   cd ControlSet001\Services\BTHPORT\Parameters\Keys
   ls
   cd <AdapterMAC>
   ls
   cd <DeviceMAC>
   hex LTK
   hex KeyLength
   hex ERand
   hex EDIV
   hex IRK
   hex CSRK
   hex CSRKInbound
   ```

   *Note: Try `CurrentControlSet` if `ControlSet001` is unavailable.*

### Step 4: Run the Script

```bash
./bluetooth-dualboot.py
```

The script will prompt for the extracted keys, generating output for the Linux Bluetooth info file. Typically, you will cut-and-paste from the registry to the script and cut-and-paste from the script to the info file.

### Step 5: Update the `info` File

Hint: The script will provide the location of the info file if you provide a MAC address.

1. **Backup Existing File**

   ```bash
   sudo cp /var/lib/bluetooth/<AdapterMAC>/<DeviceMAC>/info /var/lib/bluetooth/<AdapterMAC>/<DeviceMAC>/info.backup
   ```

2. **Edit the `info` File**

   ```bash
   sudo nano /var/lib/bluetooth/<AdapterMAC>/<DeviceMAC>/info
   ```

3. **Paste the Script Output**

4. **Save and Exit**

### Step 6: Restart Bluetooth Service

```bash
sudo systemctl restart bluetooth
```

### Step 7: Test Device

Device should now be paired on Linux. You should not have to put the device in pairing mode again because it was already paired in Windows.

## Example Run

```diff
- User entered data in red

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
-> d11b1261da93
Formatted MAC address for use in directory: D0:1B:12:61:DA:93
Please enter the following keys as extracted from the Windows registry.
If a key is not available or not required, just press Enter to skip.

Enter LTK (or LinkKey from hex <DeviceMAC>):
-> C9 96 D4 9E B2 D7 8C E9 A4 69 94 BF E3 5A 71 18
Enter KeyLength (DWORD in hex, e.g., '10 00 00 00' for 16):
-> 10
Enter ERand (QWORD in hex, 8 bytes):
-> 3C C0 BE 45 CC 73 1F F0
Enter EDIV (DWORD in hex, 4 bytes):
-> 5B 6B 00 00
Enter IRK:
-> 24 48 7C 1F 86 98 48 E3 9E 1B F2 59 96 CF FA 9B
Enter CSRK:
-> 6D 1F A4 42 06 25 7B BE A1 C3 DB A0 8D 47 E4 59
Enter CSRKInbound (optional, press Enter to skip):
-> 30 29 53 11 DB F9 57 2C FA 8F FD E0 4B 36 F1 E9
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

- **Safety**: The script doesn't modify files directly; users need to manually copy output to the `info` file.
- **Backup**: Always back up existing `info` files.
- **Permissions**: You may need `sudo` for file edits.
- **Restart Required**: Restart Bluetooth service after updating the `info` file.

## References
Supports LE:
- [Arch Linux Wiki: Bluetooth - Dual Boot Pairing](https://wiki.archlinux.org/title/Bluetooth#Dual_boot_pairing)

Does not support LE:
- [StackExchange: Bluetooth pairing on dual-boot](https://unix.stackexchange.com/questions/255509/bluetooth-pairing-on-dual-boot-of-windows-linux-mint-ubuntu-stop-having-to-p)
- [bt-dualboot GitHub](https://github.com/x2es/bt-dualboot)

## License

This project is licensed under the GNU General Public License v3.0.

Feel free to open issues or submit pull requests or incorporate the code & techniques into automated dualboot pairing projects.
