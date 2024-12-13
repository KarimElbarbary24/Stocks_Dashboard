# Database Schema Documentation

## Tables

### Table: `stock_data`
| Column    | Data Type | Key        | Description                               |
|-----------|-----------|------------|-------------------------------------------|
| `id`      | `serial`  | Primary Key | Unique identifier for each record         |
| `symbol`  | `varchar(10)` |          | Stock ticker (e.g., AAPL)                |
| `date`    | `date`    |            | Date of the stock data                   |
| `open`    | `numeric` |            | Opening price                            |
| `high`    | `numeric` |            | High price                               |
| `low`     | `numeric` |            | Low price                                |
| `close`   | `numeric` |            | Closing price                            |
| `volume`  | `bigint`  |            | Trading volume                           |

---

### Table: `technical_indicators`
| Column          | Data Type     | Key         | Description                               |
|-----------------|--------------|-------------|-------------------------------------------|
| `id`            | `serial`     | Primary Key | Unique identifier for each record         |
| `symbol`        | `varchar(10)` | Foreign Key | Stock ticker linked to `stock_data.symbol`|
| `date`          | `date`       | Foreign Key | Date linked to `stock_data.date`          |
| `sma_50`        | `numeric`    |             | 50-day simple moving average             |
| `sma_200`       | `numeric`    |             | 200-day simple moving average            |
| `rsi`           | `numeric`    |             | Relative Strength Index                  |
| `bollinger_upper` | `numeric`  |             | Upper Bollinger Band                     |
| `bollinger_lower` | `numeric`  |             | Lower Bollinger Band                     |

---

### Table: `sentiment_data`
| Column          | Data Type     | Key         | Description                               |
|-----------------|--------------|-------------|-------------------------------------------|
| `id`            | `serial`     | Primary Key | Unique identifier for each record         |
| `symbol`        | `varchar(10)` | Foreign Key | Stock ticker linked to `stock_data.symbol`|
| `date`          | `date`       | Foreign Key | Date linked to `stock_data.date`          |
| `source`        | `varchar(50)` |             | Source of sentiment (e.g., Twitter)       |
| `sentiment_score` | `numeric`  |             | Sentiment score (-1 to 1 or 0 to 100)    |
| `raw_text`      | `text`       |             | Raw text of the sentiment source         |

---

### Table: `fundamental_data`
| Column          | Data Type     | Key         | Description                               |
|-----------------|--------------|-------------|-------------------------------------------|
| `id`            | `serial`     | Primary Key | Unique identifier for each record         |
| `symbol`        | `varchar(10)` | Foreign Key | Stock ticker linked to `stock_data.symbol`|
| `report_date`   | `date`       |             | Date of the financial report             |
| `revenue`       | `bigint`     |             | Revenue in dollars                       |
| `earnings`      | `bigint`     |             | Earnings in dollars                      |
| `pe_ratio`      | `numeric`    |             | Price-to-earnings ratio                  |
| `dividend_yield` | `numeric`   |             | Dividend yield                           |

---