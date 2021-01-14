from data.db_session import db_auth
from typing import Optional
from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from services.classes import User, Equipments


graph = db_auth()


def find_user(email: str):
    user = User.match(graph, f"{email}")
    return user


def create_user(name: str, email: str, company: str, password: str) -> Optional[User]:
    if find_user(email):
        return None
    user = User()
    user.name = name
    user.email = email
    user.company = company
    user.hashed_password = hash_text(password)
    graph.create(user)
    return user


def hash_text(text: str) -> str:
    hashed_text = crypto.encrypt(text, rounds=171204)
    return hashed_text


def verify_hash(hashed_text: str, plain_text: str) -> bool:
    return crypto.verify(plain_text, hashed_text)


def login_user(email: str, password: str) -> Optional[User]:
    user = User.match(graph, f"{email}").first()
    if not user:
        print(f"Invalid User - {email}")
        return None
    if not verify_hash(user.hashed_password, password):
        print(f"Invalid Password for {email}")
        return None
    print(f"User {email} passed authentication")
    return user


def get_profile(usr: str) -> Optional[User]:
    # user = User.match(graph, f"{usr}").first()
    user_profile = graph.run(f"MATCH (x:user) WHERE x.email='{usr}' RETURN x.name as name, x.company as company, x.email as email").data()
    return user_profile

def update_profile(usr: str, name: str, company: str) -> Optional[User]:
    # user = User.match(graph, f"{usr}").first()
    user_profile = graph.run(f"MATCH (x:user) WHERE x.email='{usr}' SET x.name='{name}', x.company='{company}' RETURN x.name as name, x.company as company, x.email as email").data()
    return user_profile


def find_user_equipment(usr: str):
    
    count = graph.run("MATCH (x:user {email:$usr})-[:have_e]->(:equipments) return count(*)",usr=usr)
    print(count)
    return count

def create_equipments(usr: str,eid: str ,Site: str,Longitude:float,Latitude:float,Altitude:float,tz:str,daylight:bool,wv: float,light_pollusion: float):

    query = f"MATCH (x:user) where x.email='{usr}'  MATCH (e:equipments) where e.EID={eid}" \
    "CREATE (x)-[h:have_e{ site:$Site, longitude:$Longitude, latitude:$Latitude" \
    ", altitude:$Altitude, time_zone:$tz, daylight_saving:$daylight, water_vapor:$wv,light_pollusion:$light_pollusion}]->(e) return h.site as site, h.longitude as longitude," \
    "h.latitude as latitude, h.altitude as altitude, h.time_zone as time_zone, h.daylight_saving as daylight_saving, h.water_vapor as water_vapor, h.light_pollusion as light_pollusion"
    
    user_equipments = graph.run(query,Site=Site,Longitude=Longitude,Latitude=Latitude,Altitude=Altitude,tz=tz,daylight=daylight,wv=wv,light_pollusion=light_pollusion)
    print(user_equipments)
    return user_equipments

def update_equipments()-> Optional[Equipments]:
    user_equipments = graph.run().data()
    return user_equipments

def get_equipments(usr: str)-> Optional[Equipments]:
    if  find_user_equipment(usr) == 0:
        return None
    user_equipments = graph.run("MATCH (x:user {email:$usr})-[h:have_e]->(:equipments) return h.site as site, h.longitude as longitude," \
        "h.latitude as latitude, h.altitude as altitude, h.time_zone as time_zone, h.daylight_saving as daylight_saving, h.water_vapor as water_vapor, h.light_pollusion as light_pollusion",usr=usr)
    return user_equipments