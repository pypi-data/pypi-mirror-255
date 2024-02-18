from typing import Dict, Optional, Union

from ..plotter import plot_region as plot_region_base
from dicomset.dataset.dicom import DICOMDataset
from dicomset.types import Crop2D, PatientRegions
from dicomset.utils import arg_to_list

def plot_region(
    dataset: str,
    pat_id: str,
    centre_of: Optional[str] = None,
    crop: Optional[Union[str, Crop2D]] = None,
    region: Optional[PatientRegions] = None,
    region_label: Optional[Dict[str, str]] = None,     # Gives 'regions' different names to those used for loading the data.
    show_dose: bool = False,
    study_id: Optional[str] = None,
    use_mapping: bool = True,
    **kwargs) -> None:
    region_labels = arg_to_list(region_label, str)

    # Deal with 'regions' arg.
    patient = DICOMDataset(dataset).patient(pat_id)
    if region == 'all':
        regions = patient.list_regions()
    else:
        regions = arg_to_list(region, str)

    if study_id is not None:
        study = patient.study(study_id)
    else:
        study = patient.default_study
    ct_data = study.ct_data
    region_data = study.region_data(region=regions, use_mapping=use_mapping) if regions is not None else None
    spacing = study.ct_spacing
    dose_data = study.dose_data if show_dose else None

    if centre_of is not None:
        if type(centre_of) == str:
            if region_data is None or centre_of not in region_data:
                centre_of = study.region_data(region=centre_of, use_mapping=use_mapping)[centre_of]

    if crop is not None:
        if type(crop) == str:
            if region_data is None or crop not in region_data:
                crop = study.region_data(region=crop, use_mapping=use_mapping)[crop]

    if region_labels is not None:
        # Rename 'regions' and 'region_data' keys.
        regions = [region_labels[r] if r in region_labels else r for r in regions]
        for old, new in region_labels.items():
            region_data[new] = region_data.pop(old)

        # Rename 'centre_of' and 'crop' keys.
        if type(centre_of) == str and centre_of in region_labels:
            centre_of = region_labels[centre_of] 
        if type(crop) == str and crop in region_labels:
            crop = region_labels[crop]

    # Plot.
    plot_region_base(pat_id, ct_data.shape, spacing, centre_of=centre_of, crop=crop, ct_data=ct_data, dose_data=dose_data, region_data=region_data, **kwargs)
