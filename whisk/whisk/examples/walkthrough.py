import marimo

__generated_with = "0.10.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    from whisk.client import WhiskClient
    import asyncio
    import nest_asyncio
    import signal 
    nest_asyncio.apply()

    nats_url = "nats://localhost:4222"
    client_id = "clienta"
    user = "user1"
    password= "password"
    return (
        WhiskClient,
        asyncio,
        client_id,
        nats_url,
        nest_asyncio,
        password,
        signal,
        user,
    )


@app.cell
def _(WhiskClient, client_id, nats_url, password, user):
    from whisk.examples.app import kitchen

    client = WhiskClient(
        nats_url=nats_url, 
        client_id=client_id,
        user=user,
        password=password,
        app=kitchen
    )
    return client, kitchen


if __name__ == "__main__":
    app.run()
