from src.crud import BoardingHousesCRUD

def test_crud_operations(db_session):
    crud = BoardingHousesCRUD(db_session)

    # Create
    listing = crud.create(
        bh_name="Test House",
        description="A test boarding house",
        price_range="5000-10000",
        permit_url="http://example.com/permit",
        location_id=1,
        owner_id=1
    )
    assert listing.listing_id is not None

    # Read
    fetched = crud.get(listing.listing_id)
    assert fetched.bh_name == "Test House"
