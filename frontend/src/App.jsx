import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import CatAnimation from "./CatAnimation";

function getMetric(data, keys) {
  for (const key of keys) {
    const value = data?.[key];

    if (value !== undefined && value !== null) {
      if (typeof value === "object") {
        return (
          value.percent ??
          value.percentage ??
          value.usage ??
          value.value ??
          null
        );
      }

      return value;
    }
  }

  return null;
}

function getValue(data, keys) {
  for (const key of keys) {
    const value = data?.[key];

    if (value !== undefined && value !== null && value !== "") {
      return value;
    }
  }

  return null;
}

function formatPercent(value) {
  if (value === null || value === undefined) {
    return "--";
  }

  return `${Math.round(Number(value))}%`;
}

function SegmentedBar({ value, tone }) {
  const numericValue = Number(value);

  const filled =
    Number.isFinite(numericValue)
      ? Math.min(10, Math.max(0, Math.round(numericValue / 10)))
      : 0;

  return (
    <div
      className={`segmented-bar ${tone}`}
      aria-label={
        Number.isFinite(numericValue)
          ? `${numericValue}% used`
          : "Metric unavailable"
      }
    >
      {Array.from({ length: 10 }, (_, index) => (
        <span
          key={index}
          className={index < filled ? "filled" : ""}
        />
      ))}
    </div>
  );
}

function MetricCard({ label, value, detail, tone }) {
  return (
    <article className={`metric metric-${tone}`}>
      <div className="metric-top">
        <span className="metric-label">{label}</span>

        <strong>{formatPercent(value)}</strong>
      </div>

      <SegmentedBar
        value={value}
        tone={tone}
      />

      <p className="metric-detail">
        {detail || "--"}
      </p>
    </article>
  );
}

function getSystemName(data) {
  return (
    data?.hostname ??
    data?.host ??
    data?.system_name ??
    data?.systemName ??
    data?.node_name ??
    data?.machine_name ??
    data?.system?.hostname ??
    data?.system?.name ??
    "--"
  );
}

function getCpuDetail(data) {
  const logical =
    data?.cpu_cores ??
    data?.logical_cpus ??
    data?.logical_cpu_count ??
    data?.cpu?.logical_cpu_count;

  const physical =
    data?.cpu_physical ??
    data?.physical_cpus ??
    data?.physical_cpu_count ??
    data?.cpu?.physical_cpu_count;

  if (logical !== undefined && physical !== undefined) {
    return `${logical} Cores | ${physical} Physical`;
  }

  if (logical !== undefined) {
    return `${logical} Cores`;
  }

  return "--";
}

function getMemoryDetail(data) {
  const used =
    data?.memory_used ??
    data?.ram_used ??
    data?.used_memory ??
    data?.memory?.used;

  const total =
    data?.memory_total ??
    data?.ram_total ??
    data?.total_memory ??
    data?.memory?.total;

  if (used !== undefined && total !== undefined) {
    return `${used} / ${total}`;
  }

  return "--";
}

function getDiskDetail(data) {
  const used =
    data?.disk_used ??
    data?.storage_used ??
    data?.used_disk ??
    data?.disk?.used;

  const total =
    data?.disk_total ??
    data?.storage_total ??
    data?.total_disk ??
    data?.disk?.total;

  if (used !== undefined && total !== undefined) {
    return `${used} / ${total}`;
  }

  return "--";
}

