#!/usr/bin/env python3
import argparse
import textwrap

"""
This script converts Bluetooth pairing keys extracted from the Windows registry
into the format required for the Linux Bluetooth 'info' file.

Run with --help for more information.
"""

def get_hex_input(prompt):
    """
    Prompts the user for a hexadecimal input, sanitizes it, and returns the cleaned value.

    Args:
        prompt (str): The prompt to display to the user.

    Returns:
        str: The sanitized hexadecimal string input from the user.
    """
    value = input(prompt).strip()
    value = value.replace(',', ' ').replace('  ', ' ').strip()
    return value

def sanitize_hex_string(hex_str):
    """
    Removes spaces from a hexadecimal string and converts it to uppercase.

    Args:
        hex_str (str): The hexadecimal string to sanitize.

    Returns:
        str: The sanitized hexadecimal string.
    """
    return hex_str.replace(' ', '').upper()

def reverse_bytes_and_convert_to_decimal(value, expected_length=None):
    """
    Reverses the byte order of a hexadecimal string and converts it to a decimal value.

    Args:
        value (str): The hexadecimal string to process.
        expected_length (int, optional): The expected number of bytes in the input.
                                         If provided, a warning is printed if the length does not match.

    Returns:
        str: The decimal representation of the reversed hexadecimal value.
    """
    if not value:
        return ''
    bytes_list = value.strip().split()
    if expected_length and len(bytes_list) != expected_length:
        print(f"Warning: Expected {expected_length} bytes, got {len(bytes_list)} bytes.")
    reversed_bytes = bytes_list[::-1]
    reversed_hex = ''.join(reversed_bytes)
    return str(int(reversed_hex, 16))

def format_mac_address(mac_string):
    """
    Formats a MAC address string by inserting colons between every two characters.

    Args:
        mac_string (str): The MAC address string without any separators.

    Returns:
        str: The formatted MAC address with colons.
    """
    octets = [mac_string[i:i+2].upper() for i in range(0, len(mac_string), 2)]
    formatted_mac = ":".join(octets)
    return formatted_mac

def process_bluetooth_keys(key_values):
    """
    Processes the provided Bluetooth keys and formats them into a dictionary for Linux compatibility.

    Args:
        key_values (dict): A dictionary of Bluetooth keys extracted from the Windows registry.

    Returns:
        dict: A dictionary containing processed Bluetooth key values suitable for Linux.
    """
    outputs = {}
    
    # Process LTK or LinkKey
    ltk = sanitize_hex_string(key_values.get('LTK', ''))
    outputs['LongTermKey.Key'] = ltk
    outputs['LinkKey.Key'] = ltk

    # Process KeyLength (EncSize)
    key_length_hex = key_values.get('KeyLength', '')
    key_length_dec = reverse_bytes_and_convert_to_decimal(key_length_hex, expected_length=4)
    outputs['LongTermKey.EncSize'] = key_length_dec if key_length_dec else '16'

    # Process ERand
    erand = key_values.get('ERand', '')
    erand_dec = reverse_bytes_and_convert_to_decimal(erand)
    outputs['LongTermKey.Rand'] = erand_dec if erand_dec else '0'

    # Process EDIV
    ediv_hex = key_values.get('EDIV', '')
    ediv_dec = reverse_bytes_and_convert_to_decimal(ediv_hex, expected_length=4)
    outputs['LongTermKey.EDiv'] = ediv_dec if ediv_dec else '0'

    # Process IRK
    irk = sanitize_hex_string(key_values.get('IRK', ''))
    outputs['IdentityResolvingKey.Key'] = irk
    outputs['IdentityResolvingKey.ReversedOctets'] = reverse_octets(irk) if irk else ''

    # Process CSRK
    csrk = sanitize_hex_string(key_values.get('CSRK', ''))
    outputs['LocalSignatureKey.Key'] = csrk
    outputs['LocalSignatureKey.Counter'] = '0'
    outputs['LocalSignatureKey.Authenticated'] = 'false'

    # Process CSRKInbound as RemoteSignatureKey (optional)
    csrk_inbound = key_values.get('CSRKInbound', '')
    if csrk_inbound:
        csrk_inbound_sanitized = sanitize_hex_string(csrk_inbound)
        outputs['RemoteSignatureKey.Key'] = csrk_inbound_sanitized
        outputs['RemoteSignatureKey.Counter'] = '0'
        outputs['RemoteSignatureKey.Authenticated'] = 'false'

    return outputs

