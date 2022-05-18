db_name = 'genomics_dbs';
db = db.getSiblingDB(db_name);
db.hgnc.createIndex( { 'symbol': 1 } );
db.hgnc.createIndex( { 'alias_symbol': 1 } );
db.hgnc.createIndex( { 'prev_symbol': 1 } );
