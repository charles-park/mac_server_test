//------------------------------------------------------------------------------
//
// 2022.04.20 Mac server control app. (chalres-park)
//
//------------------------------------------------------------------------------
//------------------------------------------------------------------------------
#ifndef	__MAC_SERVER_CTL_H__
#define	__MAC_SERVER_CTL_H__

//------------------------------------------------------------------------------
#define	PYTHON_FILE_NAME	"mac_server_ctl.py"
#define	TYPE_MAC			0
#define	TYPE_UUID			1
#define TYPE_UUID_SIZE		36
#define	TYPE_MAC_SIZE		12

//------------------------------------------------------------------------------
extern	int set_erase_mac 	(char *rboard, char *rmac);
extern	int get_mac_uuid	(char *rboard, bool rtype, char *rdata, char rsize);
extern	int mac_server_test (void);

#endif	//	#define	__MAC_SERVER_CTL_H__
//------------------------------------------------------------------------------
//------------------------------------------------------------------------------