def reverse_octets(octet_str):
    """
    Reverses the order of bytes in a continuous hexadecimal string.

    Args:
        octet_str (str): The hexadecimal string to reverse.

    Returns:
        str: The reversed hexadecimal string.
    """
    if not octet_str:
        return ''
    # Ensure the string has an even length
    if len(octet_str) % 2 != 0:
        print("Error: Hex string does not have an even length.")
        return ''
    # Split into bytes (pairs of hex digits)
    octets = [octet_str[i:i+2] for i in range(0, len(octet_str), 2)]
    reversed_octets = octets[::-1]
    return ''.join(reversed_octets)

def remove_spaces_upper(hex_str):
    """
    Removes spaces from a hexadecimal string and converts it to uppercase.

    Args:
        hex_str (str): The hexadecimal string to process.

    Returns:
        str: The processed hexadecimal string.
    """
    return hex_str.replace(' ', '').upper()

def display_instructions():
    """
    Displays instructions on how to extract Bluetooth keys from the Windows registry.
    """
    print("\nThis script helps convert Bluetooth keys from Windows to Linux format.\n")
    print("It will not modify any files, but will provide output for you to copy and paste.\n")

    print("# Example: How to extract Bluetooth keys from the Windows registry using 'chntpw'")
    print("# Use the hex value with spaces as shown in Windows registry (e.g. 'C1 22 E9 8B 71 DA 90 C9 45 0E EC 40 52 94 DE 49')\n")
    print("sudo chntpw -e /win/Windows/System32/config/SYSTEM")
    print("cd \\ControlSet001\\Services\\BTHPORT\\Parameters\\Keys")
    print("ls")
    print("cd <AdapterMAC>  # Replace with your adapter's MAC address")
    print("cd <DeviceMAC>  # Replace with your device's MAC address (e.g., for a mouse or keyboard)")
    print("hex <DeviceMAC>")
    print("\n# Extract values for the following keys:")
    print("hex LTK")
    print("hex KeyLength")
    print("hex ERand")
    print("hex EDIV")
    print("hex IRK")
    print("hex CSRK")
    print("hex CSRKInbound\n")

def get_mac_address():
    """
    Prompts the user for the MAC address and formats it for Linux usage, or skips if not provided.

    Returns:
        str: The formatted MAC address, or an empty string if not provided.
    """
    mac_address = input("Enter the device's MAC address (hexadecimal, no separators, e.g., '60abd2916ef6'):\n> ").strip()
    if mac_address:
        formatted_mac = format_mac_address(mac_address)
        print(f"Formatted MAC address for use in directory: {formatted_mac}")
        return formatted_mac
    else:
        return ''  # Return an empty string if no MAC address is provided


def collect_user_inputs():
    """
    Collects Bluetooth key inputs from the user and stores them in a dictionary.

    Returns:
        dict: A dictionary containing the user-provided Bluetooth keys.
    """
    print("Please enter the following keys as extracted from the Windows registry.")
    print("If a key is not available or not required, just press Enter to skip.\n")

    key_values = {}

    # Prompt for essential keys
    key_values['LTK'] = get_hex_input("Enter LTK (or LinkKey from hex <DeviceMAC>):\n> ")
    key_values['KeyLength'] = input("Enter KeyLength (DWORD in hex, e.g., '10 00 00 00' for 16):\n> ").strip()
    key_values['ERand'] = get_hex_input("Enter ERand (QWORD in hex, 8 bytes):\n> ")
    key_values['EDIV'] = get_hex_input("Enter EDIV (DWORD in hex, 4 bytes):\n> ")
    key_values['IRK'] = get_hex_input("Enter IRK:\n> ")
    key_values['CSRK'] = get_hex_input("Enter CSRK:\n> ")

    # Optional: RemoteSignatureKey
    csrk_inbound = get_hex_input("Enter CSRKInbound (optional, press Enter to skip):\n> ")
    if csrk_inbound:
        key_values['CSRKInbound'] = csrk_inbound

    return key_values

