#!/usr/bin/env python3
import logging
import sys

from libsrg.LoggingAppBase import LoggingAppBase
from libsrg.Runner import Runner
from libsrg.Runner2 import Runner2


class SnapshotHolder:

    def __init__(self, snap: str, userat: str):
        self.snap = snap
        self.userat = userat
        self.logger = logging.getLogger(self.__class__.__name__)

    def __enter__(self):
        r = Runner(["zfs", "hold", "ztool-copy", self.snap], userat=self.userat)
        if not r.success and r.ret == 1 and r.se_lines and r.se_lines[0].find("tag already exists on this dataset") > 1:
            self.logger.info(r)
        else:
            r.raise_if_failed()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        r = Runner(["zfs", "release", "ztool-copy", self.snap], userat=self.userat)
        r.raise_if_failed()


"""
# python -m libsrg.ztool copy --help
This is a multipurpose zfs support utility

It can always be run as
* python -m libsrg.ztool mode rest...

It is normally installed with a short stub in /usr/local/bin/ztool.py, which can be run as
* ztool.py mode rest...

First argument is a mandatory positional arguments for mode, and must be one of:
  {prep,copy,xfer,info,permissions}

-----------------------------------------------------------------------------------------
COPY:
* copies from source to destination volume
* src and/or dest can be on another node if the userat arguments are used (and ssh keys are setup)
* can create new destination, or update an old copy with newer snapshots
  * first,last args allow manual control of snapshots
  * default is to copy range from first common snapshot to latest at src

usage: usage: %prog copy [-h] [--libsrg] [--logfile LOGFILE] [--logging {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}] [--src_userat SRC_USERAT] [--dst_userat DST_USERAT] [--src SRC]
                              [--dst DST] [--first FIRST] [--last LAST]
                              {prep,copy,xfer,info,permissions}



options:
  -h, --help            show this help message and exit
  --libsrg              Print version of libsrg and exit
  --logfile LOGFILE     file to log to (default = stdout)
  --logging {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}, --level {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}
  --src_userat SRC_USERAT
                        user@host for src
  --dst_userat DST_USERAT
                        user@host for dst
  --src SRC             source dataset
  --dst DST             destination dataset
  --first FIRST         index of first snapshot
  --last LAST           index of last snapshot

-------------------------------------------------------------------------------------------------
INFO: 
Sends formatted pool information to stdout
This is intended to print and keep a zfs backup disk

usage: usage: %prog info pools... [-h] [--libsrg] [--logfile LOGFILE] [--logging {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}] [--src_userat SRC_USERAT] [--dst_userat DST_USERAT] [--first FIRST]
                              [--last LAST]
                              {prep,copy,xfer,info,permissions} [pools ...]

positional arguments:
  {prep,copy,xfer,info,permissions}
  pools                 ZFS pools to inventory

options:
  -h, --help            show this help message and exit
  --libsrg              Print version of libsrg and exit
  --logfile LOGFILE     file to log to (default = stdout)
  --logging {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}, --level {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}
  --src_userat SRC_USERAT
                        user@host for src
  --dst_userat DST_USERAT
                        user@host for dst
  --first FIRST         index of first snapshot
  --last LAST           index of last snapshot

========== sample python -m libsrg.ztool info ZRaid
  pool: ZRaid
 state: ONLINE
  scan: scrub repaired 0B in 00:30:31 with 0 errors on Mon Jun 12 02:00:32 2023
config:

	NAME                                       STATE     READ WRITE CKSUM
	ZRaid                                      ONLINE       0     0     0
	  ata-WDC_WDS100T2G0A-00JH30_191077453312  ONLINE       0     0     0

errors: No known data errors

NAME                                  AVAIL   USED  USEDSNAP  USEDDS  USEDREFRESERV  USEDCHILD  QUOTA
ZRaid                                  488G   412G        0B     29K             0B       412G   none
ZRaid/CLONES                           488G    24K        0B     24K             0B         0B   none
ZRaid/COPIES                           488G    24K        0B     24K             0B         0B   none
ZRaid/COPYTEST                         488G   428K        0B     25K             0B       403K   none
ZRaid/COPYTEST/LIBVIRT_QEMU            488G   379K      350K     29K             0B         0B   none
ZRaid/COPYTEST/ZAP                     488G    24K        0B     24K             0B         0B   none
ZRaid/LEGACY                           488G    24K        0B     24K             0B         0B   none
ZRaid/MIGRATED                         488G    24K        0B     24K             0B         0B   none
ZRaid/PRIMARY                          488G   409G        0B     26K             0B       409G   none
ZRaid/PRIMARY/NFSNONE                  488G    24K        0B     24K             0B         0B   none
ZRaid/PRIMARY/NFSPUB                   488G    24K        0B     24K             0B         0B   none
ZRaid/PRIMARY/NFSUSER                  488G   409G        0B     24K             0B       409G   none
ZRaid/PRIMARY/NFSUSER/KUSERS           291G   409G      246G    163G             0B         0B   700G
ZRaid/PRIMARY/NFSUSER/LIBVIRT_IMAGES   400G  1.65M      270K   1.39M             0B         0B   400G
ZRaid/PRIMARY/NFSUSER/LIBVIRT_QEMU    10.0G   437K      408K     29K             0B         0B    10G

ZRaid/COPYTEST/LIBVIRT_QEMU@pyznap_2023-01-26_21:50:02_frequent ... ZRaid/COPYTEST/LIBVIRT_QEMU@pyznap_2022-11-25_20:34:47_yearly
ZRaid/PRIMARY/NFSUSER/KUSERS@pyznap_2023-06-15_15:50:01_frequent ... ZRaid/PRIMARY/NFSUSER/KUSERS@pyznap_2022-12-07_15:25:01_yearly
ZRaid/PRIMARY/NFSUSER/LIBVIRT_IMAGES@pyznap_2023-06-15_15:50:02_frequent ... ZRaid/PRIMARY/NFSUSER/LIBVIRT_IMAGES@pyznap_2022-11-25_20:34:45_yearly
ZRaid/PRIMARY/NFSUSER/LIBVIRT_QEMU@pyznap_2023-06-15_15:50:02_frequent ... ZRaid/PRIMARY/NFSUSER/LIBVIRT_QEMU@pyznap_2022-11-25_20:34:47_yearly
zfs-2.1.12-1
zfs-kmod-2.1.12-1

     Static hostname: kylo.home.goncalo.name
           Icon name: computer-desktop
             Chassis: desktop 🖥️
          Machine ID: aaa259174e6448ecb8f2ec4fa5163b48
             Boot ID: c1311e878073477d977123a2ce95e9f1
    Operating System: Fedora Linux 38 (Workstation Edition)
         CPE OS Name: cpe:/o:fedoraproject:fedora:38
      OS Support End: Tue 2024-05-14
OS Support Remaining: 10month 4w
              Kernel: Linux 6.3.7-200.fc38.x86_64
        Architecture: x86-64
     Hardware Vendor: System76, Inc.
      Hardware Model: Wild Dog Pro
    Firmware Version: F9b Z5
       Firmware Date: Mon 2018-01-29

--------------------------------------------------------------------
# prep

* ztool.py prep --pool POOL

Prepares pool by creating the standard set of subvolumes
POOL/CLONES
POOL/COPIES
POOL/PRIMARY/NFSPUB
POOL/PRIMARY/NFSUSER
POOL/PRIMARY/NFSNONE
POOL/MIGRATED

usage: usage: %prog [options] [-h] [--libsrg] [--logfile LOGFILE] [--logging {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}] [--src_userat SRC_USERAT] [--dst_userat DST_USERAT] [--pool POOL]
                              {prep,copy,xfer,info,permissions}

positional arguments:
  {prep,copy,xfer,info,permissions}

options:
  -h, --help            show this help message and exit
  --libsrg              Print version of libsrg and exit
  --logfile LOGFILE     file to log to (default = stdout)
  --logging {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}, --level {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}
  --src_userat SRC_USERAT
                        user@host for src
  --dst_userat DST_USERAT
                        user@host for dst
  --pool POOL           pool name

---------------------------------------------------------------------
# xfer

Performs a copy, then dismounts source and mounts destination at original mountpoint

---------------------------------------------------------------------
# permissions

sets ownership and permissions for files in NFSPUB subvolumes

# python -m libsrg.ztool permissions  --help
usage: usage: %prog [options] [-h] [--libsrg] [--logfile LOGFILE] [--logging {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}] [--src_userat SRC_USERAT] [--dst_userat DST_USERAT] [--host HOST]
                              [--chown]
                              {prep,copy,xfer,info,permissions}

positional arguments:
  {prep,copy,xfer,info,permissions}

options:
  -h, --help            show this help message and exit
  --libsrg              Print version of libsrg and exit
  --logfile LOGFILE     file to log to (default = stdout)
  --logging {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}, --level {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}
  --src_userat SRC_USERAT
                        user@host for src
  --dst_userat DST_USERAT
                        user@host for dst
  --host HOST           host name
  --chown               enable chown pubshare

"""