function App() {
  const [metrics, setMetrics] = useState({
    cpu: null,
    memory: null,
    storage: null,
    cpuDetail: "--",
    memoryDetail: "--",
    swapDetail: "--",
    storageDetail: "--",
    systemName: "--",
    loaded: false,
  });

  const [message, setMessage] = useState("");
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);

  const chatRef = useRef(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch("/api/metrics");

        if (!response.ok) {
          throw new Error("Metrics request failed");
        }

        const data = await response.json();

        setMetrics({
          cpu: getMetric(data, [
            "cpu",
            "cpu_percent",
            "cpu_usage",
            "cpuUsage",
          ]),

          memory: getMetric(data, [
            "memory",
            "ram",
            "memory_percent",
            "ram_percent",
            "memory_usage",
            "ram_usage",
          ]),

          storage: getMetric(data, [
            "storage",
            "disk",
            "storage_percent",
            "disk_percent",
            "storage_usage",
            "disk_usage",
          ]),

          cpuDetail: getCpuDetail(data),
          memoryDetail: getMemoryDetail(data),

          swapDetail:
            getValue(data, ["swap_used"]) !== null &&
            getValue(data, ["swap_total"]) !== null
              ? `${getValue(data, ["swap_used"])} / ${getValue(data, ["swap_total"])}`
              : "--",

          storageDetail: getDiskDetail(data),
          systemName: getSystemName(data),

          loaded: true,
        });
      } catch (error) {
        console.error(
          "Failed to fetch VPS metrics:",
          error
        );
      }
    };

    fetchMetrics();

    const interval = setInterval(
      fetchMetrics,
      5000
    );

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop =
        chatRef.current.scrollHeight;
    }
  }, [events, loading]);

  const sendMessage = async () => {
    const userMessage = message.trim();

    if (!userMessage || loading) {
      return;
    }

    setEvents((current) => [
      ...current,
      {
        type: "user",
        content: userMessage,
      },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(
        "/api/chat/stream",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: userMessage,
            thread_id: "default",
          }),
        }
      );

      if (!response.ok || !response.body) {
        throw new Error("Chat request failed");
      }

      const reader =
        response.body.getReader();

      const decoder =
        new TextDecoder();

      let buffer = "";

      while (true) {
        const { value, done } =
          await reader.read();

        if (done) {
          break;
        }

        buffer += decoder.decode(
          value,
          { stream: true }
        );

        const lines =
          buffer.split("\n");

        buffer =
          lines.pop() ?? "";

        for (const line of lines) {
          if (!line.trim()) {
            continue;
          }

          const event =
            JSON.parse(line);

          setEvents((current) => {
            const previous =
              current.at(-1);

            if (
              event.type === "message" &&
              previous?.type === "message"
            ) {
              return [
                ...current.slice(0, -1),
                {
                  ...previous,
                  content:
                    previous.content +
                    event.content,
                },
              ];
            }

            return [
              ...current,
              event,
            ];
          });
        }
      }
    } catch (error) {
      console.error(
        "Chat request failed:",
        error
      );

      setEvents((current) => [
        ...current,
        {
          type: "error",
          message:
            "Unable to reach VPSentinel. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">

      {/* HEADER */}
      <header className="header">

        <div>
          <div className="brand">
            VPSENTINEL{" "}
            <span>&gt;</span>
          </div>

          <p className="tagline">
            YOUR VPS. MONITORED BY AI.
          </p>
        </div>

        <div className="header-meta">

          <span className="status">
            <i />
            ONLINE
          </span>

          <span className="divider" />

          <span className="release">
            <b>v1.0.0</b>

            <small>
              {metrics.systemName}
            </small>
          </span>

        </div>

      </header>

      {/* METRICS */}
      <section
        className="metrics"
        aria-label="System metrics"
      >

        <MetricCard
          label="CPU"
          value={metrics.cpu}
          detail={metrics.cpuDetail}
          tone="cpu"
        />

        <article className="metric metric-memory">
          <div className="metric-top">
            <span className="metric-label">RAM</span>
            <strong>{formatPercent(metrics.memory)}</strong>
          </div>

          <SegmentedBar
            value={metrics.memory}
            tone="memory"
          />

          <p className="metric-detail">
            {metrics.memoryDetail}
          </p>

          <p className="swap-detail">
            SWAP: {metrics.swapDetail}
          </p>
        </article>

        <MetricCard
          label="DISK"
          value={metrics.storage}
          detail={metrics.storageDetail}
          tone="storage"
        />

      </section>

      {/* CHAT */}
      <main className="chat" aria-live="polite">

        <div className="chat-scroll" ref={chatRef}>
          <div className="chat-stream">

          {events.length === 0 && (
            <section className="welcome">
              <strong>
                VPSentinel
              </strong>

              <p>
                Your VPS is ready.
              </p>

              <span>
                &gt; Ask me to inspect
                your system.
              </span>
            </section>
          )}

          {events.map(
            (event, index) => {

              if (
                event.type === "user"
              ) {
                return (
                  <div
                    className="user-message"
                    key={index}
                  >
                    <b>&gt;</b>
                    {event.content}
                  </div>
                );
              }

              if (
                event.type ===
                "tool_call"
              ) {
                return (
                  <div
                    className="tool-call"
                    key={index}
                  >
                    <span>
                      [tool]
                    </span>{" "}
                    <code>
                      {event.tool}
                    </code>
                  </div>
                );
              }

              if (
                event.type ===
                "message"
              ) {
                return (
                  <article
                    className="agent-message"
                    key={index}
                  >

                    <h2>
                      VPSentinel
                    </h2>

                    <ReactMarkdown
                      remarkPlugins={[
                        remarkGfm,
                      ]}
                      components={{
                        pre: ({
                          children,
                        }) => (
                          <pre className="code-block">
                            {children}
                          </pre>
                        ),

                        code: ({
                          className,
                          children,
                          ...props
                        }) =>
                          className ? (
                            <code
                              className={
                                className
                              }
                              {...props}
                            >
                              {children}
                            </code>
                          ) : (
                            <code
                              className="inline-code"
                              {...props}
                            >
                              {children}
                            </code>
                          ),
                      }}
                    >
                      {event.content}
                    </ReactMarkdown>

                  </article>
                );
              }

              if (
                event.type ===
                "error"
              ) {
                return (
                  <div
                    className="error-message"
                    key={index}
                  >
                    [error]{" "}
                    {event.message}
                  </div>
                );
              }

              return null;
            }
          )}

          {loading && (
            <div className="thinking">
              VPSentinel{" "}
              <span>
                CHECKING...
              </span>
            </div>
          )}

          </div>
        </div>

        <CatAnimation
          active={loading}
        />

      </main>

      {/* INPUT */}
      <footer className="input-area">

        <label className="input-wrapper">

          <span>&gt;</span>

          <textarea
            value={message}
            onChange={(event) =>
              setMessage(
                event.target.value
              )
            }
            onKeyDown={handleKeyDown}
            placeholder="Ask VPSentinel..."
            aria-label="Ask VPSentinel"
            rows="1"
            disabled={loading}
          />

        </label>

        <button
          onClick={sendMessage}
          disabled={
            loading ||
            !message.trim()
          }
        >
          {loading
            ? "..."
            : "SEND"}
        </button>

      </footer>

    </div>
  );
}

export default App;
