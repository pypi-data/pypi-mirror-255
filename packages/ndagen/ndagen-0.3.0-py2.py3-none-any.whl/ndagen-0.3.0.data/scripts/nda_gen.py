#!python

import sys
import nibabel as nib
import json
import pandas as pd
from pathlib import Path
from argparse import ArgumentParser
import logging
import yaml
import re
import ndagen
import ndagen.config as config
import os
from datetime import datetime
import numpy as np

logger = logging.getLogger('nda_gen')
logging.basicConfig(level=logging.INFO)

def main():
    parser = ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true',
        help='See verbose logging')
    parser.add_argument('--source-files', type=Path, required=True,
        help='Path to NIFTI Files to be uploaded')
    parser.add_argument('--key-file', required=True,
        help='Path to subject key csv file')
    parser.add_argument('--nda-config', default=config.spreadsheet_variables(),
        help='YAML file with all the column names for the NDA Spreadsheet')
    parser.add_argument('--task-list', default=config.tasks(),
        help='YAML file of all tasks and their corresponding NDA number')
    parser.add_argument('--reface-info',
        help='Pass the name of the software used to reface T1w images')
    parser.add_argument('--echo-times',
        help='Path to YAML file with series descriptions and associated echo times')
    args = parser.parse_args()

    configure_logging(args.verbose)
    logger.info('Welcome to ndagen version %s', ndagen.version())

    """
    This script will go row by row in building the final csv/dataframe. Every row represents a nifti file that will be uploaded
    """

    nda_config = yaml.safe_load(open(args.nda_config))

    task_list = yaml.safe_load(open(args.task_list))

    all_variables = nda_config['nda_variables']

    tasks = task_list['tasks']

    key_file = pd.read_csv(args.key_file)

    # create final dataframe that will be added to as we go
    final_dataframe = pd.DataFrame(columns=[all_variables])

    # load in all the source file names

    source_files = [file for file in os.listdir(args.source_files) if file.endswith('.json')]

    os.chdir(args.source_files)

    ### construct all variables for each row, add each row to final dataframe

    for file in source_files:

        subjectkey = keep_all_before_non_alphanumeric(file)

        current_row = []

        nifti_file = file.replace('.json', '.nii.gz')

        # get column info from the input key file
        current_row = add_key_file_info(subjectkey, key_file, file, current_row)

        # add the image info

        current_row = add_image_info(subjectkey, file, current_row, args, tasks, nifti_file)

        # add remaining variables/columns

        current_row = add_final_cols(subjectkey, file, current_row, args, tasks, nifti_file)


        final_dataframe = add_row_to_final_df(subjectkey, current_row, final_dataframe)


    write_dataframe_to_csv(final_dataframe, args)


def add_key_file_info(subjectkey, key_file, orig_file, current_row):
    """
    Gather info from the key file for this file
    """

    key_row = key_file.index[key_file['subjectkey'] == subjectkey].tolist()[0]

    current_row.append(subjectkey)
    current_row.append(key_file.at[key_row, 'src_subject_id']) # for src_subject_id column
    current_row.append(validate_date(key_file.at[key_row, 'interview_date'])) # for interview_date column
    current_row.append(key_file.at[key_row, 'interview_age']) # for interview_age column
    current_row.append(key_file.at[key_row, 'sex']) # for sex column
    current_row.append(keep_after_first_non_alphanumeric(orig_file).replace('.json', '')) # for comments_misc column

    return current_row

def add_image_info(subjectkey, file, current_row, args, tasks, nifti_file):
    with open(file) as f:
        json_data = json.load(f)

    current_row.append(nifti_file) # for image_file column
    current_row.append('') # for image_thumbnail_file column
    current_row.append(get_image_description(file, args.source_files)) # for image_description column
    current_row.append(get_experiment_id(file, tasks)) # for experiment_id column
    current_row.append(get_scan_type(file, args.source_files)) # for scan_type column
    current_row.append('Live') # for scan_object column
    current_row.append('NIFTI') # for image_file_format column
    current_row.extend(['','']) # for data_file2 and data_file2_type columns
    current_row.append('MRI') # for image_modality column
    current_row.append(json_data['Manufacturer']) # for scanner_manufacturer_pd column
    current_row.append(json_data['ManufacturersModelName']) # for scanner_type_pd column
    current_row.append(json_data['SoftwareVersions']) # for scanner_software_versions_pd column
    current_row.append(json_data['MagneticFieldStrength']) # for magnetic_field_strength column
    current_row.append(json_data['RepetitionTime']) # for mri_repetition_time_pd column
    current_row.append(get_echo_times(json_data, args))
    current_row.append(json_data['FlipAngle']) # for flip_angle column
    current_row.append(json_data['AcquisitionMatrixPE']) # for acquisition_matrix column
    current_row.append(get_field_of_view(json_data)) # for mri_field_of_view_pd column
    current_row.append(json_data['PatientPosition']) # for patient_position column
    current_row.append('MONOCHROME2') # for photomet_interpret column
    current_row.append(json_data['ReceiveCoilName']) # for receive_coil column
    current_row.append('Body') # for transmit_coil column
    current_row.append('No') # for transformation_performed column
    current_row.append('') # for transformation_type column
    current_row.append(add_reface_info(json_data, args)) # for image_history column
    current_row.append(get_image_dimensions(nifti_file)) # for image_num_dimensions column
    current_row.append(get_image_extent1(nifti_file, json_data)) # for image_extent1 column
    current_row.append(get_image_extent2(nifti_file, json_data)) # for image_extent2 column
    current_row.append(get_image_extent3(nifti_file, json_data)) # for image_extent3 column    
    current_row.append(get_image_extent4(nifti_file, json_data)) # for image_extent4 column
    current_row.append(get_extent4_type(nifti_file, json_data)) # for extent4_type column

    return current_row

