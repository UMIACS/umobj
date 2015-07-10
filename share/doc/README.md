# umobj
Command-line utilties for UMIACS Object Storage Services

These utilities provide a command-line interface to an Amazon S3-compatible
file/object storage service, which we will refer to as an Object Store.  UMIACS
runs multiple Object Stores, but each Object Store in UMIACS has a
fully-functional web application that allows access to your files from a web
browser.

UMIACS UNIX systems have these utilities available in the standard paths.

## Setup

Setting a few environmental variables containing the credentials you'll need to
use for the Object Store for convenience is a good idea.  When logged into the
web interface, you can find these credentials on the user page.  E.g.
https://obj.umiacs.umd.edu/obj/user/

The following environmental variables are required:

 * *OBJ_ACCESS_KEY_ID* - The user's access key
 * *OBJ_SECRET_ACCESS_KEY* - The user's secret key

This environmental variable is required if you using an Object Store other
than ```obj.umiacs.umd.edu```.

 * *OBJ_SERVER*  - The object server to use

For example, if you use the ```bash``` shell, you can add the following to your
```.bashrc``` or ```.bash_profile```.

```bash
export OBJ_ACCESS_KEY_ID="31sdfadDFAHFDN+344qOEIS"
export OBJ_SECRET_ACCESS_KEY="NDSMK3233adfahadflkkPDSH092DSJKDKDJKFDLSFLNK"
```
Or in tcsh you can do the following or add it into your ```.tcshrc```.

```tcsh
setenv OBJ_ACCESS_KEY_ID "31sdfadDFAHFDN+344qOEIS"
setenv OBJ_SECRET_ACCESS_KEY "NDSMK3233adfahadflkkPDSH092DSJKDKDJKFDLSFLNK"
```

You can optionally pass the <code>--access_key</code>, <code>--secret_key</code>
and <code>--server</code> switches to the utilities to get the same behavior.

## Utilties

These utilities use a common syntax for specifying the bucket and an optional
key or path.  The bucket and key are separated by a ```:```.  For example,
```my_bucket:bar.txt``` denotes the bucket ```my_bucket``` and the
key ```bar.txt```.  For more information on a specific utility, you can pass
the flag ```-h``` or ```--help``` for help.

* lsobj
* mkobj
* cpobj
* rmobj
* chobj
* syncobj
* catobj

### lsobj

To list buckets and keys in the Object Store you can use the <b>lsobj</b> command.  
If given without an argument it will list your buckets (this can only list
buckets that you created).

```bash
$ lsobj
bob
test
zeta
```

You can then give it a bucket name to list the contents within that bucket.  If
you were granted access to a bucket that you didn't create you can also use this
command to display its contents.  This will list all the keys in your bucket,
which can take a long time.

```bash
$ lsobj test
-rwx--- 2013-10-04T15:25:09.000Z        1.8 KB  UMIACSCA.pem
-rwx--- 2013-10-04T15:25:24.000Z      311.4 KB  cover.jpg
-rwx--- 2013-10-04T15:27:39.000Z        0.0 b   foo/
-rwx--- 2013-10-04T15:27:40.000Z        0.0 b   foo/bar
-rwx--- 2013-10-04T15:25:32.000Z       31.8 KB  screenshot.jpg
-rwx--- 2013-10-04T15:26:48.000Z        8.3 KB  thunderbird.xpm
================================================================================
        TOTAL:        353.3 KB  6 Files
```

#### Directories
In an Object Store, there are only buckets and keys.  This means that any
apparent directory structure is only emulated using the UNIX ```/``` character
as the last character in a key name.  Any key in the bucket ending in a ```/```
will be interpreted as a directory.  You can also list only subdirectories with the ```lsobj``` utility.

```bash
$ lsobj test:foo/
foo/
-rwx--- 2013-10-04T15:27:39.000Z        0.0 b   foo/
-rwx--- 2013-10-04T15:27:40.000Z        0.0 b   foo/bar
================================================================================
        TOTAL:          0.0 b   2 Files
```

### mkobj

mkobj creates buckets and directories in the Object Store.  

<b>Please note that bucket names are unique in the Object Store, so you may
very well get an error back that the name has already been taken.</b>

```bash
$ mkobj foo
Created bucket foo.
$ lsobj
bob
foo
test
zeta
```

You can also create directories to group your data.

```bash
% mkobj foo:bar/
% lsobj foo
-rwx--- 2013-10-04T15:38:38.000Z        0.0 b   bar/
================================================================================
        TOTAL:          0.0 b   1 Files
```

### cpobj
Copying files to the Object Store can be done per-file or recursively both to and from the Object Store.

To copy a single file to the Object Store you can use <code>cpobj</code> and specify a bucket with a trailing <code>:</code> (with an optional additional path).

