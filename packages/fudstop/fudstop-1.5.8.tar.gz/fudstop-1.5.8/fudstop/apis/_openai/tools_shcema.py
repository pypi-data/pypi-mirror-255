import datetime



def serialize_record(record):
    return {key: value.isoformat() if isinstance(value, datetime.date) else value
            for key, value in record.items()}
tools =[
    {
    "type": "function",
    "function": {
        "name": "filter_options",
        "description": "Filter options based on several different keyword arguments.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Identifier for the ticker."
                },
                "ticker_symbol": {
                    "type": "string",
                    "description": "Ticker symbol."
                },
                "strike": {
                    "type": "object",
                    "properties": {
                        "name": "strike",
                        "type": "float",
                        "description": "Strike price."
                    }
                },
                "strike_min": {
                    "type": "object",
                    "properties": {
                        "name": "strike_min",
                        "type": "float",
                        "description": "Minimum strike price."
                    }
                },
                "strike_max": {
                    "type": "object",
                    "properties": {
                        "name": "strike_max",
                        "type": "float",
                        "description": "Maximum strike price."
                    }
                },
                "expiry": {
                    "type": "object",
                    "properties": {
                        "name": "expiry",
                        "type": "date",
                        "description": "Expiry date."
                    }
                },
                "expiry_min": {
                    "type": "object",
                    "properties": {
                        "name": "expiry_min",
                        "type": "date",
                        "description": "Minimum expiry date."
                    }
                },
                "expiry_max": {
                    "type": "object",
                    "properties": {
                        "name": "expiry_max",
                        "type": "date",
                        "description": "Maximum expiry date."
                    }
                },
                "open": {
                    "type": "object",
                    "properties": {
                        "name": "open",
                        "type": "float",
                        "description": "Open price."
                    }
                },
                "open_min": {
                    "type": "object",
                    "properties": {
                        "name": "open_min",
                        "type": "float",
                        "description": "Minimum open price."
                    }
                },
                "open_max": {
                    "type": "object",
                    "properties": {
                        "name": "open_max",
                        "type": "float",
                        "description": "Maximum open price."
                    }
                },
                "high": {
                    "type": "object",
                    "properties": {
                        "name": "high",
                        "type": "float",
                        "description": "High price."
                    }
                },
                "high_min": {
                    "type": "object",
                    "properties": {
                        "name": "high_min",
                        "type": "float",
                        "description": "Minimum high price."
                    }
                },
                "high_max": {
                    "type": "object",
                    "properties": {
                        "name": "high_max",
                        "type": "float",
                        "description": "Maximum high price."
                    }
                },
                "low": {
                    "type": "object",
                    "properties": {
                        "name": "low",
                        "type": "float",
                        "description": "Low price."
                    }
                },
                "low_min": {
                    "type": "object",
                    "properties": {
                        "name": "low_min",
                        "type": "float",
                        "description": "Minimum low price."
                    }
                },
                "low_max": {
                    "type": "object",
                    "properties": {
                        "name": "low_max",
                        "type": "float",
                        "description": "Maximum low price."
                    }
                },
                "oi": {
                    "type": "object",
                    "properties": {
                        "name": "oi",
                        "type": "float",
                        "description": "Open Interest."
                    }
                },
                "oi_min": {
                    "type": "object",
                    "properties": {
                        "name": "oi_min",
                        "type": "float",
                        "description": "Minimum Open Interest."
                    }
                },
                "oi_max": {
                    "type": "object",
                    "properties": {
                        "name": "oi_max",
                        "type": "float",
                        "description": "Maximum Open Interest."
                    }
                },
                "vol": {
                    "type": "object",
                    "properties": {
                        "name": "vol",
                        "type": "float",
                        "description": "Volume."
                    }
                },
                "vol_min": {
                    "type": "object",
                    "properties": {
                        "name": "vol_min",
                        "type": "float",
                        "description": "Minimum Volume."
                    }
                },
                "vol_max": {
                    "type": "object",
                    "properties": {
                        "name": "vol_max",
                        "type": "float",
                        "description": "Maximum Volume."
                    }
                },
                "delta": {
                    "type": "object",
                    "properties": {
                        "name": "delta",
                        "type": "float",
                        "description": "Delta."
                    }
                },
                "delta_min": {
                    "type": "object",
                    "properties": {
                        "name": "delta_min",
                        "type": "float",
                        "description": "Minimum Delta."
                    }
                },
                "delta_max": {
                    "type": "object",
                    "properties": {
                        "name": "delta_max",
                        "type": "float",
                        "description": "Maximum Delta."
                    }
                },
                "vega": {
                    "type": "object",
                    "properties": {
                        "name": "vega",
                        "type": "float",
                        "description": "Vega."
                    }
                },
                "vega_min": {
                    "type": "object",
                    "properties": {
                        "name": "vega_min",
                        "type": "float",
                        "description": "Minimum Vega."
                    }
                },
                "vega_max": {
                    "type": "object",
                    "properties": {
                        "name": "vega_max",
                        "type": "float",
                        "description": "Maximum Vega."
                    }
                },
                "iv": {
                    "type": "object",
                    "properties": {
                        "name": "iv",
                        "type": "float",
                        "description": "Implied Volatility."
                    }
                },
                "iv_min": {
                    "type": "object",
                    "properties": {
                        "name": "iv_min",
                        "type": "float",
                        "description": "Minimum Implied Volatility."
                    }
                },
                "iv_max": {
                    "type": "object",
                    "properties": {
                        "name": "iv_max",
                        "type": "float",
                        "description": "Maximum Implied Volatility."
                    }
                },
                "dte": {
                    "type": "object",
                    "properties": {
                        "name": "dte",
                        "type": "string",
                        "description": "Days to Expiry."
                    }
                },
                "dte_min": {
                    "type": "object",
                    "properties": {
                        "name": "dte_min",
                        "type": "string",
                        "description": "Minimum Days to Expiry."
                    }
                },
                "dte_max": {
                    "type": "object",
                    "properties": {
                        "name": "dte_max",
                        "type": "string",
                        "description": "Maximum Days to Expiry."
                    }
                },
                "gamma": {
                    "type": "object",
                    "properties": {
                        "name": "gamma",
                        "type": "float",
                        "description": "Gamma."
                    }
                },
                "gamma_min": {
                    "type": "object",
                    "properties": {
                        "name": "gamma_min",
                        "type": "float",
                        "description": "Minimum Gamma."
                    }
                },
                "gamma_max": {
                    "type": "object",
                    "properties": {
                        "name": "gamma_max",
                        "type": "float",
                        "description": "Maximum Gamma."
                    }
                },
                "theta": {
                    "type": "object",
                    "properties": {
                        "name": "theta",
                        "type": "float",
                        "description": "Theta."
                    }
                },
                "theta_min": {
                    "type": "object",
                    "properties": {
                        "name": "theta_min",
                        "type": "float",
                        "description": "Minimum Theta."
                    }
                },
                "theta_max": {
                    "type": "object",
                    "properties": {
                        "name": "theta_max",
                        "type": "float",
                        "description": "Maximum Theta."
                    }
                },
                "sensitivity": {
                    "type": "object",
                    "properties": {
                        "name": "sensitivity",
                        "type": "float",
                        "description": "Sensitivity."
                    }
                },
                "sensitivity_min": {
                    "type": "object",
                    "properties": {
                        "name": "sensitivity_min",
                        "type": "float",
                        "description": "Minimum Sensitivity."
                    }
                },
                "sensitivity_max": {
                    "type": "object",
                    "properties": {
                        "name": "sensitivity_max",
                        "type": "float",
                        "description": "Maximum Sensitivity."
                    }
                },
                "bid": {
                    "type": "object",
                    "properties": {
                        "name": "bid",
                        "type": "float",
                        "description": "Bid price."
                    }
                },
                "bid_min": {
                    "type": "object",
                    "properties": {
                        "name": "bid_min",
                        "type": "float",
                        "description": "Minimum Bid price."
                    }
                },
                "bid_max": {
                    "type": "object",
                    "properties": {
                        "name": "bid_max",
                        "type": "float",
                        "description": "Maximum Bid price."
                    }
                },
                "ask": {
                    "type": "object",
                    "properties": {
                        "name": "ask",
                        "type": "float",
                        "description": "Ask price."
                    }
                },
                "ask_min": {
                    "type": "object",
                    "properties": {
                        "name": "ask_min",
                        "type": "float",
                        "description": "Minimum Ask price."
                    }
                },
                "ask_max": {
                    "type": "object",
                    "properties": {
                        "name": "ask_max",
                        "type": "float",
                        "description": "Maximum Ask price."
                    }
                },
                "close": {
                    "type": "object",
                    "properties": {
                        "name": "close",
                        "type": "float",
                        "description": "Close price."
                    }
                },
                "close_min": {
                    "type": "object",
                    "properties": {
                        "name": "close_min",
                        "type": "float",
                        "description": "Minimum Close price."
                    }
                },
                "close_max": {
                    "type": "object",
                    "properties": {
                        "name": "close_max",
                        "type": "float",
                        "description": "Maximum Close price."
                    }
                },
                "cp": {
                    "type": "object",
                    "properties": {
                        "name": "cp",
                        "type": "string",
                        "description": "Call or Put."
                    }
                },
                "time_value": {
                    "type": "object",
                    "properties": {
                        "name": "time_value",
                        "type": "float",
                        "description": "Time Value."
                    }
                },
                "time_value_min": {
                    "type": "object",
                    "properties": {
                        "name": "time_value_min",
                        "type": "float",
                        "description": "Minimum Time Value."
                    }
                },
                "time_value_max": {
                    "type": "object",
                    "properties": {
                        "name": "time_value_max",
                        "type": "float",
                        "description": "Maximum Time Value."
                    }
                },
                "moneyness": {
                    "type": "object",
                    "properties": {
                        "name": "moneyness",
                        "type": "string",
                        "description": "Moneyness."
                    }
                },
                "exercise_style": {
                    "type": "object",
                    "properties": {
                        "name": "exercise_style",
                        "type": "string",
                        "description": "Exercise Style."
                    }
                },
                "option_symbol": {
                    "type": "object",
                    "properties": {
                        "name": "option_symbol",
                        "type": "string",
                        "description": "Option Symbol."
                    }
                },
                "theta_decay_rate": {
                    "type": "object",
                    "properties": {
                        "name": "theta_decay_rate",
                        "type": "float",
                        "description": "Theta Decay Rate."
                    }
                },
                "theta_decay_rate_min": {
                    "type": "object",
                    "properties": {
                        "name": "theta_decay_rate_min",
                        "type": "float",
                        "description": "Minimum Theta Decay Rate."
                    }
                },
                "theta_decay_rate_max": {
                    "type": "object",
                    "properties": {
                        "name": "theta_decay_rate_max",
                        "type": "float",
                        "description": "Maximum Theta Decay Rate."
                    }
                },
                "delta_theta_ratio": {
                    "type": "object",
                    "properties": {
                        "name": "delta_theta_ratio",
                        "type": "float",
                        "description": "Delta Theta Ratio."
                    }
                },
                "delta_theta_ratio_min": {
                    "type": "object",
                    "properties": {
                        "name": "delta_theta_ratio_min",
                        "type": "float",
                        "description": "Minimum Delta Theta Ratio."
                    }
                },
                "delta_theta_ratio_max": {
                    "type": "object",
                    "properties": {
                        "name": "delta_theta_ratio_max",
                        "type": "float",
                        "description": "Maximum Delta Theta Ratio."
                    }
                },

            "required": ["ticker"]
            }
            
        }
        }
    }

]


tools=[{
      "type": "function",
    "function": {
      "name": "law",
      "description": "Get the texas laws and help the user!",
      "parameters": {
        "type": "object",
        "properties": {
          "prompt": {"type": "string", "description": "The search term to query via user prompt."},
        },
        "required": ["prompt"]
      }
    }
  }]