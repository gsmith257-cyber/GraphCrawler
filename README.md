# GraphCrawler
GraphQL automated testing for sensative queries and mutation using introspection

Graph Crawler is an automated testing tool for any GraphQL endpoint with introspection enabled, most are by default.
It will run through and check if mutation is enabled, check for any sensative queries avaliable, such as users and files, and it will also test any easy queries it find to see if authentication is required.
It will then score the findings 1-10 with 10 being the most critical.

I hope this saves you as much time as it has for me

## Usage
```bash
python graphCrawler.py -u https://test.com/graphql/api
```
There is also a output option if you wish to save the GraphQL schema.

Example output:
<img src= />