```bash
% cpobj test.png foo:
100% |##############################################################################################|
% lsobj foo
-rwx--- 2013-10-04T15:38:38.000Z        0.0 b   bar/
-rwx--- 2013-10-07T20:06:48.000Z       18.3 KB  test.png
================================================================================
        TOTAL:         18.3 KB  2 Files
```

To copy a directory of files you will need to use the <code>-r</code> or <code>--recursive</code> flags.

```bash
% lsobj foo
================================================================================
        TOTAL:          0.0 b   0 Files
% cpobj -r /tmp/stuff foo:stuff
100% |##############################################################################################|
100% |##############################################################################################|
100% |##############################################################################################|
% lsobj foo
-rwx--- 2013-10-08T00:13:52.000Z        0.0 b   stuff/
-rwx--- 2013-10-08T00:13:55.000Z       26.0 KB  stuff/WindowsSecurity.png
-rwx--- 2013-10-08T00:13:54.000Z      226.5 KB  stuff/changepass.tiff
-rwx--- 2013-10-08T00:13:55.000Z       18.3 KB  stuff/test.png
================================================================================
        TOTAL:        270.8 KB  9 Files
```

### rmobj
You can delete your buckets and keys with ```rmobj```.  It can take a bucket and work recursively, asking you to delete all the files and the bucket itself.  It can also just delete specific files in a bucket when given on the command-line.

```bash
% rmobj -r foo
 Are you sure you want to remove all the contents of the bucket 'foo'? [yes/no] yes
 Do you want to remove the bucket 'foo'? [yes/no] no
```

```bash
% lsobj foo
-rwx--- 2013-10-09T18:44:20.000Z        1.0 KB  setup.cfg
-rwx--- 2013-10-09T18:44:17.000Z      781.0 b   setup.py
-rwx--- 2013-10-09T18:44:09.000Z      289.0 b   test-requirements.txt
================================================================================
        TOTAL:          2.0 KB  3 Files
% rmobj foo:setup.cfg foo:setup.py
% lsobj foo
-rwx--- 2013-10-09T18:44:09.000Z      289.0 b   test-requirements.txt
================================================================================
        TOTAL:        289.0 b   1 Files
```

You can also remove directories within a bucket.  To do so, you will need to pass the <code>-r</code> flag.  This will prompt you for the removal of every key under that directory unless the <code>-f</code> flag is passed as well.
```bash
% lsobj foo
-rwx--- 2013-10-10T21:58:17.000Z        0.0 b   research/
-rwx--- 2013-10-10T21:58:17.000Z        0.0 b   research/papers/
-rwx--- 2013-10-10T21:58:18.000Z        0.0 b   research/papers/paper1.tex
-rwx--- 2013-10-10T21:58:18.000Z        0.0 b   research/papers/paper2.tex
-rwx--- 2013-10-10T21:58:18.000Z        0.0 b   research/posters/
-rwx--- 2013-10-10T21:58:18.000Z        0.0 b   research/posters/poster1.tex
-rwx--- 2013-10-10T21:58:18.000Z        0.0 b   research/posters/poster2.tex
================================================================================
        TOTAL:          0.0 b   7 Files
% rmobj -rf foo:research/posters/
% lsobj foo
-rwx--- 2013-10-10T21:58:17.000Z        0.0 b   research/
-rwx--- 2013-10-10T21:58:17.000Z        0.0 b   research/papers/
-rwx--- 2013-10-10T21:58:18.000Z        0.0 b   research/papers/paper1.tex
-rwx--- 2013-10-10T21:58:18.000Z        0.0 b   research/papers/paper2.tex
================================================================================
        TOTAL:          0.0 b   4 Files
```

### chobj
You can change the ACL on a specific key(s) and specify multiple canned ACL policies in a single command.

```bash
% chobj -m clear -p liam:FULL_CONTROL -p derek:FULL_CONTROL foo:test-requirements.txt
```

### syncobj
You can use ```syncobj``` to syncronize files and directories into the object
store.  It does this by comparing the checksum between the local and remote.  This does not follow symlinks and will warn when it encounters files (character,
block, fifo, etc.) that it can not archive.

```bash
% syncobj -r devel/puppet test:
100% |#########################################################################|
```

### catobj
Use ```catobj``` to print the contents of a key to the screen.  This may be
useful to streaming the content of a file to another command for some sort of
processing without having to write the key.  If any errors are printed in the process of running this command, you can be assured that they will be printed to stderr, and should not interfere with what's being printed to stdout.

```bash
% catobj foo:something.txt
Fallaces sunt rerum species.  Mutantur omnia nos et mutamur in illis.
```

## Requirements

These utilties and libraries all work with Python 2.6+ (and are not tested
    under Python 3.x+).  They require the following modules:

- Boto > 2.5.x
- FileChunkIO
- Progressbar
- qav

If running Python 2.6, you need to have the following backports:

- argparse

These are most easily going to be satisfied with a virtualenv.

## Installation

```python setup.py install```
