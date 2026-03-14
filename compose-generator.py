import sys
HEADER_AND_SERVER_DEFINITION = """name: tp0
services:
  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - LOGGING_LEVEL=DEBUG
    volumes:
      - ./server/config.ini:/config.ini
    networks:
      - testing_net

  
"""

NETWORK_DEFINITION = """    
networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
"""

def get_filename(args) -> str:
    if len(args) != 2:
        print("Error: waiting 2 arguments: the filename and the number of clients\nInstead received: {}".format(args))
        sys.exit(1)
    return args[0]

def get_num_clients(args) -> int:
    try:        
        num_clients = int(args[1])
    except ValueError as e:
        print("Error: the second argument should be an integer. Error: {}".format(e))
        sys.exit(1)
    return num_clients


def get_client_definition(client_id):
    return f"""
  client{client_id}:
    container_name: client{client_id}
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID={client_id}
      - CLI_LOG_LEVEL=DEBUG
    volumes:
      - ./client/config.yaml:/config.yaml
    networks:
      - testing_net
    depends_on:
      - server
  """

def main():
  args = sys.argv[1:]
  filename = get_filename(args)
  num_clients = get_num_clients(args)
  with open(filename, "w") as file:
    file.write(HEADER_AND_SERVER_DEFINITION)
    for i in range(1, num_clients + 1):
      file.write(get_client_definition(i))
    file.write(NETWORK_DEFINITION)

if __name__ == "__main__":
    main()
