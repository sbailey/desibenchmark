#!/bin/bash
#SBATCH --account={{ account }}
{% if architecture != "ivybridge" -%}
#SBATCH --constraint={{ architecture }}
{% endif -%}
{% if shifter_image -%}
#SBATCH --image={{ shifter_image }}
{% endif -%}
#SBATCH --job-name={{ job_name }}
{% if license -%}
#SBATCH --license={{ license }}
{% endif -%}
{% if mail_user -%}
#SBATCH --mail-type=FAIL
#SBATCH --mail-user={{ mail_user }}
{% endif -%}
#SBATCH --nodes={{ nodes }}
#SBATCH --output=logs/{{ job_name }}-%j.out
#SBATCH --qos={{ qos }}
#SBATCH --time={{ time }}

module list

{% if set_x -%}
set -x
{% endif -%}

let n={{ mpi_ranks_per_node }}*$SLURM_JOB_NUM_NODES

outdir=$SCRATCH/temp-$SLURM_JOB_ID
mkdir -p $outdir

{% if not shifter_image -%}
source env/bin/activate
{% endif -%}

export DESI_LOGLEVEL=error
export OMP_NUM_THREADS={{ omp_num_threads }}

srun -n $n -c {{ omp_num_threads }} --cpu_bind=cores \
{%- if shifter_image %}
    shifter python /srv/desi-extract \
{%- else %}
    python ./desi-extract \
{%- endif %}
{%- if camera %}
    -c {{ camera }} \
{%- endif %}
    {{ datadir }} \
    $outdir  \
    $(date +%s)

