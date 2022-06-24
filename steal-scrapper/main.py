"""
steaL scrapper

outputs csv file on its directory [ignore it]

outputs a json file on its directory

the json file is the final result with all the data

pushes the json file to monogodb if push_to_db is True, else will only output the files mentioned above
"""


import steal_scrapper

mongodb_passwd = ""  ##your db passwd
twitch_client_id = ""
twitch_client_secret = ""
output_file_name = input("output file name: ")
num_of_pages = 76  # number of the pages you want to scrape on 1337x
push_to_db = True  # if false, it will not push the scrapped data to mongodb

scrapper = steal_scrapper.Steal(
    output_file_name,
    num_of_pages,
    twitch_client_id=twitch_client_id,
    twitch_client_secret=twitch_client_secret,
    db_passwd=passwd,
    pushdb=push_to_db,
)


scrapper.run()
