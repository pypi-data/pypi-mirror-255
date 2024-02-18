import argparse
from typing import Literal
import yaml

ROLES = Literal["Master", "Aggregator", "Leaf"]

# Instantiate the parser and give it a description that will show before help
parser = argparse.ArgumentParser(description='S2ClusterGen - Generates the deployment file based on the input.')

# Add arguments to the parser
parser.add_argument('--license', dest='license', type=str, help="SingleStore License for the cluster.", required=True)
parser.add_argument('--root-password', dest='root_password', type=str, help='Root password for the database.')
parser.add_argument('--ma-ip', dest='ma_ip', type=str, help='IP/DNS for the Master Aggregator of the cluster.', required=True)
parser.add_argument('--child-ips', nargs='*', type=str, dest='child_ips', help='IP/DNS of the child aggregators if there is any.')
parser.add_argument('--leaf-ips', nargs='+', type=str, dest='leaf_ips', help='IP/DNS of the cluster leaves, at least one.', required=True)
parser.add_argument('--version', "-v", type=str, dest="version", help="The cluster version. If not specified will be the latest.")
parser.add_argument('--high-availability', "-ha", action='store_false', dest="high_availability", help="Cluster is deployed with high availability")
parser.add_argument('--file', "-f", dest="file", help="Destination yaml file to use. Full path required.", default="cluster-gen.yaml")

# Run method to parse the arguments
args = parser.parse_args()

def node(role: ROLES):
   return {
      "register": False,
      "role": role,
      "config": {
        "auditlogsdir": "/data/memsql/instance/auditlogs",
        "datadir": "/data/memsql/instance/data",
        "plancachedir": "/data/memsql/instance/plancache",
        "tracelogsdir": "/data/memsql/instance/tracelogs",
        "port": 3306
      }
    }
def get_host(host:str, role: ROLES):
   return {
      "hostname": host,
      "localhost": False,
      "ssh": {
        "host": host,
        "private_key": "~/.ssh/id_rsa"
      },
      "nodes": [ node(role) ]
   }

def main():

  cluster = {
    "license": args.license,
    "high_availability": args.high_availability,
    "package_type": "deb",
    "root_password": args.root_password,
    "hosts": [ get_host(args.ma_ip, "Master") ]
  }
  if args.version != None:
    cluster["memsql_server_version"] = args.version

  for leaf_ip in args.leaf_ips:
    cluster["hosts"].append( get_host(leaf_ip, "Leaf"))

  if args.child_ips is not None:
    for child_ip in args.child_ips:
      cluster["hosts"].append(get_host(child_ip, "Aggregator"))

  with open(args.file, 'w') as file:
      documents = yaml.dump(cluster, file)

if __name__ == '__main__':
    main()