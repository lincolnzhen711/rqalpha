from rqalpha import run_file

config = {
  "base": {
    "start_date": "2010-01-01",
    "end_date": "2016-12-31",
    "benchmark": None,
    "accounts": {
        "future": 10000000,
    }
  },
  "extra": {
    "log_level": "warning",
  },
  "mod": {
    "sys_analyser": {
      "enabled": True,
      "plot": True,
      "record": True,
      "output_file": './CTA/dma/dma.pkl',
      "report_save_path": './CTA',
      'plot_save_file': './CTA/dma/dma.png'
    },
    "sys_progress": {
      "enabled": False,
      "show": False
    },
    "sys_simulation": {
      "enabled": True,
      "slippage": 0.01
    }
  }
}

strategy_file_path = "./CTA/dma.py"

run_file(strategy_file_path, config)