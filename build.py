#!/usr/bin/env python

import os
from os import path
import subprocess
import sys
import shutil
import logging
import coloredlogs


frontend_dir = "frontend"
homepage = "homepage"
apps = [
    "redorblack",
    "highorlow",
]

homepage_was_built = False


# Configure Logger
handler = logging.StreamHandler()
logger = logging.getLogger('websocketgames')
logger.addHandler(handler)
fmt = '%(asctime)s %(name)s:%(module)s %(message)s'
coloredlogs.install(logger=logger, level='DEBUG', fmt=fmt)


class Builder:

    files_to_check = [
        'tsconfig.json',
        'node_modules',
    ]

    def __init__(self, project_dir):
        if not path.exists(project_dir):
            raise Exception(f"Path {project_dir} does not exist")

        self.npmexec = "npm"
        if os.name == 'nt':
            self.npmexec = "npm.cmd"

        self.installed = False
        self.project_dir = project_dir
        self.appname = path.basename(project_dir)

    def copy_to_homepage(self, homepage_dir):
        homepage_build = path.join(homepage_dir, 'build')
        source = path.join(self.project_dir, 'build')
        dest = path.join(homepage_build, self.appname)
        if not path.exists(homepage_build):
            raise Exception(f"{homepage_dir} does not exist")

        if not path.exists(source):
            raise Exception(f"{source} does not exist")

        logger.info(f"{self.appname}: Copying {source} to {dest}")
        if path.exists(dest):
            shutil.rmtree(dest)
        shutil.copytree(source, dest)

    def need_install(self):
        package = path.join(self.project_dir, 'package.json')
        package_lock = path.join(self.project_dir, 'package-lock.json')
        modules = path.join(self.project_dir, 'node_modules')

        if not path.exists(modules):
            return True

        if path.exists(package):
            if path.getmtime(package) >= path.getmtime(modules):
                return True

        if path.exists(package_lock):
            if path.getmtime(package_lock) >= path.getmtime(modules):
                return True
        return False

    def need_build(self):
        # If node modules were updated rebuild
        if self.installed:
            return True

        build = path.join(self.project_dir, 'build')
        src = path.join(self.project_dir, 'src')
        if not path.exists(build):
            return True
        build_mtime = path.getmtime(build)

        for file_name in self.files_to_check:
            file = path.join(self.project_dir, file_name)
            if path.exists(file):
                if path.getmtime(file) >= build_mtime:
                    return True

        for root, __subdirList, fileList in os.walk(src, topdown=False):
            for file in fileList:
                if path.getmtime(path.join(root, file)) >= build_mtime:
                    return True
        return False

    def install(self):
        outcome = self._run_npm(['install'])
        # Update Mtime of node modules to be older than the mtime of
        # package.json. Otherwise the following runs will trigger another
        # build.
        node_modules = path.join(self.project_dir, 'node_modules')
        if path.exists(node_modules):
            atime = path.getatime(node_modules)
            mtime = path.getmtime(node_modules) + 1
            os.utime(node_modules, (atime, mtime))
        return outcome

    def build(self):
        return self._run_npm(['run', 'build'])

    def _run_npm(self, args):
        outcome = subprocess.run(
            [self.npmexec] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.project_dir
        )

        if outcome.returncode != 0:
            stdout = outcome.stdout.decode('UTF-8')
            stderr = outcome.stderr.decode('UTF-8')
            err_msg = (
                f"npm {' '.join(args)} failed\n{stdout}\n"
                f"{stderr}\nreturn code={outcome.returncode}"
            )
            print(err_msg)
            sys.exit(1)
        self.installed = True
        return outcome


def build_homepage():
    d = path.join(frontend_dir, homepage)
    builder = Builder(d)
    if builder.need_install():
        logger.info(f"homepage: installing...")
        builder.install()
    else:
        logger.info(f"homepage: no need to install")

    if builder.need_build():
        logger.info(f"building...")
        builder.build()
        global homepage_was_built
        homepage_was_built = True
    else:
        logger.info(f"homepage: no need to build")


def build_apps():
    homepage_dir = path.join(frontend_dir, homepage)
    for app in apps:
        d = path.join(frontend_dir, app)
        appname = path.basename(d)
        builder = Builder(d)
        if builder.need_install():
            logger.info(f"{appname}: installing...")
            builder.install()
        else:
            logger.info(f"{appname}: no need to install")

        if builder.need_build():
            logger.info(f"{appname}: building...")
            builder.build()
        else:
            logger.info(f"{appname}: no need to build")

        global homepage_was_built
        if builder.installed or homepage_was_built:
            logger.info(f"{appname}: copying...")
            builder.copy_to_homepage(homepage_dir)


def main():
    build_homepage()
    build_apps()


# if __name__ == 'main':
main()
