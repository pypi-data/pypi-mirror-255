from collections import Counter
import numpy as np
import os
import pandas as pd
from pandas import DataFrame
from tqdm import tqdm
<<<<<<< HEAD:mymi/reporting/dataset/dicom.py
from typing import List, Union

from mymi.dataset.dicom import DICOMDataset
from mymi.evaluation.dataset.dicom import evaluate_model
from mymi.geometry import get_extent
from mymi.types import Model, PatientRegions
from mymi.utils import append_row, encode

def create_evaluation_report(
    name: str,
    dataset: str,
    localiser: Model,
    segmenter: Model,
    region: str) -> None:
    # Save report.
    eval_df = evaluate_model(dataset, localiser, segmenter, region)
    set = DICOMDataset(dataset)
    filename = f"{name}.csv"
    filepath = os.path.join(set.path, 'reports', 'evaluation', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    eval_df.to_csv(filepath)

def get_ct_summary(
    dataset: str,
    regions: PatientRegions = 'all') -> pd.DataFrame:
=======
from typing import List, Optional

from dicomset.dataset.dicom import DICOMDataset
from dicomset.geometry import get_extent
from dicomset import types
from dicomset.types import PatientRegions
from dicomset.utils import append_row, encode

def get_ct_summary(
    dataset: str,
    region: Optional[PatientRegions] = None) -> pd.DataFrame:
>>>>>>> 210721d (Remove unnecessary files/folders.):src/dicomset/reporting/dataset/dicom.py
    # Get patients.
    set = DICOMDataset(dataset)
    pat_ids = set.list_patients(regions=region)

    cols = {
        'patient-id': str,
        'axis': int,
        'size': int,
        'spacing': float,
        'fov': float
    }
    df = pd.DataFrame(columns=cols.keys())

    for pat_id in tqdm(pat_ids):
        # Load values.
        pat = set.patient(pat_id)
        size = pat.ct_size()
        spacing = pat.ct_spacing()

        # Calculate FOV.
        fov = np.array(size) * spacing

        for axis in range(len(size)):
            data = {
                'patient-id': pat_id,
                'axis': axis,
                'size': size[axis],
                'spacing': spacing[axis],
                'fov': fov[axis]
            }
            df = append_row(df, data)

    # Set column types as 'append' crushes them.
    df = df.astype(cols)

    return df

def create_ct_summary(
    dataset: str,
<<<<<<< HEAD:mymi/reporting/dataset/dicom.py
    regions: PatientRegions = 'all') -> None:
=======
    region: Optional[PatientRegions] = None) -> None:
>>>>>>> 210721d (Remove unnecessary files/folders.):src/dicomset/reporting/dataset/dicom.py
    # Get summary.
    df = get_ct_summary(dataset, region=region)

    # Save summary.
    set = DICOMDataset(dataset)
    filepath = os.path.join(set.path, 'reports', f'ct-summary-{encode(region)}.csv')
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)

def load_ct_summary(
    dataset: str,
<<<<<<< HEAD:mymi/reporting/dataset/dicom.py
    regions: PatientRegions = 'all') -> None:
=======
    region: Optional[PatientRegions] = None) -> None:
>>>>>>> 210721d (Remove unnecessary files/folders.):src/dicomset/reporting/dataset/dicom.py
    set = DICOMDataset(dataset)
    filepath = os.path.join(set.path, 'reports', f'ct-summary-{encode(region)}.csv')
    return pd.read_csv(filepath)

def get_patient_regions_report(
    dataset: str,
    use_default_rtstruct: bool = True,
    use_mapping: bool = True) -> pd.DataFrame:
    # List patients.
    set = DICOMDataset(dataset)
    pat_ids = set.list_patients()

    # Create dataframe.
    cols = {
        'patient-id': str,
        'region': str
    }
    if not use_default_rtstruct:
        cols['study-id'] = str
        cols['series-id'] = str
        cols['rtstruct-id'] = str
    df = pd.DataFrame(columns=cols.keys())

    # Add rows.
    for pat_id in tqdm(pat_ids):
        pat = set.patient(pat_id)
        if use_default_rtstruct:
            pat_regions = pat.list_regions(use_mapping=use_mapping)

            for pat_region in pat_regions:
                data = {
                    'patient-id': pat_id,
                    'region': pat_region
                }
                df = append_row(df, data)
        else:
            study_ids = pat.list_studies()
            for study_id in study_ids:
                study = pat.study(study_id)
                series_ids = study.list_series('RTSTRUCT')
                for series_id in series_ids:
                    series = study.series(series_id, 'RTSTRUCT')
                    rtstruct_ids = series.list_rtstructs()
                    for rtstruct_id in rtstruct_ids:
                        rtstruct = series.rtstruct(rtstruct_id) 
                        pat_regions = rtstruct.list_regions(use_mapping=use_mapping)

                        for pat_region in pat_regions:
                            data = {
                                'patient-id': pat_id,
                                'study-id': study_id,
                                'series-id': series_id,
                                'rtstruct-id': rtstruct_id,
                                'region': pat_region
                            }
                            df = append_row(df, data)

    return df

