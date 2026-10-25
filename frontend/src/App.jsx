import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  useEffect(() => {
    fetch(`${API_URL}/api/forecast-accuracy`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Could not load forecast data.");
        }
        return response.json();
      })
      .then((result) => {
        setData(result);

        const timestamps = result.hourly.map((item) =>
          item.startTime.slice(0, 10)
        );

        if (timestamps.length) {
          setStartDate(timestamps.reduce((a, b) => (a < b ? a : b)));
          setEndDate(timestamps.reduce((a, b) => (a > b ? a : b)));
        }
      })
      .catch((err) => setError(err.message));
  }, []);

  const filteredRows = useMemo(() => {
    if (!data) return [];

    return data.hourly.filter((item) => {
      const date = item.startTime.slice(0, 10);
      return date >= startDate && date <= endDate;
    });
  }, [data, startDate, endDate]);

  const metrics = useMemo(() => {
    if (!filteredRows.length) return null;

    const errors = filteredRows.map(
      (row) => Number(row.actual_gen) - Number(row.forecast_gen)
    );

    return {
      mae:
        errors.reduce((sum, value) => sum + Math.abs(value), 0) / errors.length,
      rmse: Math.sqrt(
        errors.reduce((sum, value) => sum + value * value, 0) / errors.length
      ),
      count: errors.length,
    };
  }, [filteredRows]);

  const chartRows = filteredRows.map((row) => ({
    ...row,
    time: row.startTime.slice(5, 16).replace("T", " "),
  }));

  if (error)
    return (
      <main className="page">
        <p>{error}</p>
      </main>
    );
  if (!data)
    return (
      <main className="page">
        <p>Loading data...</p>
      </main>
    );

  return (
    <main className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">ENERGY ANALYTICS · GREAT BRITAIN</p>
          <h1>Wind Forecast Accuracy</h1>
          <p className="subtitle">
            Compare forecast wind generation with actual generation.
          </p>
        </div>
        <span className="period-tag">January 2026 · GMT</span>
      </header>

      <section className="filters">
        <label>
          From
          <input
            type="date"
            value={startDate}
            max={endDate || undefined}
            onChange={(event) => setStartDate(event.target.value)}
          />
        </label>

        <label>
          To
          <input
            type="date"
            value={endDate}
            min={startDate || undefined}
            onChange={(event) => setEndDate(event.target.value)}
          />
        </label>
      </section>

      <section className="metrics">
        <article className="metric-card">
          <p>Mean Absolute Error</p>
          <h2>
            {metrics
              ? metrics.mae.toLocaleString("en-GB", {
                  maximumFractionDigits: 1,
                })
              : "—"}{" "}
            <small>MW</small>
          </h2>
          <span>Average absolute forecast error</span>
        </article>

        <article className="metric-card">
          <p>Root Mean Squared Error</p>
          <h2>
            {metrics
              ? metrics.rmse.toLocaleString("en-GB", {
                  maximumFractionDigits: 1,
                })
              : "—"}{" "}
            <small>MW</small>
          </h2>
          <span>Penalises larger errors more heavily</span>
        </article>

        <article className="metric-card">
          <p>Hours evaluated</p>
          <h2>{metrics ? metrics.count : 0}</h2>
          <span>Matched hourly observations</span>
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Forecast vs actual generation</h2>
            <p>Average generation, in MW</p>
          </div>
        </div>

        {chartRows.length ? (
          <div className="chart">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartRows}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" minTickGap={35} tick={{ fontSize: 11 }} />
                <YAxis
                  width={75}
                  tick={{ fontSize: 11 }}
                  tickFormatter={(value) => value.toLocaleString("en-GB")}
                />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="actual_gen"
                  name="Actual"
                  stroke="#167d9a"
                  dot={false}
                  strokeWidth={2}
                />
                <Line
                  type="monotone"
                  dataKey="forecast_gen"
                  name="Forecast"
                  stroke="#e29b35"
                  dot={false}
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p>No observations match this date range.</p>
        )}
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Hourly observations</h2>
            <p>Positive error means actual generation exceeded forecast.</p>
          </div>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Delivery time (GMT)</th>
                <th>Actual (MW)</th>
                <th>Forecast (MW)</th>
                <th>Error (MW)</th>
              </tr>
            </thead>
            <tbody>
              {filteredRows.map((row) => (
                <tr key={row.startTime}>
                  <td>{row.startTime.slice(0, 16).replace("T", " ")}</td>
                  <td>{Number(row.actual_gen).toLocaleString("en-GB")}</td>
                  <td>{Number(row.forecast_gen).toLocaleString("en-GB")}</td>
                  <td
                    className={
                      Number(row.error_mw) >= 0 ? "positive" : "negative"
                    }
                  >
                    {Number(row.error_mw).toLocaleString("en-GB", {
                      maximumFractionDigits: 1,
                    })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <footer>
        Source: Elexon FUELHH and WINDFOR. Forecast interval interpretation and
        the assumed bidding deadline are documented project assumptions.
      </footer>
    </main>
  );
}
