import csv
from pathlib import Path
from typing import Dict, Any, Iterable

PROJECT_PATH = Path(__file__).parent

MODELS_PATH = PROJECT_PATH.parent / 'models'
MODEL_PATH = MODELS_PATH / 'space_only2.pickle'

MODELS = {
    'open_source': {
        'default': MODELS_PATH / 'model_OpenSourceAll_Logreg_BW_Without_Fs.pkl',
        'all': MODELS_PATH / 'model_OpenSourceAll_Logreg_All_Without_Fs.pkl',
        'bw': MODELS_PATH / 'model_OpenSourceAll_Logreg_BW_Without_Fs.pkl',
        'dorn': MODELS_PATH / 'model_OpenSourceAll_Logreg_Dorn_Without_Fs.pkl',
        'posnett': MODELS_PATH / 'model_OpenSourceAll_Logreg_Posnett_Without_Fs.pkl',
        'scalabrino': MODELS_PATH / 'model_OpenSourceAll_Logreg_Scal_With_Fs.pkl',
    },
    'all_merged': {
        'default': MODELS_PATH / 'model_AllMerged_MLP_Posnett_Without_Fs.pkl',
        'all': MODELS_PATH / 'model_AllMerged_MLP_All_Without_FS.pkl',
        'bw': MODELS_PATH / 'model_AllMerged_MLP_BW_With_FS.pkl',
        'dorn': MODELS_PATH / 'model_AllMerged_MLP_Dorn_Without_FS.pkl',
        'posnett': MODELS_PATH / 'model_AllMerged_MLP_Posnett_Without_Fs.pkl',
        'scalabrino': MODELS_PATH / 'model_AllMerged_MLP_Scal_With_FS.pkl',
    },
    'space_merged': {
        'default': MODELS_PATH / 'model_SpaceMerged_Knn_Posnett_Without_Fs.pkl',
        'all': MODELS_PATH / 'model_SpaceMerged_Knn_All_With_Fs.pkl',
        'bw': MODELS_PATH / 'model_SpaceMerged_Knn_BW_With_Fs.pkl',
        'dorn': MODELS_PATH / 'model_SpaceMerged_Knn_Dorn_Without_Fs.pkl',
        'posnett': MODELS_PATH / 'model_SpaceMerged_Knn_Posnett_Without_Fs.pkl',
        'scalabrino': MODELS_PATH / 'model_SpaceMerged_Knn_Scal_Without_FS.pkl',
    },
    'space_only': {
        'default': MODELS_PATH / 'model_SpaceOnly_Mlp_Posnett_Without.pkl',
        'all': MODELS_PATH / 'model_SpaceOnly_Mlp_All_With_Fs.pkl',
        'bw': MODELS_PATH / 'model_SpaceOnly_Mlp_BW_With_Fs.pkl',
        'dorn': MODELS_PATH / 'model_SpaceOnly_Mlp_Dorn_Without_Fs.pkl',
        'posnett': MODELS_PATH / 'model_SpaceOnly_Mlp_Posnett_Without.pkl',
        'scalabrino': MODELS_PATH / 'model_SpaceOnly_Mlp_Scal_Without_Fs.pkl',
    },
}


def export_csv(path: Path, rows: Iterable[Dict[str, Any]], headers=None):
    with path.open('w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        if headers:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)
