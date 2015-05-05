# DIFF-DIRS
# Author: Dan Barrese (danbarrese.com)
# Description: Compares two directories and shows any differences
#              in the files/folders contained in those directories.
#              This script is my second Python script, so there are several
#              places in the code that are mangled or hacked together.
# Skills exemplified in this script:
# * Classes
# * Static fields
# * String formatting
# * Equals (and not equals) overrides
# * Method overloading and default parameter values
# * Recursion
# * Reading file info
# * Comparison of file hashes (using filecmp module)
# * Command line interface (using argparse module)
#
# Update History:
# 2013.12.29 [DRB][1.0]    Initial implementation complete.
# 2013.12.29 [DRB][1.01]   Cleaned up comments.
# 2013.12.29 [DRB][1.02]   Fixed typo.
# 2015.05.05 [DRB]         Branched for Python2.

import os
import time
import argparse
import filecmp
import sys

parser = argparse.ArgumentParser(description='diff-dirs: "diffs" file directories.')
parser.add_argument('--path1', '-p1', metavar='P', type=str, nargs=1,
                    dest='path1', required=True,
                    help='The absolute path (P) to the first directory to compare.  (REQUIRED)')
parser.add_argument('--path2', '-p2', metavar='P', type=str, nargs=1,
                    dest='path2', required=True,
                    help='The absolute path (P) to the second directory to compare.  (REQUIRED)')
parser.add_argument('--show-all-files', '-a', dest='show_all_files', action='store_true',
                    help='shows all files even if they are equal')
parser.set_defaults(show_all_files=False)
parser.add_argument('--show-dir-trees', '-t', dest='show_dir_trees', action='store_true',
                    help='shows tree structure of chosen directories')
parser.set_defaults(show_dir_trees=False)
parser.add_argument('--column-separator', '-s', metavar='S', type=str, nargs=1,
                    dest='column_separator', required=False, default='   ',
                    help='The output column separator.  Default is "   " spaces.')
args = parser.parse_args()

output_column_separator = args.column_separator

class File:
    """Represents a file on the storage device."""
    alertlen = 3 # length of +/- alert strings defined in strcmp
    separator = output_column_separator.ljust(len(output_column_separator)+alertlen)

    def __init__(self, full_path="NA", size="NA", date_modified=None):
        self.full_path = full_path.strip()
        if self.full_path.endswith('/'):
            self.full_path = self.full_path[:-1]
        self.name = self.full_path[self.full_path.rfind('/')+1:]
        self.size = size
        self.date_modified = date_modified
        self.processed = False

    def str(self, indent=""):
        ret = indent
        ret += self.full_path.ljust(Folder.longest_filename)
        ret += output_column_separator
        ret += str(self.size).rjust(Folder.longest_size)
        ret += ''.ljust(File.alertlen)
        ret += output_column_separator
        if self.date_modified is None:
            ret += "NA".ljust(Folder.longest_date_modified)
        else:
            ret += time.asctime(self.date_modified).ljust(Folder.longest_date_modified)
        return ret

    def strcmp(self, other_file):
        ret = self.full_path.ljust(Folder.longest_filename)
        ret += output_column_separator
        ret += str(self.size).rjust(Folder.longest_size)
        if self.size > other_file.size:
            ret += "(+)"
        elif self.size < other_file.size:
            ret += "(-)"
        else:
            ret += ''.ljust(File.alertlen)
        ret += output_column_separator
        if self.date_modified is None:
            ret += "NA".ljust(Folder.longest_date_modified)
        else:
            ret += time.asctime(self.date_modified).ljust(Folder.longest_date_modified)
            if self.date_modified > other_file.date_modified:
                ret += "(+)"
            elif self.date_modified < other_file.date_modified:
                ret += "(-)"
            else:
                ret += ''.ljust(File.alertlen)
        return ret

    def __eq__(self, other):
        if other is None:
            return False
        if self.name != other.name:
            return False
        elif self.size != other.size:
            return False
        elif self.date_modified != other.date_modified:
            return False
        else:
            return True

    def __ne__(self, other):
        return not self.__eq__(other)

