
import tarfile
import os.path


def make_tarfile_from_files(output_filename, source_filenames,
                            squash_hierarchy=False):
    '''
    Given an output filename and a list of files, construct a tar.gz archive

    If `squash_hierarchy` is True, put all files in a flat hierarchy
    '''
    tar = tarfile.open(output_filename, "w:gz")
    for name in source_filenames:
        if squash_hierarchy:
            tar.add(name, arcname=os.path.basename(name))
        else:
            tar.add(name)
    tar.close()


def make_tarfile_from_directory(output_filename, source_dir):
    '''
    Make a tarfile of name `output_filename` from a `source_dir` where all
    files in the source_dir are encapsulated in a root directory named after
    the last part of source_dir.

    For example, imagine I have the following hierarchy:
        /tmo/liamfoo/archive/file1
        /tmp/liamfoo/archive/file2
        /tmp/liamfoo/recent/file3
        /tmp/liamfoo/recent/file4

    If source_dir=/tmp/liamfoo, the resulting tar would contain a directory
    named "liamfoo" at the top level with directories "archive" and "recent"
    inside of that.
    '''
    tar = tarfile.open(output_filename, "w:gz")
    tar.add(source_dir, arcname=os.path.basename(source_dir))
    tar.close()
