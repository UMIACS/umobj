#
# Regular cron jobs for the umobj package
#
0 4	* * *	root	[ -x /usr/bin/umobj_maintenance ] && /usr/bin/umobj_maintenance
