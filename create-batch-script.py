#!/usr/bin/env python

import argparse
import os

from jinja2 import Environment, FileSystemLoader
 
PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
    trim_blocks=False)


def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def render_script(args):
    with open(args.script_name, "w") as stream:
        stream.write(render_template("job.sh", vars(args)))


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--architecture", "-a",
            choices = ["ivybridge", "haswell", "knl"],
            default = "haswell",
            help = "processor architecture")
    parser.add_argument("--nodes", "-n",
            default = 5,
            help = "number of nodes",
            type = int)
    parser.add_argument("--account", "-A",
            default = "nstaff",
            help = "repository name")
    parser.add_argument("--mail-user", "-m",
            help = "contact email in case job fails")
    parser.add_argument("--qos", "-q",
            choices = ["debug", "regular", "premium"],
            default = "regular",
            help = "job submit queue")
    parser.add_argument("--time", "-t",
            default = 10,
            help = "job time limit in minutes",
            type = int)
    parser.add_argument("--set-x", "-x",
            action = "store_true",
            help = "whether script should `set -x`")
    parser.add_argument("--shifter-image", "-s",
            default = None,
            help = "use this shifter image")
    args = parser.parse_args()

    if args.architecture == "haswell":
        args.mpi_ranks_per_node = 32
        args.omp_num_threads = 2
    elif args.architecture == "knl":
        args.mpi_ranks_per_node = 68
        args.omp_num_threads = 4
    else:
        args.mpi_ranks_per_node = 24
        args.omp_num_threads = 1

    args.job_name = "-".join(["desi", 
        args.architecture, 
        "shifter" if args.shifter_image else "default",
        "{:04d}".format(args.nodes)])
    args.script_name = "{}.sh".format(args.job_name)

    return args
 
 
def main():
    render_script(parse_arguments())
 
 
if __name__ == "__main__":
    main()
