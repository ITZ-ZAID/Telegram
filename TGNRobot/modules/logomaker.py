import os
import io
import requests
import shutil 
import random
import re
import glob
import time

from io import BytesIO
from requests import get
from telethon.tl.types import InputMessagesFilterPhotos

from TGNRobot import OWNER_ID, SUPPORT_CHAT
from TGNRobot.events import register
from TGNRobot import telethn
from PIL import Image, ImageDraw, ImageFont


LOGO_LINKS            = ["https://telegra.ph/file/d1838efdafce9fe611d0c.jpg",
                         "https://telegra.ph/file/c1ff2d5ec5e1b5bd1b200.jpg",
                         "https://telegra.ph/file/08c5fbe14cc4b13d1de05.jpg",
                         "https://telegra.ph/file/66614a049d74fe2a220dc.jpg",
                         "https://telegra.ph/file/9cc1e4b24bfa13873bd66.jpg",
                         "https://telegra.ph/file/792d38bd74b0c3165c11d.jpg",
                         "https://telegra.ph/file/e1031e28a4aa4d8bd7c9b.jpg",
                         "https://telegra.ph/file/2be9027c55b5ed463fc18.jpg",
                         "https://telegra.ph/file/9fd71f8d08158d0cc393c.jpg",
                         "https://telegra.ph/file/627105074f0456f42058b.jpg",
                         "https://telegra.ph/file/62b712f741382d3c171cd.jpg",
                         "https://telegra.ph/file/496651e0d5e4d22b8f72d.jpg",
                         "https://telegra.ph/file/6619d0eee2c35e022ee74.jpg",
                         "https://telegra.ph/file/f72fcb27c9b1e762d184b.jpg",
                         "https://telegra.ph/file/01eac0fe1a722a864d7de.jpg",
                         "https://telegra.ph/file/bdcb746fbfdf38f812873.jpg",
                         "https://telegra.ph/file/d13e036a129df90651deb.jpg",
                         "https://telegra.ph/file/ab6715ce9a63523bd0219.jpg",
                         "https://telegra.ph/file/c243f4e80ebf0110f9f00.jpg",
                         "https://telegra.ph/file/ff9053f2c7bfb2badc99e.jpg",
                         "https://telegra.ph/file/00b9ebbb816285d9a59f9.jpg",
                         "https://telegra.ph/file/ad92e1c829d14afa25cf2.jpg",
                         "https://telegra.ph/file/58d45cc3374e7b28a1e67.jpg",
                         "https://telegra.ph/file/4140a0b3f27c302fd81cb.jpg",
                         "https://telegra.ph/file/c4db2b5c84c1d90f5ac8a.jpg",
                         "https://telegra.ph/file/c0da5080a3ff7643ddeb4.jpg",
                         "https://telegra.ph/file/79fad473ffe888ed771b2.jpg",
                         "https://telegra.ph/file/eafd526d9dcc164d7269f.jpg",
                         "https://telegra.ph/file/98b50e8424dd2be9fc127.jpg",
                         "https://telegra.ph/file/c1ad29c189162a1404749.jpg",
                         "https://telegra.ph/file/2d288450ebecc500addbd.jpg",
                         "https://telegra.ph/file/9715353976a99becd7632.jpg",
                         "https://telegra.ph/file/87670b02a1004bc02bd8d.jpg",
                         "https://telegra.ph/file/70789cd69114939a78242.jpg",
                         "https://telegra.ph/file/1566bd334f00645cfa993.jpg",
                         "https://telegra.ph/file/9727c37bb8c633208b915.jpg",
                         "https://telegra.ph/file/27467ef55fab117ccb278.jpg",
                         "https://telegra.ph/file/b9c62ff7810d9e84e9e2c.jpg",
                         "https://telegra.ph/file/87d22f2c95413059dda4e.jpg",
                         "https://telegra.ph/file/e528a731accbcdea140e3.jpg",
                         "https://telegra.ph/file/ee3f20c3ce71dc37fecb2.jpg",
                         "https://telegra.ph/file/a049f78377a5b8257294d.jpg",
                         "https://telegra.ph/file/54d22d39ea89423b7533f.jpg",
                         "https://telegra.ph/file/d90baa59b6fe2bc3091d3.jpg",
                         "https://telegra.ph/file/b9b3f80dc4635faaeb472.jpg",
                         "https://telegra.ph/file/d64be0a98f441a33d2aef.jpg",
                         "https://telegra.ph/file/e2c59ac97a900bab5ad7d.jpg",
                         "https://telegra.ph/file/41baf461b0a34f1a881a9.jpg",
                         "https://telegra.ph/file/8d4082052b4bd0a8cc862.jpg",
                         "https://telegra.ph/file/e7d6e0c511137ad67d843.jpg",
                         "https://telegra.ph/file/d7b97ea806d4a905b71c4.jpg",
                         "https://telegra.ph/file/6bec48ea2c96cf3d668a4.jpg",
                         "https://telegra.ph/file/aa64389b70e0de02d18c5.jpg",
                         "https://telegra.ph/file/2f75d964a59a3a4ae90e0.jpg",
                         "https://telegra.ph/file/f408df72c57cfc05e734f.jpg",
                         "https://telegra.ph/file/9d88d9dfb50106bc43c91.jpg",
                         "https://telegra.ph/file/a5a6e0f9d172fa386621e.jpg",
                         "https://telegra.ph/file/b0fc771c91409ee5cd4dc.jpg",
                         "https://telegra.ph/file/b0fc771c91409ee5cd4dc.jpg",
                         "https://telegra.ph/file/f75e59ebd4059f394479e.jpg",
                         "https://telegra.ph/file/fc0308f59023d0c997166.jpg",
                         "https://telegra.ph/file/7e1c04947f6afb6cdf25c.jpg",
                         "https://telegra.ph/file/6279bb4be7e48da194353.jpg",
                         "https://telegra.ph/file/616784fcd89f13e789685.jpg",
                         "https://telegra.ph/file/803e7dd9fafdb086bce4a.jpg",
                         "https://telegra.ph/file/d7338861b7f996ec9d40d.jpg",
                         "https://telegra.ph/file/828730cd4d73333eaf129.jpg",
                         "https://telegra.ph/file/36c9321161d49c4b3d671.jpg",
                         "https://telegra.ph/file/ebeae90b99fe482d11784.jpg",
                         "https://telegra.ph/file/70f38f92fe8d3060a31e4.jpg",
                         "https://telegra.ph/file/db12cf905f557487abc60.jpg",
                         "https://telegra.ph/file/0f9be531164c927ded8ec.jpg",
                         "https://telegra.ph/file/57fb7a6df3d666878c6f3.jpg",
                         "https://telegra.ph/file/242930d9f7aaa0b0729fd.jpg",
                         "https://telegra.ph/file/883f255792d2c2ebdd5f5.jpg",
                         "https://telegra.ph/file/36a9c0c26967edf90d42d.jpg",
                         "https://telegra.ph/file/03bdaf253c43fc97adbbe.jpg",
                         "https://telegra.ph/file/5826715ff0895a5321d2d.jpg",
                         "https://telegra.ph/file/74807bfbc85057899ea8d.png",
                         "https://telegra.ph/file/e390f7531557c12379acb.jpg",
                         "https://telegra.ph/file/0b83432e72bb0ce0ed0f1.jpg",
                         "https://telegra.ph/file/23276d7f831611e347a7c.jpg",
                         "https://telegra.ph/file/109789c7dcc615c6731fa.jpg",
                         "https://telegra.ph/file/127ef2c311b42b2dbfb62.jpg",
                         "https://telegra.ph/file/bfd7fcd13b2c353030ef0.jpg",
                         "https://telegra.ph/file/0f7773c27b1379e2f3bea.jpg",
                         "https://telegra.ph/file/4606e5c76a4a6c893a721.png",
                         "https://telegra.ph/file/f46c4569d77d9a6be6aed.jpg",
                         "https://telegra.ph/file/2b4718637a7396e3b23d9.jpg",
                         "https://telegra.ph/file/40bce3c8e8ae3cd0198b9.jpg",
                         "https://telegra.ph/file/ac61cfac3290ed635f8cc.jpg",
                         "https://telegra.ph/file/55313171c70692e838451.jpg",
                         "https://telegra.ph/file/f503ce00794cadbdacdd2.jpg",
                         "https://telegra.ph/file/2153d9fad3613041fcd28.jpg",
                         "https://telegra.ph/file/6a7a790fe964c8c264b61.jpg",
                         "https://telegra.ph/file/103d2f4b7b1088890ae24.jpg",
                         "https://telegra.ph/file/63501bb4f1de53a81dba1.jpg",
                         "https://telegra.ph/file/00fdb4e3a06a6f6e81c35.jpg",
                         "https://telegra.ph/file/e2fbfce637048d2e042da.jpg",
                         "https://telegra.ph/file/29d3c7c297c40a17cde4b.jpg",
                         "https://telegra.ph/file/97c7aa91c51f72f82c2d9.jpg",
                         "https://telegra.ph/file/0096988891ba9b884d2dd.jpg",
                         "https://telegra.ph/file/12cb5cb6512b754deb92d.jpg",
                         "https://telegra.ph/file/38387c8384879e0ddb803.jpg",
                         "https://telegra.ph/file/3353253a27522219cc1ce.jpg",
                         "https://telegra.ph/file/daae7def66cb1d1aefa23.jpg",
                         "https://telegra.ph/file/e5fe618ad651777061c54.jpg",
                         "https://telegra.ph/file/3c56aa160ec242b1670eb.jpg",
                         "https://telegra.ph/file/0794ddfefdc770646c478.jpg",
                         "https://telegra.ph/file/05bc05a4b878e54ed3b20.jpg",
                         "https://telegra.ph/file/ef7ffbd3839645e33a0ec.jpg",
                         "https://telegra.ph/file/1daa50b9d3e26a5509cc2.png",
                         "https://telegra.ph/file/510600a5b93d83ce048f3.jpg",
                         "https://telegra.ph/file/0ede8bd4788327111ecbf.jpg",
                         "https://telegra.ph/file/e9f546797e42e821a91e1.jpg",
                         "https://telegra.ph/file/fc7fbefe92599bd79d038.jpg",
                         "https://telegra.ph/file/b88d6e78e206eb73e2e54.jpg",
                         "https://telegra.ph/file/48f8c62829953e82441e8.jpg",
                         "https://telegra.ph/file/56f7b34cae98a491e2b35.jpg",
                         "https://telegra.ph/file/9c23b4302926d40c46e12.jpg",
                         "https://telegra.ph/file/9bf850ea98a2b252ff233.jpg",
                         "https://telegra.ph/file/e764f0b3e2ecc56167803.jpg",
                         "https://telegra.ph/file/289f9cebe37f31a943f98.jpg",
                         "https://telegra.ph/file/0c647be0f5a48d576d692.jpg",
                         "https://telegra.ph/file/41c5b44c4f5978828b5b5.jpg",
                         "https://telegra.ph/file/9cdce279bdf240a933c14.jpg",
                         "https://telegra.ph/file/f20424687f94e9c285133.jpg",
                         "https://telegra.ph/file/e7858eb025e1ddb2f6267.jpg",
                         "https://telegra.ph/file/3e984aa5ab96df166f2a4.jpg",
                         "https://telegra.ph/file/e43e28aa952eaee6a5315.jpg",
                         "https://telegra.ph/file/6d222dcaf9ba1072c6062.jpg",
                         "https://telegra.ph/file/21e696bbefcfe39c6e74e.jpg",
                         "https://telegra.ph/file/64ec61e41da3d4aded33d.jpg",
                         "https://telegra.ph/file/5b1d8766504ff75c1bd1f.jpg",
                         "https://telegra.ph/file/731879a344b3b49fe51bd.jpg",
                         "https://telegra.ph/file/6221afc84b357ed0d1fc5.jpg",
                         "https://telegra.ph/file/499bb1117771d8c020038.jpg",
                         "https://telegra.ph/file/2690d73bc32cfdb986629.jpg",
                         "https://telegra.ph/file/21255de971701b9df0902.jpg",
                         "https://telegra.ph/file/434a35e7fe5e2c000c598.jpg",
                         "https://telegra.ph/file/22a5d3621aba0b370d0b6.png",
                         "https://telegra.ph/file/ae31845d1df2c4a84915b.png",
                         "https://telegra.ph/file/ae2b809c8d11e7fa4121d.png",
                         "https://telegra.ph/file/ccb7f3113994d5d2b26f6.png",
                         "https://telegra.ph/file/5e53f0257ff12a7b0737a.png",
                         "https://telegra.ph/file/a613600a9f9f8ee29f0f7.jpg",
                         "https://telegra.ph/file/129c14fada1a8c0b151f5.jpg",
                         "https://telegra.ph/file/c7552ed4246ccd8efd301.jpg",
                         "https://telegra.ph/file/e794f772243d46467bcce.jpg",
                         "https://telegra.ph/file/b6c43b9bd63f5f764d60b.jpg",
                         "https://telegra.ph/file/11585459a3950de7f307c.png",
                         "https://telegra.ph/file/37cde08802c3cea25a03f.jpg",
                         "https://telegra.ph/file/d8d2db623223dee65963e.png",
                         "https://telegra.ph/file/b7229017ffee2d814c646.jpg",
                         "https://telegra.ph/file/65630efca60bfbdf84bc9.jpg",
                         "https://telegra.ph/file/b8ce571c2f66a7c7070e5.jpg",
                         "https://telegra.ph/file/a39f63f61f143ec00f19f.jpg",
                         "https://telegra.ph/file/f7d946d8caaa21bf96dbf.jpg",
                         "https://telegra.ph/file/9e4bef8ae0725d6b62108.png",
                         "https://telegra.ph/file/3550089b22f3c8f506226.jpg",
                         "https://telegra.ph/file/4275a4d4d6d433406b5fa.jpg",
                         "https://telegra.ph/file/c476583ff55e1947461ad.jpg",
                         "https://telegra.ph/file/87d2e5c0170ead00a2bc2.jpg",
                         "https://telegra.ph/file/5027dd7379cc432c06e73.jpg",
                         "https://telegra.ph/file/9e447fcaf3c66ddefb603.jpg",
                         "https://telegra.ph/file/e5375f8233bea4f74b0f8.jpg",
                         "https://telegra.ph/file/a1297510a64733cc5845f.jpg",
                         "https://telegra.ph/file/ff04b594b699ce72316d7.jpg",
                         "https://telegra.ph/file/093836a52cb166f161819.jpg",
                         "https://telegra.ph/file/1e64bae43ca10d628ff6d.jpg",
                         "https://telegra.ph/file/678ff9bb3405158a9155e.jpg",
                         "https://telegra.ph/file/ab332ced3f63b96c375c5.jpg",
                         "https://telegra.ph/file/a736d6cac93294c323303.jpg",
                         "https://telegra.ph/file/dce8565bf7742f3d7122b.jpg",
                         "https://telegra.ph/file/3f97672eb7b50426d15ff.jpg",
                         "https://telegra.ph/file/19c6250369f8588a169c7.jpg",
                         "https://telegra.ph/file/13d53b03a48448156564c.jpg",
                         "https://telegra.ph/file/d21ff0d35553890e8cf34.jpg",
                         "https://telegra.ph/file/a5e4cb43178642ba3709d.jpg",
                         "https://telegra.ph/file/ecf108d25a6f5f56f91f4.jpg",
                         "https://telegra.ph/file/8bd2b561b4c1f7164f934.png",
                         "https://telegra.ph/file/7717658e6930c8196a904.jpg",
                         "https://telegra.ph/file/dc85d43c4fc5062de7274.jpg",
                         "https://telegra.ph/file/ff05c19f228ab2ed3d39d.jpg",
                         "https://telegra.ph/file/ff05c19f228ab2ed3d39d.jpg",
                         "https://telegra.ph/file/0d686bfffcb92a2fbdb0f.jpg",
                         "https://telegra.ph/file/0d686bfffcb92a2fbdb0f.jpg",
                         "https://telegra.ph/file/cdc66f16fbfb75971df2f.jpg",
                         "https://telegra.ph/file/5c575892b9f9534fd4f31.jpg",
                         "https://telegra.ph/file/78ffc400d4f3236b00e6b.jpg",
                         "https://telegra.ph/file/89d32e5bbf084a376c803.jpg",
                         "https://telegra.ph/file/b5d7dbcdce241013a061b.jpg",
                         "https://telegra.ph/file/c1d228bc1859213d258d7.jpg",
                         "https://telegra.ph/file/c6b0720b9f765809ea20a.jpg",
                         "https://telegra.ph/file/df7e648f2e68ff8e1a1e6.jpg",
                         "https://telegra.ph/file/5148f764cbc4700519909.jpg",
                         "https://telegra.ph/file/479e7f51c682dcd1f013f.jpg",
                         "https://telegra.ph/file/54a9eb0afe7a0f9c7c2f3.jpg",
                         "https://telegra.ph/file/73c52ee54567a61dac47a.jpg",
                         "https://telegra.ph/file/1427dbba81bd21b1bfc56.jpg",
                         "https://telegra.ph/file/1427dbba81bd21b1bfc56.jpg",
                         "https://telegra.ph/file/b0816374b470a5f9c66a6.jpg",
                         "https://telegra.ph/file/e10840ec9bea9bbfaff0e.jpg",
                         "https://telegra.ph/file/5935275d3ee09bc5a47b8.png",
                         "https://telegra.ph/file/c27e64f1e8ece187c8161.jpg",
                         "https://telegra.ph/file/055e9af8500ab92755358.jpg",
                         "https://telegra.ph/file/f18f71167f9318ea28571.jpg",
                         "https://telegra.ph/file/e2e26f252a5e25a1563c5.jpg",
                         "https://telegra.ph/file/47ccb13820d6fc54d872b.jpg",
                         "https://telegra.ph/file/f2ddccd28ceaeae90b2a3.jpg",
                         "https://telegra.ph/file/951c872f7f8d551995652.jpg",
                         "https://telegra.ph/file/8e8842f9fe207b8abd951.jpg",
                         "https://telegra.ph/file/8a14ecd2347ef88e81201.jpg",
                         "https://telegra.ph/file/b3869374ce0af9f26f92a.jpg",
                         "https://telegra.ph/file/8e17f8d3633a5696a1ccf.jpg",
                         "https://telegra.ph/file/b29d8956ae249773b0ec7.png",
                         "https://telegra.ph/file/d0eebe724b67d2ef7647e.jpg",
                         "https://telegra.ph/file/5780b3273162d2b9ba9ec.jpg",
                         "https://telegra.ph/file/e2d56d5dbb108ba7af20c.jpg",
                         "https://telegra.ph/file/1a4f50dd1e4ec9f04bfa1.jpg",
                         "https://telegra.ph/file/99b56305fa9c50767f574.jpg",
                         "https://telegra.ph/file/0859e0104c671bc9b6b7d.jpg",
                         "https://telegra.ph/file/b3af2980caf7040702171.jpg",
                         "https://telegra.ph/file/14be160df3b84c59e268e.jpg",
                         "https://telegra.ph/file/b958155e1e8e9ab9a0416.jpg",
                         "https://telegra.ph/file/24fff051c39b815e5078a.jpg",
                         "https://telegra.ph/file/258c02c002e89287d5d9b.jpg",
                         "https://telegra.ph/file/d2abc99773a9d4954c2ba.jpg",                       
                         "https://telegra.ph/file/9849b3940f063b065f4e3.jpg"
                         ]

