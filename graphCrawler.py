import json
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from graphql import *
import argparse
import os
import subprocess
import time
import random

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url",
                    dest="url",
                    help="The Graphql endpoint URL.",
                    action='store',
                    required=True)
parser.add_argument("-o", "--output",
                    dest="output_path",
                    help="Saves schema to this filename + the url.",
                    action='store')
parser.add_argument("-e", "--explore",
                    dest="explore",
                    help="Explore mode will explore a domain for subdmomains with GraphQL endpoints",
                    action='store_true')
parser.add_argument("-i", "--inputFile",
                    dest="inputFile",
                    help="Add a file with a list of endpoints to search",
                    action='store')
parser.add_argument("-s", "--schemaFile",
                    dest="schemaFile",
                    help="Add a file containing the Graphql schema")
parser.add_argument("-a", "--headers",
                    nargs='+',
                    dest="headers",
                    help="Adds specified headers to the request",
                    action='store')


args = parser.parse_args()
mutationLocation = 0
bad_words = ["error", "Invalid token", "INTERNAL_SERVER_ERROR", "Unauthorized"]
sensative_words = ["users", "user", "password", "reset", "edit", "config", "file", "files", "permissions", "products", "role", "register"]

#print ascii art
print("""

 ██████╗ ██████╗  █████╗ ██████╗ ██╗  ██╗ ██████╗██████╗  █████╗ ██╗    ██╗██╗     ███████╗██████╗ 
██╔════╝ ██╔══██╗██╔══██╗██╔══██╗██║  ██║██╔════╝██╔══██╗██╔══██╗██║    ██║██║     ██╔════╝██╔══██╗
██║  ███╗██████╔╝███████║██████╔╝███████║██║     ██████╔╝███████║██║ █╗ ██║██║     █████╗  ██████╔╝
██║   ██║██╔══██╗██╔══██║██╔═══╝ ██╔══██║██║     ██╔══██╗██╔══██║██║███╗██║██║     ██╔══╝  ██╔══██╗
╚██████╔╝██║  ██║██║  ██║██║     ██║  ██║╚██████╗██║  ██║██║  ██║╚███╔███╔╝███████╗███████╗██║  ██║
 ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝╚══════╝╚═╝  ╚═╝
                                                                                                   
github.com/gsmith257-cyber/GraphCrawler
From: S1n1st3r

""")



def clairvoyance(filename):
  print("[+] Trying to grab the schema using Clairvoyance (this could take a while)...")
  try:
    a = os.system("python3 -m clairvoyance -o ./" + filename + " -w ./wordlist/google-10000-english-no-swears.txt " + args.url + " > /dev/null 2>&1")
  except subprocess.TimeoutExpired:
    print(f'Timeout for clairvoyance expired')

#find endpoints from urls
def graphinder(url):
  #get the domain of the url
  print("[+] Setting up Graphinder from escape.tech")
  try:
    a = os.system("docker pull escapetech/graphinder > /dev/null 2>&1")
  except:
    print("[-] Error pulling Graphinder, ensure you have Docker installed")
    exit()
  print("[+] Running Graphinder")
  #run graphinder
  try:
    a = os.system("docker run -it --rm escapetech/graphinder -d " + url + " > results 2>&1")
    a = None
  except:
    print("[-] Error running Graphinder")
  #check if there is an output file
  output = []
  if os.path.isfile("results"):
    with open('results','r') as file:
      with open('results2','w') as f:
        for line in file:
          if not line.isspace():
            f.write(line)
    #delete every line with INF or SCS in it
    counter = 0
    with open("results2", "r") as f:
      #skip the first 20 lines
      for line in f:
        if counter > 20:
          if "INF" not in line and "SCS" not in line:
            if counter >= 22:
              print(line.strip())
              output.append(line.strip())
            else:
              counter += 1
        else:
          counter += 1
    if len(output) > 0:
      #replace http:// with https://
      output = [x.replace("http://", "https://") for x in output]
      print("[+] Graphinder found the following endpoints:")
      for line in output:
        print(line)
      return output
    #open the output file
    else:
       print("[-] Graphinder found no endpoints")
       exit()
  else:
    print("[-] Graphinder encountered an error")
    exit()
  
