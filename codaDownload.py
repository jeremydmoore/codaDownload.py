#!c:\python27\python.exe
#
# A utility to clean up the coda urls to keep just
# the file types I want. Eventually, I want to just
# pass metaIDs to python for it to grab the urls automatically
# through but I'll work on that a little bit over time
#
# v0.30 - added an MD5 hash check for the downloaded tiffs
# v0.20 - set the file's basename as the foldername you want and
#         the program now downloads the TIFFs into that folder
# v0.10 - opens a file, keeps only the .tif files and wgets them
# v0.01 - just get it to open one file, and write everything
#         with *.tif to a second file.
#
import sys, os, contextlib, errno

# context manager under MIT license http://opensource.org/licenses/MIT) here:
# http://code.activestate.com/recipes/576620-changedirectory-context-manager/

@contextlib.contextmanager
def working_directory(path):
    """A context manager which changes the working directory to the given
    path, and then changes it back to its previous value on exit.

    """
    prev_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)

# SO came through with a fix for my mkdir problem:
# http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise


def main(fileIn):
    with open(fileIn) as f:
        lines = []
        for line in f.readlines():
            # add manifest-md5.txt and *.tif to lines
            if line.endswith('manifest-md5.txt\n'):
                lines.append(line)
            if line.endswith('.tif\n'):
                lines.append(line)
                
    # get the directory name from the dir_name.urls file
    dir_name = os.path.splitext(os.path.basename(fileIn))[0]
    mkdir_p(dir_name) # create the directory
    
    with working_directory(dir_name): # change to new directory
        for url in lines:
            os.system('wget %s' %url) # download the files

        with open('manifest-md5.txt') as f:
            lines = []
            hashes = []
            tiffs = []
            # strip everything from the manifest but the .tif files
            for line in f.readlines():
                if line.endswith('.tif\n'):
                    lines.append(line)
            for line in lines:
                # split on white space and grab the hashes
                hashes.append(line.split()[0])
                # split on forward slash and grab the last section
                # which is the filename
                tiffs.append(line.split('/')[-1])

            # a new list where the hashes and tiffs are brought together to look
            # like "hashes  tiffs" so they can be md5 checked in the folder.
            # The lists are zipped together then iterated over.
            new_md5 = ''.join(i + '  ' + j for i,j in zip(hashes,tiffs))

        with open('md5-check.txt', 'w') as f: # write new_md5 to a text file
            for line in new_md5:
                f.write(line)

        os.system('md5sum -c md5-check.txt') #checksum the downloaded tiffs
                

         
def usage():
    print sys.argv[0], "filename"
    print 'find lines ending with ".tif"'
    print 'wget those lines into a folder'
    print 'with the same name as the'
    print 'filename and do a checksum.'

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        usage()
