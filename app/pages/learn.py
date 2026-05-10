import streamlit.components.v1 as components


components.html(
    """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <style>
    :root {
      --bg-base: #061a15;
      --txt-main: #effff8;
      --txt-soft: #d8f7e8;
      --neon-green: #2ecc71;
      --electric-teal: #00d2ff;
      --card-bg: rgba(9, 26, 20, 0.74);
      --glass-border: rgba(166, 247, 213, 0.33);
    }
    html, body {
      width: 100%;
      height: 100%;
      margin: 0;
      overflow: hidden;
      font-family: Inter, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: radial-gradient(circle at 20% 0%, #0d3025 0%, var(--bg-base) 46%, #030806 100%);
      color: var(--txt-main);
    }
    .learn-shell {
      width: 100%;
      height: 100vh;
      margin: 0;
      padding: 12px 18px 16px 18px;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .hero {
      text-align: center;
      max-width: 980px;
      line-height: 1.5;
      font-size: 1.03rem;
      color: var(--txt-main);
      margin: 2px 0 8px 0;
    }
    .bubble-zone {
      width: 100%;
      max-width: 1220px;
      min-height: 520px;
      display: flex;
      justify-content: center;
      align-items: center;
      margin-top: 4px;
      position: relative;
      flex-shrink: 0;
    }
    .cluster {
      width: min(1180px, 98vw);
      height: min(520px, 56vh);
      position: relative;
    }
    @keyframes levitate {
      0%, 100% { transform: translateY(0px); opacity: 0.9; }
      50% { transform: translateY(-10px); opacity: 1; }
    }
    .orb {
      position: absolute;
      min-width: 120px;
      width: 178px;
      height: 178px;
      border-radius: 50%;
      border: 1px solid var(--glass-border);
      background:
        radial-gradient(circle at 30% 24%, rgba(46, 204, 113, 0.26), rgba(0, 210, 255, 0.16) 45%, rgba(6, 26, 21, 0.78) 72%),
        linear-gradient(145deg, rgba(255, 255, 255, 0.08), rgba(10, 22, 18, 0.18));
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      box-shadow:
        0 16px 34px rgba(0, 0, 0, 0.35),
        inset 0 0 0 1px rgba(255, 255, 255, 0.03),
        inset 0 0 20px rgba(46, 204, 113, 0.1),
        inset 0 0 14px rgba(0, 210, 255, 0.1);
      color: var(--txt-main);
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      line-height: 1.28;
      font-size: 0.88rem;
      font-weight: 600;
      padding: 12px;
      box-sizing: border-box;
      animation: levitate 3s ease-in-out infinite;
      cursor: pointer;
      transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
      user-select: none;
    }
    .orb:hover {
      border-color: rgba(0, 210, 255, 0.75);
      box-shadow:
        0 20px 38px rgba(0, 0, 0, 0.4),
        0 0 0 1px rgba(0, 210, 255, 0.38),
        0 0 30px rgba(0, 210, 255, 0.3),
        inset 0 0 22px rgba(46, 204, 113, 0.16);
    }
    .orb.active {
      width: 202px;
      height: 202px;
      border-color: rgba(0, 210, 255, 0.8);
      box-shadow:
        0 20px 42px rgba(0, 0, 0, 0.4),
        0 0 0 1px rgba(0, 210, 255, 0.45),
        0 0 38px rgba(0, 210, 255, 0.44),
        inset 0 0 24px rgba(46, 204, 113, 0.2);
      z-index: 8;
    }
    .orb.market {
      width: 224px;
      height: 224px;
    }
    .sub-orb {
      position: absolute;
      width: 86px;
      height: 86px;
      border-radius: 50%;
      border: 1px solid var(--glass-border);
      background:
        radial-gradient(circle at 30% 24%, rgba(46, 204, 113, 0.2), rgba(0, 210, 255, 0.14) 46%, rgba(6, 26, 21, 0.82) 72%),
        linear-gradient(145deg, rgba(255, 255, 255, 0.08), rgba(10, 22, 18, 0.18));
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      box-shadow: 0 10px 22px rgba(0, 0, 0, 0.35);
      color: var(--txt-soft);
      font-size: 0.66rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      opacity: 0;
      transition: transform 0.33s ease, opacity 0.33s ease;
      pointer-events: none;
      z-index: 6;
    }
    .market:hover .sub-orb { opacity: 1; }
    .market .s1 { transform: translate(0, 0); }
    .market .s2 { transform: translate(0, 0); }
    .market .s3 { transform: translate(0, 0); }
    .market .s4 { transform: translate(0, 0); }
    .market:hover .s1 { transform: translate(-124px, -14px); }
    .market:hover .s2 { transform: translate(124px, -14px); }
    .market:hover .s3 { transform: translate(-70px, 112px); }
    .market:hover .s4 { transform: translate(70px, 112px); }

    .o1 { left: 8%; top: 8%; animation-delay: -0.1s; }
    .o2 { left: 28%; top: 2%; width: 190px; height: 190px; animation-delay: -0.8s; }
    .o3 { left: 49%; top: 8%; width: 176px; height: 176px; animation-delay: -1.1s; }
    .o4 { left: 70%; top: 10%; width: 188px; height: 188px; animation-delay: -0.4s; }
    .o5 { left: 6%; top: 45%; width: 198px; height: 198px; animation-delay: -1.5s; }
    .o6 { left: 29%; top: 49%; width: 186px; height: 186px; animation-delay: -0.2s; }
    .o7 { left: 51%; top: 50%; width: 172px; height: 172px; animation-delay: -0.9s; }
    .o8 { left: 70%; top: 43%; animation-delay: -1.35s; }

    .answer-layer {
      width: 100%;
      max-width: 1120px;
      margin-top: 8px;
      padding: 0 8px;
      box-sizing: border-box;
      position: relative;
      z-index: 2;
    }
    .answer-card {
      border: 1px solid rgba(0, 210, 255, 0.42);
      border-radius: 18px;
      background: linear-gradient(145deg, rgba(11, 31, 24, 0.9), rgba(5, 16, 12, 0.92));
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      box-shadow: 0 18px 36px rgba(0, 0, 0, 0.34), 0 0 18px rgba(46, 204, 113, 0.14);
      padding: 14px 16px 15px 16px;
      color: var(--txt-soft);
      line-height: 1.58;
      font-size: 0.95rem;
      opacity: 0;
      transform: translateY(10px);
      transition: opacity 0.25s ease, transform 0.25s ease;
      min-height: 180px;
      max-height: 33vh;
      overflow: auto;
    }
    .answer-card.visible {
      opacity: 1;
      transform: translateY(0);
    }
    .answer-card h3 {
      margin: 0 0 8px 0;
      font-size: 1.05rem;
      color: #f0fffa;
      letter-spacing: 0.01em;
    }
    .answer-card .highlight {
      color: var(--neon-green);
      font-weight: 700;
    }
    .answer-card ul { margin: 8px 0 0 18px; padding: 0; }
    .answer-card li { margin: 4px 0; }
  </style>
</head>
<body>
  <div class="learn-shell">
    <div class="hero">
      Welcome to the Knowledge Repository. Engage with the modules below to master power system economics.
    </div>

    <div class="bubble-zone">
      <div class="cluster">
        <div class="orb o1 active" data-key="lmp-smp">LMP vs SMP</div>
        <div class="orb o2" data-key="congestion">Congestion &amp;<br>Nodal Pricing</div>
        <div class="orb o3" data-key="milp">MILP Solver Logic</div>
        <div class="orb o4" data-key="optimal">The Optimal Solution</div>
        <div class="orb o5" data-key="zonal">Zonal Pricing vs<br>Nodal LMPs</div>
        <div class="orb o6" data-key="redispatch">Redispatching Mechanics</div>
        <div class="orb o7" data-key="merit">Generator Merit Order</div>
        <div class="orb market o8" data-key="horizon">
          <span>Market Horizon</span>
          <div class="sub-orb s1">DAM</div>
          <div class="sub-orb s2">Intraday</div>
          <div class="sub-orb s3">Balancing</div>
          <div class="sub-orb s4">Forward</div>
        </div>
      </div>
    </div>

    <div class="answer-layer">
      <div id="answerCard" class="answer-card visible"></div>
    </div>
  </div>

  <script>
    const content = {
      "lmp-smp": {
        title: "1. LMP vs SMP",
        html: `
          <p><span class="highlight">SMP (System Marginal Price)</span> represents a uniform price across the entire network, assuming a copper-plate system with no transmission constraints. <span class="highlight">LMP (Locational Marginal Price)</span> computes a unique value for each node, reflecting physical constraints of the grid.</p>
          <p><strong>Key Distinction:</strong> SMP ignores bottlenecks; LMP reflects the true marginal cost of energy at specific locations.</p>
          <p>Indicative form: \\(LMP_i = \\lambda + \\sum_k PTDF_{k,i}(\\mu_k^+ - \\mu_k^-)\\).</p>
        `
      },
      "congestion": {
        title: "2. Congestion & Nodal Pricing",
        html: `
          <p>Congestion arises when power flow reaches a line thermal limit. Under nodal pricing, this induces <span class="highlight">price decoupling</span>.</p>
          <p>Importing nodes typically see higher prices because local expensive units must be committed, while exporting nodes can see lower prices when low-cost generation cannot be transferred.</p>
        `
      },
      "milp": {
        title: "3. MILP Solver Logic",
        html: `
          <p><span class="highlight">MILP</span> (Mixed-Integer Linear Programming) is the engine for unit commitment with discrete on/off variables.</p>
          <p><strong>Objective:</strong> minimize total cost (fuel + start-up) while satisfying binary and physical constraints such as minimum up/down times and ramp-rate limits.</p>
        `
      },
      "optimal": {
        title: "4. The Optimal Solution",
        html: `
          <p>The optimal solution is the feasible dispatch that minimizes total system cost while respecting power-balance and network constraints.</p>
          <p>It represents the most economically efficient operating point under Kirchhoff-consistent flows and generator technical limits.</p>
        `
      },
      "zonal": {
        title: "5. Zonal Pricing vs Nodal LMPs",
        html: `
          <p><span class="highlight">Zonal pricing</span> aggregates many nodes into one area price and may mask internal congestion.</p>
          <p><span class="highlight">Nodal pricing</span> prices each bus individually, providing more granular and physically accurate economic signals.</p>
        `
      },
      "redispatch": {
        title: "6. Redispatching Mechanics",
        html: `
          <p>Redispatch is a post-market corrective action by the TSO when physical violations remain after initial clearing.</p>
          <p>Selected generators are instructed to increase or decrease output to relieve bottlenecks, usually at additional cost.</p>
        `
      },
      "merit": {
        title: "7. Generator Merit Order",
        html: `
          <p>The merit order ranks plants by marginal cost (MC), from lowest to highest.</p>
          <p>Low-MC resources dispatch first; higher-MC units enter later and can set market-clearing price.</p>
        `
      },
      "horizon": {
        title: "8. Market Horizon: DAM, Intraday, Balancing, Forward",
        html: `
          <ul>
            <li><span class="highlight">Forward</span>: long-horizon contracts for hedging.</li>
            <li><span class="highlight">DAM (Day-Ahead)</span>: primary 24h-ahead volume clearing.</li>
            <li><span class="highlight">Intraday</span>: near-delivery adjustments for load/RES changes.</li>
            <li><span class="highlight">Balancing</span>: real-time reserve activation to maintain 50Hz.</li>
          </ul>
        `
      }
    };

    const card = document.getElementById("answerCard");
    const orbs = document.querySelectorAll(".orb[data-key]");

    function renderCard(key) {
      const item = content[key];
      if (!item) return;
      card.classList.remove("visible");
      setTimeout(() => {
        card.innerHTML = `<h3>${item.title}</h3>${item.html}`;
        card.classList.add("visible");
        if (window.MathJax && window.MathJax.typesetPromise) {
          window.MathJax.typesetPromise([card]).catch(() => {});
        }
      }, 110);
    }

    function setActive(target) {
      orbs.forEach((orb) => orb.classList.remove("active"));
      target.classList.add("active");
    }

    orbs.forEach((orb) => {
      orb.addEventListener("click", () => {
        const key = orb.getAttribute("data-key");
        setActive(orb);
        renderCard(key);
      });
    });

    renderCard("lmp-smp");
  </script>
</body>
</html>
""",
    height=940,
    scrolling=False,
)
