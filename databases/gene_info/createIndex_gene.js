db_name = 'bio_api';
db = db.getSiblingDB(db_name);
db.gene_grch37.createIndex( { 'hgnc_symbol': 1 } );
db.gene_grch38.createIndex( { 'hgnc_symbol': 1 } );