#! /usr/bin/env python3
import configparser
import logging
import os
import platform
from importlib.metadata import version

from libsrg.Runner import Runner


class Info:
    def __init__(self, hostname: str = None):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.ver = version('libsrg')
        self.node = platform.node()
        self.node0 = self.node.split('.')[0]
        self.config = configparser.ConfigParser()
        self.uname = os.uname()
        self.like_fedora=False
        self.like_rhel=False
        self.like_redhat=False
        self.like_debian=False
        if hostname:
            userat = f"root@{hostname}"
            self.hostname = hostname
        else:
            userat = None
            self.hostname = self.node0

        r = Runner("cat /etc/os-release", userat=userat)
        if not r.success:
            raise Exception(f"os-release failed for {userat}")
        data = r.so_lines
        # add a section header
        data.insert(0, "[osrelease]")
        self.config.read_string("\n".join(data))
        # for key in self.config:
        #     self.logger.info(key)
        osrelease = self.config['osrelease']
        self.osrelease = osrelease
        # for key, val in osrelease.items():
        #     self.logger.info(f"{key} = {val}")

        # fedora has 'id' lower case, raspian upper
        # configparser says keys are case insensitive
        self.id = (osrelease['ID']).strip('"\'')
        if 'id' in osrelease:
            self.id = osrelease['id'].strip('"\'')
        else:
            self.id = 'unknown'
            self.logger.error(f"'id' not found in {osrelease}")

        # raspian 'ID_LIKE' says, "But you can call me Debian"
        if 'ID_LIKE' in osrelease:
            self.id_like = (osrelease['ID_LIKE']).strip('"\'')
        else:
            self.id_like = self.id
        # self.logger.info(f"id={self.id}, id_like={self.id_like} ")

        if 'PRETTY_NAME' in osrelease:
            self.pretty_name = (osrelease['PRETTY_NAME']).replace('"', '')
        else:
            self.pretty_name = self.id + " " + osrelease['VERSION_ID']

        if "rhel" in self.id or "rhel" in self.id_like:
            self.like_rhel = True
        elif "fedora" in self.id or "fedora" in self.id_like:
            self.like_fedora = True
        elif "debian" in self.id or "debian" in self.id_like:
            self.like_debian = True
        elif "ubuntu" in self.id or "ubuntu" in self.id_like:
            self.like_debian = True

        self.like_redhat = self.like_fedora or self.like_rhel

        self.uid = os.getuid()

    def __str__(self):
        return f"{self.hostname=} {self.id=} {self.id_like=} {self.pretty_name=} {self.uname=}"

    def is_root(self) ->bool:
        return self.uid == 0

    def exit_if_not_root(self):
        if not self.is_root():
            self.logger.critical("Must run as root, uid={self.uid}, hostname={self.hostname}")
            exit(-1)

if __name__ == '__main__':
    # info = Info("nas0")
    info = Info()
    print(f"In version {info.ver} {__file__} on {info.node}")
    print(info)
    print(list(info.osrelease.keys()))
    print(list(info.osrelease.values()))

