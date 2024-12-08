# Using the CLI Client

You can interact with the KitchenAI API using the CLI client. This allows you to interact with the API from the command line.

```bash
kitchenai client <SUBCOMMAND>
```

![SUBCOMMANDS](../../../_static/images/client-help.png)


# health

Check the health of the API.

```bash
kitchenai client health
```

# labels

View the registered labels in the API.

```bash
kitchenai client labels
```

# query

Query the API given a label and a query.
```bash
kitchenai client query
```

# agent
run your agent workloads through this endpoint
```bash
kitchenai client agent
```

# embed  
Manage the CRUD operations for embeddings. They are one-off text contents that you want to embed.
```bash
kitchenai client embed
```

# file

Manage the CRUD operations for files in the Django DB.

```bash
kitchenai client file
```
