# GraphCrawler

![](https://github.com/gsmith257-cyber/GraphCrawler/raw/main/GraphCrawler.PNG)

GraphQL automated testing for sensative queries and mutation using introspection

Graph Crawler is an automated testing tool for any GraphQL endpoint with introspection enabled, most are by default.
It will run through and check if mutation is enabled, check for any sensative queries avaliable, such as users and files, and it will also test any easy queries it find to see if authentication is required.
<div>
If introspection is not enabled on the endpoint it will check if it is an Apollo Server and then can run [Clairvoyance](https://github.com/nikitastupin/clairvoyance) to brute force and grab the suggestions to try to build the schema ourselves. (See the Clairvoyance project for greater details on this)
It will then score the findings 1-10 with 10 being the most critical.
<div>
If you want to dig deeper into the schema you can also use [graphql-path-enum](https://gitlab.com/dee-see/graphql-path-enum/) to look for paths to certain types, like user IDs, emails, etc.

I hope this saves you as much time as it has for me

## Usage
```bash
python graphCrawler.py -u https://test.com/graphql/api -o <fileName>
```
The output option is not required and by default it will output to schema.json

Example output:
<div>
<img src=https://github.com/gsmith257-cyber/GraphCrawler/blob/main/output.PNG />

