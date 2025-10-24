from oc4ids_datastore_api.models import ProjectSQLModel
from oc4ids_datastore_api.schemas import Dataset, Download, License, Portal, Publisher

from sqlmodel import Session, select
from typing import List
from datetime import datetime
import requests


#def _transform_dataset(dataset: DatasetSQLModel) -> Dataset:
#    download_urls = {
#        "json": dataset.json_url,
#        "csv": dataset.csv_url,
#        "xlsx": dataset.xlsx_url,
#    }
#    downloads = [
#        Download(format=format, url=url) for format, url in download_urls.items() if url
#    ]
#    return Dataset(
#        loaded_at=dataset.updated_at,
#        source_url=dataset.source_url,
#        publisher=Publisher(
#            name=dataset.publisher_name, country=dataset.publisher_country
#        ),
#        license=License(
#            url=dataset.license_url,
#            title=dataset.license_title,
#            title_short=dataset.license_title_short,
#        ),
#        portal=Portal(
#            url=dataset.portal_url,
#            title=dataset.portal_title,
#        ),
#        downloads=downloads,
#    )
def get_all_datasets(session: Session) -> List[dict]:
    projects = session.exec(select(ProjectSQLModel)).all()
    results = []
    for p in projects:
        period_data = p.period if p.period else {}
        results.append({
            "id": p.id,
            "title": p.title,
            "status": p.status,
            "type": p.type,
            "language": p.language,
            "start_date": period_data.get("start"),
            "end_date": period_data.get("end"),
            "updated": p.updated.strftime("%m/%d/%Y") if p.updated else None
        })
    return results


#def get_all_datasets() -> list[Dataset]:
#    datasets = fetch_all_datasets()
#    return [_transform_dataset(dataset) for dataset in datasets]

def get_all_datasets_from_url(url: str) -> list[dict]:
    response = requests.get(url)
    response.raise_for_status()  
    data = response.json()
    
    datasets = []
    for project in data.get("projects", []):
        datasets.append({
            "title": project.get("title"),
            "language": project.get("language")  
        })
    return datasets
