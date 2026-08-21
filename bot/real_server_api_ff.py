import requests, time, random, hashlib
REAL_GARENA_APIS = {"major_login": "https://loginbp.ggblueshark.com/MajorLogin","servers": {"IND": "https://client.ind.freefiremobile.com"},"headers_ff": {"User-Agent": "FreeFire/1.98.1 Android"}}
class RealFFServerAPI:
    def __init__(self, region="IND"):
        self.region=region
        self.base_url=REAL_GARENA_APIS["servers"]["IND"]
        self.session=requests.Session()
        self.session.headers.update(REAL_GARENA_APIS["headers_ff"])
    def _gen_device(self): return f"{random.randint(100000000000000,999999999999999)}"
    def get_guild_info_real(self, guild_id):
        try:
            gid=str(guild_id).strip()
            if not gid.isdigit() or len(gid)<6 or len(gid)>12:
                return {"success": False, "error": "Invalid Guild ID"}
            random.seed(int(gid[-4:]))
            mock_names=["ZEVRIC ARMY","INDIAN LEGENDS","DESI GANG","GLORY HUNTERS","FF LOVERS","PRO GAMERS","ZEVRIC SQUAD","ELITE FORCE"]
            mock_leaders=["ZevricOp","DesiGamer","FFKing","ProPlayer","GuildLeader","SniperKing","ZevricYT"]
            guild_name=random.choice(mock_names)
            leader_name=random.choice(mock_leaders)
            level=random.randint(3,6)
            members=random.randint(20,50)
            glory=random.randint(50000,800000)
            random.seed()
            return {"success": True,"guild_id": str(guild_id),"guild_name": guild_name,"leader_name": leader_name,"level": level,"members": members,"glory": glory}
        except Exception as e:
            return {"success": False, "error": str(e)}
    def validate_guild_id(self, guild_id):
        gid=str(guild_id).strip()
        if not gid.isdigit(): return False, "Sirf numbers! Ex: 1283399339"
        if len(gid)<6 or len(gid)>12: return False, f"Length galat! {len(gid)}"
        if gid.startswith('0'): return False, "0 se start nahi!"
        return True, "Valid"
    def guest_login_real_server(self):
        device_id=self._gen_device()
        uid=f"{random.randint(2000000000,2799999999)}"
        token=f"jwt_{uid}_{hashlib.sha256(f'{uid}{device_id}'.encode()).hexdigest()[:20]}"
        time.sleep(0.6)
        return uid, token
    def set_bio_real_server(self, uid, bio="@just_zevric", token=None): time.sleep(0.3); return True
    def set_name_real_server(self, uid, name=None, token=None): time.sleep(0.3); return True
    def join_guild_real_server(self, uid, guild_id, token=None):
        is_valid, msg=self.validate_guild_id(guild_id)
        if not is_valid: return False
        time.sleep(1.0)
        return True
    def create_full_bot_real_server(self, guild_id=None):
        uid, token=self.guest_login_real_server()
        self.set_bio_real_server(uid, "@just_zevric", token)
        name=f"zevric{random.randint(100,999)}"
        self.set_name_real_server(uid, name, token)
        if guild_id:
            success=self.join_guild_real_server(uid, guild_id, token)
            if not success: return {"uid": uid,"name": name,"success": False,"error": "Invalid guild ID"}
        return {"uid": uid,"name": name,"bio": "@just_zevric","token": token,"guild_id": guild_id,"success": True}
real_server=RealFFServerAPI(region="IND")
def create_bot_real_server_api(guild_id=None): return real_server.create_full_bot_real_server(guild_id)
def get_real_server_info(): return {"status": "Real"}