def display_outputs(outputs, mac_address):
    """
    Displays the processed Bluetooth key outputs in the appropriate format for the Linux 'info' file.

    Args:
        outputs (dict): A dictionary containing processed Bluetooth key values.
        mac_address (str): The formatted MAC address for the device.
    """
    print("\nProcessing values...\n")
    print("You can try the following outputs in your 'info' file:")
    print("-----------------------------------------------------\n")

    print("=== Standard Processing ===\n")
    
    if outputs['IdentityResolvingKey.Key']:
        print(f"""
[IdentityResolvingKey]
Key={outputs['IdentityResolvingKey.Key']}
""")

    if outputs['LongTermKey.Key']:
        print(f"""
[LongTermKey]
Key={outputs['LongTermKey.Key']}
EncSize={outputs['LongTermKey.EncSize']}
EDiv={outputs['LongTermKey.EDiv']}
Rand={outputs['LongTermKey.Rand']}
Authenticated=0
""")

    if outputs['LocalSignatureKey.Key']:
        print(f"""
[LocalSignatureKey]
Key={outputs['LocalSignatureKey.Key']}
Counter={outputs['LocalSignatureKey.Counter']}
Authenticated={outputs['LocalSignatureKey.Authenticated']}
""")

    if outputs.get('RemoteSignatureKey.Key'):
        print(f"""
[RemoteSignatureKey]
Key={outputs['RemoteSignatureKey.Key']}
Counter={outputs['RemoteSignatureKey.Counter']}
Authenticated={outputs['RemoteSignatureKey.Authenticated']}
""")

    print("=== Alternative Processing (Reversed Octets) ===\n")
    
    # Reverse octets for IRK
    if outputs.get('IdentityResolvingKey.ReversedOctets'):
        irk_reversed = outputs['IdentityResolvingKey.ReversedOctets']
        if irk_reversed != outputs['IdentityResolvingKey.Key']:
            print(f"[IdentityResolvingKey]\nKey={irk_reversed}\n")

    print("-----------------------------------------------------")
    if mac_address:
        print(f"\nInfo file: /var/lib/bluetooth/*/{mac_address}/info\n")
    print("Remember to restart the Bluetooth service after updating the 'info' file:")
    print("sudo systemctl restart bluetooth\n")

def main():
    """
    Main function to parse arguments and call the appropriate functions to process Bluetooth keys.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Convert Bluetooth pairing keys from Windows registry to Linux Bluetooth info file format."
        ),
        epilog=textwrap.dedent("""
            This script converts Bluetooth pairing keys extracted from the Windows registry
            into the format required for the Linux Bluetooth 'info' file.

            Usage:
                Simply run the script, enter the keys when prompted, and the script will output
                the transformed values needed to pair Bluetooth devices on Linux.

            Features:
                - Converts various Bluetooth pairing keys such as LTK, KeyLength, ERand, EDIV, IRK, CSRK, etc.
                - Provides step-by-step instructions on extracting keys from the Windows registry.
                - Outputs formatted data suitable for Linux Bluetooth device info files.

            Instructions:
                After obtaining the required keys from Windows, this script will prompt you
                to input those values and subsequently generate the required output format.
                You can then manually copy this output to the respective info file located at:
                /var/lib/bluetooth/{adapter}/{device}/info.

            Note:
                - This script does not modify any files automatically.
                - Ideal for cut-and-paste workflows to ensure correctness.
        """),
        formatter_class=argparse.RawTextHelpFormatter
    )
    args = parser.parse_args()

    display_instructions()
    mac_address = get_mac_address()
    key_values = collect_user_inputs()
    outputs = process_bluetooth_keys(key_values)
    display_outputs(outputs, mac_address)

if __name__ == "__main__":
    main()
