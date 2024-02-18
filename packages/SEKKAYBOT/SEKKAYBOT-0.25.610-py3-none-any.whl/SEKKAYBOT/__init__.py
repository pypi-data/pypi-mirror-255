try:
    # System imports.
    from typing import Tuple, Any, Union, Optional

    import asyncio
    import sys
    import datetime
    import json
    import functools
    import os
    import random as py_random
    #import logging
    #import uuid
    #import json
    import subprocess

    print('Attempting to install packages now.')

    for module in (
        'crayons',
        'git+https://github.com/PirxcyFinal/fortnitepy',
        'PirxcyPinger',
        'FortniteAPIAsync',
        'sanic==21.6.2',
        'aiohttp',
        'requests'
    ):
        #try:
          #subprocess.check_call([sys.executable, "-m", "pip", "uninstall", module, "--y"])
        #except:
          #pass
          subprocess.check_call([sys.executable, "-m", "pip", "install", module])

    os.system('clear')

    print('Installed packages, restarting script.')

    # Third party imports.
    from fortnitepy.ext import commands
    from colorama import Fore, init
    init(autoreset=True)
    from functools import partial

    from datetime import timedelta


    import crayons
    try:
      import PirxcyPinger
    except:
      pass
    import fortnitepy
    import FortniteAPIAsync
    import sanic
    import aiohttp
    #import uvloop
    import requests
  #22.12.0

except ModuleNotFoundError as e:
    python = sys.executable
    os.execl(python, python, *sys.argv)




os.system('clear')
print(crayons.cyan(f'\nSekkayBOT made by Sekkay & Cousin. USE CODE DEXE !'))
print(crayons.cyan(f'Discord server: discord.gg/tvJtRF25s2 - For support, questions, etc.'))

sanic_app = sanic.Sanic(__name__)
server = None


@sanic_app.middleware('response')
async def custom_banner(request: sanic.request.Request, response: sanic.response.HTTPResponse):
    response.headers["Access-Control-Allow-Origin"] = "*/*"

  
@sanic_app.route("/old")
async def oldindex(request):
    return sanic.response.json({"status": "online"})

@sanic_app.route('/', methods=['GET'])
async def root(request: sanic.request.Request) -> None:
    if 'Accept' in request.headers and request.headers['Accept'] == 'application/json':
        return sanic.response.json(
            {
                "status": "online"
            }
        )

    return sanic.response.html(
        """
<html>
   <head>
      <style>
         body {
         font-family: Arial, Helvetica, sans-serif;
         position: absolute;
         left: 50%;
         top: 50%;  
         -webkit-transform: translate(-50%, -50%);
         transform: translate(-50%, -50%);
         background-repeat: no-repeat;
         background-attachment: fixed;
         background-size: cover;
         background-color: #333;
         color: #f1f1f1;
         }
 
        ::-webkit-scrollbar {
          width: 0;
        }
        :root {
          --gradient: linear-gradient(90deg, #4ce115, #15c5e1, #e17815);
 
        }
        body {
          font-family: basic-sans, sans-serif;
          min-height: 100vh;
          display: flex;
          justify-content: ;
          align-items: center;
          font-size: 1.125em;
          line-height: 1.6;
          color: #2e2d2d;
          background: #ddd;
          background-size: 300%;
          background-image: var(--gradient);
          animation: bg-animation 25s infinite;
        }
        @keyframes bg-animation {
          0% {background-position: left}
          50% {background-position: right}
          100% {background-position: left}
        }
        .content {
          background: white;
          width: 70vw;
          padding: 3em;
          box-shadow: 0 0 3em rgba(0,0,0,.15);
        }
        .title {
          margin: 0 0 .5em;
          text-transform: uppercase;
          font-weight: 900;
          font-style: italic;
          font-size: 3rem;
          color: #2e2d2d;
          line-height: .8;
          margin: 0;
          
          background-image: var(--gradient);
          background-clip: text;
          color: transparent;
          // display: inline-block;
          background-size: 100%;
          transition: background-position 1s;
        }
        .title:hover {
          background-position: right;
        }
        .fun {
          color: white;
 
      </style>
   </head>
   <body>
      <center>
         <h2 id="response">
            """ + f"""Online now {name}""" + """
            <h2>
            """ + f"""Total Friends: {friend}/1000""" + """
            </h2>
            <h2>
            """ + f"""💎 Version {__version__} 💎""" + """
 
            </h2>
         </h2>
      </center>
   </body>
</html>
        """
    )


@sanic_app.route("/default")
async def xxc(request):
    return sanic.response.json(
        {
            "username": name,
            "friend_count": friend,
            "cid": cid
        }
    )

@sanic_app.route('/ping', methods=['GET'])
async def accept_ping(request: sanic.request.Request) -> None:
    return sanic.response.json(
        {
            "status": "online"
        }
    )


@sanic_app.route('/name', methods=['GET'])
async def display_name(request: sanic.request.Request) -> None:
    return sanic.response.json(
        {
            "display_name": name
        }
    )



name = ""
cid = ""
friend = ""
code = ""

password = "0098"
admin = "lil Sekkay","Sekkay Bot","TwitchCousin","Dexe Bot","MathyslolFN"
copied_player = ""
errordiff = 'errors.com.epicgames.common.throttled', 'errors.com.epicgames.friends.inviter_friendships_limit_exceeded'
__version__ = "10.0"

with open('info.json') as f:
    try:
        info = json.load(f)
    except json.decoder.JSONDecodeError as e:
        print(Fore.RED + ' [ERROR] ' + Fore.RESET + "")
        print(Fore.LIGHTRED_EX + f'\n {e}')
        exit(1)

def is_admin():
    async def predicate(ctx):
        return ctx.author.display_name in info['FullAccess']
    return commands.check(predicate)

prefix = '!','?','/','',' ','+'

