diff-dirs
=========

##Description
This script shows file differences in two directories, recursively.

##Installation
diff-dirs is a Python 3 script, so you must have Python 3 installed to run it.  Run it via `python3 diff-dirs.py <args>`.

##diff-dirs -h
```
usage: diff-dirs.py [-h] --path1 P --path2 P [--show-all-files]
                    [--show-dir-trees]

optional arguments:
  -h, --help            show this help message and exit
  --path1 P, -p1 P      The absolute path (P) to the first directory to
                        compare. (REQUIRED)
  --path2 P, -p2 P      The absolute path (P) to the second directory to
                        compare. (REQUIRED)
  --show-all-files, -a  shows all files even if they are equal
  --show-dir-trees, -t  shows tree structure of chosen directories
```

#Example Showing Output
Here is example output of `python3.3 diff-dirs --path1 test1 --path2 test2 --show-all-files --show-dir-trees`:
```
test1
    test1/hello.txt           6     Thu Jan  9 12:36:52 2014
    test1/hashme.txt         33     Thu Jan  9 12:36:22 2014
    test1/unique.txt         29     Thu Jan  9 12:37:39 2014
    test1/touch.txt           9     Thu Jan  9 12:30:36 2014
    test1/world.txt           6     Thu Jan  9 12:29:17 2014
    test1/foo
        test1/foo/hello.txt       6     Thu Jan  9 12:36:52 2014
        test1/foo/hashme.txt     33     Thu Jan  9 12:36:22 2014
    test1/bar
        test1/bar/touch.txt       9     Thu Jan  9 12:30:36 2014
test2
    test2/hello.txt           6     Thu Jan  9 12:36:52 2014
    test2/hashme.txt         33     Thu Jan  9 12:36:22 2014
    test2/touch.txt           9     Thu Jan  9 12:30:47 2014
    test2/world.txt           9     Thu Jan  9 12:29:41 2014
    test2/baz
        test2/baz/world.txt       9     Thu Jan  9 12:29:41 2014
    test2/foo
        test2/foo/hello.txt       6     Thu Jan  9 12:36:52 2014
        test2/foo/hashme.txt     33     Thu Jan  9 12:36:22 2014
    test2/bar
        test2/bar/touch.txt       9     Thu Jan  9 12:30:36 2014

Legend:
< > means there was no matching file found on the other folder.
<~> means the file info is different (i.e. mismatched file size).
<=> means the files are equal by file info and by hash.
<!> means the files are equal by file info but their hashes differ.
<@> means the files are equal by hashes and file size but have different modification dates.

test1/hello.txt           6     Thu Jan  9 12:36:52 2014     <=>  test2/hello.txt           6     Thu Jan  9 12:36:52 2014    
test1/hashme.txt         33     Thu Jan  9 12:36:22 2014     <!>  test2/hashme.txt         33     Thu Jan  9 12:36:22 2014    
test1/unique.txt         29     Thu Jan  9 12:37:39 2014     < >  NA                       NA     NA                      
test1/touch.txt           9     Thu Jan  9 12:30:36 2014(-)  <@>  test2/touch.txt           9     Thu Jan  9 12:30:47 2014(+) 
test1/world.txt           6(-)  Thu Jan  9 12:29:17 2014(-)  <~>  test2/world.txt           9(+)  Thu Jan  9 12:29:41 2014(+) 
test1/foo/hello.txt       6     Thu Jan  9 12:36:52 2014     <=>  test2/foo/hello.txt       6     Thu Jan  9 12:36:52 2014    
test1/foo/hashme.txt     33     Thu Jan  9 12:36:22 2014     <=>  test2/foo/hashme.txt     33     Thu Jan  9 12:36:22 2014    
test1/bar/touch.txt       9     Thu Jan  9 12:30:36 2014     <=>  test2/bar/touch.txt       9     Thu Jan  9 12:30:36 2014    
```