def create_patient_regions_report(
    dataset: str,
    use_default_rtstruct: bool = True,
    use_mapping: bool = True) -> None:
    pr_df = get_patient_regions_report(dataset, use_default_rtstruct=use_default_rtstruct, use_mapping=use_mapping)
    set = DICOMDataset(dataset)
    filename = 'region-count'
    if use_default_rtstruct:
        filename = f'{filename}-default'
    if use_mapping:
        filename = f'{filename}-mapped'
    filename = f'{filename}.csv'
    filepath = os.path.join(set.path, 'reports', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    pr_df.to_csv(filepath, index=False)

def load_patient_regions_report(
    dataset: str,
    exists_only: bool = False,
    use_default_rtstruct: bool = True,
    use_mapping: bool = True) -> Union[DataFrame, bool]:
    set = DICOMDataset(dataset)
    filename = 'region-count'
    if use_default_rtstruct:
        filename = f'{filename}-default'
    if use_mapping:
        filename = f'{filename}-mapped'
    filename = f'{filename}.csv'
    filepath = os.path.join(set.path, 'reports', filename)
    if os.path.exists(filepath):
        if exists_only:
            return True
        else:
            return pd.read_csv(filepath)
    else:
        if exists_only:
            return False
        else:
            raise ValueError(f"Patient regions report doesn't exist for dataset '{dataset}'.")

def get_regions_containing(
    dataset: str,
    s: str,
    case: bool = False,
    use_mapping: bool = False) -> DataFrame:
    df = load_patient_regions_report(dataset, use_mapping=use_mapping)
    count_df = df.groupby('region')['patient-id'].count().rename('count').reset_index()
    if case:
        count_df = count_df[count_df['region'].str.contains(s)]
    else:
        count_df = count_df[count_df['region'].str.lower().str.contains(s.lower())]
    count_df = count_df.sort_values('count', ascending=False)
    return count_df

def get_mapped_duplicates(dataset: str) -> DataFrame:
    # Allows us to check 'region-map.csv' mapping for duplicates rather than running 
    # 'create_patient_regions_report(..., use_mapping=True)' which will break on each duplicate.
    region_map = DICOMDataset(dataset).region_map
    if region_map is None:
        raise ValueError(f"No 'region-map.csv' found for DICOMDataset '{dataset}'.")
    df = load_patient_regions_report(dataset, use_mapping=False)
    df['mapped'] = df[['patient-id', 'region']].apply(lambda row: region_map.to_internal(row['region'], pat_id=row['patient-id'])[0], axis=1)
    df = df.groupby('patient-id')['mapped'].apply(list).reset_index()
    df['mapped'] = df['mapped'].apply(lambda regions: [i for i, count in Counter(regions).items() if count > 1])
    df['duplicates'] = df['mapped'].apply(lambda dups: len(dups) > 0)
    df = df[df['duplicates']]
    return df

def region_overlap(
    dataset: str,
    clear_cache: bool = True,
    regions: PatientRegions = 'all') -> int:
    # List regions.
    set = DICOMDataset(dataset)
    regions_df = set.list_regions(clear_cache=clear_cache) 
    regions_df = regions_df.drop_duplicates()
    regions_df['count'] = 1
    regions_df = regions_df.pivot(index='patient-id', columns='region', values='count')

    # Filter on requested regions.
    def filter_fn(row):
        if type(regions) == str:
            if regions == 'all':
                return True
            else:
                return row[regions] == 1
        else:
            keep = True
            for region in regions:
                if row[region] != 1:
                    keep = False
            return keep
    regions_df = regions_df[regions_df.apply(filter_fn, axis=1)]
    return len(regions_df) 

def get_region_summary(
    dataset: str,
    region: PatientRegions) -> pd.DataFrame:
    set = DICOMDataset(dataset)
<<<<<<< HEAD:mymi/reporting/dataset/dicom.py
    pat_ids = set.list_patients(region=region)
=======
    pat_ids = set.list_patients(regions=regions)
>>>>>>> 210721d (Remove unnecessary files/folders.):src/dicomset/reporting/dataset/dicom.py

    cols = {
        'patient': str,
        'region': str,
        'axis': str,
        'extent-mm': float,
        'spacing-mm': float
    }
    df = pd.DataFrame(columns=cols.keys())

    axes = [0, 1, 2]

    # Initialise empty data structure.
    data = {}
    for region in regions:
        data[region] = {}
        for axis in axes:
            data[region][axis] = []

<<<<<<< HEAD:mymi/reporting/dataset/dicom.py
    for pat_id in tqdm(pat_ids):
=======
    for pat in tqdm(pat_ids):
>>>>>>> 210721d (Remove unnecessary files/folders.):src/dicomset/reporting/dataset/dicom.py
        # Get spacing.
        pat = set.patient(pat_id)
        spacing = pat.ct_spacing()

        # Get region data.
        pat_regions = set.patient(pat).list_regions(whitelist=regions)
        rs_data = set.patient(pat).region_data(region=pat_regions)

        # Add extents for all regions.
        for r in rs_data.keys():
            r_data = rs_data[r]
            min, max = get_extent(r_data)
            for axis in axes:
                extent_vox = max[axis] - min[axis]
                extent_mm = extent_vox * spacing[axis]
                data = {
                    'patient': pat,
                    'region': r,
                    'axis': axis,
                    'extent-mm': extent_mm,
                    'spacing-mm': spacing[axis]
                }
                df = append_row(df, data)

    # Set column types as 'append' crushes them.
    df = df.astype(cols)

    return df

def create_region_summary_report(
    dataset: str,
    regions: List[str]) -> None:
    # Generate summary report.
    df = get_region_summary(dataset, regions)

    # Save report.
    filename = 'region-summary.csv'
    set = DICOMDataset(dataset)
    filepath = os.path.join(set.path, 'reports', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
