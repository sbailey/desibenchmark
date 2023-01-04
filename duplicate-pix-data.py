#!/usr/bin/python3

import os
import shutil
import subprocess
import numpy as np

# EDIT this to point to the location of your benchmark-z/pix directory
workingdir = '/pscratch/sd/s/stephey/desi/benchmark-z/pix'

start_year = 2019
create_years = [2020,2021,2022,2023]
create_days = np.arange(1,10,1)

# this step will duplicate the 2019 data for the requested years
for year in create_years:
    for day in create_days:
        #first let's figure out which dir to copy (always 2019)
        fixed_year_month_day = [str(start_year), str(10), str(day).zfill(2)]
        dir_to_copy = ''.join(fixed_year_month_day)
        #print(dir_to_copy)

        #dir to create
        new_year_month_day = [str(year), str(10), str(day).zfill(2)]
        dir_to_create = ''.join(new_year_month_day)
        #print(dir_to_create)

        #ok ready let's do it
        copy_path = os.path.join(workingdir, dir_to_copy)
        print("will copy {}".format(copy_path))
        new_path = os.path.join(workingdir, dir_to_create)
        print("will create {}".format(new_path))
        shutil.copytree(copy_path, new_path)

        print("done")

#nights have been duplicated from the orig 2019 data for 2020-2023
#for each year, we need to add 1, 2, 3... as a leading digit
#for all filenames

#it's important that there are no filename collisions within the entire pix dataset

# 2019 is already appropriately named, need to rename copies of 2019 
month = 10
# need to zero-pad
nights = [str(x).zfill(2) for x in create_days]
print("nights", nights)

#loop over year and add 1, 2, 3 to each increasing year
#loop over nights within year
#issue rename command
#use the unix rename function, not the perl one!
#rename 0000 0001 *.fits

for i, year in enumerate(create_years, start=1):
    for night in nights:
        target_dir = '{}/{}{}{}'.format(workingdir, year, month, night)
        print("target_dir", target_dir)
        os.chdir(target_dir)

        rename_command = 'rename 0000 000{} *.fits'.format(i)
        print("rename_command", rename_command)
        # dry run
        subprocess.run(rename_command, shell=True)
        print("done renaming {}", target_dir)




