import sys
import os
import asyncio

from odroid_factory_api import API_MANAGER

if __name__ == "__main__":
    args = sys.argv

    args_cnt = len(args)
    board_name = 'None'

    if args_cnt != 3:
        print ('error:')
        print ('usage : python3 mac_server_ctl.py [option1] [option2]')
        print ('      [option1] r : request mac addr [option2 {board name}]')
        print ('      [option1] e : erase mac addr [option2 {erase mac addr}]')
        print ('      e.g) python3 mac_server_ctl.py r m1')
        print ('           python3 mac_server_ctl.py e 001e06123456')
        quit()

    if args[1] == 'r':
        board_name = args[2]
        print ('request mac address', 'board name =', board_name)
    elif args[1] == 'e':
        mac_addr = args[2]
        print ('erase mac addr', 'mac address =', mac_addr)
    else :
        print ("error: unknown message", f'args[1] = {args[1]}, args[2] = {args[2]}')
        quit()
    
    # odroid mac server control class get
    api_manager = API_MANAGER(board=board_name)

    # Log message disaplay control (1 = enable)
    api_manager.log_en(0)
    # api infomation (server info) display
    api_manager.info_print()
    
    # get mac address for board-name from the mac server.
    uuid = asyncio.run(api_manager.request_mac_addr())
    # info update
    asyncio.run(api_manager.update_record({'uuid': uuid}))

    # remove current mac address info or set mac address
    # api_manager.set_mac_addr ('001e06510034')
    asyncio.run(api_manager.delete_assigned_sign())

    # mac display
    if "001e06" in uuid:
        ret_msg = 'sucess' + ',' + api_manager.mac_addr + ',' + api_manager.uuid_mac
        print (ret_msg)