@register(pattern="^/logo ?(.*)")
async def lego(event):
 quew = event.pattern_match.group(1)
 if event.sender_id == OWNER_ID:
     pass
 else:

  if not quew:
     await event.reply('Please Gimmie A Text For The Logo.')
     return
 pesan = await event.reply('Logo In A Process. Please Wait.')
 try:
    text = event.pattern_match.group(1)
    randc = random.choice(LOGO_LINKS)
    img = Image.open(io.BytesIO(requests.get(randc).content))
    draw = ImageDraw.Draw(img)
    image_widthz, image_heightz = img.size
    pointsize = 500
    fillcolor = "black"
    shadowcolor = "blue"
    fnt = glob.glob("./TGNRobot/utils/Logo/*")
    randf = random.choice(fnt)
    font = ImageFont.truetype(randf, 120)
    w, h = draw.textsize(text, font=font)
    h += int(h*0.21)
    image_width, image_height = img.size
    draw.text(((image_widthz-w)/2, (image_heightz-h)/2), text, font=font, fill=(255, 255, 255))
    x = (image_widthz-w)/2
    y = ((image_heightz-h)/2+6)
    draw.text((x, y), text, font=font, fill="white", stroke_width=1, stroke_fill="black")
    fname = "ZaidRobot.png"
    img.save(fname, "png")
    await telethn.send_file(event.chat_id, file=fname, caption = f"Made by @TGN_RO_BOT")         
    await pesan.delete()
    if os.path.exists(fname):
            os.remove(fname)
 except Exception as e:
    await event.reply(f'Error, Report @{SUPPORT_CHAT}, {e}')
