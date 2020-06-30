wget "https://storage.scrapinghub.com/items/458526/1/2?apikey=7ed8f26e9e4d48bcad71be9226d812c2&format=csv&saveas=items_jnbk_2.csv&fields=Break%20Id,Maker,Model,Year,Engine%20Vol,Engine%20No,Body,Front%20Rotor,Front%20Brake,Rear%20Rotor,Rear%20Brake,Parking%20Shoe,Specifications,Alternatives,Cross%20References,Product%20Url,Image%20Url&include_headers=1" --output-document=jnbk/items_jnbk_2.csv
python3 download.py
rm items_jnbk_2.csv
