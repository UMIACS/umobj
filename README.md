# umobj

[![PyPI](https://img.shields.io/pypi/v/umobj.svg)](https://pypi.python.org/pypi/umobj)
[![LGPL License badge](https://img.shields.io/badge/License-LGPL-blue.svg)](./LICENSE)
<!-- [![GitHub tag](https://img.shields.io/github/tag/umiacs/umobj.svg)](https://github.com/umiacs/umobj/releases)
     shields.io is having some serious problems with certain
	 services/badges -->


Command-line utilties for S3-compatible Object Storage

These utilities provide a command-line interface to an Amazon S3-compatible
file/object storage services, also known as an Object Store.

## Installation

```pip install umobj```

or

```python setup.py install```

## Setup

For convenience, consider setting a few environmental variables that umobj will use to authenticate you.

 * *OBJ_ACCESS_KEY_ID* - The user's access key
 * *OBJ_SECRET_ACCESS_KEY* - The user's secret key
 * *OBJ_SERVER* - The object server endpoint

For example, if you use the ```bash``` shell, you can add the following to your
```.bashrc``` or ```.bash_profile```.

```bash
export OBJ_ACCESS_KEY_ID="<YOUR_ACCESS_KEY>"
export OBJ_SECRET_ACCESS_KEY="<YOUR_SECRET_KEY>"
export OBJ_SERVER="s3.amazonaws.com"
```

You can optionally pass the <code>--access_key</code>,
<code>--secret_key</code> and <code>--server</code> switches to the utilities
to get the same behavior.

## Utilties

These utilities use a common syntax for specifying the bucket and an optional
key or path.  The bucket and key are separated by a ```:```.  For example,
```my_bucket:bar.txt``` denotes the bucket ```my_bucket``` and the key
```bar.txt```.  For more information on a specific utility, you can pass the
flag ```-h``` or ```--help``` for help.

* [lsobj](#lsobj)
* [mkobj](#mkobj)
* [cpobj](#cpobj)
* [rmobj](#rmobj)
* [chobj](#chobj)
* [syncobj](#syncobj)
* [catobj](#catobj)
* [streamobj](#streamobj)
* [cmpobj](#cmpobj)
* [webobj](#webobj)

<a name="lsobj"></a>
### lsobj

To list buckets and keys in the Object Store you can use the <b>lsobj</b>
command.  If given without an argument, it will list your buckets.

```bash
$ lsobj
bob
test
zeta
```

You can then give it a bucket name to list the contents within that bucket.

```bash
% lsobj -l test
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

In an Object Store, there are only buckets and keys.  This means that any
apparent directory structure is only emulated using the UNIX ```/``` character
in a key name.  Any key in the bucket ending in a ```/``` will be interpreted
as a directory.  You can also list only subdirectories with the ```lsobj```
utility.

```bash
% lsobj -l test:foo/
foo/
-rwx---	2013-10-04T15:27:39.000Z	    0.0 b 	foo/
-rwx---	2013-10-04T15:27:40.000Z	    0.0 b 	foo/bar
================================================================================
		TOTAL:  	    0.0 b  	2 Files
```

<a name="mkobj"></a>
### mkobj

mkobj creates buckets and directories in the Object Store.

<b>Please note that bucket names are unique in the Object Store, so you may
very well get an error back that the name has already been taken.</b>

```bash
% mkobj foo
Created bucket foo.
% lsobj
bob
foo
test
zeta
```

You can also create directories to group your data.

```bash
% mkobj foo:bar/
% lsobj -l foo
-rwx---	2013-10-04T15:38:38.000Z	    0.0 b 	bar/
================================================================================
		TOTAL:  	    0.0 b  	1 File
```

<a name="mkobj"></a>
### cpobj

Copying files to the Object Store can be done per-file or recursively both to
and from the Object Store.

To copy a single file to the Object Store you can use <code>cpobj</code> and
specify a bucket with a trailing <code>:</code> (with an optional additional
path).

```bash
% cpobj test.png foo:
100% |#########################################################################|
% lsobj -l foo
-rwx---	2013-10-04T15:38:38.000Z	    0.0 b 	bar/
-rwx---	2013-10-07T20:06:48.000Z	   18.3 KB	test.png
================================================================================
		TOTAL:  	   18.3 KB 	2 Files
```

To copy a directory of files you will need to use the <code>-r</code> or
<code>--recursive</code> flags.

```bash
% lsobj foo
================================================================================
		TOTAL:  	    0.0 b  	0 Files
% cpobj -r /tmp/stuff foo:stuff
100% |#########################################################################|
100% |#########################################################################|
100% |#########################################################################|
% lsobj -l foo
-rwx---	2013-10-08T00:13:52.000Z	    0.0 b 	stuff/
-rwx---	2013-10-08T00:13:55.000Z	   26.0 KB	stuff/WindowsSecurity.png
-rwx---	2013-10-08T00:13:54.000Z	  226.5 KB	stuff/changepass.tiff
-rwx---	2013-10-08T00:13:55.000Z	   18.3 KB	stuff/test.png
================================================================================
		TOTAL:  	  270.8 KB 	9 Files
```

<a name="rmobj"></a>
### rmobj

You can delete your buckets and keys with ```rmobj```.  It can take a bucket
and work recursively to delete all the files and the bucket itself.
It can also just delete specific files in a bucket.

```bash
% rmobj -r foo
 Are you sure you want to remove all the contents of the bucket 'foo'? [yes/no] yes
 Do you want to remove the bucket 'foo'? [yes/no] no
```

```bash
% lsobj -l foo
-rwx---	2013-10-09T18:44:20.000Z	    1.0 KB	setup.cfg
-rwx---	2013-10-09T18:44:17.000Z	  781.0 b 	setup.py
-rwx---	2013-10-09T18:44:09.000Z	  289.0 b 	test-requirements.txt
================================================================================
		TOTAL:  	    2.0 KB 	3 Files
% rmobj foo:setup.cfg foo:setup.py
% lsobj -l foo
-rwx---	2013-10-09T18:44:09.000Z	  289.0 b 	test-requirements.txt
================================================================================
		TOTAL:  	  289.0 b  	1 File
```

You can also remove directories within a bucket.  To do so, you will need to
pass the <code>-r</code> flag.  This will prompt once for the removal of every
key under that directory unless the <code>-f</code> flag is passed as well.  
Specifying <code>-i</code> will prompt for every file.

```bash
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

You can use a glob character to delete all bucket contents, but not the
bucket itself.

```bash
% rmobj -rf foo:*
% lsobj foo
================================================================================
		TOTAL:  	    0.0 b  	0 Files
```

<a name="chobj"></a>
### chobj

Use ```chobj``` to set permissions/ACLs on buckets and keys.

```bash
% chobj -m clear -p liam:FULL_CONTROL -p derek:FULL_CONTROL foo:test-requirements.txt
```

<a name="syncobj"></a>
### syncobj
You can use ```syncobj``` to synchronize files and directories into the Object
Store.  It does this by comparing the checksum between the local and remote
versions of the key.  This does not follow symlinks and will warn when it
encounters files (character, block, fifo, etc...) that it can not archive.

```bash
% syncobj -r devel/puppet test:
100% |#########################################################################|
```

<a name="catobj"></a>
### catobj

Use ```catobj``` to print the contents of a key to stdout.  This may be useful
for streaming the content of a file to another command for some sort of
processing without having to write the key to an intermediary file.  If any
errors are printed in the process of running this command, you can be assured
that they will be printed to stderr, and should not interfere with what's being
printed to stdout.

```bash
% catobj foo:something.txt
Fallaces sunt rerum species.  Mutantur omnia nos et mutamur in illis.
```

<a name="streamobj"></a>
### streamobj

Use ```streamobj``` to read the contents of a data stream that has been piped from
stdout and upload it to a bucket. This allows you to send large amounts of data to
a bucket without saving it all on disk or in memory first. A name for the file
must be specified using the -n flag because a name can't be inferred from the
data stream.

```bash
% stream_source | streamobj -n filename foo:somedirectory
```

<a name="cmpobj"></a>
### cmpobj

Use ```cmpobj``` to check the md5 sum of a key in a bucket or compare the md5 sums of a local directory to a bucket. The key is downloaded in order for the correct md5 hash to be generated. Bagit archives can also be verified, which is done by retrieving the manifest and comparing the expected checksums to the ones computed by downloading each key.

```bash
% cmpobj mybucket:foo.txt
9029668a43dfa60f1f267eea59111bbc
```

<a name="webobj"></a>
### webobj

Use ```webobj``` to configure web configurations of a bucket. Currently, this
supports setting a S3 website configuration such that bucket can be served as a
static site.

```bash
% webobj -m create -c website --index=index.html --error=error.html mybucket
% webobj -m examine -c website mybucket
Index: index.html
Error Key: error.html
% webobj -m delete -c website mybucket

```

## Requirements

These utilties and libraries all work with Python 2.6+ (and are not tested
under Python 3.x+).  They require the following modules:

- Boto > 2.5.x
- FileChunkIO
- Progressbar
- qav

When running on Python 2.6, you need to have the following backports:

- argparse

These are most easily going to be satisfied with a virtualenv.

## Report an issue

The official repository for umobj is hosted in the [UMIACS Gitlab](https://gitlab.umiacs.umd.edu/staff/umobj) service. Please open new issues in the Gitlab tracker.

## License

    umobj - Command-line utilties for S3-compatible Object Storage
    Copyright (C) 2017  UMIACS

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

    Email:
        github@umiacs.umd.edu
