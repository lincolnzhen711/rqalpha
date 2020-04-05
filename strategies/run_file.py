from rqalpha import run_file

config = {
  "base": {
    "start_date": "2018-07-01",
    "end_date": "2018-12-31",
    "benchmark": None,
    "accounts": {
        "future": 10000000,

    }
  },
  "extra": {
    "log_level": "info",
  },
  "mod": {
    "sys_analyser": {
      "enabled": True,
      "plot": True
    }
  }
}

strategy_file_path = "./CTA/trend.py"

run_file(strategy_file_path, config)