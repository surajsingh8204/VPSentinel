import { useEffect, useState } from "react";

const idleStates = ["idle", "stretch", "groom"];

function CatAnimation({ active }) {
  const [state, setState] = useState("idle");

  useEffect(() => {
    if (active) {
      setState("thinking");
      return undefined;
    }

    const cycle = setInterval(() => {
      setState((current) => {
        const index = idleStates.indexOf(current);
        return idleStates[(index + 1) % idleStates.length];
      });
    }, 5200);

    return () => clearInterval(cycle);
  }, [active]);

  const speech = active
    ? "CHECKING..."
    : state === "stretch"
      ? "STRETCH!"
      : state === "groom"
        ? "ALL GOOD"
        : "KEEP GOING";

  return (
    <aside
      className={`cat-assistant cat-${state}`}
      aria-hidden="true"
    >
      <div className="cat-bubble">
        {speech}
        <br />
        ^_^
      </div>

      <svg
        className="cat-svg"
        viewBox="0 0 180 120"
        role="presentation"
      >
        {/* Ground shadow */}
        <ellipse
          className="cat-shadow"
          cx="98"
          cy="108"
          rx="55"
          ry="5"
        />

        {/* Tail */}
        <path
          className="cat-tail"
          d="M54 74C23 67 25 28 47 29c11 1 9 14 1 13-10-1-9 17 9 19"
        >
          <animateTransform
            attributeName="transform"
            type="rotate"
            values="0 54 74;-12 54 74;0 54 74;8 54 74;0 54 74"
            dur={active ? "1.4s" : "3.2s"}
            repeatCount="indefinite"
          />
        </path>

        {/* Legs sit behind the body, so they do not overlay it. */}
        <path
          className="cat-legs"
          d="M66 94v12h23V95M108 94v12h25V91"
        />

        {/* Body */}
        <path
          className="cat-body"
          d="M54 68c-9 7-11 22-3 32 12 13 55 13 76 2 10-5 9-22-2-30-14-11-56-14-71-4Z"
        />

        {/* Body patch */}
        <path
          className="cat-patch body-patch"
          d="M75 70c8 5 10 18 4 30H58c-7-12-4-26 5-31Z"
        />

        {/* Body stripes */}
        <path
          className="cat-stripe"
          d="M93 67c-4 12-2 23 4 34M108 69c-2 12 0 22 6 31"
        />

        {/* Head */}
        <g className="cat-head">
          <animateTransform
            attributeName="transform"
            type="rotate"
            values={
              state === "groom"
                ? "0 140 72;-8 140 72;-3 140 72;0 140 72"
                : active
                  ? "0 140 72;3 140 72;0 140 72"
                  : "0 140 72;2 140 72;0 140 72"
            }
            dur={
              state === "groom"
                ? "2.4s"
                : active
                  ? "1.8s"
                  : "4s"
            }
            repeatCount="indefinite"
          />

          {/* Head */}
          <path d="M121 43 128 25l12 16 20-9-2 22c8 10 4 30-10 37-20 11-42-3-39-24-1-10 4-19 12-24Z" />

          {/* Inner ears */}
          <path
            className="cat-ear-inner"
            d="m128 32 4 11 7-4M150 43l7-6-1 13"
          />

          {/* Face */}
          <g className="cat-face">
            <path d="M132 65h1M151 64h1" />

            <path d="m141 70 3 2 3-2M144 72v5" />

            <path
              className="cat-whiskers"
              d="m132 72-17-3m18 7-17 3m36-7 17-4m-17 9 16 4"
            />

            <animate
              attributeName="opacity"
              values="1;1;1;0;1"
              dur="4.2s"
              repeatCount="indefinite"
            />
          </g>
        </g>

        {/* Yarn sits in front of the cat. */}
        <g className="cat-yarn">
          <circle cx="176" cy="97" r="11" />

          <path d="M168 91c8 4 4 12 15 12" />
          <path d="M177 86c-4 8 8 5 4 17" />

          <animateTransform
            attributeName="transform"
            type="rotate"
            values="0 176 97;-5 176 97;0 176 97;5 176 97;0 176 97"
            dur="3.8s"
            repeatCount="indefinite"
          />
        </g>
      </svg>
    </aside>
  );
}

export default CatAnimation;
