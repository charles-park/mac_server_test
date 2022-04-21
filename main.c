//------------------------------------------------------------------------------
//
// 2022.04.14 Argument parser app. (chalres-park)
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
#include "mac_server_ctl.h"
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
static void print_usage(const char *prog)
{
	printf("Usage: %s [-bre]\n", prog);
	puts("  -b --board_name     request board name.\n"
	     "  -r --request        request from server. (mac or uuid)\n"
	     "  -e --erase          request erase mac.\n"
		 "  e.g) request mac \n"
		 "       mac_server_test -b n2l -r mac\n"
		 "  e.g) request uuid \n"
		 "       mac_server_test -b n2l -r uuid\n"
		 "  e.g) request erase mac \n"
		 "       mac_server_test -b n2l -e 001e06123456\n"
	);
	exit(1);
}

//------------------------------------------------------------------------------
static char *OPT_REQUEST_BOARD = "None";
static char *OPT_ERASE_MAC = "000000000000";
static bool OPT_REQUEST_MAC = false;

static void parse_opts (int argc, char *argv[])
{
	while (1) {
		static const struct option lopts[] = {
			{ "board_name", 1, 0, 'b' },
			{ "request",	1, 0, 'r' },
			{ "erase",		1, 0, 'e' },
			{ NULL, 0, 0, 0 },
		};
		int c;

		c = getopt_long(argc, argv, "b:r:e:", lopts, NULL);

		if (c == -1)
			break;

		switch (c) {
		case 'b':
			tolowerstr (optarg);
			OPT_REQUEST_BOARD = optarg;
			break;
		case 'r':
			tolowerstr (optarg);
            if (!strncmp("mac", optarg, strlen("mac")))
				OPT_REQUEST_MAC = true;
			else
				OPT_REQUEST_MAC = false;
			break;
		case 'e':
			OPT_ERASE_MAC = optarg;
			break;
		default:
			print_usage(argv[0]);
			break;
		}
	}
}

//------------------------------------------------------------------------------
int main(int argc, char **argv)
{
    parse_opts(argc, argv);
	mac_server_test();
	return 0;
}

//------------------------------------------------------------------------------
//------------------------------------------------------------------------------
