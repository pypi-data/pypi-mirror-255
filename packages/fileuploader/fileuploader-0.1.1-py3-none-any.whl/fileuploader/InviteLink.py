import aiohttp as aiohttp
import fileuploader.exceptions as exceptions
import fileuploader.group as Group

class User:
    def __init__(self):
        self.accessToken = None
        self.username = None


class InviteLink:
    def __init__(self, link: str):
        self.link: str = link.split("/")[-1]
        self.link_full = link

    def __str__(self):
        return f"<InviteLink link:{self.link}>"
    
    async def join(self, user: User) -> Group.Group:
        """Join to the group by invite link"""
        if not user.accessToken:
            raise exceptions.NotAuthorized("The user has not been initialized")
        
        async with aiohttp.ClientSession("https://fu.andcool.ru") as session:
            async with session.post(f"/api/join/{self.link}", 
                                    headers={"Authorization": "Bearer " + user.accessToken}) as response:
                if response.status == 200:
                    response_json = await response.json()
                    group = Group.Group()
                    group.group_id = response_json['group_id']
                    group.group_name = response_json['name']
                    return group

                errors = {
                    400: exceptions.AlreadyInGroup,
                    404: exceptions.InvalidLink
                }
                raise errors.get(response.status, exceptions.UnhandledError(response.status))
            
    async def info(self, user: User) -> Group.Group:
        """Get info about group by link"""
        if not user.accessToken:
            raise exceptions.NotAuthorized("The user has not been initialized")
        
        async with aiohttp.ClientSession("https://fu.andcool.ru") as session:
            async with session.post(f"/api/invite_info/{self.link}", 
                                    headers={"Authorization": "Bearer " + user.accessToken}) as response:
                if response.status == 200:
                    response_json = await response.json()
                    group = Group.Group()
                    group.group_id = response_json['group_id']
                    group.group_name = response_json['name']
                    return group

                errors = {
                    404: exceptions.InvalidLink
                }
                raise errors.get(response.status, exceptions.UnhandledError(response.status))