def add_final_cols(subjectkey, file, current_row, args, tasks, nifti_file):
    with open(file) as f:
        json_data = json.load(f)

    current_row.extend(['','']) # for image_extent5 and extent5_type columns
    current_row.extend(['Millimeters','Millimeters','Millimeters']) # for image_unit1, image_unit2 and image_unit3 columns
    current_row.append(get_image_unit4(nifti_file)) # for image_unit4 column
    current_row.append('') # image_unit5 column
    current_row.extend([json_data['SliceThickness'], json_data['SliceThickness'], json_data['SliceThickness']]) # for image_resolution1, image_resolution2 and image_resolution3 columns
    current_row.append(get_image_resolution4(nifti_file)) # for image_resolution4 column
    current_row.append(json_data['SliceThickness']) # for image_slice_thickness column
    current_row.append(get_image_orientation(nifti_file)) # for image_orientation column
    current_row.extend(['' for _ in range(12)]) # for qc_outcome, qc_description, qc_fail_quest_reason, decay_correction, frame_end_times, frame_end_unit, frame_start_times, frame_start_unit, pet_isotope pet_tracer, time_diff_inject_to_image and time_diff_units columns
    current_row.append(json_data['PulseSequenceDetails']) # for pulse_seq column
    current_row.append('') # for slice_acquisition column
    current_row.append(get_software(json_data)) # for software_preproc column
    current_row.extend(['' for _ in range(2)]) # for study and week columns
    current_row.append(get_task_name(file, tasks)) # for experiment_description column
    current_row.append(find_session(file)) # for visit column
    current_row.append(get_slice_timing(json_data)) # for slice_timing column
    current_row.extend(['' for _ in range(3)]) # for bvek_bval_files, bvecfile, bvalfile columns
    current_row.append(json_data['DeviceSerialNumber']) # for deviceserialnumber column
    current_row.extend(['' for _ in range(32)]) # for the final 32 columns, starting with procdate and endign with year_mta

    return current_row


def get_extent4_type(nifti_file, json_data):
    is_functional = check_for_functional(nifti_file)
    if is_functional is False:
        return ''
    else:
        return 'Time'

def get_echo_times(json_data, args):
    if args.echo_times:
        echos_yaml = yaml.safe_load(open(args.echo_times))
        all_series_descriptions = echos_yaml['echo_times']
        echo_times = None
        for description in all_series_descriptions:
            if json_data['SeriesDescription'] == description:
                echo_times = all_series_descriptions[description]
        if not echo_times:
            return json_data['EchoTime']
        else:
            return echo_times
    else:
        return json_data['EchoTime']

def get_slice_timing(json_data):
    try:
        return json_data['SliceTiming']
    except:
        return ''

def find_session(file):
    pattern = r'sess?(\d*)'
    match = re.search(pattern, file, re.IGNORECASE)
    if match:
        return match.group(0)
    else:
        return None

def get_task_name(file, tasks):
    for task in tasks:
        if task in file:
            return task
    return ''

def get_software(json_data):
    conversion_software = json_data['ConversionSoftware']
    software_version = json_data['ConversionSoftwareVersion']

    return f'{conversion_software} {software_version}'

def get_image_orientation(nifti_file):
    affine_matrix = nib.load(nifti_file).affine
    rotation_matrix = affine_matrix[:3, :3]
    x_axis, y_axis, z_axis = rotation_matrix[:, 0], rotation_matrix[:, 1], rotation_matrix[:, 2]
    axial_threshold = 0.99
    coronal_threshold = 0.99
    if np.dot(z_axis, np.array([0, 0, 1])) > axial_threshold:
        image_view = "Axial"
    elif np.dot(y_axis, np.array([0, 1, 0])) > coronal_threshold:
        image_view = "Coronal"
    else:
        image_view = "Sagittal"

    return image_view

