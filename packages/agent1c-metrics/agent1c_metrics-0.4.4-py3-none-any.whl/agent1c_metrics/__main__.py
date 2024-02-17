import click, uvicorn

@click.command()
@click.option("--reload", is_flag=True, help="Reload if code changes")
@click.option("--host", default='0.0.0.0', type=str, required=False, help="Host for reading")
@click.option("--port", default='8144', type=str, required=False, help="Port for reading")
def main(reload:bool,host:str, port:str) -> None:
    uvicorn.run("agent1c_metrics.viewer:app", port=8144, log_level="info", host=host, reload=reload)

if __name__ == "__main__":
    main()