from lib.ota_updater import OTAUpdater
import time

global ota_updater

def download_and_install_update_if_available():
    global ota_updater
    ota_updater = OTAUpdater('https://github.com/DvdSpijker/uPythonLibs')
    ota_updater.download_and_install_update_if_available('WuiFui', '89NZ6DWRNPFD!')

def start():
    global ota_updater
    print("Started")
    time.sleep(5)
    ota_updater.check_for_update_to_install_during_next_reboot()

def boot():
    download_and_install_update_if_available()
    start()


boot()