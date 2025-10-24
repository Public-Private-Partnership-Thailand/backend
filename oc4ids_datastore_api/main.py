from fastapi import FastAPI,Depends
from sqlmodel import Session
from oc4ids_datastore_api.database import get_session
from oc4ids_datastore_api.schemas import Dataset
from oc4ids_datastore_api.services import get_all_datasets
from oc4ids_datastore_api.models import ProjectSQLModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


@app.get("/api/datasets")
def read_projects(session: Session = Depends(get_session)):
    return get_all_datasets(session)

@app.get("/api/datasets/{project_id}")
def read_project(project_id: str, session: Session = Depends(get_session)):
    project = session.get(ProjectSQLModel, project_id)
    if not project:
        return {"error": "Project not found"}
    return project
    

@app.post("/api/datasets")
def create_project(project: ProjectSQLModel, session: Session = Depends(get_session)):
    session.add(project)
    session.commit()
    session.refresh(project)
    return {"message": "Project created successfully", "project": project}
#@app.post("/api/datasets")
#def post_datasets() -> list[Dataset]:
#    return upload_new_datasets()
origins = [
    "http://127.0.0.1:8080",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        
    allow_credentials=True,
    allow_methods=["*"],           
    allow_headers=["*"],          
)
