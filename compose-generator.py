#Ejercicio N°1:
# Definir un script de bash generar-compose.sh
#  que permita crear una definición de Docker Compose
#  con una cantidad configurable de clientes. El nombre
#  de los containers deberá seguir el formato propuesto: client1, client2, client3, etc.

# El script deberá ubicarse en la raíz del proyecto y
# recibirá por parámetro el nombre del archivo de salida y la cantidad de clientes esperados:

# ./generar-compose.sh docker-compose-dev.yaml 5

# Considerar que en el contenido del script pueden invocar un subscript de Go o Python:

# #!/bin/bash
# echo "Nombre del archivo de salida: $1"
# echo "Cantidad de clientes: $2"
# python3 mi-generador.py $1 $2
# En el archivo de Docker Compose de salida se pueden definir volúmenes, variables de
# entorno y redes con libertad, pero recordar actualizar este script cuando se modifiquen
# tales definiciones en los sucesivos ejercicios.

from re import I
import sys
INDENT_LEN=4
INDENT_STR=" "

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

def write_line_with_indent(file, line, indent_size=INDENT_LEN):
    file.write(INDENT_STR * indent_size + line + "\n")

def write_header_and_server_definition(file):
    header = """
name: tp0
services:
  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - LOGGING_LEVEL=DEBUG
    networks:
      - testing_net
"""
    file.write(header)

def write_network_definition(file):
    header = """    
networks:
  testing_net:
    ipam:
    driver: default
    config:
      - subnet: 172.25.125.0/24
"""
    file.write(header)

def format_client_definition(client_id):
    return f"""
  client{client_id}:
    container_name: client{client_id}
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID={client_id}
      - CLI_LOG_LEVEL=DEBUG
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
        write_header_and_server_definition(file)
        for i in range(1, num_clients + 1):
            client_definition = format_client_definition(i)
            file.write(client_definition)
        write_network_definition(file)
    

if __name__ == "__main__":
    main()
