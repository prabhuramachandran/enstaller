import re
import os
import sys
import subprocess
import shutil
import zipfile
from os.path import dirname, expanduser, isdir, isfile, join
from optparse import OptionParser


verbose = False
eggs_dir = local_repo = prefix = pkgs_dir = python_exe = None


def unzip(zip_path, dir_path):
    """
    unpack the zip file into dir_path, creating directories as required
    """
    print "Unzipping: %r" % zip_path
    print "     into: %r" % dir_path
    z = zipfile.ZipFile(zip_path)
    for name in z.namelist():
        if name.endswith('/') or name.startswith('.unused'):
            continue
        path = join(dir_path, *name.split('/'))
        dpath = dirname(path)
        if not isdir(dpath):
            os.makedirs(dpath)
        fo = open(path, 'wb')
        fo.write(z.read(name))
        fo.close()
    z.close()


def parse_dists_file(path):
    pat = re.compile(r'(([+-]{2})\s*)?(\w\S+)$')
    for line in open(path):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        m = pat.match(line)
        if m is None:
            sys.exit('Error: invalid line in dists.txt: %r' % line)
        pkg = m.group(3)
        if pkg.endswith('.egg'):
            pkg = pkg[:-4]
        yield pkg


def registry_pkg(pkg):
    return join(pkgs_dir, pkg, 'EGG-INFO', 'registry.txt')


def cp_to_repo(pkg, force=False):
    fn = pkg + '.egg'
    path = join(local_repo, fn)
    if not isfile(path) or force:
        shutil.copyfile(join(eggs_dir, fn), path)
    return path


def bootstrap_enstaller(pkg):
    assert pkg.startswith('enstaller-')
    code = ("import sys;"
            "sys.path.insert(0, %r);"
            "from egginst.bootstrap import main;"
            "main()" % cp_to_repo(pkg))
    subprocess.check_call([python_exe, '-c', code])


def update_pkgs(pkgs):
    if not isdir(local_repo):
        os.makedirs(local_repo)

    if not isfile(python_exe):
        unzip(cp_to_repo(pkgs[0]), prefix)

    if not isfile(registry_pkg(pkgs[1])):
        bootstrap_enstaller(pkgs[1])

    if sys.platform == 'win32':
        egginst_py = join(prefix, r'Scripts\egginst-script.py')
    else:
        egginst_py = join(prefix, 'bin/egginst')

    for pkg in pkgs[1:]:
        if isfile(registry_pkg(pkg)):
            continue
        subprocess.check_call([python_exe, egginst_py, '--hook',
                               '--pkgs-dir', pkgs_dir, cp_to_repo(pkg)])


def main():
    if sys.platform == 'win32' and not sys.executable.endswith('python.exe'):
        default_eggs_dir = dirname(sys.executable)
    else:
        default_eggs_dir = os.getcwd()


    p = OptionParser(usage="usage: %prog [options]",
                     description=__doc__)

    p.add_option("--root",
                 action="store",
                 default=join(expanduser('~'), 'canopy'),
                 help="install location, defaults to %default",
                 metavar='PATH')

    p.add_option("--eggs-dir",
                 action="store",
                 default=default_eggs_dir,
                 help="directory with eggs to install (and dists.txt), "
                      "defaults to %default",
                 metavar='PATH')

    p.add_option('-v', "--verbose", action="store_true")

    opts, args = p.parse_args()

    if args:
        p.error('no argument expected, try -h')

    global verbose, eggs_dir, local_repo, prefix, pkgs_dir, python_exe

    eggs_dir = opts.eggs_dir
    verbose = opts.verbose

    if verbose:
        print "eggs_dir = %r" % eggs_dir

    pkgs = list(parse_dists_file(join(eggs_dir, 'dists.txt')))

    if verbose:
        for pkg in pkgs:
            print "\t" + pkg

    local_repo = join(opts.root, 'repo')
    prefix = join(opts.root, pkgs[0])
    pkgs_dir = join(prefix, 'pkgs')
    if sys.platform == 'win32':
        python_exe = join(prefix, 'python.exe')
    else:
        python_exe = join(prefix, 'bin', 'python')

    if verbose:
        print "local_repo = %r" % local_repo
        print "prefix = %r" % prefix
        print "python_exe = %r" % python_exe

    update_pkgs(pkgs)
    return subprocess.call([
            python_exe,
            join(pkgs_dir, pkgs[-1], 'EGG-INFO', 'app_entry.py')
            ])


if __name__ == '__main__':
    sys.exit(main())
