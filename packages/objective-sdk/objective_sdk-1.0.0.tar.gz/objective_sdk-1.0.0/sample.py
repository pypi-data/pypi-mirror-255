from objective import Index, ObjectStore

# Add an object to the object store
obj_store = ObjectStore()
obj_store.upsert_object(
    id=1,
    object={
        "title": "Sevendayz Men's Shady Records Eminem Hoodie Hoody Black Medium",
        "brand": "sevendayz",
        "imageURLHighRes": [
            "https://images-na.ssl-images-amazon.com/images/I/41gMYeiNASL.jpg"
        ],
    },
)

# Create an index using data from the Object Store
index = Index.from_template(
    template_name="text-neural-base", searchable=["title", "brand"]
)