def get_image_resolution4(nifti_file):
    if check_for_functional(nifti_file):
        return 1
    else:
        return ''

def get_image_unit4(nifti_file):
    if check_for_functional(nifti_file):
        return 'Seconds'
    else:
        return ''

def check_for_functional(nifti_file):
    nifti_img = nib.load(nifti_file)
    dimensions = nifti_img.header.get_data_shape()
    if len(dimensions) > 3:
        return True
    else:
        return False  

def validate_date(input_date):
    try:
        parsed_date = datetime.strptime(input_date, '%m/%d/%Y')
        return input_date
    except ValueError:
        logger.error('The date on the key file csv is not in valid format. Please change it to MM-DD-YYYY format and try again. Exiting.')
        sys.exit(1)

def get_image_extent4(nifti_file, json_data):
    nifti_img = nib.load(nifti_file)
    dimensions = nifti_img.header.get_data_shape()
    if len(dimensions) > 3:
        return round(dimensions[3] * json_data['RepetitionTime'])
    else:
        return ''    

def get_image_extent3(nifti_file, json_data):
    nifti_img = nib.load(nifti_file)
    dimensions = nifti_img.header.get_data_shape()
    if 'MPR' in json_data['SeriesDescription'] or 'T2' in json_data['SeriesDescription']:
        return round(dimensions[0] * json_data['SliceThickness'])  
    else:
        return round(dimensions[2] * json_data['SliceThickness'])


def get_image_extent2(nifti_file, json_data):
    nifti_img = nib.load(nifti_file)
    dimensions = nifti_img.header.get_data_shape()
    return round(dimensions[1] * json_data['SliceThickness'])


def get_image_extent1(nifti_file, json_data):
    nifti_img = nib.load(nifti_file)
    dimensions = nifti_img.header.get_data_shape()
    if 'MPR' in json_data['SeriesDescription'] or 'T2' in json_data['SeriesDescription']:
        return round(dimensions[2] * json_data['SliceThickness'])
    else:
        return round(dimensions[0] * json_data['SliceThickness'])



def get_image_dimensions(nifti_file):
    nifti_img = nib.load(nifti_file)
    dimensions = nifti_img.header.get_data_shape()
    return len(dimensions)


def add_reface_info(json, args):
    if args.reface_info:
        if 'MPR' in json['SeriesDescription'] or 'T2' in json['SeriesDescription']:
            return args.reface_info
    else:
        return ''

def get_field_of_view(json_file):
    dim1 = round((json_file['BaseResolution']) * (json_file['SliceThickness']))
    dim2 = round((json_file['AcquisitionMatrixPE']) * (json_file['SliceThickness']))

    return f'{dim1}x{dim2}'
 

def get_scan_type(json_file, source_files_dir):
    with open(f'{source_files_dir}/{json_file}') as f:
        json_file = json.load(f)

    if 'T2' in json_file['SeriesDescription']:
        return 'MR structural (T2)'
    elif 'MPR' in json_file['SeriesDescription']:
        return 'MR structural (T1)'
    elif 'FMAP' in json_file['SeriesDescription']:
        return 'Field Map'
    else:
        return 'fMRI'

def get_experiment_id(file, tasks):
    for task in tasks.keys():
        if task in file:
            return tasks[task]

def get_image_description(json_file, source_files_dir):
    with open(f'{source_files_dir}/{json_file}') as f:
        json_file = json.load(f)

    if 'T2' in json_file['SeriesDescription']:
        return 'MRI_T2'
    elif 'MPR' in json_file['SeriesDescription']:
        return 'MRI_T1_MEMPR'
    elif 'FMAP' in json_file['SeriesDescription']:
        return 'MRI_fieldmap'
    else:
        return 'fMRI'


def keep_all_before_non_alphanumeric(string):
    match = re.search(r'\W', string)
    if match:
        index = match.start()
        return string[:index]
    else:
        return string

def keep_after_first_non_alphanumeric(input_string):
    pattern = r'[^a-zA-Z0-9](.*)$'
    match = re.search(pattern, input_string)
    if match:
        return match.group(1)
    else:
        return input_string

def add_row_to_final_df(subject_key, row_data, final_df):

    logger.info(f'Adding data for scan {row_data[6]}')

    final_df.loc[len(final_df.index)] = row_data

    return final_df

def write_dataframe_to_csv(final_df, args):
    todays_date = datetime.today().strftime('%Y-%m-%d')
    filename = f'nda_upload_file_{todays_date}.csv'
    output_path = os.path.join(args.source_files, filename)
    final_df.to_csv(output_path, index=False)
    logger.info(f'{filename} written to {args.source_files}')


def configure_logging(verbose):
    level = logging.INFO
    if verbose:
        level = logging.DEBUG
    logging.basicConfig(
        level=level,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )




if __name__ == '__main__':
    main()

