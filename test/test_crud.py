from src.crud import DocumentCRUD

def test_crud_operations(db_session):
    crud = DocumentCRUD(db_session)

    # Create
    doc = crud.create(filename="test.png", r2_key="uploads/test.png")
    assert doc.id is not None

    # Read
    fetched_doc = crud.get(doc.id)
    assert fetched_doc.filename == "test.png"

    # Delete
    assert crud.delete(doc.id) is True
    assert crud.get(doc.id) is None