class Folder:
    """Represents a folder on the storage device."""
    longest_filename = 0
    longest_size = 0
    longest_date_modified = 0
    show_info_with_no_diff = args.show_all_files
    separator                = output_column_separator + "   " + output_column_separator
    separator_no_match       = output_column_separator + "< >" + output_column_separator
    separator_diff_file_info = output_column_separator + "<~>" + output_column_separator
    separator_exact          = output_column_separator + "<=>" + output_column_separator
    separator_diff_hashes    = output_column_separator + "<!>" + output_column_separator
    separator_diff_mdates    = output_column_separator + "<@>" + output_column_separator

    def __init__(self, full_path):
        self.full_path = full_path.strip()
        if self.full_path.endswith('/'):
            self.full_path = self.full_path[:-1]
        self.name = self.full_path[self.full_path.rfind('/')+1:]
        self.folders = []
        self.files = []
        self.header = ""
        self.header_printed = False
        self.processed = False

    def add_file(self, file):
        """Adds a file to the folder."""
        self.files.append(file)

    def add_folder(self, folder):
        """Adds a folder to the folder."""
        self.folders.append(folder)

    def file_count(self):
        """Counts number of files in this folder."""
        return len(self.files)

    def str(self, indent=""):
        ret = indent + self.full_path
        if self.files is not None and len(self.files) > 0:
            for file in self.files:
                ret += "\n" + file.str(indent + "    ")
        if self.folders is not None and len(self.folders) > 0:
            for folder in self.folders:
                ret += "\n" + folder.str(indent + "    ")
        return ret

    def compare_to(self, other_folder):
        """Compare this folder to other (in that direction)."""
        if not self.processed:
            # Define header string for the folders under comparison.
            length_to_middle = Folder.longest_filename + Folder.longest_size + Folder.longest_date_modified + 2*len(File.separator) + File.alertlen
            self.header += ''.ljust(length_to_middle, "-")
            self.header += Folder.separator
            self.header += ''.ljust(length_to_middle, "-")
            self.header += "\n"
            self.header += ("$ " + self.full_path).ljust(length_to_middle)
            self.header += Folder.separator
            if other_folder is not None:
                self.header += "$ " + other_folder.full_path
            self.header += "\n"
            self.header += ''.ljust(length_to_middle, "-")
            self.header += Folder.separator
            self.header += ''.ljust(length_to_middle, "-")

            # Compare all files in this folder to matching files in other folder.
            for file in self.files:
                if not file.processed:
                    # Build file comparison string to show diff.
                    other_file = None
                    if other_folder is not None:
                        # Find matching file in other folder.
                        other_file = next((f for f in other_folder.files if file.name == f.name), None)
                        if other_file is not None:
                            other_file.processed = True
                    print_file_diff(self, file, other_file)

            # Print any remaining files in other folder that were not found in this folder.
            if other_folder is not None:
                other_folder.__compare_files_rtl(self)

            # Process all subfolders of this folder.
            self.__process_subfolders(other_folder)

            # Process all subfolders of other folder.
            if other_folder is not None:
                other_folder.__process_subfolders_rtl(self)

            self.processed = True

    def __compare_files_rtl(self, other_folder):
        """Compare other folder to this (in that direction)."""
        # NOTE: here the "self" refers to the "other" folder.
        for file in self.files:
            if not file.processed:
                # Print file comparison.
                if not other_folder.header_printed:
                    #print(other_folder.header)
                    other_folder.header_printed = True
                sys.stdout.write(File().str())
                sys.stdout.write(''.ljust(File.alertlen) + Folder.separator_no_match)
                print file.str()

    def __process_subfolders_rtl(self, other_folder):
        if other_folder.folders is not None:
            for other_subfolder in other_folder.folders:
                other_subfolder = next((f for f in other_folder.folders if other_subfolder.name == f.name), None)
                if other_subfolder is not None:
                    other_subfolder.compare_to(other_folder)

    def __process_subfolders(self, other_folder):
        if self.folders is not None:
            for subfolder in self.folders:
                if other_folder is not None:
                    other_subfolder = next((f for f in other_folder.folders if subfolder.name == f.name), None)
                    subfolder.compare_to(other_subfolder)
                else:
                    subfolder.compare_to(None)

    def __eq__(self, other):
        if other is None:
            return False
        elif self.full_path != other.full_path:
            return False
        else:
            if self.files is not None:
                for file in self.files:
                    if file not in other.files:
                        return False
            if self.folders is not None:
                for folder in self.folders:
                    if folder not in other.folders:
                        return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

