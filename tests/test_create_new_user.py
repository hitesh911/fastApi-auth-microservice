from preprocessor import loadProject

loadProject()

from app.api.endpoints.auth.user import create_new_user


print(create_new_user("787647171"))