//------------------------------------------------------------------------------
//
// 2022.04.20 Mac server control app. (chalres-park)
//
//------------------------------------------------------------------------------
//------------------------------------------------------------------------------
#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include <ctype.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/fb.h>
#include <getopt.h>

#include "typedefs.h"
//------------------------------------------------------------------------------
//------------------------------------------------------------------------------
static void tolowerstr (char *p)
{
	int i, c = strlen(p);

	for (i = 0; i < c; i++, p++)
		*p = tolower(*p);
}

//------------------------------------------------------------------------------
static void toupperstr (char *p)
{
	int i, c = strlen(p);

	for (i = 0; i < c; i++, p++)
		*p = toupper(*p);
}

//------------------------------------------------------------------------------
#define	PYTHON_FILE_NAME	"mac_server_ctl.py"
#define	TYPE_MAC			0
#define	TYPE_UUID			1
#define TYPE_UUID_SIZE		36
#define	TYPE_MAC_SIZE		12

//------------------------------------------------------------------------------
int set_erase_mac (char *rboard, char *rmac)
{
	FILE *fp;
	byte_t rwbuf[4096];

	// python send command setup
	memset(rwbuf, 0, sizeof(rwbuf));
	sprintf(rwbuf, "python3 %s -e %s %s\n", PYTHON_FILE_NAME, rboard, rmac);

	if (NULL == (fp = popen(rwbuf, "r")))
	{
		err("popen() error!\n");
		return 0;
	}

	// read buffer init
	memset(rwbuf, 0, sizeof(rwbuf));
	while (fgets(rwbuf, 4096, fp)) {
		if (strstr(rwbuf, "success") != NULL) {
			pclose(fp);
			return 1;
		}
	}
	pclose(fp);
	return 0;
}

//------------------------------------------------------------------------------
int get_mac_uuid (char *rboard, bool rtype, char *rdata, char rsize)
{
	FILE *fp;
	byte_t rwbuf[4096], need_buf_size = 0;

	need_buf_size = rtype ? TYPE_UUID_SIZE : TYPE_MAC_SIZE;
	if (rsize < need_buf_size) {
		err ("read buffer size error!\n");
		return 0;
	}
	memset (rdata, 0, rsize);

	// python send command setup
	memset(rwbuf, 0, sizeof(rwbuf));
	sprintf(rwbuf, "python3 %s -r %s\n", PYTHON_FILE_NAME, rboard);

	if (NULL == (fp = popen(rwbuf, "r")))
	{
		err("popen() error!\n");
		return 0;
	}

	// read buffer init
	memset(rwbuf, 0, sizeof(rwbuf));
	while (fgets(rwbuf, 4096, fp)) {
		if (strstr(rwbuf, "success") != NULL) {
			char *p = strstr(rwbuf, "001e06");
			/* rtype == 1 is uuid */
			strncpy(rdata, rtype ? (p + 13) : (p), rsize);
			pclose(fp);
			return 1;
		}
	}
	pclose(fp);
	return 0;
}

//------------------------------------------------------------------------------
int mac_server_test (void)
{
	int ret = 0;
	byte_t mac_uuid[TYPE_UUID_SIZE+1];

	memset(mac_uuid, 0, sizeof(mac_uuid));
	ret = get_mac_uuid("m1", TYPE_UUID, mac_uuid, TYPE_UUID_SIZE);
	printf("get uuid = %s, return = %d\n", mac_uuid, ret);

	memset(mac_uuid, 0, sizeof(mac_uuid));
	ret = get_mac_uuid("m1", TYPE_MAC, mac_uuid, TYPE_MAC_SIZE);
	printf("get mac = %s, return = %d\n", mac_uuid, ret);
	ret = set_erase_mac ("m1", mac_uuid);
	printf("erase mac = %s, return = %d\n", mac_uuid, ret);
	return 0;
}

//------------------------------------------------------------------------------
//------------------------------------------------------------------------------
