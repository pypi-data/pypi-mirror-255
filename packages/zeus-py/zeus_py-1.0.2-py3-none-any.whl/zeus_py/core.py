import httpx


class Zeus():
        def __init__(self):
            self.api_key = None


    ## Login async-function
        async def login(self, appId : str) -> None:
            '''
            Get the API key from the Zeus API with specifi appID
            In : appId (string)
            Out : None (API key is stored in self.api_key)
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
                    self.api_key = response.text  # Assign the response content to self.api_key
                elif response.status_code == 400:
                    raise Exception("Error 400 : Bad request")
                elif response.status_code == 403:
                    raise Exception("Error 403 : Access to API is forbidden")
                elif response.status_code == 500:
                    raise Exception("Error 500 : Internal server error")

# Get some data from the zeus database   
        async def get_groups(self) -> dict :
            '''
            Get all groups referenced in the Zeus database
            In : None
            Out : Groups (dict)
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
                    except Exception:
                        raise Exception("Error 403 : Access to API is forbidden")
                elif response.status_code == 500:
                    raise Exception("Error 500 : Internal server error")

# Get some data from the zeus database with specific id (teacher, group, location, course)
        async def get_course_by_id(self, id : int) -> dict:
            '''
            Get a specific course in Zeus database with it's specific id
            In : id
            Out : Course
            '''
            url = f"https://zeus.ionis-it.com/api/Course/{str(id)}"
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
                    except Exception:
                        raise Exception("Error 403 : Access to API is forbidden")
                elif response.status_code == 500:
                    raise Exception("Error 500 : Internal server error")

        async def get_course_by_teacher(self, id : int) -> dict:
            '''
            Get course in Zeus database with specific teacher
            In : id of the teacher
            Out : Course
            '''
            url = f"https://zeus.ionis-it.com/api/Course/Teacher/{str(id)}"
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
                    except Exception:
                        raise Exception("Error 403 : Access to API is forbidden")
                elif response.status_code == 500:
                    raise Exception("Error 500 : Internal server error")
                
        async def get_course_by_group(self, groupId : int, StartDate: str, EndDate : str) -> dict:
            '''
            Get a course by its group
            In : id of the group, StartDate, EndDate
            Out : Course
            '''
            url = f"https://zeus.ionis-it.com/api/reservation/filter/displayable?Groups={str(groupId)}&StartDate={StartDate}&EndDate={EndDate}"
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
                    except Exception:
                        raise Exception("Error 403 : Access to API is forbidden")
                elif response.status_code == 500:
                    raise Exception("Error 500 : Internal server error")

        async def get_group_by_id(self, id : int) -> dict:
            '''
            Get a specific group in Zeus database with it's specific id
            In : id of the group
            Out : group
            '''
            url = f"https://zeus.ionis-it.com/api/group/{str(id)}"
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
                    except Exception:
                        raise Exception("Error 403 : Access to API is forbidden")
                elif response.status_code == 500:
                    raise Exception("Error 500 : Internal server error")
                
        async def get_course_by_location(self, roomId : int, StartDate : str, EndDate : str) -> dict:
            '''
            Get a course by its group
            In : id of the group, StartDate, EndDate
            Out : Course
            '''
            url = f"https://zeus.ionis-it.com/api/reservation/filter/displayable?Rooms={str(roomId)}&StartDate={StartDate}&EndDate={EndDate}"
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
                        await self.get_course_by_location(roomId, StartDate, EndDate)
                    except Exception:
                        raise Exception("Error 403 : Access to API is forbidden")
                elif response.status_code == 500:
                    raise Exception("Error 500 : Internal server error")
                