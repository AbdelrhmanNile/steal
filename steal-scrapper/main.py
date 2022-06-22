import steal_scrapper

mongodb_passwd = "" ##your db passwd
twitch_secret = "" 
csvname = input("output file name: ")
testing = steal.Steal(csvname, 76,twitch_secret=twitch_secret, db_passwd=passwd, pushdb=True)
testing.run()
