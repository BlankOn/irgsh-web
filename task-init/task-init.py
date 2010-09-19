#!/usr/bin/env python

import ConfigParser, os
import errno
import sys 
import xmlrpclib
import tarfile
import shutil
from irgsh.dvcs import *
from debian_bundle import deb822
from debian_bundle.changelog import Changelog


class TaskInit:
    def __init__(self):
        config = ConfigParser.ConfigParser()
        files = config.read(['/etc/irgsh/task-init.conf','task-init.conf'])
        try:
            server = config.get('task', 'server')
        except ConfigParser.NoSectionError:
            print "No 'task' section in configuration file(s):"
            print files
            sys.exit(-1)
        except ConfigParser.NoOptionError:
            print "No 'server' option in configuration file(s):"
            print files
            sys.exit(-1)
             
        try:
            self.copy_path = config.get('task', 'copy-path')
        except ConfigParser.NoOptionError:
            print "No 'copy-path' option in configuration file(s):"
            print files
            sys.exit(-1)
 
        list = []
        self.x = xmlrpclib.ServerProxy(server)
        try:
            list = self.x.get_new_tasks()
        except Exception as e:
            print "Unable to contact %s:" % server
            print e
            sys.exit(-1)

        for entry in list:
            self.init_task(entry)

    def init_task(self, entry):
        info = self.x.get_task_info(entry)
        path = os.path.join("./", "task", str(entry))
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

        try:
            self.init_and_copy_debian(info, entry, path)
            self.init_and_copy_orig(info, entry, path)
            self.x.start_assigning(entry)
        except Exception as e:
            print "Unable to initialize task %d: %s" % (entry, e)
            self.x.task_init_failed(entry, str(e))

    def init_and_copy_debian(self, info, entry, path):
        d = DvcsLoader(info['debian_vcs'], info['debian_url'])        
        if d.instance.export(path) == False:
            raise Exception("Unable to export")

        basename = os.path.join(path, os.path.basename(d.instance.url))
        try:
            debian_info = self.explode_debian(basename)
            (code, msg) = self.x.populate_debian_info(entry, debian_info)
            if code == -1:
                raise Exception(msg)
        except Exception as e:
            shutil.rmtree(basename)
            raise

        t = tarfile.open(basename + ".tar.bz2", "w:bz2")
        t.add(basename)
        t.close()
        shutil.rmtree(basename)
        (code, msg) = self.x.set_debian_copy(entry, "%s/task/%d/%s.tar.bz2" % (self.copy_path, entry, os.path.basename(basename)))

    def explode_debian(self, dir):
        control = os.path.join(dir, "debian", "control")
        if not os.path.isfile(control):
            raise Exception("Not a debian directory")

        f = open(control)
        source = ""
        packages = []
        for p in deb822.Packages.iter_paragraphs(f):
            if p.has_key("Source"):
                source = p["Source"]
                name = source
                arch = 'source'
            else:
                name = p["Package"]
                arch = p["Architecture"]

            package = {
                "package": name,
                "architecture": arch, 
            }
            packages.append(package)

        f.close()
        if source == "":
            raise Exception("No source package found")

        if len(packages) < 2:
            raise Exception("No binary packages found")

        changelog = os.path.join(dir, "debian", "changelog")
        if not os.path.isfile(changelog):
            raise Exception("Changelog not found")

        f = open(changelog)
        c = Changelog(f)
        version = str(c.get_version())
        source_c = c.get_package()
        c_line = ""
        copy = 0
        f.seek(0)
        for line in f:
            if line == "\n":
                copy = copy + 1
                continue
            if copy == 1:
                c_line += line

            if copy == 2:
                break

        f.close()

        if source_c != source:
            raise Exception("Mismatch source package names")

        retval = { "source": source,
                   "version": version, 
                   "changelog": c_line,
                   "packages": packages, 
                }

        return retval


    def init_and_copy_orig(self, info, entry, path):
        if info['orig_url'] == "":
            return

        d = DvcsLoader('tarball', info['orig_url'])        
        if d.instance.export(path) == False:
            raise Exception("Unable to export")

        (code, msg) = self.x.set_orig_copy(entry, "%s/task/%d/%s.tar.bz2" % (self.copy_path, entry, os.path.basename(info['orig_url'])))

t = TaskInit()
