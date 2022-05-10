# AutoCypher
A [Cypher](https://neo4j.com/developer/cypher/) query synthesizer, which could generating query from user given Input/Output exampls.

## Environment
[neo4j docker](https://neo4j.com/developer/docker-run-neo4j/) or any neo4j database environment is required.


## Usage
Examples should be put in `example/example`. And modify path inside `AutoCypher/synthesizer.py`

```bash
$ python3 AutoCypher/synthesizer.py
Synthesize on example/example2
...
Found target query:
<synthesized query>
```

## Project Progress
This is an ongoing project. Not all Cypher statements are supported. 
Currently, it could find query that only contains
`MATCH`, `WHERE`, and `RETURN`.