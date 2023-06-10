# This script is used to start either or both of:
# (a) Zookeeper docker container
# (b) Zookeeper ambassador docker container (that's gonna run on the machine
#     that's running a Zookeeper docker container)
#
# Usage:
#
#     python -m docker_python_helpers/run_zookeeper.py <ARGS>
from __future__ import print_function

import argparse
import os
import os.path
import re
import sys

from . import docker_run

parser = argparse.ArgumentParser(
  description="runs the Zookeeper Docker container",
  # disable `-h` option because the shell script which invokes this script will
  # pass in a `-h` flag
  add_help=False
)

zk_group = parser.add_mutually_exclusive_group()

zk_group.add_argument(
  "--no-zookeeper", action="store_true", dest="no_zookeeper",
  help="Do not start a Zookeeper docker container"
)

zk_group.add_argument(
  "--no-dash-p", action="store_true", dest="no_dash_p",
  help=re.sub(
    r"""\s+""", " ",
    """Do not generate any `-p` flags for the docker run command. This prevents
    ports on the Zookeeper docker container from being exposed on the host
    machine.
    """
  )
)

parser.add_argument(
  "-p", action="append", dest="p",
  help="-p arguments to pass to `docker run` command for Zookeeper container"
)

if __name__ == "__main__":
  stormConfig = docker_run.get_storm_config()
  ipv4Addresses = docker_run.get_ipv4_addresses(
    stormConfig["is_localhost_setup"],
    stormConfig.get("all_machines_are_ec2_instances", False)
  )
  foundCurrentServer = False
  for zk_server in stormConfig["storm.yaml"]["storm.zookeeper.servers"]:
    if zk_server in stormConfig["servers"] and \
        stormConfig["servers"][zk_server] in ipv4Addresses:
      foundCurrentServer = True
      break
  if not foundCurrentServer:
    raise RuntimeError(re.sub("\s+", " ",
      """IP address of this machine does not match any IP address supplied in
      the `storm.yaml` -> `storm.zookeeper.servers` section of
      `config/storm-supervisor.yaml`.
      """).strip()
    )

  # See the usage of this script at the top of the file... and you'll
  # understand why we need to subscript `sys.argv` from 2
  args_to_parse = list(sys.argv[2:])
  # Locate "--" in sys.argv[2:] . If "--" is present, that means the user
  # wants to start a Zookeeper ambassador docker container. All the args after
  # "--" are for that container.
  double_dash_idx = None
  ambassador_args = None
  try:
    double_dash_idx = args_to_parse.index("--")
    ambassador_args = args_to_parse[double_dash_idx + 1:]
    args_to_parse = args_to_parse[:double_dash_idx]
  except ValueError:
    pass

  # Parse arguments for Zookeeper Docker container
  zk_args, zk_rem_args = parser.parse_known_args(args_to_parse)
  if zk_args.no_zookeeper and ambassador_args is None:
    print(
      "Must start at least one of Zookeeper or Zookeeper ambassador. Exiting.",
      file=sys.stderr
    )
    sys.exit(1)
  zk_docker_run_args = docker_run.construct_docker_run_args(
    zk_rem_args, ipv4Addresses
  )
  zk_docker_port_args = docker_run.construct_docker_run_port_args(["zookeeper"])
  p_args = None
  if zk_args.no_dash_p:
    # We won't be making the ports exposed through `--expose` available on the
    # physical machine.
    # Hence we extract the `-p` arguments generated by the
    # `docker_run.construct_docker_run_port_args` function into `p_args`.
    port_extractor_parser = argparse.ArgumentParser()
    port_extractor_parser.add_argument("-p", action="append", dest="p")
    p_args, port_rem_args = port_extractor_parser.parse_known_args(
      zk_docker_port_args
    )
    zk_docker_port_args = port_rem_args

  if not zk_args.no_zookeeper:
    # Start Zookeeper Docker container.
    # Any `-p` flag passed initially to this script before the `--` separator is
    # meant for the Zookeeper docker container and must be included here.
    # Hence we grab them from `zk_args`.
    if zk_args.p:
      zk_docker_port_args.append(
        " ".join(["-p {}".format(x) for x in zk_args.p])
      )
    dockerRunCmd = "docker run {} {}".format(" ".join(zk_docker_port_args),
      zk_docker_run_args
    )
    print(dockerRunCmd)
    os.system(dockerRunCmd)

  if ambassador_args is not None:
    # Start Zookeeper ambassador docker container.
    # If the `--no-dash-p` option was supplied to this script AND the `--`
    # separator is on sys.argv (meaning the user wants to run the Zookeeper
    # ambassador container), we grab every `-p` argument generated by the
    # `docker_run.construct_docker_run_port_args` function (now at `p_args`)
    # and include them in the `docker run` command for the Zookeeper ambassador
    # docker container.
    if p_args is not None:
      ambassador_args = [" ".join(["-p {}".format(x) for x in p_args.p])] + \
        ambassador_args
    docker_run_cmd = "docker run {}".format(" ".join(ambassador_args))
    print(docker_run_cmd)
    os.system(docker_run_cmd)
