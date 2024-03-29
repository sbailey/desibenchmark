#!/usr/bin/python3

import os
import shutil
import subprocess
import numpy as np
import argparse

def get_month(workingdir, start_year):
    """
    determine the month digit from the start-year of workingdir
    note this must be zero-padded
    """
    os.chdir(workingdir)
    #read first dirname starting with start_year
    all_dirnames = [x[1] for x in os.walk(workingdir)]
    all_dirnames_flat = [item for sublist in all_dirnames for item in sublist]
    #print("all_dirnames_flat", all_dirnames_flat)
    #now search for dirnames with start_year and take the first hit
    dirname_match = [s for s in all_dirnames_flat if str(start_year) in s][0]
    #parse out the two digits following start_year
    #first start by chopping off the leading year digits
    #this leave the month and the day
    month_day = dirname_match.split(str(start_year))[1]
    #then cut off last two digits (this is the day)
    #leaving the month
    month = str(month_day[:-2])

    return month


def dup_start_year(workingdir, start_year, create_years, create_days, month):
    """
    # this step will duplicate the start_year data for the requested years
    """
    for year in create_years:
        for day in create_days:
            fixed_year_month_day = [str(start_year), str(month), str(day).zfill(2)]
            dir_to_copy = ''.join(fixed_year_month_day)
     
            #dir to create
            new_year_month_day = [str(year), str(month), str(day).zfill(2)]
            dir_to_create = ''.join(new_year_month_day)
     
            #ok ready let's do it
            copy_path = os.path.join(workingdir, dir_to_copy)
            print("will copy {}".format(copy_path))
            new_path = os.path.join(workingdir, dir_to_create)
            print("will create {}".format(new_path))
            shutil.copytree(copy_path, new_path)
     
            print("done")
    return


def rename_files(workingdir, create_years, create_days, month):
    """
    #nights have been duplicated from the start-year
    #for each year, we need to add 1, 2, 3... as a leading digit
    #for all filenames for each increasing year
    #use the unix rename function, not the perl one!
    #rename 0000 0001 *.fits
    important that there are no filename collisions in the entire dataset
    """

    for i, year in enumerate(create_years, start=1):
        for day in create_days:
            #day must be zero-padded
            day_pad = str(day).zfill(2)
            target_dir = '{}/{}{}{}'.format(workingdir, year, month, day_pad)
            print("will rename ", target_dir)
            os.chdir(target_dir)
    
            rename_command = 'rename 0000 000{} *.fits'.format(i)
            subprocess.run(rename_command, shell=True)
            print("done")
    return


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--workingdir", type=str, required=True, help="location of benchmark-z/pix directory to augment")
    parser.add_argument("--start-year", type=int, default=2019, help="starting year already in benchmark-z/pix")
    parser.add_argument("--create-years", type=int, nargs="*", default=['2020','2021','2022','2023'], help="additional years to create")
    parser.add_argument("--create-days", type=int, nargs="*", default=list(range(1,10)), help="days of month to replicate")
    args = parser.parse_args()

    workingdir = args.workingdir
    start_year = args.start_year
    create_years = args.create_years
    create_days = args.create_days

    month = get_month(workingdir, start_year)
    dup_start_year(workingdir, start_year, create_years, create_days, month)
    rename_files(workingdir, create_years, create_days, month)

if __name__ == '__main__':
    main()
   