def main(url, args):
  outputFile = args.output_path
  headers = args.headers
  schemaFile = args.schemaFile

  #add headers if needed
  if headers:
      headers = {header.split(":")[0]:header.split(":")[1] for header in headers}
      transport = AIOHTTPTransport(url=url, headers=headers)
  else:
      transport = AIOHTTPTransport(url=url)

  if schemaFile is None:
      #get the graphql schema
      client = Client(transport=transport, fetch_schema_from_transport=True)
      #download the graphql schema
      schema = client.schema

      # grab the schema from the endpoint
      introspectionQuery = gql(
          """
          query IntrospectionQuery {
        __schema {
          queryType { name }
          mutationType { name }
          types {
            ...FullType
          }
          directives {
            name
            description
            args {
              ...InputValue
            }
          }
        }
      }

        fragment FullType on __Type {
          kind
          name
          description
          fields {
            name
            description
            args {
              ...InputValue
            }
            type {
              ...TypeRef
            }
            isDeprecated
            deprecationReason
          }
          inputFields {
            ...InputValue
          }
          interfaces {
            ...TypeRef
          }
          enumValues {
            name
            description
            isDeprecated
            deprecationReason
          }
          possibleTypes {
            ...TypeRef
          }
        }

        fragment InputValue on __InputValue {
          name
          description
          type { ...TypeRef }
          defaultValue
        }

        fragment TypeRef on __Type {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
              }
            }
          }
        }

      """
      )

      result = None
      # Execute the query on the transport
      resp = "n"
      print("[+] Downloading schema for " + url + " ...")
      random_number = random.randint(1000, 9999 - 1)
      filename = "output" + "_" + str(random_number) + ".json"
      if outputFile:
        filename = outputFile + ".json"
      try:
        result = client.execute(introspectionQuery)
        with open(filename, "w") as f:
          json.dump(result, f, indent=2)
        new_line = '''{\n
          "data": '''
        with open(filename, 'r+') as file:
          content = file.read()
          file.seek(0)
          file.write(new_line + content)
        with open(filename, 'a') as file:
          file.write("\n}")
          
      except Exception as e:
        print("[-] Error downloading schema, is introspection enabled?")
        if "Apollo" in str(e) or "apollo" in str(e):
          print("[+] Apollo server detected")
          resp = input("Do you want to try to grab the schema using Clairvoyance? [y/n] ")
          if resp == "y":
            clairvoyance(filename)
            print("Sleeping for 15 minutes while it runs...")
            time.sleep(900)
            print("[+] I'm awake now, let's continue...")

          else:
            print("[-] Exiting...")
            return
        else:
          print("[-] Exiting...")
          return
  else:
      #schema file supplied 
      if not os.path.exists(schemaFile):
          print(f"[-] Supplied schema file {schemaFile} does not exist. Exiting...")
          return
      filename = schemaFile

  #cleanup query result with json
  with open(filename, "r", encoding="utf8") as f:
    result = json.load(f)

    #[__schema]["mutationType"]
    #[__schema]["types"][' "kind": "OBJECT",']["users"]

    #see if mutation type is present
    mutationEnabled = False
    if "mutationType" in result["data"]["__schema"]:
      try:
        mutation_type = result["data"]["__schema"]["mutationType"]["name"]
        print("[+] Mutation enabled! Name: " + mutation_type)
        mutationEnabled = True
      except:
        print("[-] Error getting mutation name, it could be disabled")
    else:
      print("[-] Mutation disabled")

    i = 0
    while i < 1000:
      try:
        if result["data"]["__schema"]["types"][i]["name"] == mutation_type:
            print(f"[+] Located mutation in schema : {i}")
            mutationLocation = i
            print("[+] I'll leave this for you to test, scipts arent gentle with editing data")
            break
        i += 1
      except:
        break




    #print out the users object from result
    #loop through until you find name of Query
    i = 0
    while i < 1000:
      try:
        if result["data"]["__schema"]["types"][i]["name"] == "Query":
            print(f"[+] Located queries location in schema : {i}")
            break
        i += 1
      except:
        break

    sensative_locations = []
    h = 0
    while h < 1000:
      try:
        if result["data"]["__schema"]["types"][i]["fields"][h]["name"] in sensative_words:
            print(f"[+] Located sensative query in schema : {h}")
            sensative_locations.append(h)
        h += 1
      except:
        break
    print("[+] " + str(len(sensative_locations)) + " sensative queries found")
    for j in sensative_locations:
        print("[+]  " + result["data"]["__schema"]["types"][i]["fields"][j]["name"] + " is a sensative query")

    print("[+] Checking authorization...")

    easy_queries = []
    q = 0
    while q < h:
        try:
          if result["data"]["__schema"]["types"][i]["fields"][q]["args"][0]["name"] == 1:
            print("*", end="")
          q += 1
        except:
            print(f"[+] Found easy query in schema : {q}")
            easy_queries.append(q)
            q += 1

    #test the queries
    badCount = 0
    goodCount = 0
    field = ""
    for k in easy_queries:
        name = result["data"]["__schema"]["types"][i]["fields"][k]["name"]
        if "delete" in name or "Delete" in name:
          prompter = input("This query, " + str(name) + ", contains 'delete'. Are you sure you want to execute?: (y/n)")
          if prompter == "n":
            continue
        print("[+] Testing easy query : " + name)
        #get the type of the query and get fields of the type
        try:
          type = result["data"]["__schema"]["types"][i]["fields"][k]["type"]["ofType"]["name"]
        except:
          type = result["data"]["__schema"]["types"][i]["fields"][k]["type"]["name"]
        f = 0
        while f < 1000:
            try:
                name2 = result["data"]["__schema"]["types"][f]["name"]
                if name2 == type:
                    try:
                      field = result["data"]["__schema"]["types"][f]["fields"][0]["name"]
                    except:
                      field = None
                    break
                f += 1
            except Exception as e:
                f += 1
                pass
        
        if field is None:
          queryText = """
            query {{{name}}}
            """.format(name=name)
        else:
          queryText = """
              query {{{name}{{{field}}}}}
              """.format(name=name, field=field)
        try:
          query = gql(
              queryText
          )
        except Exception as e:
          print("Simple query errored out. Possibly bad read on schema")
        try:
          result2 = client.execute(query)
          result2 = json.loads(json.dumps(result))
          good2go = True
          for l in bad_words:
              if l in result2:
                  print("[-] " + l + " found in result")
                  good2go = False
          if good2go:
              print("[+] query authorized")
              goodCount += 1
        except Exception as e:
            print("[-] Bad word found in result")
            badCount += 1

    if badCount > 1:
        print("[-] Although introspection is enabled, most queries are not authorized it seems")

    #set the criticality rating
    senseCount = len(sensative_locations)
    if senseCount > 4:
      senseCount = 4
    if len(easy_queries) > 0:
      rating = (senseCount * 0.1) + (goodCount / len(easy_queries)) * 0.1
    else:
      rating = (senseCount * 0.1)
    if mutationEnabled:
      rating += 0.5
    rating = round((rating*10), 2)
    print("[+] Criticalilty rating : " + str(rating))
    print("Do you want to get the possible paths to access the sensative node?")
    print("example: username from the user field")
    resp = input("(y/n): ")
    if resp == "y":
      x = True
      while x:
        type = input("Type of the sensative node: ")
        print("[+] Getting possible paths to " + type)
        os.system("./support/graphql-path-enum -i " + filename + " -t " + type)
        resp = input("Do you want to get more paths? (y/n): ")
        if resp == "n":
          x = False


    print("Do you want me to list the queries that are available from the schema?")
    resp = input("(y/n): ")
    if resp == "y":
      locations = []
      h = 0
      while h < 1000:
        try:
          print(result["data"]["__schema"]["types"][i]["fields"][h]["name"])
          h += 1
        except:
          break
      print("[+] " + str(h) + " queries found")
    print("Do you want me to list the mutations that are available from the schema?")
    resp = input("(y/n): ")
    if resp == "y":
      locations = []
      h = 0
      while h < 1000:
        try:
          print(result["data"]["__schema"]["types"][mutationLocation]["fields"][h]["name"])
          h += 1
        except:
          break
      print("[+] " + str(h) + " mutations found")
    print("[-] Exiting...")
    return
    
    #critical 9+
    #high 7+
    #medium 5+
    #low 1-5

if __name__ == "__main__": 
  if args.explore:
    output = graphinder(args.url)
    if output is not None:
      for url in output:
        main(url, args)
      print("[+] Done")
      exit()
  else:
    if args.inputFile is not None:
      try:
        with open(args.inputFile, 'r') as f:
          for line in f:
            main(line.strip(), args)
      except Exception as e:
        print(e)
    else:
      main(args.url, args)
    print("[+] Done")
    exit()