class SekkayBot(commands.Bot):
    def __init__(self, device_id: str, account_id: str, secret: str, loop=asyncio.get_event_loop(), **kwargs) -> None:
        global code
        self.status = '🏁 Starting 🏁'
        
        self.fortnite_api = FortniteAPIAsync.APIClient()
        self.loop = asyncio.get_event_loop()

        super().__init__(
            command_prefix=prefix,
            case_insensitive=True,
            auth=fortnitepy.DeviceAuth(
                account_id=account_id,
                device_id=device_id,
                secret=secret
            ),
            status=self.status,
            platform=fortnitepy.Platform('PSN'),
            **kwargs
        )

        self.session = aiohttp.ClientSession()

        self.default_skin = "CID_NPC_Athena_Commando_M_Apparition_Grunt"
        self.default_backpack = "BID_833_TieDyeFashion"
        self.default_pickaxe = "Pickaxe_Lockjaw"
        self.banner = "otherbanner51"
        self.banner_colour = "defaultcolor22"
        self.default_level = 1000
        self.default_bp_tier = 1000
        self.sanic_app = sanic_app
        self.invitecc = ''
        self.invite_message = f'{code}'
        self.request_message = f'{code}'
        self.welcome_message =  "WELCOME"

        self.blacklist_invite = 'SekkayBot','COUSINFN','MathyslolFN'

        #ggg = requests.get(f"https://3bcd68df-f1ff-4a83-88ec-90690125c3ff-00-ptb5gqyw2xpi.worf.replit.dev/pseudos").json()
        #self.list_pseudo = ggg['pseudos']
        #self.codecc = py_random.choice(self.list_pseudo)
        self.codecc = ""

        self.banned_player = ""
        self.banned_msg = ""

        self.restart2 = "F"
        self.version = "0.0"
        self.backlist = "0.0"
        self.web = "F"



    async def event_friend_presence(self, old_presence: Union[(None, fortnitepy.Presence)], presence: fortnitepy.Presence):
        if not self.is_ready():
            await self.wait_until_ready()
        if self.invitecc == 'True':
            if old_presence is None:
                friend = presence.friend
                if friend.display_name != self.blacklist_invite:
                  if not len(self.friends) > 100:
                    pass
                  else:
                    try:
                        await friend.send(self.invite_message)
                    except:
                        pass
                    else:
                        if not self.party.member_count >= 16:
                            await friend.invite()

    async def set_and_update_party_prop(self, schema_key: str, new_value: Any) -> None:
        prop = {schema_key: self.party.me.meta.set_prop(schema_key, new_value)}

        await self.party.patch(updated=prop)

    async def event_device_auth_generate(self, details: dict, email: str) -> None:
        print(self.user.display_name)

    async def add_list(self) -> None:
        try:
            await self.add_friend('8719f7d05da740f9b19ac0fdd15ae200')
        except: 
          pass    

    async def event_ready(self) -> None:
        global name
        global friend
        global cid

        #get user outfit
        cid = self.party.me.outfit

        coro = self.sanic_app.create_server(
            host='0.0.0.0',
            port=8000,
            return_asyncio_server=True,
            access_log=False
        )
        self.server = await coro
        name = self.user.display_name
        friend = len(self.friends)

        print(crayons.green(f'Client ready as {self.user.display_name}.'))

        await asyncio.sleep(3)

        self.loop.create_task(self.add_list())


        self.loop.create_task(self.invitefriends())


        self.loop.create_task(self.update_api())

        self.loop.create_task(self.pinger())

        
        self.loop.create_task(self.delete_friends_last_logout())


        self.loop.create_task(self.update_settings())

        self.loop.create_task(self.check_update())

        self.loop.create_task(self.status_change())

        self.loop.create_task(self.check_leader())

        #self.loop.create_task(self.pseudos_update())




        try:   
          print(f'incoming pending friends: {len(self.incoming_pending_friends)}')
          for pending in self.incoming_pending_friends:
            #print('getting friends')
            try:
              epic_friend = await pending.accept()
              if isinstance(epic_friend, fortnitepy.Friend):
                  print(f"Accepted: {epic_friend.display_name}.")
              else:
                  print(f"Declined: {pending.display_name}.")
            except fortnitepy.InviteeMaxFriendshipsExceeded:
              await pending.decline()

              print(f"Declined: {pending.display_name}.")
              
            except fortnitepy.HTTPException as epic_error:
                if epic_error.message_code != 'errors.com.epicgames.common.throttled':
                    raise
                await asyncio.sleep(int(epic_error.message_vars[0] + 1))
                try:
                  await pending.accept()
                except:
                  try:
                    await pending.decline()
                  except:
                    pass
            except:
              try:
                await pending.decline()
                print(f"Declined: {pending.display_name}.")
              except:
                print('error')

        except:
          pass
        #print(f'incoming pending friends: {len(self.incoming_pending_friends)}')






  
    async def delete_friends_last_logout(self):
      now = datetime.datetime.now()
      try:
        for friend in self.friends:
          if friend.last_logout < now - timedelta(hours=504):
              await friend.remove()
              print(f'removed {friend}')
      except:
        pass


    #async def pseudos_update(self):
      #pseudoslol = requests.get('https://3bcd68df-f1ff-4a83-88ec-90690125c3ff-00-ptb5gqyw2xpi.worf.replit.dev/pseudos').json()

      
      #if len(self.friends) == 0 or len(self.friends) == 1:
        #url = "https://3bcd68df-f1ff-4a83-88ec-90690125c3ff-00-ptb5gqyw2xpi.worf.replit.dev/pseudos"
        #data = {
          #"id": f"{self.user.display_name}"}
        
        #xxxx = requests.post(url, json=data)
        
      #elif len(self.friends) > 100:
        #url = "https://3bcd68df-f1ff-4a83-88ec-90690125c3ff-00-ptb5gqyw2xpi.worf.replit.dev/remove"
        #data = {
            #"id": f"{self.user.display_name}"}
        
        #xxx = requests.post(url, json=data)
      #else:
        #if not self.user.display_name in pseudoslol['pseudos']:
          #url = "https://3bcd68df-f1ff-4a83-88ec-90690125c3ff-00-ptb5gqyw2xpi.worf.replit.dev/pseudos"
          #data = {
              #"id": f"{self.user.display_name}"}
          
          #xx = requests.post(url, json=data)



  
          

    async def check_leader(self):
      
        party_sekkay = requests.get('https://efb77a24-4c60-4996-a55f-cd15386be21f-00-11tqwhk3cgd59.worf.replit.dev/party.json').json

        try:
          
          self.web = party_sekkay['auto_leave_if_u_not_leader']
  
          if self.web == "T":
              if not self.party.me.leader:
                  await self.party.me.leave()
        except:
          pass

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// CHECK/ERROR/PARTY ////////////////////////////////////////////////////////////////////////////////////////////////////////

    async def check_party_validity(self):
      if not len(self.friends) > 100:
        await self.party.set_privacy(fortnitepy.PartyPrivacy.PRIVATE)
      else:
        await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// PARTY/INVITE ////////////////////////////////////////////////////////////////////////////////////////////////////////            

    async def event_party_invite(self, invite: fortnitepy.ReceivedPartyInvitation) -> None:
      if not len(self.friends) > 100:
        pass
      else:
        if invite.sender.display_name in info['FullAccess']:
            await invite.accept()
        elif invite.sender.display_name in admin:
            await invite.accept()    
        else:
            await invite.decline()
            await invite.sender.send(self.invite_message)
            await invite.sender.invite()

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// CHECK/FRIENDS/ADD ////////////////////////////////////////////////////////////////////////////////////////////////////////            

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// FRIENDS/ADD ////////////////////////////////////////////////////////////////////////////////////////////////////////

    async def pinger(self):
        try:
            await PirxcyPinger.post(f"https://{os.environ['REPL_ID']}.id.repl.co")
        except:
            pass
        return

    async def update_api(self) -> None:
        resp = requests.post(
                url=f'https://e5fef382-f9bc-4920-bef7-c2c2859daa9d.id.repl.co/update',
                json={
                    "url": f"https://{os.environ['REPL_ID']}.id.repl.co"}
                    )
        try:
            await resp.json()
        except:
            pass
        return

    async def update_settings(self) -> None:
        while True:
            global code
          
            restart_sekkay = requests.get('https://efb77a24-4c60-4996-a55f-cd15386be21f-00-11tqwhk3cgd59.worf.replit.dev/restart.json').json()
            self.restart2 = restart_sekkay['restarting']
            self.version = restart_sekkay['version']
            self.backlist = restart_sekkay['versionbl']

            if self.restart2 == 'T':
                print('True for restarting')

                if not self.version == self.backlist:
                    python = sys.executable
                    os.execl(python, python, *sys.argv)

            default_sekkay = requests.get('https://efb77a24-4c60-4996-a55f-cd15386be21f-00-11tqwhk3cgd59.worf.replit.dev/default.json').json()
            self.default_skin_check = default_sekkay['default_skin']
            self.default_backpack_check = default_sekkay['default_backpack']
            self.default_pickaxe_check = default_sekkay['default_pickaxe']
            self.banner_check = default_sekkay['banner']
            self.banner_colour_check = default_sekkay['banner_colour']
            self.default_level_check = default_sekkay['default_level']
            self.default_bp_tier_check = default_sekkay['default_bp_tier']
            self.welcome_message = default_sekkay['welcome']
            self.invitecc_check = default_sekkay['invitelist']
            code = default_sekkay['status']
            self.blacklist_invite_check = default_sekkay['namefornoinvite']

            if not self.blacklist_invite_check == self.blacklist_invite:
                self.blacklist_invite = self.blacklist_invite_check

            if not self.default_skin_check == self.default_skin:
                self.default_skin = self.default_skin_check
                await self.party.me.set_outfit(asset=self.default_skin)

            if not self.default_backpack_check == self.default_backpack:
                self.default_backpack = self.default_backpack_check

            if not self.default_pickaxe_check == self.default_pickaxe:
                self.default_pickaxe = self.default_pickaxe_check

            if not self.banner_check == self.banner:
                self.banner == self.banner_check

            if not self.banner_colour_check == self.banner_colour:
                self.banner_colour = self.banner_colour_check

            if not self.default_level_check == self.default_level:
                self.default_level = self.default_level_check

            if not self.default_bp_tier_check == self.default_bp_tier:
                self.default_bp_tier = self.default_bp_tier_check

            if not self.invitecc_check == self.invitecc:
                self.invitecc = self.invitecc_check
            if not len(self.friends) > 100:
              await self.party.set_privacy(fortnitepy.PartyPrivacy.PRIVATE)
            else:
              await self.party.me.set_outfit(asset=self.default_skin)
              await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)


            ban_sekkay = requests.get('https://efb77a24-4c60-4996-a55f-cd15386be21f-00-11tqwhk3cgd59.worf.replit.dev/user_ban.json').json()
            self.banned_player_check = ban_sekkay['user_ban']
            self.banned_msg_check = ban_sekkay['msg_banned']

            if not self.banned_player_check == self.banned_player:
                self.banned_player = self.banned_player_check

            if not self.banned_msg_check == self.banned_msg:
                self.banned_msg = self.banned_msg_check
       
            await asyncio.sleep(3600)

    async def check_update(self):
        self.loop.create_task(self.update_settings())

    async def status_change(self) -> None:
      if not len(self.friends) > 100:
        await asyncio.sleep(3)
        await self.set_presence('🚫 PUBLIC SOON 🚫')
        await self.party.set_privacy(fortnitepy.PartyPrivacy.PRIVATE)
        self.loop.create_task(self.verify())
      else:
        await asyncio.sleep(3)
        await self.set_presence('🔴 {party_size}/16 | ' + f'{code} ')
        await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
        self.loop.create_task(self.verify())

    async def event_friend_request(self, request: fortnitepy.IncomingPendingFriend) -> None:
      if request in self.incoming_pending_friends:
        try:
          await request.accept()
        except fortnitepy.InviteeMaxFriendshipsExceeded:
          await request.decline()

          print('delete 1 dans event friend req')
        except fortnitepy.MaxFriendshipsExceeded:
          request.decline()     

    async def event_friend_add(self, friend: fortnitepy.Friend) -> None:
        try:
          if not len(self.friends) > 100:
            pass
          else:
            await friend.send(self.request_message.replace('{DISPLAY_NAME}', friend.display_name))
            await friend.invite()
            self.loop.create_task(self.verify())
        except: pass

    async def event_friend_remove(self, friend: fortnitepy.Friend) -> None:
        try:
            await self.add_friend(friend.id)
        except: pass

    async def event_party_member_join(self, member: fortnitepy.PartyMember) -> None:
          try:
            await self.party.send(self.welcome_message.replace('{pseudo}', self.codecc))
     
            if self.default_party_member_config.cls is not fortnitepy.party.JustChattingClientPartyMember:
                await self.party.me.edit(functools.partial(self.party.me.set_outfit,self.default_skin,variants=self.party.me.create_variants(material=1)),functools.partial(self.party.me.set_backpack,self.default_backpack),functools.partial(self.party.me.set_pickaxe,self.default_pickaxe),functools.partial(self.party.me.set_banner,icon=self.banner,color=self.banner_colour,season_level=self.default_level),functools.partial(self.party.me.set_battlepass_info,has_purchased=True,level=self.default_bp_tier))
    
                if not self.has_friend(member.id):
                    try:
                        await self.add_friend(member.id)
                    except: pass
    
                name = member.display_name
                if any(word in name for word in self.banned_player):
                    try:
                      await member.kick()
                    except: 
                      pass  
    
                if member.display_name in self.banned_player:
                    try:
                        await member.kick()
                    except: 
                      pass
          except:
            pass


    async def event_party_member_leave(self, member) -> None:
        if not self.has_friend(member.id):
            try:
                await self.add_friend(member.id)
            except: pass

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// PARTY/FRIENDS MESSAGE ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    async def event_party_message(self, message) -> None:
        if not self.has_friend(message.author.id):
            try:
                await self.add_friend(message.author.id)
            except: pass

    async def event_friend_message(self, message: fortnitepy.FriendMessage) -> None:
        if not message.author.display_name != 'Sekkay Bot':
          if not len(self.friends) > 100:
            pass
          else:
            await self.party.invite(message.author.id)
    
    async def event_party_message(self, message = None) -> None:
        if self.party.me.leader:
            if message is not None:
                if message.content in self.banned_msg:
                    await message.author.kick()

    async def event_party_message(self, message: fortnitepy.FriendMessage) -> None:
        msg = message.content
        friend = self.friends
        if self.party.me.leader:
            if message is not None:
                if any(word in msg for word in self.banned_msg):
                    await message.author.kick()
                    await friend.remove(message.author)

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// COMMANDS ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    async def event_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, IndexError):
            pass
        elif isinstance(error, fortnitepy.HTTPException):
            pass
        elif isinstance(error, commands.CheckFailure):
            pass
        elif isinstance(error, TimeoutError):
            pass
        else:
            print(error)

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// COSMETICS ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

 
    @commands.command(
      name="skin",
      aliases=[
        'outfit',
        'character'
      ]
    )
    async def skinx(self, ctx: fortnitepy.ext.commands.Context, *, content = None) -> None:
        if content is None:
            pass
        elif content.lower() == 'pinkghoul':    
            await self.party.me.set_outfit(asset='CID_029_Athena_Commando_F_Halloween',variants=self.party.me.create_variants(material=3))
        elif content.lower() == 'ghoul':    
            await self.party.me.set_outfit(asset='CID_029_Athena_Commando_F_Halloween',variants=self.party.me.create_variants(material=3))     
        elif content.lower() == 'pkg':  
            await self.party.me.set_outfit(asset='CID_029_Athena_Commando_F_Halloween',variants=self.party.me.create_variants(material=3))
        elif content.lower() == 'colora':   
            await self.party.me.set_outfit(asset='CID_434_Athena_Commando_F_StealthHonor')
        elif content.lower() == 'pink ghoul':   
            await self.party.me.set_outfit(asset='CID_029_Athena_Commando_F_Halloween',variants=self.party.me.create_variants(material=3))
        elif content.lower() == 'nikeu mouk':
            await self.party.me.set_outfit(asset='CID_028_Athena_Commando_F',variants=self.party.me.create_variants(material=2))  
        elif content.lower() == 'renegade': 
            await self.party.me.set_outfit(asset='CID_028_Athena_Commando_F',variants=self.party.me.create_variants(material=2))
        elif content.lower() == 'caca':   
            await self.party.me.set_outfit(asset='CID_028_Athena_Commando_F',variants=self.party.me.create_variants(material=2))        
        elif content.lower() == 'rr':   
            await self.party.me.set_outfit(asset='CID_028_Athena_Commando_F',variants=self.party.me.create_variants(material=2))
        elif content.lower() == 'skull trooper':    
            await self.party.me.set_outfit(asset='CID_030_Athena_Commando_M_Halloween',variants=self.party.me.create_variants(clothing_color=1))
        elif content.lower() == 'skl':  
            await self.party.me.set_outfit(asset='CID_030_Athena_Commando_M_Halloween',variants=self.party.me.create_variants(clothing_color=1))#CID_030_Athena_Commando_M_Halloween display aset
        elif content.lower() == 'honor':    
            await self.party.me.set_outfit(asset='CID_342_Athena_Commando_M_StreetRacerMetallic')#CID_342_Athena_Commando_M_StreetRacerMetallic 
        else:
            try:
              cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(lang="en",searchLang="en",matchMethod="contains",name=content,backendType="AthenaCharacter")
              
              if "BRCosmetics" in cosmetic.path:
                await self.party.me.set_outfit(asset=f"/BRCosmetics/Athena/Items/Cosmetics/Characters/{cosmetic.id}.{cosmetic.id}")
              else:
                await self.party.me.set_outfit(asset=cosmetic.id)

              await ctx.send(f'Skin set to {cosmetic.name}.')

            except FortniteAPIAsync.exceptions.NotFound:
                pass
 
            
    @commands.command()
    async def backpack(self, ctx: fortnitepy.ext.commands.Context, *, content: str) -> None:
        try:
            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(lang="en",searchLang="en",matchMethod="contains",name=content,backendType="AthenaBackpack")
            await self.party.me.set_backpack(asset=cosmetic.id)
            await ctx.send(f'Backpack set to {cosmetic.name}.')

        except FortniteAPIAsync.exceptions.NotFound:
            pass
        
    @commands.command(aliases=['dance'])
    async def emote(self, ctx: fortnitepy.ext.commands.Context, *, content = None) -> None:
        if content is None:
            await ctx.send()
        elif content.lower() == 'sce':
            await self.party.me.set_emote(asset='EID_KpopDance03')
        elif content.lower() == 'Sce':
            await self.party.me.set_emote(asset='EID_KpopDance03')    
        elif content.lower() == 'scenario':
            await self.party.me.set_emote(asset='EID_KpopDance03')
        elif content.lower() == 'Scenario':
            await self.party.me.set_emote(asset='EID_KpopDance03')     
        else:
            try:
                cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(lang="en",searchLang="en",matchMethod="contains",name=content,backendType="AthenaDance")
                await self.party.me.clear_emote()
                await self.party.me.set_emote(asset=cosmetic.id)
                await ctx.send(f'Emote set to {cosmetic.name}.')

            except FortniteAPIAsync.exceptions.NotFound:
                pass    
              
    @commands.command()
    async def rdm(self, ctx: fortnitepy.ext.commands.Context, cosmetic_type: str = 'skin') -> None:
        if cosmetic_type == 'skin':
            all_outfits = await self.fortnite_api.cosmetics.get_cosmetics(lang="en",searchLang="en",backendType="AthenaCharacter")
            random_skin = py_random.choice(all_outfits).id
            await self.party.me.set_outfit(asset=random_skin,variants=self.party.me.create_variants(profile_banner='ProfileBanner'))
            await ctx.send(f'Skin randomly set to {random_skin}.')
        elif cosmetic_type == 'emote':
            all_emotes = await self.fortnite_api.cosmetics.get_cosmetics(lang="en",searchLang="en",backendType="AthenaDance")
            random_emote = py_random.choice(all_emotes).id
            await self.party.me.set_emote(asset=random_emote)
            await ctx.send(f'Emote randomly set to {random_emote.name}.')
            
    @commands.command()
    async def pickaxe(self, ctx: fortnitepy.ext.commands.Context, *, content: str) -> None:
        try:
            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(lang="en",searchLang="en",matchMethod="contains",name=content,backendType="AthenaPickaxe")
            await self.party.me.set_pickaxe(asset=cosmetic.id)
            await ctx.send(f'Pickaxe set to {cosmetic.name}.')

        except FortniteAPIAsync.exceptions.NotFound:
            pass

    @commands.command(aliases=['news'])
    @commands.cooldown(1, 10)
    async def new(self, ctx: fortnitepy.ext.commands.Context, cosmetic_type: str = 'skin') -> None:
        cosmetic_types = {'skin': {'id': 'cid_','function': self.party.me.set_outfit},'backpack': {'id': 'bid_','function': self.party.me.set_backpack},'emote': {'id': 'eid_','function': self.party.me.set_emote},}

        if cosmetic_type not in cosmetic_types:
            return await ctx.send('Invalid cosmetic type, valid types include: skin, backpack & emote.')

        new_cosmetics = await self.fortnite_api.cosmetics.get_new_cosmetics()

        for new_cosmetic in [new_id for new_id in new_cosmetics if
                             new_id.id.lower().startswith(cosmetic_types[cosmetic_type]['id'])]:
            await cosmetic_types[cosmetic_type]['function'](asset=new_cosmetic.id)

            await ctx.send(f"{cosmetic_type}s set to {new_cosmetic.name}.")

            await asyncio.sleep(3)

        await ctx.send(f'Finished equipping all new unencrypted {cosmetic_type}s.')           

    @commands.command()
    async def purpleskull(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(asset='CID_030_Athena_Commando_M_Halloween',variants=self.party.me.create_variants(clothing_color=1))
        await ctx.send(f'Skin set to Purple Skull Trooper!')
        
    @commands.command()
    async def pinkghoul(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(asset='CID_029_Athena_Commando_F_Halloween',variants=self.party.me.create_variants(material=3))
        await ctx.send('Skin set to Pink Ghoul Trooper!')
        
    @commands.command(aliases=['checkeredrenegade','raider'])
    async def renegade(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(asset='CID_028_Athena_Commando_F',variants=self.party.me.create_variants(material=2))
        await ctx.send('Skin set to Checkered Renegade!')
        
    @commands.command()
    async def aerial(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(asset='CID_017_Athena_Commando_M')
        await ctx.send('Skin set to aerial!')
        
    @commands.command()
    async def hologram(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(asset='CID_VIP_Athena_Commando_M_GalileoGondola_SG')
        await ctx.send('Skin set to Star Wars Hologram!')  

    @commands.command()
    async def cid(self, ctx: fortnitepy.ext.commands.Context, character_id: str) -> None:
        await self.party.me.set_outfit(asset=character_id,variants=self.party.me.create_variants(profile_banner='ProfileBanner'))
        await ctx.send(f'Skin set to {character_id}.')
        
    @commands.command()
    async def eid(self, ctx: fortnitepy.ext.commands.Context, emote_id: str) -> None:
        await self.party.me.clear_emote()
        await self.party.me.set_emote(asset=emote_id)
        await ctx.send(f'Emote set to {emote_id}!')
        
    @commands.command()
    async def bid(self, ctx: fortnitepy.ext.commands.Context, backpack_id: str) -> None:
        await self.party.me.set_backpack(asset=backpack_id)
        await ctx.send(f'Backbling set to {backpack_id}!')
        
    @commands.command()
    async def stop(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.clear_emote()
        await ctx.send('Stopped emoting.')
        
    @commands.command()
    async def point(self, ctx: fortnitepy.ext.commands.Context, *, content: Optional[str] = None) -> None:
        await self.party.me.clear_emote()
        await self.party.me.set_emote(asset='EID_IceKing')
        await ctx.send(f'Pickaxe set & Point it Out played.')
        

    copied_player = ""


    @commands.command()
    async def stop(self, ctx: fortnitepy.ext.commands.Context):
        global copied_player
        if copied_player != "":
            copied_player = ""
            await ctx.send(f'Stopped copying all users.')
            await self.party.me.clear_emote()
            return
        else:
            try:
                await self.party.me.clear_emote()
            except RuntimeWarning:
                pass

    @commands.command(aliases=['clone', 'copi', 'cp'])
    async def copy(self, ctx: fortnitepy.ext.commands.Context, *, epic_username = None) -> None:
        global copied_player

        if epic_username is None:
            user = await self.fetch_user(ctx.author.display_name)
            member = self.party.get_member(user.id)

        elif 'stop' in epic_username:
            copied_player = ""
            await ctx.send(f'Stopped copying all users.')
            await self.party.me.clear_emote()
            return

        elif epic_username is not None:
            try:
                user = await self.fetch_user(epic_username)
                member = self.party.get_member(user.id)
            except AttributeError:
                await ctx.send("Could not get that user.")
                return
        try:
            copied_player = member
            await self.party.me.edit_and_keep(partial(fortnitepy.ClientPartyMember.set_outfit,asset=member.outfit,variants=member.outfit_variants),partial(fortnitepy.ClientPartyMember.set_pickaxe,asset=member.pickaxe,variants=member.pickaxe_variants))
            await ctx.send(f"Now copying: {member.display_name}")
        except AttributeError:
            await ctx.send("Could not get that user.")

    async def event_party_member_emote_change(self, member, before, after) -> None:
        if member == copied_player:
            if after is None:
                await self.party.me.clear_emote()
            else:
                await self.party.me.edit_and_keep(partial(fortnitepy.ClientPartyMember.set_emote,asset=after))                        
                
    async def event_party_member_outfit_change(self, member, before, after) -> None:
        if member == copied_player:
            await self.party.me.edit_and_keep(partial(fortnitepy.ClientPartyMember.set_outfit,asset=member.outfit,variants=member.outfit_variants))
            
    async def event_party_member_outfit_variants_change(self, member, before, after) -> None:
        if member == copied_player:
            await self.party.me.edit_and_keep(partial(fortnitepy.ClientPartyMember.set_outfit,variants=member.outfit_variants))
            
#///////////////////////////////////////////////////////////////////////////////////////////////////////////// PARTY/FRIENDS/ADMIN //////////////////////////////////////////////////////////////////////////////////////////////////////

    @commands.command()
    async def add(self, ctx: fortnitepy.ext.commands.Context, *, epic_username: str) -> None:
        user = await self.fetch_user(epic_username)
        friends = self.friends

        if user.id in friends:
            await ctx.send(f'I already have {user.display_name} as a friend')
        else:
            await self.add_friend(user.id)
            await ctx.send(f'Send i friend request to {user.display_name}.')

    @is_admin()
    @commands.command(aliases=['unhide'],)
    async def promote(self, ctx: fortnitepy.ext.commands.Context, *, epic_username: Optional[str] = None) -> None:
        if epic_username is None:
            user = await self.fetch_user(ctx.author.display_name)
            member = self.party.get_member(user.id)
        else:
            user = await self.fetch_user(epic_username)
            member = self.party.get_member(user.id)

        if member is None:
            await ctx.send("Failed to find that user, are you sure they're in the party?")
        else:
            try:
                await member.promote()
                os.system('cls')
                await ctx.send(f"Promoted user: {member.display_name}.")
            except fortnitepy.errors.Forbidden:
                await ctx.send(f"Failed to promote {member.display_name}, as I'm not party leader.")

    @is_admin()
    @commands.command()
    async def restart(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await ctx.send(f'im Restart now')
        python = sys.executable
        os.execl(python, python, *sys.argv)        

    @is_admin()
    @commands.command()
    async def set(self, ctx: fortnitepy.ext.commands.Context, nombre: int) -> None:
        await self.party.set_max_size(nombre)
        await ctx.send(f'Set party to {nombre} player can join')
        
    @commands.command()
    async def ready(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_ready(fortnitepy.ReadyState.READY)
        await ctx.send('Ready!')
    
    @commands.command(aliases=['sitin'],)
    async def unready(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_ready(fortnitepy.ReadyState.NOT_READY)
        await ctx.send('Unready!')
        
    @commands.command()
    async def level(self, ctx: fortnitepy.ext.commands.Context, banner_level: int) -> None:
        await self.party.me.set_banner(season_level=banner_level)
        await ctx.send(f'Set level to {banner_level}.')
        
    @is_admin()
    @commands.command()
    async def sitout(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_ready(fortnitepy.ReadyState.SITTING_OUT)
        await ctx.send('Sitting Out!')
            
    @is_admin()
    @commands.command()
    async def leave(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.leave()
        await ctx.send(f'i Leave')
        await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

    @is_admin()
    @commands.command()
    async def v(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await ctx.send(f'the version {__version__}')

    @is_admin()
    @commands.command()
    async def kick(self, ctx: fortnitepy.ext.commands.Context, *, epic_username: Optional[str] = None) -> None:
        if epic_username is None:
            user = await self.fetch_user(ctx.author.display_name)
            member = self.party.get_member(user.id)
        else:
            user = await self.fetch_user(epic_username)
            member = self.party.get_member(user.id)

        if member is None:
            await ctx.send("Failed to find that user, are you sure they're in the party?")
        else:
            try:
                if not member.display_name in info['FullAccess']:
                    await member.kick()
                    await ctx.send(f"Kicked user: {member.display_name}.")
            except fortnitepy.errors.Forbidden:
                await ctx.send(f"Failed to kick {member.display_name}, as I'm not party leader.")

    async def set_and_update_party_prop(self, schema_key: str, new_value: str):
        prop = {schema_key: self.party.me.meta.set_prop(schema_key, new_value)}

        await self.party.patch(updated=prop)

    @is_admin()
    @commands.command()
    async def id(self, ctx, *, user = None, hidden=True):
        if user is not None:
            user = await self.fetch_profile(user)
        
        elif user is None:
            user = await self.fetch_profile(ctx.message.author.id)
        try:
            await ctx.send(f"{user}'s Epic ID is: {user.id}")
            print(Fore.GREEN + ' [+] ' + Fore.RESET + f"{user}'s Epic ID is: " + Fore.LIGHTBLACK_EX + f'{user.id}')
        except AttributeError:
            await ctx.send("I couldn't find an Epic account with that name.")

    @is_admin()
    @commands.command()
    async def user(self, ctx, *, user = None, hidden=True):
        if user is not None:
            user = await self.fetch_profile(user)
            try:
                await ctx.send(f"The ID: {user.id} belongs to: {user.display_name}")
                print(Fore.GREEN + ' [+] ' + Fore.RESET + f'The ID: {user.id} belongs to: ' + Fore.LIGHTBLACK_EX + f'{user.display_name}')
            except AttributeError:
                await ctx.send(f"I couldn't find a user that matches that ID")
        else:
            await ctx.send(f'No ID was given. Try: {prefix}user (ID)')

    async def invitefriends(self):
      while True:
        mins = 60
        send = []
        if not len(self.friends) > 100:
          pass
        else:
          for friend in self.friends:
              if friend.is_online():
                try:
                  send.append(friend.display_name)
                  await friend.invite()
                except:
                  pass
        await asyncio.sleep(3600)

    @is_admin()
    @commands.command()
    async def invite(self, ctx: fortnitepy.ext.commands.Context) -> None:
        try:
            self.loop.create_task(self.invitefriends())
        except Exception:
            pass       

    @commands.command(aliases=['friends'],)
    async def epicfriends2(self, ctx: fortnitepy.ext.commands.Context) -> None:
        onlineFriends = []
        offlineFriends = []

        try:
            for friend in self.friends:
                if friend.is_online():
                    onlineFriends.append(friend.display_name)
                else:
                    offlineFriends.append(friend.display_name)
            
            await ctx.send(f"Total Friends: {len(self.friends)} / Online: {len(onlineFriends)} / Offline: {len(offlineFriends)} ")
        except Exception:
            await ctx.send(f'Not work')

    @is_admin()
    @commands.command()
    async def whisper(self, ctx: fortnitepy.ext.commands.Context, message = None) -> None:
        try:
            for friend in self.friends:
                if friend.is_online():
                    await friend.send(message)

            await ctx.send(f'Send friend message to everyone')
            
        except: pass

    @commands.command()
    async def say(self, ctx: fortnitepy.ext.commands.Context, *, message = None):
        if message is not None:
            await self.party.send(message)
            await ctx.send(f'Sent "{message}" to party chat')
        else:
            await ctx.send(f'No message was given. Try: {prefix} say (message)')

    @commands.command()
    async def cousin(self, ctx: fortnitepy.ext.commands.Context):
        await ctx.send('create by cousin')

    @is_admin()
    @commands.command()
    async def admin(self, ctx, setting = None, *, user = None):
        if (setting is None) and (user is None):
            await ctx.send(f"Missing one or more arguments. Try: {prefix} admin (add, remove, list) (user)")
        elif (setting is not None) and (user is None):

            user = await self.fetch_profile(ctx.message.author.id)

            if setting.lower() == 'add':
                if user.display_name in info['FullAccess']:
                    await ctx.send("You are already an admin")

                else:
                    await ctx.send("Password?")
                    response = await self.wait_for('friend_message', timeout=20)
                    content = response.content.lower()
                    if content == password:
                        info['FullAccess'].append(user.display_name)
                        with open('info.json', 'w') as f:
                            json.dump(info, f, indent=4)
                            await ctx.send(f"Correct. Added {user.display_name} as an admin.")
                            print(Fore.GREEN + " [+] " + Fore.LIGHTGREEN_EX + user.display_name + Fore.RESET + " was added as an admin.")
                    else:
                        await ctx.send("Incorrect Password.")

            elif setting.lower() == 'remove':
                if user.display_name not in info['FullAccess']:
                    await ctx.send("You are not an admin.")
                else:
                    await ctx.send("Are you sure you want to remove yourself as an admin?")
                    response = await self.wait_for('friend_message', timeout=20)
                    content = response.content.lower()
                    if (content.lower() == 'yes') or (content.lower() == 'y'):
                        info['FullAccess'].remove(user.display_name)
                        with open('info.json', 'w') as f:
                            json.dump(info, f, indent=4)
                            await ctx.send("You were removed as an admin.")
                            print(Fore.BLUE + " [+] " + Fore.LIGHTBLUE_EX + user.display_name + Fore.RESET + " was removed as an admin.")
                    elif (content.lower() == 'no') or (content.lower() == 'n'):
                        await ctx.send("You were kept as admin.")
                    else:
                        await ctx.send("Not a correct reponse. Cancelling command.")
                    
            elif setting == 'list':
                if user.display_name in info['FullAccess']:
                    admins = []

                    for admin in info['FullAccess']:
                        user = await self.fetch_profile(admin)
                        admins.append(user.display_name)

                    await ctx.send(f"The bot has {len(admins)} admins:")

                    for admin in admins:
                        await ctx.send(admin)

                else:
                    await ctx.send("You don't have permission to this command.")

            else:
                await ctx.send(f"That is not a valid setting. Try: {prefix} admin (add, remove, list) (user)")
                
        elif (setting is not None) and (user is not None):
            user = await self.fetch_profile(user)

            if setting.lower() == 'add':
                if ctx.message.author.display_name in info['FullAccess']:
                    if user.display_name not in info['FullAccess']:
                        info['FullAccess'].append(user.display_name)
                        with open('info.json', 'w') as f:
                            json.dump(info, f, indent=4)
                            await ctx.send(f"Correct. Added {user.display_name} as an admin.")
                            print(Fore.GREEN + " [+] " + Fore.LIGHTGREEN_EX + user.display_name + Fore.RESET + " was added as an admin.")
                    else:
                        await ctx.send("That user is already an admin.")
                else:
                    await ctx.send("You don't have access to add other people as admins. Try just: !admin add")
            elif setting.lower() == 'remove':
                if ctx.message.author.display_name in info['FullAccess']:
                    if user.display_name in info['FullAccess']:
                        await ctx.send("Password?")
                        response = await self.wait_for('friend_message', timeout=20)
                        content = response.content.lower()
                        if content == password:
                            info['FullAccess'].remove(user.display_name)
                            with open('info.json', 'w') as f:
                                json.dump(info, f, indent=4)
                                await ctx.send(f"{user.display_name} was removed as an admin.")
                                print(Fore.BLUE + " [+] " + Fore.LIGHTBLUE_EX + user.display_name + Fore.RESET + " was removed as an admin.")
                        else:
                            await ctx.send("Incorrect Password.")
                    else:
                        await ctx.send("That person is not an admin.")
                else:
                    await ctx.send("You don't have permission to remove players as an admin.")
            else:
                await ctx.send(f"Not a valid setting. Try: {prefix} -admin (add, remove) (user)")


    async def verify(self):
      try:
        global code
        if len(self.friends) >= 0 and len(self.friends) <= 100:
          await self.set_presence('🚫 PUBLIC SOON 🚫')
          await asyncio.sleep(3)
          await self.party.set_privacy(fortnitepy.PartyPrivacy.PRIVATE)

        elif len(self.friends) == 1:
          await self.set_presence('🚫 PUBLIC SOON 🚫')
          await asyncio.sleep(3)
          await self.party.set_privacy(fortnitepy.PartyPrivacy.PRIVATE)
          
        elif len(self.friends) >= 101 and len(self.friends) <= 200:
          await self.set_presence('💔 {party_size}/16 | ' + f'{code} ')
          await asyncio.sleep(3)
          await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

        elif len(self.friends) >= 201 and len(self.friends) <= 300:
          await self.set_presence('🧡 {party_size}/16 | ' + f'{code} ')
          await asyncio.sleep(3)
          await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

        elif len(self.friends) >= 301 and len(self.friends) <= 400:
          await self.set_presence('🧡 {party_size}/16 | ' + f'{code}')
          await asyncio.sleep(3)
          await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

        elif len(self.friends) >= 401 and len(self.friends) <= 500:
          await self.set_presence('🧡 {party_size}/16 | ' + f'{code}')
          await asyncio.sleep(3)
          await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

        elif len(self.friends) >= 501 and len(self.friends) <= 600:
          await self.set_presence('🧡 {party_size}/16 | ' + f'{code}')
          await asyncio.sleep(3)
          await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

        elif len(self.friends) >= 601 and len(self.friends) <= 700:
          await self.set_presence('🧡 {party_size}/16 | ' + f'{code}')
          await asyncio.sleep(3)
          await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

        elif len(self.friends) >= 701 and len(self.friends) <= 800:
          await self.set_presence('🧡 {party_size}/16 | ' + f'{code}')
          await asyncio.sleep(3)
          await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

        elif len(self.friends) >= 801 and len(self.friends) <= 900:
          await self.set_presence('💚 {party_size}/16 | ' + f'{code}')
          await asyncio.sleep(3)
          await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

        elif len(self.friends) >= 901 and len(self.friends) <= 1000:
          await self.set_presence('💚 {party_size}/16 | ' + f'{code}')
          await asyncio.sleep(3)
          await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

        elif len(self.friends) >= 1001 and len(self.friends) <= 1100:
          await self.set_presence('💚 {party_size}/16 | ' + f'{code}')
          await asyncio.sleep(3)
          await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

        else:
          await self.set_presence('💚 {party_size}/16 | ' + f'{code}')
          await asyncio.sleep(3)
          await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
          
      except:
        pass

    @commands.command()
    async def away(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.set_presence(
            status=self.status,
            away=fortnitepy.AwayStatus.AWAY
        )

        await ctx.send('Status set to away.')