class Ztool(LoggingAppBase):

    def __init__(self):
        super().__init__()

        self.first_snap = None
        self.n_snaps = None
        self.last_snap = None
        self.verb_lookup = {
            "prep": self.parse_prep,
            "copy": self.parse_copy,
            "xfer": self.parse_xfer,
            "info": self.parse_inventory,
            "permissions": self.parse_permissions,
        }

        self.report: list[str] = []

        all_verbs = self.verb_lookup.keys()
        self.parser.add_argument("verb", action='store', choices=all_verbs, default=None)
        self.parser.add_argument('--src_userat', help='user@host for src', dest='src_userat', type=str,
                                 default="root@localhost")
        self.parser.add_argument('--dst_userat', help='user@host for dst', dest='dst_userat', type=str,
                                 default="root@localhost")

        if len(sys.argv) < 2 or sys.argv[1] not in all_verbs:
            # this call enables logging and will fail with message
            self.perform_parse()
            self.logger.critical(f"bad verb: {sys.argv} not in {all_verbs}")
            exit()

        self.verb_lookup[sys.argv[1]]()

    def parse_permissions(self):
        # setup any program specific command line arguments
        self.parser.add_argument('--host', help='host name', dest='host', type=str, default="localhost")
        self.parser.add_argument('--chown', help='enable chown pubshare', dest='chown',
                                 action='store_true', default=False)
        # invoke the parser
        self.perform_parse()
        #
        self.logger.info(f"after parsing {self.args}")
        #
        self.do_permissions()

    def do_permissions(self):
        userat = f"root@{self.args.host}"

        self.do_permissions_samba(userat)

        r = Runner(["zpool", "list", "-H", "-o", "name"], userat=userat)
        r.raise_if_failed()
        for pool in r.so_lines:
            self.do_permissions_pool(pool, userat)

    def do_permissions_samba(self, userat):
        r = Runner(["grep", "path", "/etc/samba/gnas_gpub.conf"], userat=userat)
        if not r.success:
            return
        r1 = Runner("setsebool -P samba_export_all_ro=1 samba_export_all_rw=1", userat=userat)
        for line in r.so_lines:
            path = line.split('=')[-1].strip()
            r2 = Runner(["semanage", "fcontext", "-at", "samba_share_t", f'"{path}(/.*)?"'], userat=userat)
            if r2.ret == 1 and r2.se_lines and r2.se_lines[0].endswith("already defined"):
                self.logger.info(r2)
            else:
                r2.raise_if_failed()
            r3 = Runner(["restorecon", "-v", "-R", path], userat=userat)
            r3.raise_if_failed()

    def do_permissions_pool(self, pool, userat):
        r = Runner(["zfs", "list", "-H", "-o", "name", "-r", pool], userat=userat)
        r.raise_if_failed()
        vols = r.so_lines
        leafs = vols.copy()
        for v1 in vols:
            for v2 in vols:
                if v1 == v2 or v2 not in leafs:
                    continue
                if v1.startswith(v2 + "/"):
                    leafs.remove(v2)
                    break
        self.logger.info(f"{leafs=}")
        for v in leafs:
            # if v.startswith(f"{pool}/COPIES/"):
            #     r1 = Runner(["zfs", "set", "readonly=on", v], userat=userat)
            if self.args.chown and (
                    v.startswith(f"{pool}/PRIMARY/NFSPUB/") or v.startswith(f"{pool}/PRIMARY/NFSNONE/")):
                rs = Runner(["zfs", "get", "mountpoint", "-H", v, ], userat=userat)
                if len(rs.so_lines) != 1:
                    raise Exception(f"expected one output line in {rs}")
                _v, _mp, mountpoint, source = rs.so_lines[0].split()
                r2 = Runner(["chown", "-Rc", "pubshare:pubshare", mountpoint], userat=userat)
                r2.raise_if_failed()

    def parse_prep(self):
        # setup any program specific command line arguments
        self.parser.add_argument('--pool', help='pool name', dest='pool', type=str, default="ZTINY")
        self.parser.add_argument('--mask', help='network mask', dest='mask', type=str, default="10.0.4.1/25")
        # invoke the parser
        self.perform_parse()
        #
        self.logger.info(f"after parsing {self.args}")
        #
        self.verify_pool()
        self.prep_pool()

    def parse_xfer(self):
        self.parser.add_argument('--src', help='source dataset', dest='src', type=str,
                                 default="ZRaid/MASTER/LIBVIRT_QEMU")
        self.parser.add_argument('--dst', help='destination dataset', dest='dst', type=str,
                                 default="ZRaid/COPYTEST/LIBVIRT_QEMU")
        self.parser.add_argument('--first', help='index of first snapshot', dest='first', type=int, default=0)
        self.parser.add_argument('--last', help='index of last snapshot', dest='last', type=int, default=-1)
        # invoke the parser
        self.perform_parse()
        #
        self.logger.info(f"after parsing {self.args}")
        #
        rs = Runner(["zfs", "get", "mountpoint", "-H", self.args.src, ], userat=self.args.src_userat)
        if len(rs.so_lines) != 1:
            raise Exception(f"expected one output line in {rs}")
        vol, mp, src_mountpoint, source = rs.so_lines[0].split()
        # if source != "local":
        #     raise Exception(f"expected mountpoint to be local {rs}")

        self.do_copy()
        if source == "local":
            rs2 = Runner(["zfs", "inherit", "mountpoint", self.args.src, ], userat=self.args.src_userat)
            rs2.log(throw=True)
            rd2 = Runner(["zfs", "set", f"mountpoint={src_mountpoint}", self.args.dst, ], userat=self.args.dst_userat)
            rd2.log(throw=True)

    def parse_copy(self):
        self.parser.add_argument('--src', help='source dataset', dest='src', type=str,
                                 default="ZRaid/MASTER/LIBVIRT_QEMU")
        self.parser.add_argument('--dst', help='destination dataset', dest='dst', type=str,
                                 default="ZRaid/COPYTEST/LIBVIRT_QEMU")
        self.parser.add_argument('--first', help='index of first snapshot', dest='first', type=int, default=0)
        self.parser.add_argument('--last', help='index of last snapshot', dest='last', type=int, default=-1)
        self.parser.add_argument('--replicate', help='Add -R replicate command to send', dest='repl',action='store_true', default=False )
        # invoke the parser
        self.perform_parse()
        #
        self.logger.info(f"after parsing {self.args}")
        #
        self.do_copy()

    def prep_pool(self):
        self.create_vol("CLONES")
        self.create_vol("COPIES")
        self.create_vol("PRIMARY/NFSPUB")
        self.create_vol("PRIMARY/NFSUSER")
        self.create_vol("PRIMARY/NFSNONE")
        self.create_vol("MIGRATED")

        if self.args.mask:
            enab = "rw="+self.args.mask
        else:
            enab = "rw=*"

        self.set_parent("PRIMARY/NFSNONE", "sharenfs", "off")
        self.set_parent("PRIMARY/NFSUSER", "sharenfs", enab)
        # noinspection PyPep8
        opts = f"{enab},wdelay,no_subtree_check,mountpoint,sec=sys,all_squash,anonuid=3300,anongid=3300,secure,async"
        self.set_parent("PRIMARY/NFSPUB", "sharenfs",
                        opts)

        self.set_parent("COPIES", "sharenfs", "off")
        self.set_parent("COPIES", "readonly", "on")

        self.set_parent("MIGRATED", "sharenfs", "off")

    def recursive_create(self, vol: str, userat: str):
        # read a param as proof of existance
        r0 = Runner(["zfs", "get", "readonly", "-H", vol, ], userat=userat)
        self.logger.info(r0)
        if not r0.success:
            # find parent
            parts = vol.split('/')
            if len(parts) < 2:
                raise (f"no parent for {vol}")
            pvol = '/'.join(parts[0:-1])  # excludes last

            self.logger.info(f"{vol} not found, checking {pvol}")
            # ensure parent is ready
            self.recursive_create(pvol, userat)
            self.logger.info(f"{vol} not found, back from checking {pvol}")

            # see if parent was readonly and set readonly=off
            r1 = Runner(["zfs", "get", "readonly", "-H", pvol, ], userat=userat)
            r1.log(throw=True)
            if len(r1.so_lines) != 1:
                raise Exception(f"expected one output line in {r1}")
            _, _, old_ro, source = r1.so_lines[0].split('\t')
            if old_ro in ["on", "True"]:
                r2 = Runner(["zfs", "set", "readonly=off", pvol, ], userat=userat)
                r2.log(throw=True)
            r3 = Runner(["zfs", "create", vol], userat=userat)
            r3.log(throw=True)
            if old_ro in ["on", "True"]:
                if source == "local":
                    r4 = Runner(["zfs", "set", "readonly=on", pvol, ], userat=userat)
                    r4.log(throw=True)
                else:
                    r5 = Runner(["zfs", "inherit", "readonly", pvol, ], userat=userat)
                    r5.log(throw=True)

    def set_parent(self, parvol: str, vname: str, value: str):
        pool = self.args.pool
        vol = pool + "/" + parvol
        r1 = Runner(["zfs", "set", f"{vname}={value}", vol], userat=self.args.dst_userat)
        self.logger.info(r1)
        r2 = Runner(["zfs", "list", "-rH", "-o", "name", vol, ], userat=self.args.dst_userat)
        for subv in r2.so_lines:
            if subv == vol:
                continue
            self.logger.info(subv)
            r3 = Runner(["zfs", "inherit", vname, subv], userat=self.args.dst_userat)
            self.logger.info(r3)

    def create_vol(self, vname: str):
        pool = self.args.pool
        vol = pool + "/" + vname

        r1 = Runner(["zfs", "create", "-p", "-u", vol], userat=self.args.dst_userat)
        r2 = Runner(["zfs", "list", vol], userat=self.args.dst_userat)
        if r2.success:
            self.logger.info(r2)
        else:
            self.logger.error(r1)
            self.logger.error(r2)
            exit()

    def verify_pool(self):
        if not self.args.pool:
            self.logger.error("--pool must be specified")
            exit()

        r = Runner(["zpool", "status", self.args.pool], userat=self.args.dst_userat)
        self.logger.info(r)

    def do_copy(self):



        rs = Runner(["zfs", "list", "-o", "name", "-t", "snapshot", "-r", "-H", self.args.src],
                    userat=self.args.src_userat)
        # for l in r.so_lines[0:5]:
        #     self.logger.info(l.split())
        # for l in r.so_lines[-5:]:
        #     self.logger.info(l.split())
        if len(rs.so_lines) < 1:
            self.logger.error("source dataset does not have any snapshots")
            exit(-1)
        self.first_snap = rs.so_lines[self.args.first]
        self.last_snap = rs.so_lines[self.args.last]
        self.n_snaps = len(rs.so_lines)

        self.recursive_create(self.args.dst, self.args.dst_userat)

        rd = Runner(["zfs", "list", "-o", "name", "-t", "snapshot", "-r", "-H", self.args.dst],
                    userat=self.args.dst_userat)

        if not rd.success:
            c = Runner(["zfs", "create", "-p", "-u", self.args.dst], userat=self.args.dst_userat)
            if c.success:
                self.logger.info(c)
            else:
                self.logger.error(c)
                exit()

        rd = Runner(["zfs", "list", "-o", "name", "-t", "snapshot", "-r", "-H", self.args.dst],
                    userat=self.args.dst_userat)
        if not rd.success:
            self.logger.error(rd)
            exit()

        src_snaps_list = [x.split("@")[-1] for x in rs.so_lines]
        src_snaps_set = set(src_snaps_list)
        dst_snaps_list = [x.split("@")[-1] for x in rd.so_lines]
        dst_snaps_set = set(dst_snaps_list)
        common_snaps_set = src_snaps_set.intersection(dst_snaps_set)
        if not common_snaps_set:
            self.logger.info(f"source does not have any snapshots matching {dst_snaps_set}")
            self.logger.info(f"--- Transfer initial snapshot ({self.args.first} of {self.n_snaps}) ---")
            cmd1 = ["zfs", "send", self.first_snap]
            cmd2 = ["zfs", "receive", "-F", "-u", self.args.dst]
            if self.args.repl:
                cmd1.append("-R")
            with SnapshotHolder(snap=self.first_snap, userat=self.args.src_userat):
                s = Runner2(cmd1, cmd2, userat1=self.args.src_userat, userat2=self.args.dst_userat)
            if s.success:
                self.logger.info(s)
            else:
                self.logger.error(s)
                exit()
        else:
            # reform a list of common snapshots in original order, dont depend on alphabetical sort
            common_snaps_list = [s for s in src_snaps_list if s in common_snaps_set]
            # best = sorted(list(common_snaps_set))[-1]
            best = common_snaps_list[-1]
            self.first_snap = f"{self.args.src}@{best}"
            self.logger.info(f"selected {self.first_snap} as last common snapshot")

        rd = Runner(["zfs", "list", "-o", "name", "-t", "snapshot", "-r", "-H", self.args.dst],
                    userat=self.args.dst_userat)
        if not rd.success:
            self.logger.error(rd)
            self.logger.error(f"Could not read snapshot from existing dst {self.args.dst}")
            exit()

        if self.first_snap == self.last_snap:
            self.logger.info(
                f"No incremental snapshots -- last common ({self.first_snap} is also last {self.last_snap}) ---")
        else:
            self.logger.info(f"Transfer incremental snapshots ({self.first_snap} to  {self.last_snap}) ---")
            cmd1 = ["zfs", "send", "-I", self.first_snap, self.last_snap]
            cmd2 = ["zfs", "receive", "-F", "-u", self.args.dst]
            if self.args.repl:
                cmd1.append("-R")
            with (SnapshotHolder(snap=self.first_snap, userat=self.args.src_userat),
                  SnapshotHolder(snap=self.last_snap, userat=self.args.src_userat)):
                s = Runner2(cmd1, cmd2, userat1=self.args.src_userat, userat2=self.args.dst_userat)
            if s.success:
                self.logger.info(s)
            else:
                self.logger.error(s)
                exit()

    def parse_inventory(self):
        self.parser.add_argument('pools', nargs="*", help='ZFS pools to inventory', type=str)
        self.parser.add_argument('--first', help='index of first snapshot', dest='first', type=int, default=0)
        self.parser.add_argument('--last', help='index of last snapshot', dest='last', type=int, default=-1)
        # invoke the parser
        self.perform_parse()
        #
        self.logger.info(f"after parsing {self.args}")
        #
        self.do_inventory()

    def do_inventory(self):
        if self.args.pools:
            for p in self.args.pools:
                self.process1pool(p)
        else:
            r0 = Runner(["zpool", "list", "-o", "name", "-H"], userat=self.args.dst_userat)
            if r0.success:
                for lin in r0.so_lines:
                    self.process1pool(lin)
        self.trailer()
        print()
        for line in self.report:
            print(line)
        print()

    def trailer(self):
        self.run_append(["zfs", "version"])
        self.run_append(["date"])
        self.run_append(["hostnamectl --json=pretty"])

    def run_append(self, cmd):
        r0 = Runner(cmd, userat=self.args.dst_userat)
        if r0.success:
            self.report.extend(r0.so_lines)
            self.report.append("")
        else:
            raise (Exception(r0))

    def process1pool(self, pool: str):
        r0 = Runner(["zpool", "status", pool], userat=self.args.dst_userat)
        if r0.success:
            self.report.extend(r0.so_lines)
            self.report.append("")
        else:
            raise (Exception(r0))
        r0 = Runner(["zfs", "list", "-o", "name,avail,used,usedsnap,usedds,quota", "-r", pool], userat=self.args.dst_userat)
        if r0.success:
            self.report.extend(r0.so_lines)
            self.report.append("")
        else:
            raise (Exception(r0))

        # r = Runner(["zfs", "list", "-t", "snapshot", "-r", "-H", pool])
        r = Runner(["zfs", "list", "-H", "-o", "name", "-r", pool], userat=self.args.dst_userat)
        if r.success:
            for vol in r.so_lines:
                self.logger.info(f"{vol=}")
                self.process1vol(vol)

    def process1vol(self, vol: str):
        if "/" not in vol:
            return
        r = Runner(["zfs", "list", "-t", "snapshot", "-d", "1", "-H", "-o", "name", vol], userat=self.args.dst_userat)
        if r.success:
            if not r.so_lines:
                return
            first = r.so_lines[0]
            last = r.so_lines[-1]
            self.logger.info(f"{first} -- {last}")
            self.report.append(f"{last}")
            self.report.append(f"   ... {first}")

    @classmethod
    def demo(cls):
        app = Ztool()


if __name__ == '__main__':
    Ztool.demo()
