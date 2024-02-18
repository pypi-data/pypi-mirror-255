import httpx


class Zeus():
    def __init__(self):
        self.api_key = None


    async def login(self, appId):
        '''
        Athenticate the current objet with the API Key
        In : API key
        Out : None
        '''
        url = "https://zeus.ionis-it.com/api/Application/Login"
        headers = {
            'accept': 'text/plain',
            'Content-Type': 'application/json'
        }

        data = {"appId": appId}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)

            if response.status_code == 200:
                self.api_key = response
            elif response.status_code == 400:
                raise Exception("Error 400 : Bad request")
            elif response.status_code == 403:
                raise Exception("Error 403 : Access to API is forbidden")
            elif response.status_code == 500:
                raise Exception("Error 500 : Internal server error")
            
 
    async def get_course_by_id(self, id):
        '''
        Get a specific course in Zeus database with it's specific id
        In : id
        Out : Course
        '''
        url = f"https://zeus.ionis-it.com/api/Course/{id}"
        headers = {
            'accept': 'text/plain',
            'Authorization': f'Bearer {self.api_key}'
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                raise Exception("Error 400 : Bad request")
            elif response.status_code == 403:
                try:
                    await self.login(self.api_key)
                    await self.get_course_by_id(id)
                except Exception as e:
                    raise Exception("Error 403 : Access to API is forbidden")
            elif response.status_code == 500:
                raise Exception("Error 500 : Internal server error")

    async def get_course_by_teacher(self, id):
        '''
        Get course in Zeus database with specific teacher
        In : id of the teacher
        Out : Course
        '''
        url = f"https://zeus.ionis-it.com/api/Course/Teacher/{id}"
        headers = {
            'accept': 'text/plain',
            'Authorization': f'Bearer {self.api_key}'
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                raise Exception("Error 400 : Bad request")
            elif response.status_code == 403:
                try:
                    await self.login(self.api_key)
                    await self.get_course_by_teacher(id)
                except Exception as e:
                    raise Exception("Error 403 : Access to API is forbidden")
            elif response.status_code == 500:
                raise Exception("Error 500 : Internal server error")
            
    async def get_groups(self):
        '''
        Get all groups
        In : None
        Out : List of groups
        '''
        url = "https://zeus.ionis-it.com/api/group"
        headers = {
            'accept': 'text/plain',
            'Authorization': f'Bearer {self.api_key}'
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                raise Exception("Error 400 : Bad request")
            elif response.status_code == 403:
                try:
                    await self.login(self.api_key)
                    await self.get_groups()
                except Exception as e:
                    raise Exception("Error 403 : Access to API is forbidden")
            elif response.status_code == 500:
                raise Exception("Error 500 : Internal server error")
            
    async def get_course_by_group(self, groupId, StartDate, EndDate):
        '''
        Get a course by its group
        In : id of the group, StartDate, EndDate
        Out : Course
        '''
        url = f"https://zeus.ionis-it.com/api/reservation/filter/displayable?Groups={groupId}&StartDate={StartDate}&EndDate={EndDate}"
        headers = {
            'accept': 'text/plain',
            'Authorization': f'Bearer {self.api_key}'
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                raise Exception("Error 400 : Bad request")
            elif response.status_code == 403:
                try:
                    await self.login(self.api_key)
                    await self.get_course_by_group(groupId, StartDate, EndDate)
                except Exception as e:
                    raise Exception("Error 403 : Access to API is forbidden")
            elif response.status_code == 500:
                raise Exception("Error 500 : Internal server error")

    async def get_group_by_id(self, id):
        '''
        Get a specific group in Zeus database with it's specific id
        In : id of the group
        Out : group
        '''
        url = f"https://zeus.ionis-it.com/api/group/{id}"
        headers = {
            'accept': 'text/plain',
            'Authorization': f'Bearer {self.api_key}'
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                raise Exception("Error 400 : Bad request")
            elif response.status_code == 403:
                try:
                    await self.login(self.api_key)
                    await self.get_group_by_id(id)
                except Exception as e:
                    raise Exception("Error 403 : Access to API is forbidden")
            elif response.status_code == 500:
                raise Exception("Error 500 : Internal server error")
            
    async def get_course_by_location(self, roomId, StartDate, EndDate):
        '''
        Get a course by its group
        In : id of the group, StartDate, EndDate
        Out : Course
        '''
        url = f"https://zeus.ionis-it.com/api/reservation/filter/displayable?Rooms={roomId}&StartDate={StartDate}&EndDate={EndDate}"
        headers = {
            'accept': 'text/plain',
            'Authorization': f'Bearer {self.api_key}'
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                raise Exception("Error 400 : Bad request")
            elif response.status_code == 403:
                try:
                    await self.login(self.api_key)
                    await self.get_course_by_group(roomId, StartDate, EndDate)
                except Exception as e:
                    raise Exception("Error 403 : Access to API is forbidden")
            elif response.status_code == 500:
                raise Exception("Error 500 : Internal server error")