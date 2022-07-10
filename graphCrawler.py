import json
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from graphql import *
import argparse
import os
import multiprocessing
import time

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url",
                    dest="url",
                    help="The Graphql endpoint URL.",
                    action='store',
                    required=True)
parser.add_argument("-o", "--output",
                    dest="output_path",
                    help="Saves schema to this file",
                    action='store')

args = parser.parse_args()

bad_words = ["error", "Invalid token", "INTERNAL_SERVER_ERROR", "Unauthorized"]
sensative_words = ["users", "user", "password", "reset", "edit", "config", "file", "files", "permissions", "products", "role", "register"]
#get the graphql schema
transport = AIOHTTPTransport(url=args.url)
client = Client(transport=transport, fetch_schema_from_transport=True)
#download the graphql schema
schema = client.schema

def clairvoyance():
  print("[+] Trying to grab the schema using Clairvoyance (this could take a while)...")
  #os.system("python3 -m clairvoyance -o ./data.json -w ./google-10000-english/google-10000-english-no-swears.txt " + args.url)
  print("[+] Schema downloaded successfully")

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

# Execute the query on the transport
resp = "n"
print("[+] Downloading schema...")
try:
  result = client.execute(introspectionQuery)
  filename = "schema.json"
  if args.output_path:
    filename = args.output_path
  with open(filename, "w") as f:
    json.dump(result, f, indent=2)
  new_line = '''{\n
    "data": '''
  with open('file.txt', 'r+') as file:
    content = file.read()
    file.seek(0)
    file.write(new_line + content)
  with open('file.txt', 'a') as file:
    file.write("\n}")
    
except:
  print("[-] Error downloading schema, is introspection enabled?")
  if "Apollo" or "apollo" in result:
    print("[+] Apollo server detected")
    resp = input("Do you want to try to grab the schema using Clairvoyance? [y/n] ")
    if resp == "y":
      p = multiprocessing.Process(target=clairvoyance)
      p.start()

      # Wait for 15 min or until process finishes
      #p.join(900)
      p.join(1)

      # If thread is still active
      if p.is_alive():
        print("[-] Clairvoyance is still running... let's kill it...")
        # Terminate - may not work if process is stuck for good
        p.terminate()
        # OR Kill - will work for sure, no chance for process to finish nicely however
        # p.kill()
        p.join()

    else:
      print("[-] Exiting...")
      exit()
#cleanup query result with json
with open(filename, "r") as f:
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

  print("[+] Checking autherization...")

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
      query = gql(
          queryText
      )
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

  #critical 9+
  #high 7+
  #medium 5+
  #low 1-5
