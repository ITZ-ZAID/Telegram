# 🅣🅖🅝 🅡🅞🅑🅞🅣

[![ᴅᴇᴘʟᴏʏ](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Itsunknown-12/TGN-Robot)

## 🅡🅔🅟🅞 🅢🅣🅐🅣🅢
![github card](https://github-readme-stats.vercel.app/api/pin/?username=Itsunknown-12&repo=Zaid-Robot&theme=dark)


<h1 align = "center"> ❝𝐓𝐡𝐞 𝐌𝐨𝐬𝐭 𝐏𝐨𝐰𝐞𝐫𝐟𝐮𝐥𝐥 𝐆𝐫𝐨𝐮𝐩 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭 𝐁𝐨𝐭❞ </h1>


<p align = "center"><a herf = "https://t.me/Mrjokerlk_bot" alt = "Mrjoker"><img src = "https://telegra.ph/file/6525d89de5b72003d80fa.png" width = "900"></a></p>

<p align = "center">
<a href = "https://python.org">
<img src = "https://forthebadge.com/images/badges/made-with-python.svg">
</p>
</a>

<p align = "center">
<a href = "https://github.com/kjeymax/MR-JOKER_BOT">
<img src = "https://forthebadge.com/images/badges/open-source.svg">
</p>
</a>


<p align="Center">
<a href="https://github.com/kjeymax/MR-JOKER_BOT/discussions" alt="Mr Joker"> <img src="https://img.shields.io/badge/%F0%9F%A4%A1-Mr%20Joker%20Discussions-9cf" /> </a>


[![MRJOKER](https://img.shields.io/github/forks/kjeymax/MR-JOKER_BOT?color=Red%20&label=Github%20Fork&style=for-the-badge)](https://github.com/kjeymax/MR-JOKER_BOT)
[![MRJOKER](https://img.shields.io/github/watchers/kjeymax/MR-JOKER_BOT?color=red&style=for-the-badge)](https://github.com/kjeymax/MR-JOKER_BOT)


## Configuration 

<h3 align = "justify">Create a new <u>config.py</u> or rename <u>sample_config.py</u> to <u>config.py</u> file in same dir and import, then extend this class.</h3>

- `TOKEN`                  : Your [bot Token](https://t.me/BotFather), As a string
- `API_ID & API_HASH`      : Get API_ID & API_HASH from my.telegram.org, used for telethon based modules.
- `SQLALCHEMY_DATABASE_URI`: Your database URL
-  `OWNER_ID`              : An integer of consisting of your [owner ID](https://t.memy_id_bot)
-   `OWNER_USERNAME`       : Your username (without the @)
-   `SUPPORT_CHAT`         : Your Telegram support group chat username
-   `EVENT_LOGS`           : Event logs channel to note down important bot level events, recommend to make this public. ex: `-100:123`
-   `JOIN_LOGGER`          : A channel where bot will print who added it to what group, useful during debugging or spam handling.
-   `CASH_API_KEY`         :Required for currency converter. [Get yours from](https://www.alphavantage.co/support/#api-key)
-   `TIME_API_KEY`         : Required for timezone information. [Get yours from](https://timezonedb.com/api)
-   `DEV_USERS`            : ID of users who are Devs of your bot (can use /py etc.). If you are a noob and would come and bother Mr.Joker support then keep the current ID's here at they are and add yours. 
-   `sw_api`               : Spamwatch API Token, Get one from [@SpamWatchBot](https://t.me/SpamWatchBot)
-   `STRICT_GBAN`          : Enforce gbans across new groups as well as old groups. When a gbanned user talks, he will be banned.
-   `DRAGONS`              : A space separated list of user IDs who you want to assign as sudo users
-   `DEMONS`               : A space separated list of user IDs who you wanna assign as support users(gban perms only)
-   `TIGERS`               : A space separated list of user IDs who you wanna assign as tiger users.
-   `WOLVES`               : A space separated list of user IDs who you want to assign as whitelisted - can't be banned with your bot.
-   `ENV`                  : Setting this to ANYTHING will enable environment variables. Leave it as it is
-   `WEBHOOK`              : Setting this to ANYTHING will enable webhooks. If you dont know how this works leave it as it is
-   `PORT`                 : Port to use for your webhooks. Better leave this as it is on heroku
-   `URL`                  : The Heroku App URL :-  `https://<appname>.herokuapp.com`
-   `No_LOAD`              : Dont load these modules cause they shit, space separation
-   `BL_CHATS`             : List of chats you want blacklisted.
-   `ALLOW_EXCL`           : Set this to True if you want ! to be a command prefix along with /. Recommended is True
-   `DEL_CMDS`             : Set this to True if you want to delete command messages from users who don't have the perms to run that command.
-   `AI_API_KEY`           : Make your bot talk using Intellivoid's chatbot API, [Get your key from](https://coffeehouse.intellivoid.net/)
-   `BAN_STICKER`          : ID of the sticker you want to use when banning people
-   `WALL_API`             : Required for wallpaper. [Get your's from](https://wall.alphacoders.com/)  
-   `ARQ_API_URL`          : https://thearq.tech/ 👈 Fill in this way
-   `ARQ_API_KEY`          : Start this boat https://t.me/ARQRobot. Get the key
-   `REM_BG_API_KEY`       : Go to this site https://www.remove.bg/api#remove-background. Get your api key
-    `GENIUS_API_TOKEN`    : Go to this site https://docs.genius.com/. Get your api token
 
 
## Python dependencies

<h3 align = "justify">Install the necessary python dependencies by moving to the project directory and running:</h3>

```
pip3 install -U -r requirements.txt

```


## Database

<h3 align = "justify">If you wish to use a database-dependent module (eg: locks, notes, userinfo, users, filters, welcomes), you'll need to have a database installed on your system. I use postgres, so I recommend using it for optimal compatibility.</br></br>

In the case of postgres, this is how you would set up a the database on a debian/ubuntu system. Other distributions may vary</h3>

- Install postgresql  

```
sudo apt-get update && sudo apt-get install postgresql 

```

- Change to the postgres user 
 
 ```
 sudo su - postgres
 
 ```
 
 - Create a new database user (change YOUR_USER appropriately)
 
 ```
 createuser -P -s -e YOUR_USER
 
 ```
 
This will be followed by you needing to input your password.

- create a new database table:

```

createdb -O YOUR_USER YOUR_DB_NAME

```

Change YOUR_USER and YOUR_DB_NAME appropriately.

- finally:

```

psql YOUR_DB_NAME -h YOUR_HOST YOUR_USER

```

<h3 align = "justify">This will allow you to connect to your database via your terminal. By default, YOUR_HOST should be 0.0.0.0:5432.</br></br>

You should now be able to build your database URI. This will be:</h3>

```
sqldbtype://username:pw@hostname:port/db_name

```

<h3 align = "justify">Replace sqldbtype with whichever db youre using (eg postgres, mysql, sqllite, etc) repeat for your username, password, hostname (localhost?), port (5000), and db name.</h3>

## Support
[![HITECH](https://img.shields.io/badge/LKHITECH-Channel-red?style=for-the-badge&logo=telegram)](https://telegram.dog/lkhitech)</br></br>
[![HITECH](https://img.shields.io/badge/LKHITECH-Group-red?style=for-the-badge&logo=telegram)](https://telegram.dog/hitechlkgroup)</br></br>
[![CONTACT ME](https://img.shields.io/badge/Telegram-Contact%20Me-informational)](https://t.me/kavinduaj)

## Discussions
<p align="left">
<a href="https://github.com/kjeymax/MR-JOKER_BOT/discussions" alt="Mr Joker"> <img src="https://img.shields.io/badge/%F0%9F%A4%A1-Mr%20Joker%20Discussions-9cf" /> </a>

## Credits

 - [Utah](https://github.com/minatouzuki/utah).
 - [WilliamButcherBot](https://github.com/thehamkercat/WilliamButcherBot)
 - [Alita_Robot](https://github.com/DivideProjects/Alita_Robot/)
 - [Saitama Robot](https://github.com/AnimeKaizoku/SaitamaRobot)

<h3 align = "justify">Don't forget to star this repo if you liked it.</br></br>

Enjoy Your Bot! 💝</h3> 

