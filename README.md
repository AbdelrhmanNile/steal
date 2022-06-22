# About
<img src = "https://i.imgur.com/0pZy9V2.png">

<h1 align="center">steaL - The L Stands For Linux</h1>
steaL is a free and opensource game-center and bittorrent client for Linux, steaL fetches all the repacks uploaded by [johncena141](https://1337x.to/user/johncena141/) on 1337x

just download the game and run it! everything is pre-configuired for you thank's to  johncena141 repacks! <br />


steaL's database gets updated weekly to fetch new released johncena141 repacks <br />

# IMPORTANT

please read [johncena141's documents](https://github.com/jc141x/jc141-bash/tree/master/setup) to understand more about how their repacks work, and double check the dependencies for their repacks

# Dependencies

Arch Linux:
```
sudo pacman -S python

sudo pacman -S sharutils

yay -S zpaq

yay -S dwarfs

sudo pacman -S fuse-overlaysfs

sudo pacman -S tcsh
```

python modules:
```
pip3 install kivy

pip3 install pandas

pip3 install pebble
```

node.js:
```
npm install webtorrent-cli -g
```

# Build and Install

download:
```
git clone https://github.com/AbdelrhmanNile/steal.git
```

cd to cloned repo:
```
cd steal/
```

build:
```
chmod +x build.sh && ./build.sh 
```

install:
```
sudo make install
```

# Run and Conf

to run steaL, in your command line type:
```
steal
```

after first run, the directory ~/.config/steal will be created
it contains 2 files conf.json and library.csv

conf.json has two parameters:
```
{
    "lib_path": "/home/USER/Games", <-- default path to save the downloaded games is Games dir in your user's home, change it to whatever
    "num_of_cards": "50" <-- number of games displayed in Browse tab
}
```

library.csv contains info about the games you download { name, cover url and launching script }

# Usage
just search for the game you want and downloaded it, wait until it finish extracting {zpaq takes time to extract, be patient}

after it's done go to Library tab and type update in the search bar to refresh your game Library and make new downloaded games appear

to launch a game just click on it

Enjoy!!


# Known issues

1- steal takes several seconds to launch, and it freezes for a second when you search for a game, it's all caused by the blocking Api calls that steal makes to fetch the data from the database

i believe it could be solved by implementing the calls in a async way, if you can solve it please contribute and make a pull-request

2- when you download a new game it won't appear in Library tab unless you type update in the search bar or re-start steal

3- the UI is not hte most polished and sexy, in fact it's ugly, so if you can make it better you are very welcome to contribute :3

4- source code is kinda a mess, i'll add more comments when i have time

you could say this is a beta release, it will get better in the future
