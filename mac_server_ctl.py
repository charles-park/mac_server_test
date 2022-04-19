import sys
import os
import asyncio

from odroid_factory_api import API_MANAGER

if __name__ == "__main__":
    args = sys.argv

    args_cnt = len(args)
    board_name = 'None'

    if args_cnt != 3:
        print ('usage : python3 mac_server_ctl.py [option1] [option2]')
        print ('      [option1] r : request mac addr [option2 {board name}]')
        print ('      [option1] e : erase mac addr [option2 {erase mac addr}]')
        print ('      e.g) python3 mac_server_ctl.py r m1')
        print ('           python3 mac_server_ctl.py e 001e06123456')
        quit()

    # odroid mac server control class get
    api_manager = API_MANAGER(board=args[2])
    # Log message disaplay control (1 = enable)
    api_manager.log_en(0)
    # api infomation (server info) display
    api_manager.info_print()

    if args[1] == 'r':
        # get mac address for board-name from the mac server.
        uuid = asyncio.run(api_manager.request_mac_addr())
        if "error" in uuid :
            print ('error, request_mac_addr()!\n', uuid)
            quit()
        else :
            # info update
            asyncio.run(api_manager.update_record({'uuid': uuid}))
    elif args[1] == 'e':
        # remove current mac address info or set mac address

        if '001e06' in args[2] and len(args[2]) == 12:
            api_manager.set_mac_addr (args[2])
            msg = asyncio.run(api_manager.delete_assigned_sign())
        else:
            print ('error, input mac addr,', f'input mac = {args[2]}, mac len = {len(args[2])}')
            quit()
        if "error" in msg:
            print ('error, delete_assigned_sign()', msg)
            quit()
    else :
        print ("error, unknown message", f'args[1] = {args[1]}, args[2] = {args[2]}')
        quit()

    # mac display
    if "001e06" in uuid:
        ret_msg = 'sucess' + ',' + api_manager.mac_addr + ',' + api_manager.uuid_mac
        print (ret_msg)
        api_manager.log_en(1)
        api_manager.info_print()
        # if test
        asyncio.run(api_manager.delete_assigned_sign())