def read_dir(folder):
    """Reads a directory and all files/folders within it, recursively."""
    path = folder.full_path

    # Add all files to the folder.
    for name in os.listdir(path):
        filepath = os.path.join(path, name)
        if os.path.isfile(filepath):
            # Save file info.
            stat = os.stat(filepath)
            bytes = stat[6]
            date_modified = time.localtime(stat[8])
            f = File(filepath, bytes, date_modified)
            folder.add_file(f)

            # Check for longest paramaters.
            if len(f.full_path) > Folder.longest_filename:
                Folder.longest_filename = len(f.full_path)
            if len(str(f.size)) > folder.longest_size:
                Folder.longest_size = len(str(f.size))
            if len(time.asctime(f.date_modified)) > Folder.longest_date_modified:
                Folder.longest_date_modified = len(time.asctime(f.date_modified))

    # Add all folders to the folder.
    for name in os.listdir(path):
        filepath = os.path.join(path, name)
        if not os.path.isfile(filepath):
            # Save folder info.
            stat = os.stat(filepath)
            bytes = stat[6]
            date_modified = time.asctime(time.localtime(stat[8]))
            f = Folder(filepath)
            folder.add_folder(f)

            # Recursively read subdirectory.
            read_dir(f)
    return folder

def print_file_diff(folder, file, other_file):
    """Pretty print the differences between the two given files."""
    diffstr = ""
    files_are_different = False
    if file is None and other_file is not None:
        files_are_different = True
        diffstr = File().str()
        diffstr += ''.ljust(File.alertlen)
        diffstr += Folder.separator_no_match
        diffstr += other_file.str()
    elif file is not None and other_file is None:
        files_are_different = True
        diffstr = file.str()
        diffstr += ''.ljust(File.alertlen)
        diffstr += Folder.separator_no_match
        diffstr += File().str()
    elif file is not None and other_file is not None:
        files_are_different = file != other_file
        diffstr = file.strcmp(other_file)
        if file.size != other_file.size:
            diffstr += Folder.separator_diff_file_info
        else:
            # Hash both files and compare the hashes.
            shallow = False
            if filecmp.cmp(file.full_path, other_file.full_path, shallow):
                files_are_different = False
                if file.date_modified == other_file.date_modified:
                    diffstr += Folder.separator_exact
                else:
                    diffstr += Folder.separator_diff_mdates
            else:
                files_are_different = True
                if file.date_modified == other_file.date_modified:
                    diffstr += Folder.separator_diff_hashes
                else:
                    diffstr += Folder.separator_diff_mdates
        diffstr += other_file.strcmp(file)

    if Folder.show_info_with_no_diff or files_are_different:
        if not folder.header_printed:
            #print(folder.header)
            folder.header_printed = True
        print diffstr

###############################################################################
# MAIN
###############################################################################

path1 = args.path1[0]
fold1 = read_dir(Folder(path1))
path2 = args.path2[0]
fold2 = read_dir(Folder(path2))

if args.show_dir_trees:
    print fold1.str()
    print fold2.str()
    print

print "Legend:"
print "< > means there was no matching file found on the other folder."
print "<~> means the file info is different (i.e. mismatched file size)."
print "<=> means the files are equal by file info and by hash."
print "<!> means the files are equal by file info but their hashes differ."
print "<@> means the files are equal by hashes and file size but have different modification dates."
print ""

fold1.compare_to(fold2)
