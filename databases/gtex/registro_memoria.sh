while [ 1 ];
do
docker stats  bio_api_mongo_db --no-stream | grep bio_api_mongo_db | awk '{print $4$5$6}'; 
sleep 10;
done
