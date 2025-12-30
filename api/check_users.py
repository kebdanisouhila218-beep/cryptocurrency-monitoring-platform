from pymongo import MongoClient

client = MongoClient('mongodb://127.0.0.1:27017/')
db = client['crypto_db']

users = list(db.users.find({'is_active': True}, {'username': 1, 'email': 1}))
print('Utilisateurs actifs:')
for user in users:
    print(f'  - {user["username"]}: {user.get("email", "NO EMAIL")}')
print(f'Total: {len(users)} utilisateurs')
