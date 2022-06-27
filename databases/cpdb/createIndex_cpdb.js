db_name = 'bio_api';
db = db.getSiblingDB(db_name);
db.cpdb.createIndex( { 'hgnc_symbol_ids': 1 } );