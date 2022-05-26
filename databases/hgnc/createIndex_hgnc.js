db_name = 'genomics_dbs';
db = db.getSiblingDB(db_name);
db.hgnc.createIndex( { 'symbol': 1 } );
db.hgnc.createIndex( { 'alias_symbol': 1 } );
db.hgnc.createIndex( { 'prev_symbol': 1 } );
db.hgnc.createIndex( { 'entrez_id': 1 } );
db.hgnc.createIndex( { 'ensembl_gene_id': 1 } );