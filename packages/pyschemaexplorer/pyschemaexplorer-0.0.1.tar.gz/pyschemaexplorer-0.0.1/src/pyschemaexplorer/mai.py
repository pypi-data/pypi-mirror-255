from sqlalchemy import create_engine

# Configuration de la connexion à la base de données
engine = create_engine("sqlite:///ma_base.db")

# RÃ©cupÃ©ration du nom des tables
tables = engine.table_names()

# Itération sur les tables
for table in tables:
    # Affichage du nom de la table
    print(f"Table: {table}")

    # RÃ©cupÃ©ration des informations des champs
    metadata = engine.table_metadata(table)

    # Itération sur les champs
    for column in metadata.columns:
        # Affichage du nom du champ et de son type
        print(f"    {column.name}: {column.type}")
