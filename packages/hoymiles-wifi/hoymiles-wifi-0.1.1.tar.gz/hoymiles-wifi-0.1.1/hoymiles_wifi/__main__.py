import argparse
import asyncio
from dataclasses import dataclass
from hoymiles_wifi.inverter import Inverter

from hoymiles_wifi.utils import (
    generate_version_string,
    generate_sw_version_string, 
    generate_dtu_version_string
)

from hoymiles_wifi.const import (
    DTU_FIRMWARE_URL_00_01_11
)

@dataclass
class VersionInfo:
    dtu_hw_version: str
    dtu_sw_version: str
    inverter_hw_version: str
    inverter_sw_version: str

    def __str__(self):
        return (
            f'dtu_hw_version: "{self.dtu_hw_version}"\n'
            f'dtu_sw_version: "{self.dtu_sw_version}"\n'
            f'inverter_hw_version: "{self.inverter_hw_version}"\n'
            f'inverter_sw_version: "{self.inverter_sw_version}"\n'
        )

# Inverter commands
async def get_real_data_new(inverter):
    return await inverter.get_real_data_new()

async def get_real_data_hms(inverter):
    return await inverter.get_real_data_hms()

async def get_real_data(inverter):
    return await inverter.get_real_data()

async def get_config(inverter):
    return await inverter.get_config()

async def network_info(inverter):
    return await inverter.network_info()

async def app_information_data(inverter):
    return await inverter.app_information_data()

async def app_get_hist_power(inverter):
    return await inverter.app_get_hist_power()

async def set_power_limit(inverter):

    RED = '\033[91m'
    END = '\033[0m'

    print(RED + "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" + END)
    print(RED + "!!! Danger zone! This will change the power limit of the inverter. !!!" + END)
    print(RED + "!!!  Please be careful and make sure you know what you are doing.  !!!" + END)
    print(RED + "!!!          Only proceed if you know what you are doing.          !!!" + END)
    print(RED + "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" + END)
    print("")


    cont = input("Do you want to continue? (y/n): ")
    if(cont != 'y'):
        return

    power_limit = int(input("Enter the new power limit (0-100): "))

    if(power_limit < 0 or power_limit > 100):
        print("Error. Invalid power limit!")
        return
    
    print(f"Setting power limit to {power_limit}%")
    cont = input("Are you sure? (y/n): ") 

    if(cont != 'y'):
        return

    return await inverter.set_power_limit(power_limit)


async def set_wifi(inverter):
    wifi_ssid = input("Enter the new wifi SSID: ").strip()
    wifi_password = input("Enter the new wifi password: ").strip()
    print(f'Setting wifi to "{wifi_ssid}"')
    print(f'Setting wifi password to "{wifi_password}"')
    cont = input("Are you sure? (y/n): ")
    if(cont != 'y'):
        return
    return await inverter.set_wifi(wifi_ssid, wifi_password)

async def firmware_update(inverter):
    RED = '\033[91m'
    END = '\033[0m'

    print(RED + "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" + END)
    print(RED + "!!!    Danger zone! This will update the firmeware of the DTU.     !!!" + END)
    print(RED + "!!!  Please be careful and make sure you know what you are doing.  !!!" + END)
    print(RED + "!!!          Only proceed if you know what you are doing.          !!!" + END)
    print(RED + "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" + END)
    print("")

    cont = input("Do you want to continue? (y/n): ")
    if(cont != 'y'):
        return
    
    print("Please select a firmware version:")
    print("1.) V00.01.11")
    print("2.) Custom URL")

    while True:
        selection = input("Enter your selection (1 or 2): ")

        if selection == "1":
            url = DTU_FIRMWARE_URL_00_01_11
            break
        elif selection == "2":
            url = input("Enter the custom URL: ").strip()
            break
        else:
            print("Invalid selection. Please enter 1 or 2.")
    
    print()
    print(f'Firmware update URL: "{url}"')
    print()

    cont = input("Do you want to continue? (y/n): ")
    if(cont != 'y'):
        return
    
    return await inverter.update_dtu_firmware()

async def restart(inverter):

    cont = input("Do you want to restart the device? (y/n): ")
    if(cont != 'y'):
        return
    
    return await inverter.restart()

async def turn_off(inverter):
    cont = input("Do you want to turn *OFF* the device? (y/n): ")
    if(cont != 'y'):
        return
    
    return await inverter.turn_off()

async def turn_on(inverter):
    cont = input("Do you want to turn *ON* the device? (y/n): ")
    if(cont != 'y'):
        return
    
    return await inverter.turn_on()

async def get_information_data(inverter):
    return await inverter.get_information_data()

async def get_version_info(inverter):
    response = await app_information_data(inverter)

    if not response:
        return None

    return VersionInfo(
        dtu_hw_version="H" + generate_dtu_version_string(response.dtu_info.dtu_hw_version),
        dtu_sw_version="V" + generate_dtu_version_string(response.dtu_info.dtu_sw_version),
        inverter_hw_version="H" + generate_version_string(response.pv_info[0].pv_hw_version),
        inverter_sw_version="V" + generate_sw_version_string(response.pv_info[0].pv_sw_version),
    )
    

def print_invalid_command(command):
    print(f"Invalid command: {command}")

async def main():
    parser = argparse.ArgumentParser(description="Hoymiles HMS Monitoring")
    parser.add_argument(
        "--host", type=str, required=True, help="IP address or hostname of the inverter"
    )    
    parser.add_argument(
        "command",
        type=str,
        choices=[
            "get-real-data-new",
            "get-real-data-hms",
            "get-real-data",
            "get-config",
            "network-info",
            "app-information-data",
            "app-get-hist-power",
            "set-power-limit",
            "set-wifi",
            "firmware-update",
            "restart",
            "turn-on",
            "turn-off",
            "get-information-data",
            "get-version-info"
        ],
        help="Command to execute",
    )
    args = parser.parse_args()
    
    inverter = Inverter(args.host)

    # Execute the specified command using a switch case
    switch = {
        'get-real-data-new': get_real_data_new,
        'get-real-data-hms': get_real_data_hms,
        'get-real-data': get_real_data,
        'get-config': get_config,
        'network-info': network_info,
        'app-information-data': app_information_data,
        'app-get-hist-power': app_get_hist_power,
        'set-power-limit': set_power_limit,
        'set-wifi': set_wifi,
        'firmware-update': firmware_update,
        'restart': restart,
        'turn-on': turn_on,
        'turn-off': turn_off,
        'get-information-data': get_information_data,
        'get-version-info': get_version_info,
    }

    command_func = switch.get(args.command, print_invalid_command)
    response = await command_func(inverter)

    if response:
        print(f"{args.command.capitalize()} Response: \n{response}")
    else:
        print(f"No response or unable to retrieve response for {args.command.replace('_', ' ')}")


def run_main():
    asyncio.run(main())

if __name__ == "__main__":
    run_main()