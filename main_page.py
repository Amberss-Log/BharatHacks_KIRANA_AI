from IPython.display import display, HTML

# Replace 'your_html_string' with your actual HTML content
html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>BharatBricks — Main App</title>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;500;600;700;800&family=Noto+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet"/>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --saffron:#E8541A;--saffron-light:#FFF0EA;--saffron-mid:#F7A97A;--saffron-dark:#C84414;
  --green:#1A7A4A;--green-light:#E8F5EE;--green-dark:#125c37;
  --amber:#F5A623;--red:#D93B3B;--blue:#1A5CE8;
  --ink:#1A1A1A;--ink2:#3A3A3A;--muted:#6B6B6B;--border:#E2E2E2;--border2:#F0EDE8;
  --card:#FFFFFF;--bg:#F7F4F0;--radius:14px;
  --urgent:#D93B3B;--urgent-bg:#FEF2F2;
  --weekly:#1A5CE8;--weekly-bg:#EFF4FF;
  --seasonal:#7C3AED;--seasonal-bg:#F5F0FF;
}
body{font-family:'Noto Sans',sans-serif;background:var(--bg);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
h1,h2,h3,.display{font-family:'Baloo 2',sans-serif}

/* ── Phone frame ── */
.phone-frame{
  width:390px;height:844px;background:var(--card);border-radius:36px;
  box-shadow:0 0 0 1px rgba(0,0,0,.08),0 32px 80px rgba(0,0,0,.18);
  overflow:hidden;display:flex;flex-direction:column;position:relative;
}

/* ── Status bar ── */
.status-bar{
  height:44px;background:var(--saffron);display:flex;align-items:center;
  justify-content:space-between;padding:0 20px;flex-shrink:0;
}
.status-bar .sb-left{font-family:'Baloo 2',sans-serif;font-size:14px;font-weight:700;color:#fff;display:flex;align-items:center;gap:6px}
.status-bar .sb-right{font-size:11px;color:rgba(255,255,255,.85);font-weight:600;font-family:'Baloo 2',sans-serif}
.status-dot{width:7px;height:7px;border-radius:50%;background:#4ADE80;box-shadow:0 0 0 2px rgba(74,222,128,.3)}

/* ── View container ── */
.view{display:none;flex-direction:column;flex:1;overflow:hidden}
.view.active{display:flex}

/* ══════════════════════════════════════════
   MAIN SCREEN
══════════════════════════════════════════ */
#view-main{background:var(--bg)}

.main-header{
  background:var(--saffron);padding:14px 20px 18px;flex-shrink:0;
}
.main-header .greeting{font-size:12px;color:rgba(255,255,255,.75);font-weight:500;margin-bottom:2px}
.main-header .shop-name{font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:700;color:#fff;margin-bottom:10px}
.stats-row{display:flex;gap:8px}
.stat-pill{flex:1;background:rgba(255,255,255,.15);border-radius:10px;padding:9px 10px;text-align:center}
.stat-pill .sv{font-family:'Baloo 2',sans-serif;font-size:16px;font-weight:700;color:#fff}
.stat-pill .sl{font-size:10px;color:rgba(255,255,255,.75);margin-top:1px;font-weight:500}

.action-buttons{display:flex;gap:10px;padding:14px 16px 10px;flex-shrink:0}
.action-btn{
  flex:1;height:72px;border-radius:16px;border:none;cursor:pointer;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;
  font-family:'Baloo 2',sans-serif;font-size:13px;font-weight:700;
  transition:all .18s;letter-spacing:.2px;
}
.action-btn .ab-icon{font-size:22px}
.btn-log{background:var(--green);color:#fff;box-shadow:0 4px 16px rgba(26,122,74,.25)}
.btn-log:hover{background:var(--green-dark);transform:translateY(-2px)}
.btn-ai{background:var(--saffron);color:#fff;box-shadow:0 4px 16px rgba(232,84,26,.25)}
.btn-ai:hover{background:var(--saffron-dark);transform:translateY(-2px)}
.btn-log:active,.btn-ai:active{transform:translateY(0)}

.section-label{
  padding:0 16px 8px;font-family:'Baloo 2',sans-serif;
  font-size:13px;font-weight:700;color:var(--muted);letter-spacing:.5px;text-transform:uppercase;
  display:flex;justify-content:space-between;align-items:center;flex-shrink:0;
}
.section-label span{font-size:11px;font-weight:500;color:var(--saffron);text-transform:none;letter-spacing:0;cursor:pointer}

.orders-list{flex:1;overflow-y:auto;padding:0 16px 16px}
.order-card{
  background:#fff;border-radius:12px;border:1px solid var(--border2);
  padding:12px 14px;margin-bottom:8px;display:flex;align-items:center;gap:12px;
  animation:slideIn .25s ease;
}
@keyframes slideIn{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:translateY(0)}}
.order-id-badge{
  width:36px;height:36px;border-radius:10px;background:var(--saffron-light);
  font-family:'Baloo 2',sans-serif;font-size:12px;font-weight:700;color:var(--saffron);
  display:flex;align-items:center;justify-content:center;flex-shrink:0;
}
.order-info{flex:1}
.order-info .oi-top{display:flex;justify-content:space-between;align-items:center}
.order-info .oi-id{font-family:'Baloo 2',sans-serif;font-size:13px;font-weight:700;color:var(--ink)}
.order-info .oi-amt{font-family:'Baloo 2',sans-serif;font-size:14px;font-weight:700;color:var(--green)}
.order-info .oi-sub{font-size:11px;color:var(--muted);margin-top:2px}
.order-empty{text-align:center;padding:40px 20px;color:var(--muted)}
.order-empty .oe-icon{font-size:36px;margin-bottom:8px}
.order-empty p{font-size:13px;font-family:'Baloo 2',sans-serif;font-weight:600}
.order-empty small{font-size:11px}

/* ══════════════════════════════════════════
   LOG SALE SCREEN
══════════════════════════════════════════ */
#view-log{background:var(--bg)}

.log-header{
  background:#fff;padding:14px 16px 12px;border-bottom:1px solid var(--border2);
  display:flex;align-items:center;gap:10px;flex-shrink:0;
}
.back-btn{
  width:36px;height:36px;border-radius:10px;border:1px solid var(--border);
  background:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;
  font-size:18px;color:var(--muted);transition:all .15s;flex-shrink:0;
}
.back-btn:hover{border-color:var(--saffron);color:var(--saffron)}
.log-header-text{flex:1}
.log-header-text h3{font-family:'Baloo 2',sans-serif;font-size:17px;font-weight:700;color:var(--ink)}
.log-header-text p{font-size:11px;color:var(--muted);margin-top:1px}

.log-search-area{padding:12px 16px;flex-shrink:0;background:#fff;border-bottom:1px solid var(--border2)}
.search-input-wrap{position:relative}
.search-input-wrap input{
  width:100%;padding:11px 16px 11px 40px;border:1.5px solid var(--border);
  border-radius:10px;font-size:14px;font-family:'Noto Sans',sans-serif;
  color:var(--ink);background:#FAFAFA;outline:none;transition:border-color .2s;
}
.search-input-wrap input:focus{border-color:var(--saffron);background:#fff}
.search-icon{position:absolute;left:14px;top:50%;transform:translateY(-50%);font-size:15px;color:var(--muted)}

.quick-items{padding:10px 16px;flex-shrink:0}
.qi-label{font-size:10px;font-weight:600;color:var(--muted);letter-spacing:.5px;text-transform:uppercase;margin-bottom:8px;font-family:'Baloo 2',sans-serif}
.qi-scroll{display:flex;gap:8px;overflow-x:auto;padding-bottom:4px}
.qi-scroll::-webkit-scrollbar{display:none}
.qi-chip{
  flex-shrink:0;padding:7px 12px;border-radius:8px;border:1.5px solid var(--border);
  background:#fff;font-size:12px;font-weight:600;color:var(--ink2);cursor:pointer;
  font-family:'Baloo 2',sans-serif;transition:all .15s;white-space:nowrap;
}
.qi-chip:hover{border-color:var(--saffron);color:var(--saffron)}

.cart-area{flex:1;overflow-y:auto;padding:10px 16px}
.cart-label{font-size:10px;font-weight:600;color:var(--muted);letter-spacing:.5px;text-transform:uppercase;margin-bottom:8px;font-family:'Baloo 2',sans-serif}
.cart-item{
  background:#fff;border-radius:10px;border:1px solid var(--border2);
  padding:10px 12px;margin-bottom:8px;display:flex;align-items:center;gap:10px;
}
.ci-name{flex:1;font-size:13px;font-weight:600;color:var(--ink);font-family:'Baloo 2',sans-serif}
.ci-price{font-size:12px;color:var(--muted);margin-top:1px}
.ci-qty{display:flex;align-items:center;gap:8px}
.ci-qty button{
  width:28px;height:28px;border-radius:7px;border:1.5px solid var(--border);
  background:#fff;font-size:16px;cursor:pointer;display:flex;align-items:center;
  justify-content:center;font-family:'Baloo 2',sans-serif;font-weight:700;
  color:var(--ink);transition:all .15s;line-height:1;
}
.ci-qty button:hover{border-color:var(--saffron);color:var(--saffron)}
.ci-qty .qty-val{font-family:'Baloo 2',sans-serif;font-size:15px;font-weight:700;color:var(--ink);min-width:20px;text-align:center}
.ci-del{width:28px;height:28px;border-radius:7px;border:none;background:var(--urgent-bg);
  color:var(--urgent);cursor:pointer;font-size:14px;display:flex;align-items:center;justify-content:center}

.cart-empty{text-align:center;padding:30px 20px;color:var(--muted)}
.cart-empty .ce-icon{font-size:30px;margin-bottom:8px}
.cart-empty p{font-size:13px;font-family:'Baloo 2',sans-serif;font-weight:600}

.log-footer{padding:12px 16px 20px;background:#fff;border-top:1px solid var(--border2);flex-shrink:0}
.total-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.total-label{font-size:13px;color:var(--muted);font-weight:500}
.total-amt{font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800;color:var(--green)}
.confirm-btn{
  width:100%;height:50px;border-radius:12px;border:none;background:var(--green);color:#fff;
  font-family:'Baloo 2',sans-serif;font-size:15px;font-weight:700;cursor:pointer;
  display:flex;align-items:center;justify-content:center;gap:8px;
  transition:all .2s;letter-spacing:.3px;
}
.confirm-btn:hover{background:var(--green-dark);transform:translateY(-1px)}
.confirm-btn:active{transform:translateY(0)}
.confirm-btn:disabled{background:#C8C8C8;cursor:not-allowed;transform:none}

/* ══════════════════════════════════════════
   BILL CONFIRM SCREEN
══════════════════════════════════════════ */
#view-bill{background:var(--bg)}

.bill-header{
  background:#fff;padding:14px 16px 12px;border-bottom:1px solid var(--border2);
  display:flex;align-items:center;gap:10px;flex-shrink:0;
}
.bill-scroll{flex:1;overflow-y:auto;padding:16px}
.bill-card{background:#fff;border-radius:14px;border:1px solid var(--border2);overflow:hidden;margin-bottom:12px}
.bill-top{padding:14px 16px;border-bottom:1px solid var(--border2)}
.bill-oid{font-family:'Baloo 2',sans-serif;font-size:13px;color:var(--muted);font-weight:600}
.bill-shop{font-family:'Baloo 2',sans-serif;font-size:17px;font-weight:700;color:var(--ink);margin-top:2px}
.bill-time{font-size:11px;color:var(--muted);margin-top:2px}
.bill-items{padding:10px 16px}
.bill-item-row{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid var(--border2)}
.bill-item-row:last-child{border-bottom:none}
.bir-name{font-size:13px;color:var(--ink);font-weight:500}
.bir-detail{font-size:11px;color:var(--muted);margin-top:1px}
.bir-amt{font-family:'Baloo 2',sans-serif;font-size:13px;font-weight:700;color:var(--ink)}
.bill-total-row{padding:12px 16px;background:var(--green-light);display:flex;justify-content:space-between;align-items:center}
.bt-label{font-family:'Baloo 2',sans-serif;font-size:14px;font-weight:700;color:var(--green)}
.bt-amt{font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800;color:var(--green)}

.payment-section{background:#fff;border-radius:14px;border:1px solid var(--border2);padding:14px 16px;margin-bottom:12px}
.ps-label{font-family:'Baloo 2',sans-serif;font-size:12px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.4px;margin-bottom:10px}
.pay-options{display:flex;gap:8px}
.pay-opt{
  flex:1;padding:10px 8px;border:1.5px solid var(--border);border-radius:10px;
  text-align:center;cursor:pointer;transition:all .15s;background:#fff;
}
.pay-opt:hover{border-color:var(--saffron-mid)}
.pay-opt.active{border-color:var(--saffron);background:var(--saffron-light)}
.pay-opt .po-icon{font-size:18px;margin-bottom:3px}
.pay-opt .po-label{font-size:10px;font-weight:600;color:var(--ink);font-family:'Baloo 2',sans-serif}

.paid-btn{
  width:100%;height:52px;border-radius:12px;border:none;background:var(--green);color:#fff;
  font-family:'Baloo 2',sans-serif;font-size:16px;font-weight:700;cursor:pointer;
  display:flex;align-items:center;justify-content:center;gap:8px;
  transition:all .2s;letter-spacing:.3px;margin-bottom:0;
}
.paid-btn:hover{background:var(--green-dark);transform:translateY(-1px)}

/* ══════════════════════════════════════════
   AI DASHBOARD SCREEN
══════════════════════════════════════════ */
#view-ai{background:var(--bg)}

.ai-header{
  background:linear-gradient(135deg,#1A1A2E 0%,#16213E 60%,#0F3460 100%);
  padding:14px 16px 16px;flex-shrink:0;
}
.ai-header-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
.ai-back{
  width:34px;height:34px;border-radius:10px;border:1px solid rgba(255,255,255,.15);
  background:rgba(255,255,255,.08);cursor:pointer;display:flex;align-items:center;
  justify-content:center;font-size:16px;color:rgba(255,255,255,.8);transition:all .15s;
}
.ai-back:hover{background:rgba(255,255,255,.15)}
.ai-title-wrap{}
.ai-title{font-family:'Baloo 2',sans-serif;font-size:18px;font-weight:700;color:#fff}
.ai-subtitle{font-size:11px;color:rgba(255,255,255,.6);margin-top:1px}
.ai-tag{
  display:flex;align-items:center;gap:5px;background:rgba(74,222,128,.15);
  border:1px solid rgba(74,222,128,.3);border-radius:20px;padding:4px 10px;
}
.ai-tag-dot{width:6px;height:6px;border-radius:50%;background:#4ADE80;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.ai-tag span{font-size:10px;font-weight:600;color:#4ADE80;font-family:'Baloo 2',sans-serif}

.ai-summary-row{display:flex;gap:8px}
.ai-sum-card{flex:1;background:rgba(255,255,255,.08);border-radius:10px;padding:10px;border:1px solid rgba(255,255,255,.1)}
.ai-sum-val{font-family:'Baloo 2',sans-serif;font-size:17px;font-weight:700;color:#fff}
.ai-sum-label{font-size:10px;color:rgba(255,255,255,.6);margin-top:2px;font-weight:500}

.ai-tabs{display:flex;background:#fff;border-bottom:2px solid var(--border2);flex-shrink:0}
.ai-tab{
  flex:1;padding:11px 6px;text-align:center;cursor:pointer;
  font-family:'Baloo 2',sans-serif;font-size:11px;font-weight:700;color:var(--muted);
  border-bottom:2px solid transparent;margin-bottom:-2px;transition:all .15s;
  display:flex;flex-direction:column;align-items:center;gap:2px;
}
.ai-tab .tab-icon{font-size:14px}
.ai-tab.active{color:var(--saffron);border-bottom-color:var(--saffron)}

.ai-content{flex:1;overflow-y:auto;padding:14px 14px 16px}

/* Insight cards */
.insight-card{
  background:#fff;border-radius:14px;border:1px solid var(--border2);
  margin-bottom:12px;overflow:hidden;
}
.ic-header{padding:12px 14px 10px;display:flex;align-items:flex-start;gap:10px;border-bottom:1px solid var(--border2)}
.ic-badge{
  padding:3px 8px;border-radius:6px;font-size:9px;font-weight:700;
  font-family:'Baloo 2',sans-serif;letter-spacing:.4px;text-transform:uppercase;flex-shrink:0;margin-top:2px;
}
.badge-urgent{background:var(--urgent-bg);color:var(--urgent)}
.badge-weekly{background:var(--weekly-bg);color:var(--weekly)}
.badge-seasonal{background:var(--seasonal-bg);color:var(--seasonal)}
.badge-summary{background:var(--green-light);color:var(--green)}
.ic-title{font-family:'Baloo 2',sans-serif;font-size:14px;font-weight:700;color:var(--ink);flex:1}
.ic-sub{font-size:11px;color:var(--muted);margin-top:2px;line-height:1.4}
.ic-body{padding:10px 14px}
.product-row{
  display:flex;align-items:center;justify-content:space-between;
  padding:7px 0;border-bottom:1px solid var(--border2);
}
.product-row:last-child{border-bottom:none}
.pr-left{display:flex;align-items:center;gap:8px}
.pr-icon{width:28px;height:28px;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:14px}
.pr-icon.urgent{background:var(--urgent-bg)}
.pr-icon.ok{background:var(--green-light)}
.pr-name{font-size:12px;font-weight:600;color:var(--ink);font-family:'Baloo 2',sans-serif}
.pr-stock{font-size:10px;color:var(--muted);margin-top:1px}
.pr-right{text-align:right}
.pr-action{font-size:11px;font-weight:700;color:var(--urgent);font-family:'Baloo 2',sans-serif}
.pr-units{font-size:10px;color:var(--muted);margin-top:1px}

.trend-chip{
  display:inline-flex;align-items:center;gap:5px;padding:6px 10px;border-radius:8px;
  font-size:11px;font-weight:600;font-family:'Baloo 2',sans-serif;margin:3px 3px 3px 0;
}
.trend-up{background:#F0FDF4;color:#16A34A}
.trend-down{background:var(--urgent-bg);color:var(--urgent)}
.trend-new{background:var(--seasonal-bg);color:var(--seasonal)}

.chart-bar-row{display:flex;align-items:flex-end;gap:4px;height:60px;margin:10px 0 4px}
.bar-wrap{flex:1;display:flex;flex-direction:column;align-items:center;gap:3px}
.bar{border-radius:4px 4px 0 0;width:100%;transition:height .4s ease;background:var(--saffron);opacity:.7}
.bar.today{opacity:1;background:var(--saffron)}
.bar-label{font-size:9px;color:var(--muted);font-family:'Baloo 2',sans-serif;font-weight:600}

.notify-banner{
  background:linear-gradient(135deg,#1A1A2E,#0F3460);
  border-radius:12px;padding:12px 14px;display:flex;align-items:center;gap:10px;margin-bottom:12px;
}
.nb-icon{font-size:20px;flex-shrink:0}
.nb-text h4{font-family:'Baloo 2',sans-serif;font-size:13px;font-weight:700;color:#fff;margin-bottom:2px}
.nb-text p{font-size:11px;color:rgba(255,255,255,.65);line-height:1.4}
.nb-btn{
  flex-shrink:0;padding:7px 12px;border-radius:8px;border:none;
  background:var(--saffron);color:#fff;font-size:11px;font-weight:700;
  font-family:'Baloo 2',sans-serif;cursor:pointer;white-space:nowrap;
}

/* ══════════════════════════════════════════
   TOAST
══════════════════════════════════════════ */
.toast{
  position:absolute;bottom:90px;left:50%;transform:translateX(-50%) translateY(16px);
  background:#1A1A1A;color:#fff;padding:10px 18px;border-radius:10px;
  font-size:13px;font-weight:600;font-family:'Baloo 2',sans-serif;
  opacity:0;transition:all .3s;pointer-events:none;white-space:nowrap;z-index:100;
}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
</style>
</head>
<body>

<div class="phone-frame">

  <!-- STATUS BAR -->
  <div class="status-bar">
    <div class="sb-left">
      <div class="status-dot"></div>
      BharatBricks 🌿
    </div>
    <div class="sb-right" id="clock">10:42 AM</div>
  </div>

  <!-- ════════ MAIN VIEW ════════ -->
  <div class="view active" id="view-main">
    <div class="main-header">
      <div class="greeting">Namaste, Sharma Ji 🙏</div>
      <div class="shop-name">Sharma Ji Kirana Store</div>
      <div class="stats-row">
        <div class="stat-pill"><div class="sv" id="today-sales">₹0</div><div class="sl">Aaj Ki Bikri</div></div>
        <div class="stat-pill"><div class="sv" id="today-orders">0</div><div class="sl">Orders Aaj</div></div>
        <div class="stat-pill"><div class="sv">Indore</div><div class="sl">Location</div></div>
      </div>
    </div>

    <div class="action-buttons">
      <button class="action-btn btn-log" onclick="showView('log')">
        <span class="ab-icon">🧾</span>
        Bikri Log Karo
      </button>
      <button class="action-btn btn-ai" onclick="showView('ai')">
        <span class="ab-icon">✨</span>
        AI Dashboard
      </button>
    </div>

    <div class="section-label">
      Aaj Ki Bikri Log
      <span onclick="clearOrders()">Saaf Karo</span>
    </div>

    <div class="orders-list" id="orders-list">
      <div class="order-empty">
        <div class="oe-icon">🛒</div>
        <p>Koi order abhi tak nahi</p>
        <small>Bikri Log karo button se shuru karein</small>
      </div>
    </div>
  </div>

  <!-- ════════ LOG SALE VIEW ════════ -->
  <div class="view" id="view-log">
    <div class="log-header">
      <button class="back-btn" onclick="showView('main')">←</button>
      <div class="log-header-text">
        <h3>Bikri Log Karo</h3>
        <p>Item add karo, phir confirm karo</p>
      </div>
    </div>

    <div class="log-search-area">
      <div class="search-input-wrap">
        <span class="search-icon">🔍</span>
        <input type="text" id="search-input" placeholder="Product ka naam type karo..."
          oninput="filterProducts(this.value)" autocomplete="off">
      </div>
    </div>

    <div class="quick-items">
      <div class="qi-label">Jaldi Add Karo</div>
      <div class="qi-scroll" id="quick-scroll"></div>
    </div>

    <div class="cart-area">
      <div class="cart-label">Cart / Thela</div>
      <div id="cart-list"></div>
    </div>

    <div class="log-footer">
      <div class="total-row">
        <span class="total-label">Kul Rakam (Total)</span>
        <span class="total-amt" id="cart-total">₹0</span>
      </div>
      <button class="confirm-btn" id="confirm-btn" onclick="showView('bill')" disabled>
        🧾 Bill Banao →
      </button>
    </div>
  </div>

  <!-- ════════ BILL VIEW ════════ -->
  <div class="view" id="view-bill">
    <div class="bill-header">
      <button class="back-btn" onclick="showView('log')">←</button>
      <div class="log-header-text">
        <h3>Bill / Raseed</h3>
        <p>Check karo aur confirm karo</p>
      </div>
    </div>

    <div class="bill-scroll">
      <div class="bill-card">
        <div class="bill-top">
          <div class="bill-oid" id="bill-oid">Order #—</div>
          <div class="bill-shop">Sharma Ji Kirana Store</div>
          <div class="bill-time" id="bill-time">—</div>
        </div>
        <div class="bill-items" id="bill-items-list"></div>
        <div class="bill-total-row">
          <span class="bt-label">Kul Rakam</span>
          <span class="bt-amt" id="bill-total-display">₹0</span>
        </div>
      </div>

      <div class="payment-section">
        <div class="ps-label">Payment Tarika</div>
        <div class="pay-options">
          <div class="pay-opt active" id="pay-cash" onclick="selectPay('cash')">
            <div class="po-icon">💵</div>
            <div class="po-label">Cash</div>
          </div>
          <div class="pay-opt" id="pay-upi" onclick="selectPay('upi')">
            <div class="po-icon">📱</div>
            <div class="po-label">UPI</div>
          </div>
          <div class="pay-opt" id="pay-credit" onclick="selectPay('credit')">
            <div class="po-icon">📒</div>
            <div class="po-label">Udhaar</div>
          </div>
        </div>
      </div>

      <button class="paid-btn" onclick="confirmPayment()">
        ✅ Paisa Mila — Order Confirm Karo
      </button>
    </div>
  </div>

  <!-- ════════ AI DASHBOARD VIEW ════════ -->
  <div class="view" id="view-ai">
    <div class="ai-header">
      <div class="ai-header-top">
        <button class="ai-back" onclick="showView('main')">←</button>
        <div class="ai-title-wrap">
          <div class="ai-title">AI Insights ✨</div>
          <div class="ai-subtitle">Aapki dukan ke liye</div>
        </div>
        <div class="ai-tag"><div class="ai-tag-dot"></div><span>Live</span></div>
      </div>
      <div class="ai-summary-row">
        <div class="ai-sum-card"><div class="ai-sum-val">₹4,320</div><div class="ai-sum-label">Kal Ki Bikri</div></div>
        <div class="ai-sum-card"><div class="ai-sum-val">↑ 12%</div><div class="ai-sum-label">Is Hafte</div></div>
        <div class="ai-sum-card"><div class="ai-sum-val">3 🚨</div><div class="ai-sum-label">Urgent Items</div></div>
      </div>
    </div>

    <div class="ai-tabs">
      <div class="ai-tab active" id="tab-urgent" onclick="switchTab('urgent')"><span class="tab-icon">🚨</span>Urgent</div>
      <div class="ai-tab" id="tab-weekly" onclick="switchTab('weekly')"><span class="tab-icon">📅</span>Hafta</div>
      <div class="ai-tab" id="tab-seasonal" onclick="switchTab('seasonal')"><span class="tab-icon">🌤️</span>Mausam</div>
      <div class="ai-tab" id="tab-summary" onclick="switchTab('summary')"><span class="tab-icon">📊</span>Sarvekshan</div>
    </div>

    <div class="ai-content" id="ai-content"></div>
  </div>

  <!-- TOAST -->
  <div class="toast" id="toast"></div>
</div>

<script>
// ── State ──────────────────────────────────────────────────────────────────
let cart = {};
let orders = [];
let orderCounter = 1001;
let selectedPayment = 'cash';
let currentBillId = null;

// ── Product Catalog (demo) ─────────────────────────────────────────────────
const PRODUCTS = [
  {id:'p1', name:'Aata (5kg)', emoji:'🌾', price:180, unit:'bag'},
  {id:'p2', name:'Maggi Noodles', emoji:'🍜', price:14, unit:'pkt'},
  {id:'p3', name:'Tata Salt (1kg)', emoji:'🧂', price:24, unit:'pkt'},
  {id:'p4', name:'Surf Excel (500g)', emoji:'🫧', price:58, unit:'pkt'},
  {id:'p5', name:'Amul Butter', emoji:'🧈', price:58, unit:'pcs'},
  {id:'p6', name:'Parle-G Biscuit', emoji:'🍪', price:10, unit:'pkt'},
  {id:'p7', name:'Dettol Soap', emoji:'🧼', price:38, unit:'pcs'},
  {id:'p8', name:'Tata Tea (250g)', emoji:'🍵', price:90, unit:'pkt'},
  {id:'p9', name:'Sunflower Oil (1L)', emoji:'🫙', price:140, unit:'btl'},
  {id:'p10',name:'Good Day Biscuit', emoji:'🍪', price:30, unit:'pkt'},
  {id:'p11',name:'Colgate (100ml)', emoji:'🪥', price:60, unit:'tube'},
  {id:'p12',name:'Rice (5kg)', emoji:'🍚', price:220, unit:'bag'},
];

// ── View switching ─────────────────────────────────────────────────────────
function showView(id) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById('view-' + id).classList.add('active');
  if (id === 'log') renderLog();
  if (id === 'bill') renderBill();
  if (id === 'ai') renderAI('urgent');
}

// ── Clock ──────────────────────────────────────────────────────────────────
function updateClock() {
  const now = new Date();
  let h = now.getHours(), m = now.getMinutes();
  const ampm = h >= 12 ? 'PM' : 'AM';
  h = h % 12 || 12;
  document.getElementById('clock').textContent = h + ':' + String(m).padStart(2,'0') + ' ' + ampm;
}
setInterval(updateClock, 10000);
updateClock();

// ── LOG SALE ──────────────────────────────────────────────────────────────
function renderLog() {
  // Quick chips
  const qscroll = document.getElementById('quick-scroll');
  qscroll.innerHTML = PRODUCTS.slice(0, 8).map(p =>
    `<div class="qi-chip" onclick="addToCart('${p.id}')">${p.emoji} ${p.name.split(' ')[0]}</div>`
  ).join('');
  renderCart();
}

function filterProducts(q) {
  const qscroll = document.getElementById('quick-scroll');
  const filtered = q
    ? PRODUCTS.filter(p => p.name.toLowerCase().includes(q.toLowerCase()))
    : PRODUCTS.slice(0,8);
  qscroll.innerHTML = filtered.length
    ? filtered.map(p => `<div class="qi-chip" onclick="addToCart('${p.id}')">${p.emoji} ${p.name}</div>`).join('')
    : `<div class="qi-chip" style="color:var(--muted)">Koi result nahi</div>`;
}

function addToCart(pid) {
  const p = PRODUCTS.find(x => x.id === pid);
  if (!p) return;
  if (cart[pid]) cart[pid].qty++;
  else cart[pid] = { ...p, qty: 1 };
  showToast(p.emoji + ' ' + p.name.split(' ')[0] + ' add hua!');
  renderCart();
}

function changeQty(pid, delta) {
  if (!cart[pid]) return;
  cart[pid].qty += delta;
  if (cart[pid].qty <= 0) delete cart[pid];
  renderCart();
}

function renderCart() {
  const list = document.getElementById('cart-list');
  const keys = Object.keys(cart);
  if (!keys.length) {
    list.innerHTML = `<div class="cart-empty"><div class="ce-icon">🛒</div><p>Cart khali hai</p></div>`;
  } else {
    list.innerHTML = keys.map(pid => {
      const item = cart[pid];
      return `<div class="cart-item">
        <span style="font-size:18px">${item.emoji}</span>
        <div style="flex:1">
          <div class="ci-name">${item.name}</div>
          <div class="ci-price">₹${item.price} / ${item.unit}</div>
        </div>
        <div class="ci-qty">
          <button onclick="changeQty('${pid}',-1)">−</button>
          <span class="qty-val">${item.qty}</span>
          <button onclick="changeQty('${pid}',1)">+</button>
        </div>
        <button class="ci-del" onclick="changeQty('${pid}',-999)">🗑</button>
      </div>`;
    }).join('');
  }
  const total = Object.values(cart).reduce((s, i) => s + i.price * i.qty, 0);
  document.getElementById('cart-total').textContent = '₹' + total.toLocaleString('en-IN');
  document.getElementById('confirm-btn').disabled = !keys.length;
}

// ── BILL ──────────────────────────────────────────────────────────────────
function renderBill() {
  currentBillId = orderCounter;
  const now = new Date();
  const timeStr = now.toLocaleTimeString('en-IN', {hour:'2-digit', minute:'2-digit'}) + 
    ', ' + now.toLocaleDateString('en-IN');
  document.getElementById('bill-oid').textContent = 'Order #' + currentBillId;
  document.getElementById('bill-time').textContent = timeStr;

  const items = Object.values(cart);
  const total = items.reduce((s, i) => s + i.price * i.qty, 0);
  document.getElementById('bill-items-list').innerHTML = items.map(i =>
    `<div class="bill-item-row">
      <div><div class="bir-name">${i.emoji} ${i.name}</div><div class="bir-detail">${i.qty} × ₹${i.price}</div></div>
      <div class="bir-amt">₹${(i.price*i.qty).toLocaleString('en-IN')}</div>
    </div>`
  ).join('');
  document.getElementById('bill-total-display').textContent = '₹' + total.toLocaleString('en-IN');
}

function selectPay(mode) {
  selectedPayment = mode;
  ['cash','upi','credit'].forEach(m => document.getElementById('pay-'+m).classList.toggle('active', m === mode));
}

function confirmPayment() {
  const items = Object.values(cart);
  const total = items.reduce((s, i) => s + i.price * i.qty, 0);
  const order = {
    id: orderCounter++,
    time: new Date().toLocaleTimeString('en-IN', {hour:'2-digit', minute:'2-digit'}),
    total,
    items: items.length,
    payment: selectedPayment
  };
  orders.unshift(order);
  cart = {};

  // Update stats
  const allTotal = orders.reduce((s, o) => s + o.total, 0);
  document.getElementById('today-sales').textContent = '₹' + allTotal.toLocaleString('en-IN');
  document.getElementById('today-orders').textContent = orders.length;

  renderOrdersList();
  showView('main');
  showToast('✅ Order #' + order.id + ' confirm ho gaya!');
}

function renderOrdersList() {
  const list = document.getElementById('orders-list');
  if (!orders.length) {
    list.innerHTML = `<div class="order-empty"><div class="oe-icon">🛒</div><p>Koi order abhi tak nahi</p><small>Bikri Log karo button se shuru karein</small></div>`;
    return;
  }
  const payIcon = {cash:'💵', upi:'📱', credit:'📒'};
  list.innerHTML = orders.map(o =>
    `<div class="order-card">
      <div class="order-id-badge">#${o.id}</div>
      <div class="order-info">
        <div class="oi-top">
          <span class="oi-id">${o.items} item${o.items>1?'s':''} ${payIcon[o.payment]||''}</span>
          <span class="oi-amt">₹${o.total.toLocaleString('en-IN')}</span>
        </div>
        <div class="oi-sub">${o.time} • ${o.payment.charAt(0).toUpperCase()+o.payment.slice(1)}</div>
      </div>
    </div>`
  ).join('');
}

function clearOrders() {
  orders = [];
  document.getElementById('today-sales').textContent = '₹0';
  document.getElementById('today-orders').textContent = '0';
  renderOrdersList();
}

// ── AI DASHBOARD ──────────────────────────────────────────────────────────
const AI_TABS = ['urgent','weekly','seasonal','summary'];

function switchTab(tab) {
  AI_TABS.forEach(t => document.getElementById('tab-'+t).classList.toggle('active', t === tab));
  renderAI(tab);
}

function renderAI(tab) {
  const content = document.getElementById('ai-content');
  if (tab === 'urgent') content.innerHTML = renderUrgent();
  else if (tab === 'weekly') content.innerHTML = renderWeekly();
  else if (tab === 'seasonal') content.innerHTML = renderSeasonal();
  else content.innerHTML = renderSummary();
}

function renderUrgent() {
  return `
  <div class="notify-banner">
    <span class="nb-icon">🔔</span>
    <div class="nb-text">
      <h4>Daily Alert Chalaye?</h4>
      <p>Har roz subah 8 baje urgent stock alerts paayein</p>
    </div>
    <button class="nb-btn" onclick="showToast('Notifications ON!')">Haan</button>
  </div>

  <div class="insight-card">
    <div class="ic-header">
      <div class="ic-badge badge-urgent">🚨 Urgent</div>
      <div>
        <div class="ic-title">Abhi Yeh Order Karo</div>
        <div class="ic-sub">Stock khatam hone wala hai — 1-2 din mein</div>
      </div>
    </div>
    <div class="ic-body">
      ${[
        {name:'Aata (5kg)',stock:'2 bags bache',order:'10 bags',emoji:'🌾'},
        {name:'Tata Salt',stock:'3 pkt bache',order:'24 pkt',emoji:'🧂'},
        {name:'Maggi Noodles',stock:'8 pkt bache',order:'48 pkt',emoji:'🍜'},
      ].map(p => `
        <div class="product-row">
          <div class="pr-left">
            <div class="pr-icon urgent">${p.emoji}</div>
            <div><div class="pr-name">${p.name}</div><div class="pr-stock">Bacha: ${p.stock}</div></div>
          </div>
          <div class="pr-right">
            <div class="pr-action">Order Karo</div>
            <div class="pr-units">${p.order} suggested</div>
          </div>
        </div>`).join('')}
    </div>
  </div>

  <div class="insight-card">
    <div class="ic-header">
      <div class="ic-badge badge-summary">✅ Theek Hai</div>
      <div>
        <div class="ic-title">Yeh Items Sahi Hain</div>
        <div class="ic-sub">2+ hafte ka stock available</div>
      </div>
    </div>
    <div class="ic-body">
      ${[
        {name:'Parle-G',stock:'120 pkt',emoji:'🍪'},
        {name:'Dettol Soap',stock:'45 pcs',emoji:'🧼'},
        {name:'Rice (5kg)',stock:'18 bags',emoji:'🍚'},
      ].map(p => `
        <div class="product-row">
          <div class="pr-left">
            <div class="pr-icon ok">${p.emoji}</div>
            <div><div class="pr-name">${p.name}</div><div class="pr-stock">${p.stock} available</div></div>
          </div>
          <div class="pr-right"><div style="font-size:16px">✅</div></div>
        </div>`).join('')}
    </div>
  </div>`;
}

function renderWeekly() {
  return `
  <div class="insight-card">
    <div class="ic-header">
      <div class="ic-badge badge-weekly">📅 Hafta</div>
      <div>
        <div class="ic-title">Is Hafte Ka Order Plan</div>
        <div class="ic-sub">Pichle 4 haftey ke trends pe based</div>
      </div>
    </div>
    <div class="ic-body">
      ${[
        {name:'Aata (5kg)',order:'25 bags',price:'₹4,500',emoji:'🌾'},
        {name:'Sunflower Oil',order:'30 btl',price:'₹4,200',emoji:'🫙'},
        {name:'Surf Excel',order:'60 pkt',price:'₹3,480',emoji:'🫧'},
        {name:'Tata Tea',order:'20 pkt',price:'₹1,800',emoji:'🍵'},
        {name:'Colgate',order:'36 tube',price:'₹2,160',emoji:'🪥'},
      ].map(p => `
        <div class="product-row">
          <div class="pr-left">
            <div class="pr-icon ok">${p.emoji}</div>
            <div><div class="pr-name">${p.name}</div><div class="pr-stock">${p.order}</div></div>
          </div>
          <div class="pr-right">
            <div style="font-size:12px;font-weight:700;color:var(--ink);font-family:'Baloo 2',sans-serif">${p.price}</div>
          </div>
        </div>`).join('')}
      <div style="margin-top:10px;padding:10px;background:var(--weekly-bg);border-radius:8px;display:flex;justify-content:space-between">
        <span style="font-size:12px;font-weight:600;color:var(--weekly);font-family:'Baloo 2',sans-serif">Kul Estimate</span>
        <span style="font-size:14px;font-weight:800;color:var(--weekly);font-family:'Baloo 2',sans-serif">₹16,140</span>
      </div>
    </div>
  </div>

  <div class="insight-card">
    <div class="ic-header">
      <div class="ic-badge badge-weekly">📈 Trend</div>
      <div>
        <div class="ic-title">Top Selling Items</div>
        <div class="ic-sub">Pichle 7 din ki bikri</div>
      </div>
    </div>
    <div class="ic-body">
      <div class="chart-bar-row">
        ${[40,55,70,45,80,65,95].map((h,i) =>
          `<div class="bar-wrap">
            <div class="bar ${i===6?'today':''}" style="height:${h}%"></div>
            <div class="bar-label">${['Sat','Sun','Mon','Tue','Wed','Thu','Fri'][i]}</div>
          </div>`
        ).join('')}
      </div>
      <p style="font-size:11px;color:var(--muted);text-align:center">Aaj (Fri) sabse zyada bikri expect hai</p>
    </div>
  </div>`;
}

function renderSeasonal() {
  return `
  <div class="insight-card">
    <div class="ic-header">
      <div class="ic-badge badge-seasonal">🎉 Tyohar</div>
      <div>
        <div class="ic-title">Aane Wale Festivals</div>
        <div class="ic-sub">Abhi se stock taiyaar karo</div>
      </div>
    </div>
    <div class="ic-body">
      ${[
        {name:'Holi (March 25)',items:'Colours, Cold drinks, Pichkari, Mathri',emoji:'🎨'},
        {name:'Ram Navami (April 6)',items:'Puja samagri, Dry fruits, Mishri, Ghee',emoji:'🪔'},
        {name:'Akshaya Tritiya (April 30)',items:'Gold-plated pooja items, Dry fruits',emoji:'✨'},
      ].map(f => `
        <div style="padding:10px 0;border-bottom:1px solid var(--border2)">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
            <span style="font-size:16px">${f.emoji}</span>
            <span style="font-family:'Baloo 2',sans-serif;font-size:13px;font-weight:700;color:var(--ink)">${f.name}</span>
          </div>
          <p style="font-size:11px;color:var(--muted);line-height:1.5">${f.items}</p>
        </div>`).join('')}
    </div>
  </div>

  <div class="insight-card">
    <div class="ic-header">
      <div class="ic-badge badge-seasonal">🌤️ Mausam</div>
      <div>
        <div class="ic-title">Mausam Ke Hisaab Se</div>
        <div class="ic-sub">Indore — Garmi Shuru Hogi</div>
      </div>
    </div>
    <div class="ic-body">
      <p style="font-size:12px;color:var(--muted);margin-bottom:10px;line-height:1.5">April se June tak garmi ki wajah se ye products zyada bikenge:</p>
      <div style="display:flex;flex-wrap:wrap">
        <span class="trend-chip trend-up">↑ Cold drinks</span>
        <span class="trend-chip trend-up">↑ ORS / Electral</span>
        <span class="trend-chip trend-up">↑ Ice cream</span>
        <span class="trend-chip trend-up">↑ Nimbu pani</span>
        <span class="trend-chip trend-down">↓ Hot beverages</span>
        <span class="trend-chip trend-new">🆕 Cooler salt</span>
      </div>
    </div>
  </div>`;
}

function renderSummary() {
  return `
  <div class="insight-card">
    <div class="ic-header">
      <div class="ic-badge badge-summary">📊 Sarvekshan</div>
      <div>
        <div class="ic-title">Is Mahine Ka Sarvekshan</div>
        <div class="ic-sub">March 2025 — Aaj Tak</div>
      </div>
    </div>
    <div class="ic-body">
      ${[
        ['Kul Bikri', '₹1,18,440', ''],
        ['Daily Average', '₹3,948', ''],
        ['Top Product', 'Aata (5kg)', '🌾'],
        ['Peak Time', '6–8 PM', '⏰'],
        ['Avg Bill', '₹182', ''],
        ['UPI Payments', '38%', '📱'],
      ].map(([l,v,e]) => `
        <div class="product-row">
          <div class="pr-name" style="font-weight:500;font-family:'Noto Sans',sans-serif;font-size:12px;color:var(--muted)">${l}</div>
          <div style="font-family:'Baloo 2',sans-serif;font-size:13px;font-weight:700;color:var(--ink)">${e} ${v}</div>
        </div>`).join('')}
    </div>
  </div>

  <div class="insight-card">
    <div class="ic-header">
      <div class="ic-badge badge-summary">💡 Salah</div>
      <div>
        <div class="ic-title">AI Ki Salah</div>
        <div class="ic-sub">Aapki dukan ke liye personalized</div>
      </div>
    </div>
    <div class="ic-body">
      ${[
        {icon:'🕕',text:'Sham 6 baje se pehle staff ko busy rakhein — highest footfall time hai.'},
        {icon:'📱',text:'UPI adoption badhao — digital payments wale 22% zyada kharcha karte hain.'},
        {icon:'🌾',text:'Aata aur oil ek hi supplier se lo — combo discount milne ki zyada chance hai.'},
      ].map(s => `
        <div style="display:flex;gap:10px;padding:8px 0;border-bottom:1px solid var(--border2)">
          <span style="font-size:18px;flex-shrink:0">${s.icon}</span>
          <p style="font-size:12px;color:var(--ink2);line-height:1.5">${s.text}</p>
        </div>`).join('')}
    </div>
  </div>`;
}

// ── Toast ──────────────────────────────────────────────────────────────────
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2000);
}

// ── Init ──────────────────────────────────────────────────────────────────
renderOrdersList();
</script>
</body>
</html>"""
display(HTML(html_content))