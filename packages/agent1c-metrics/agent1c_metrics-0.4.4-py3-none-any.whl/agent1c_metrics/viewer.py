
from fastapi import FastAPI
from agent1c_metrics.api import settings_api, metrics
from agent1c_metrics import __version__, settings

app = FastAPI(title="1C-agent metrics")
app.include_router(settings_api.router)
app.include_router(metrics.router)
app.version = __version__

from agent1c_metrics.reader import get_data
from agent1c_metrics import settings

@app.get("/")
async def root():

    result = get_data()
    
    return result

if __name__ == "__main__":
    print('Run __main__.py module instead.')
else:
    print(settings)