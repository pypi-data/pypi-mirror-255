from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from string import Template
from agent1c_metrics.reader import get_data

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get('/', response_class=PlainTextResponse)
async def metrics():
    result = [
        "# HELP agent1c_metrics_infobase_logsize Cumulative size of 1cv8log folder.",
        "# TYPE agent1c_metrics_infobase_logsize gauge",
        
        "# HELP agent1c_metrics_infobase_changed_lastday A metric with a boolean value labeled with ibase information.",
        "# TYPE agent1c_metrics_infobase_changed_lastday gauge",
        
        "# HELP agent1c_metrics_infobase_changed_lastweek A metric with a boolean value labeled with ibase information.",
        "# TYPE agent1c_metrics_infobase_changed_lastweek gauge",
        
        "# HELP agent1c_metrics_infobase_changed_lastmonth A metric with a boolean value labeled with ibase information.",
        "# TYPE agent1c_metrics_infobase_changed_lastmonth gauge",

        "# HELP agent1c_metrics_infobase_block_sessions A metric with a boolean value labeled with ibase information.",
        "# TYPE agent1c_metrics_infobase_block_sessions gauge",

        "# HELP agent1c_metrics_infobase_block_tasks A metric with a boolean value labeled with ibase information.",
        "# TYPE agent1c_metrics_infobase_block_tasks gauge",

        "# HELP agent1c_metrics_infobase_inactivity A metric with a int value contains days of inactivity of the base calculated from log modification time.",
        "# TYPE agent1c_metrics_infobase_inactivity gauge",
    ]

    #result.append("# TYPE logtype_by_infobase gauge")
    templates = [
        Template("agent1c_metrics_infobase_logsize{host=\"$host\",port=\"$port\",ibname=\"$name\",ibid=\"$id\",type=\"$logtype\",dbserver=\"$dbserver\",dbname=\"$dbname\"} $logsize"),
        Template("agent1c_metrics_infobase_changed_lastday{host=\"$host\",port=\"$port\",ibname=\"$name\",ibid=\"$id\",type=\"$logtype\",dbserver=\"$dbserver\",dbname=\"$dbname\"} $mtime_lastday"),
        Template("agent1c_metrics_infobase_changed_lastweek{host=\"$host\",port=\"$port\",ibname=\"$name\",ibid=\"$id\",type=\"$logtype\",dbserver=\"$dbserver\",dbname=\"$dbname\"} $mtime_lastweek"),
        Template("agent1c_metrics_infobase_changed_lastmonth{host=\"$host\",port=\"$port\",ibname=\"$name\",ibid=\"$id\",type=\"$logtype\",dbserver=\"$dbserver\",dbname=\"$dbname\"} $mtime_lastmonth"),
        Template("agent1c_metrics_infobase_block_sessions{host=\"$host\",port=\"$port\",ibname=\"$name\",ibid=\"$id\",type=\"$logtype\",dbserver=\"$dbserver\",dbname=\"$dbname\"} $block_sessions"),
        Template("agent1c_metrics_infobase_block_tasks{host=\"$host\",port=\"$port\",ibname=\"$name\",ibid=\"$id\",type=\"$logtype\",dbserver=\"$dbserver\",dbname=\"$dbname\"} $block_tasks"),
        Template("agent1c_metrics_infobase_inactivity{host=\"$host\",port=\"$port\",ibname=\"$name\",ibid=\"$id\",type=\"$logtype\",dbserver=\"$dbserver\",dbname=\"$dbname\"} $inactivity"),
    ]
    #t_logtype = Template("agent1c_metrics_logtype_by_infobase{host=\"$host\",port=\"$port\",ibname=\"$ibname\",ibid=\"$ibid\",type=\"$type\"} 1")
    data = get_data()
    for cluster_info in data['clusters']:
        for ib in cluster_info['data']['bases']:
            for t in templates:
                cluster_prepared_info = { key:val for key, val in cluster_info['data']['cluster'].items() if key not in ['id','name'] }
                ib_prepared_data = dict(map(lambda k: (k,(1 if ib[k] else 0) if type(ib[k])==bool else ib[k]),ib))
                ib_prepared_block_data = dict(map(lambda k: (k,(1 if ib_prepared_data['block'][k] else 0) if type(ib_prepared_data['block'][k])==bool else ib_prepared_data['block'][k]),ib_prepared_data['block']))
                result.append(t.safe_substitute(**cluster_prepared_info,**ib_prepared_data,**ib_prepared_block_data))
    return PlainTextResponse('\n'.join(result))