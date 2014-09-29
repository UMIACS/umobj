# umobj
Command Line Utilties for UMIACS Object Storage Services

They are provided to support our [Ceph](http://ceph.com) Object Stores so that
our users may interact with them on the command line.  In addition, each Ceph
Object Store in UMIACS has a fully-functional web application that allows
access to your storage from a web browser.

These are a collection of utilities written in Python using the
standard Boto library.  They all support some common environment
variables that can be set to avoid needing to specified each
command line.  UMIACS supported systems have these available in the standard
paths.

## Setup

The following environmental variables are required to be set.

 * *OBJ_ACCESS_KEY_ID* - The users access key
 * *OBJ_SECRET_ACCESS_KEY* - The users secret key

This environment variable is required if you using an alternative Object Store
than ```obj.umiacs.umd.edu```.

 * *OBJ_SERVER*  - The object server to use

For example if you use the ```bash``` shell you can add the following to your
```.bashrc``` or ```.bash_profile```.

```
export OBJ_ACCESS_KEY_ID="31sdfadDFAHFDN+344qOEIS"
export OBJ_SECRET_ACCESS_KEY="NDSMK3233adfahadflkkPDSH092DSJKDKDJKFDLSFLNK"
```

You can optionally pass the <code>--access_key</code>, <code>--secret_key</code>
and <code>--server</code> switches to the utilities to get the same behavior.

## Utilties

These utilities use a common syntax for specifying the bucket and an optional
key or path.  The bucket and key is separated by a ```:```.  For example,
```my_bucket:bar.txt``` specifies the bucket ```my_bucket``` and the
key ```bar.txt```.  For more information on a specific utility you can pass the
flag ```-h``` or ```--help``` for help.

* lsobj
* mkobj
* cpobj
* rmobj
* chobj
* syncobj

### lsobj

To list buckets and keys in the Object Store you can use the <b>lsobj</b> command.  
If given without an argument it will list your buckets (this will only list
buckets that you created).

```
$ lsobj
bob
test
zeta
```

You can then give it a bucket name to list the contents within that bucket.  If
you were granted access to a bucket that you didn't create you can also use this
command to display its contents.  This will list all the keys in your bucket,
which can take a long time.

```
$ lsobj test
-rwx---	2013-10-04T15:25:09.000Z	    1.8 KB	UMIACSCA.pem
-rwx---	2013-10-04T15:25:24.000Z	  311.4 KB	cover.jpg
-rwx---	2013-10-04T15:27:39.000Z	    0.0 b 	foo/
-rwx---	2013-10-04T15:27:40.000Z	    0.0 b 	foo/bar
-rwx---	2013-10-04T15:25:32.000Z	   31.8 KB	screenshot.jpg
-rwx---	2013-10-04T15:26:48.000Z	    8.3 KB	thunderbird.xpm
================================================================================
		TOTAL:  	  353.3 KB 	6 Files
```

#### Directories
In an object store there are only buckets and keys (key=value store).  This
means that your traditional POSIX directory structure is only emulated using
the UNIX ```/``` character as the last character in a key name.  Any key in
the bucket ending in a ```/``` will be interpreted by the ```lsobj``` utility and
website as a directory.   You can also list only subdirectories with the
```lsobj``` utility.

<pre>
$ lsobj test:foo/
foo/
-rwx---	2013-10-04T15:27:39.000Z	    0.0 b 	foo/
-rwx---	2013-10-04T15:27:40.000Z	    0.0 b 	foo/bar
================================================================================
		TOTAL:  	    0.0 b  	2 Files
</pre>

### mkobj

mkobj creates buckets and directories in the Object Store.  

<b>Please note that bucket names are unique in the Object Store, so you may
very well get an error back that the name has already been used.</b>  

```
$ mkobj foo
Created bucket foo.
$ lsobj
bob
foo
test
zeta
```

You can also create directories within your buckets to provide a way to group your data.

```
% mkobj foo:bar/
% lsobj foo
-rwx---	2013-10-04T15:38:38.000Z	    0.0 b 	bar/
================================================================================
		TOTAL:  	    0.0 b  	1 Files
```

### cpobj
Copying files to the Object Store can be done per-file or recursively both to and from the Object Store.

To copy a single file to the Object Store you can use <code>cpobj</code> and specify a bucket with a trailing <code>:</code> (with an optional additional path).

```
% cpobj test.png foo:
100% |##############################################################################################|
% lsobj foo
-rwx---	2013-10-04T15:38:38.000Z	    0.0 b 	bar/
-rwx---	2013-10-07T20:06:48.000Z	   18.3 KB	test.png
================================================================================
		TOTAL:  	   18.3 KB 	2 Files
```

To copy a directory of files you will need to use the <code>-r</code> or <code>--recursive</code> flags.

```
% lsobj foo
================================================================================
		TOTAL:  	    0.0 b  	0 Files
% cpobj -r /tmp/stuff foo:stuff
100% |##############################################################################################|
100% |##############################################################################################|
100% |##############################################################################################|
% lsobj foo
-rwx---	2013-10-08T00:13:52.000Z	    0.0 b 	stuff/
-rwx---	2013-10-08T00:13:55.000Z	   26.0 KB	stuff/WindowsSecurity.png
-rwx---	2013-10-08T00:13:54.000Z	  226.5 KB	stuff/changepass.tiff
-rwx---	2013-10-08T00:13:55.000Z	   18.3 KB	stuff/test.png
================================================================================
		TOTAL:  	  270.8 KB 	9 Files
```

### rmobj
You can delete your buckets and keys with ```rmobj```.  It can take a bucket and work recursively, asking you to delete all the files and the bucket itself.  It can also just delete specific files in a bucket when given on the command line.

```
% rmobj -r foo
 Are you sure you want to remove all the contents of the bucket 'foo'? [yes/no] yes
 Do you want to remove the bucket 'foo'? [yes/no] no
```

```
% lsobj foo
-rwx---	2013-10-09T18:44:20.000Z	    1.0 KB	setup.cfg
-rwx---	2013-10-09T18:44:17.000Z	  781.0 b 	setup.py
-rwx---	2013-10-09T18:44:09.000Z	  289.0 b 	test-requirements.txt
================================================================================
		TOTAL:  	    2.0 KB 	3 Files
% rmobj foo:setup.cfg foo:setup.py
% lsobj foo
-rwx---	2013-10-09T18:44:09.000Z	  289.0 b 	test-requirements.txt
================================================================================
		TOTAL:  	  289.0 b  	1 Files
```

You can also remove directories within a bucket.  To do so, you will need to pass the <code>-r</code> flag.  This will prompt you for the removal of every key under that directory unless the <code>-f</code> flag is passed as well.
```
% lsobj foo
-rwx---	2013-10-10T21:58:17.000Z	    0.0 b 	research/
-rwx---	2013-10-10T21:58:17.000Z	    0.0 b 	research/papers/
-rwx---	2013-10-10T21:58:18.000Z	    0.0 b 	research/papers/paper1.tex
-rwx---	2013-10-10T21:58:18.000Z	    0.0 b 	research/papers/paper2.tex
-rwx---	2013-10-10T21:58:18.000Z	    0.0 b 	research/posters/
-rwx---	2013-10-10T21:58:18.000Z	    0.0 b 	research/posters/poster1.tex
-rwx---	2013-10-10T21:58:18.000Z	    0.0 b 	research/posters/poster2.tex
================================================================================
		TOTAL:  	    0.0 b  	7 Files
% rmobj -rf foo:research/posters/
% lsobj foo
-rwx---	2013-10-10T21:58:17.000Z	    0.0 b 	research/
-rwx---	2013-10-10T21:58:17.000Z	    0.0 b 	research/papers/
-rwx---	2013-10-10T21:58:18.000Z	    0.0 b 	research/papers/paper1.tex
-rwx---	2013-10-10T21:58:18.000Z	    0.0 b 	research/papers/paper2.tex
================================================================================
		TOTAL:  	    0.0 b  	4 Files
```

### chobj
You can change the ACL on a specific key(s) and specify multiple canned ACL policies in a single command.

```
% chobj -p liam:FULL_CONTROL -p derek:FULL_CONTROL foo:test-requirements.txt
```

### syncobj
You can use ```syncobj``` to syncronize files and directories into the object
store.  It does this by comparing the checksum between the local and remote.  This
does not follow symlinks and will warn when it encounters files (character,
block, fifo, etc.) that it can not archive.

```
% syncobj -r devel/puppet test:
100% |#########################################################################|
```

## Requirements

These utilties and libraries are work with Python 2.6+ (and are not tested
    under Python 3.x+).  They require the following modules:

- Boto > 2.5.x
- FileChunkIO
- Progressbar

If running python 2.6 you need to have the following backports

- argparse

These are most easily going to be satisfied with a virtualenv.

## Installation

```python setup.py install```
