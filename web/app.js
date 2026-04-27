/* Ariyan Bot — Premium Dashboard */
const D = window.__DASH_DATA__ || {};
let view = 'home';
let page = 'overview';
let features = {};
const gid = D.guildId || '';
const BOT = (D.botUser||'ARIYAN').toUpperCase();

// Configs
const automodItems=[
	{db:'antiInviteOn',t:'Anti-Invites',d:'Block Discord invite links'},
	{db:'antiLinkOn',t:'Anti-Links',d:'Block all external links'},
	{db:'antiSpamOn',t:'Anti-Spam',d:'Detect and prevent spam'},
	{db:'antiBadwordOn',t:'Anti-Badwords',d:'Filter inappropriate language'},
	{db:'antiMentionOn',t:'Anti-Mention Spam',d:'Prevent excessive mentions'},
	{db:'antiAllCapsOn',t:'Anti-All Caps',d:'Block excessive capitals'},
	{db:'antiEmojiSpamOn',t:'Anti-Emoji Spam',d:'Prevent emoji spam'},
	{db:'antiNukeOn',t:'Anti-Nuke',d:'Protect server from nuking attacks'},
];
const featureItems=[
	{db:'automodOn',t:'Automod',d:'Anti-spam & moderation system'},
	{db:'antinukeOn',t:'Anti-Nuke System',d:'Advanced server protection'},
	{db:'welcomeOn',t:'Welcome System',d:'Greet new members'},
	{db:'ticketOn',t:'Ticket System',d:'Support ticket management'},
	{db:'loggingOn',t:'Logging',d:'Server audit logging'},
	{db:'musicOn',t:'Music System',d:'Play music in voice channels'},
	{db:'aiOn',t:'AI Chatbot',d:'Hindi girl AI assistant'},
];
const settCards=[
	{icon:'🔘',t:'Feature Toggle',s:'Enable/disable features',d:'Quickly enable or disable bot features.',bg:'bg-blue',pg:'ftoggle'},
	{icon:'🛡️',t:'Automod',s:'Anti-spam & moderation',d:'Configure anti-spam, bad words, and moderation.',bg:'bg-cyan',pg:'automod'},
	{icon:'🤖',t:'AI Chatbot',s:'Smart conversations',d:'Configure AI personality and chat settings.',bg:'bg-purple'},
	{icon:'👋',t:'Welcome System',s:'Member greetings',d:'Configure welcome messages and autoroles.',bg:'bg-green'},
	{icon:'🎵',t:'Music System',s:'Play & queue songs',d:'Music player with queue and controls.',bg:'bg-pink'},
	{icon:'🎫',t:'Ticket System',s:'Support tickets',d:'Ticket categories and staff management.',bg:'bg-orange'},
];
const landFeats=[
	{icon:'🛡️',t:'Advanced Anti-Nuke',d:'Military-grade protection against server nuking, mass bans, and channel deletion with instant lockdown.'},
	{icon:'🤖',t:'AI Girl Chatbot',d:'Smart Hindi AI chatbot with cute girl personality. Sweet, caring, and can roast too! 💕'},
	{icon:'✅',t:'Intelligent Automod',d:'Smart content filtering with anti-spam, anti-links, badword detection, and configurable thresholds.'},
	{icon:'🎵',t:'Music System',d:'High quality music playback with queue management, filters, and playlist support.'},
	{icon:'🎫',t:'Ticket System',d:'Professional support tickets with transcripts, staff roles, and custom categories.'},
	{icon:'⚡',t:'350+ Commands',d:'Moderation, fun, games, economy, utility, embeds, AFK, sticky messages, and much more.'},
];

// API
async function loadF(){if(!gid)return;try{const r=await fetch(`/api/dashboard/features/${gid}`);const d=await r.json();if(d.success){features=d.features;rPage();}}catch(e){}}
async function togF(f,v){if(!gid)return;features[f]=v;rPage();try{const r=await fetch(`/api/dashboard/toggle/${gid}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({feature:f,value:v})});const d=await r.json();if(!d.success){features[f]=!v;rPage();}}catch(e){features[f]=!v;rPage();}}
function initSock(){if(typeof io==='undefined')return;const s=io();if(gid)s.emit('join_guild',gid);s.on('feature_toggle',d=>{features[d.feature]=d.value;rPage();})}

// Nav
function goHome(){view='home';render();}
function goDash(){view='login';render();}
function enterDash(){view='dash';page='overview';loadF();render();}
function goPremium(){view='premium';render();}
function navTo(p){page=p;rPage();}
function togSub(){document.getElementById('sb-sub')?.classList.toggle('open');document.getElementById('sb-tog')?.classList.toggle('open');}
function tBtn(k){return `<button class="toggle ${features[k]?'on':''}" data-f="${k}"></button>`}
function bindT(){document.querySelectorAll('.toggle[data-f]').forEach(el=>{el.onclick=()=>togF(el.dataset.f,!features[el.dataset.f])})}

function render(){const r=document.getElementById('app');if(view==='home')r.innerHTML=homeHTML();else if(view==='login')r.innerHTML=loginHTML();else if(view==='premium')r.innerHTML=premiumHTML();else{r.innerHTML=dashHTML();rPage();}}
function rPage(){const c=document.getElementById('dash-c');if(!c)return;const m={overview:overviewHTML,settings:settingsHTML,ftoggle:ftoggleHTML,automod:automodHTML};c.innerHTML=(m[page]||overviewHTML)();bindT();document.querySelectorAll('.sb-item[data-p]').forEach(e=>e.classList.remove('active'));document.querySelector(`[data-p="${page}"]`)?.classList.add('active');}

/* ===== LOGIN GATE PAGE ===== */
function loginHTML(){
return `<div class="login-page">
	<div class="login-card">
		<div class="login-avatar"><img src="${D.avatar}" onerror="this.style.display='none'" alt=""></div>
		<div class="login-badge">SECURE ACCESS</div>
		<h1 class="login-title"><span class="login-white">ARIYAN</span> <span class="login-purple">BOT</span></h1>
		<div class="login-version">V2.0 NEURAL CORE</div>
		<a class="login-btn" href="https://discord.com/oauth2/authorize?client_id=${D.botId}&scope=bot%20applications.commands&permissions=8" target="_blank"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" style="opacity:.8"><circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/><line x1="12" y1="2" x2="12" y2="22" stroke="currentColor" stroke-width="1.5"/><line x1="2" y1="12" x2="22" y2="12" stroke="currentColor" stroke-width="1.5"/></svg> Add Ariyan to Server</a>

		<a class="login-btn-secondary" href="${D.supportServer}" target="_blank">💬 Join Support Server</a>

		<p class="login-info">By authenticating, you establish a secure link<br>with the <strong>Ariyan</strong> Bot Network.<br>Made with 💖 by Ariyan</p>
	</div>
</div>`;}


/* ===== LANDING PAGE ===== */
function homeHTML(){
return `
<nav class="topnav">
	<div class="topnav-brand"><img src="${D.avatar}" onerror="this.style.display='none'" alt=""><span>ARIYAN<br>BOT</span></div>
	<div class="nav-pill"><div class="nav-center">
		<a href="#" class="active" onclick="goHome();return false">Home</a>
		<a href="#" onclick="goDash();return false">Dashboard</a>
		<a href="#stats">Status</a>
		<a href="#features">Features</a>
	</div></div>
	<button class="premium-pill" onclick="goPremium()">👑 Premium</button>
	<div class="lang-wrap" onclick="this.classList.toggle('open')">
		<div class="nav-lang"><span class="lang-flag">🟢</span> <span class="lang-code">IN</span> ▾</div>
		<div class="lang-dropdown">
			<div class="lang-opt active"><span class="lang-c">IN</span> हिन्दी</div>
			<div class="lang-opt"><span class="lang-c">US</span> English</div>
			<div class="lang-opt"><span class="lang-c">BD</span> বাংলা</div>
		</div>
	</div>
	<div class="nav-user-icon" onclick="goDash()"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm0 2c-3.33 0-10 1.67-10 5v2h20v-2c0-3.33-6.67-5-10-5z"/></svg></div>
</nav>

<section class="hero">
	<h1><span class="white">SUPERCHARGE<br>YOUR SERVER</span><span class="purple">${BOT} BOT</span></h1>
	<p class="hero-desc">Ariyan Bot protects your community with advanced anti-nuke, intelligent automod, AI chatbot, music system, and 350+ powerful commands.</p>
	<div class="hero-buttons">
		<a class="btn-add" href="https://discord.com/oauth2/authorize?client_id=${D.botId}&scope=bot%20applications.commands&permissions=8" target="_blank">◉ Add to Discord</a>
		<a class="btn-support" href="${D.supportServer}" target="_blank">💬 Support Server</a>
	</div>
</section>

<div class="stat-strip">
	<div class="stat"><div class="num">${D.servers}</div><div class="label">Active Servers</div></div>
	<div class="stat"><div class="num">${Number(D.users).toLocaleString()}</div><div class="label">Global Users</div></div>
	<div class="stat"><div class="num">${D.commands||'350+'}</div><div class="label">Commands</div></div>
	<div class="stat"><div class="num">${D.cogs||93}</div><div class="label">Modules</div></div>
</div>

<div class="section" id="stats">
	<div class="section-header">
		<div><h2><span class="glow">LIVE STATISTICS</span></h2><div class="section-sub">Real-time bot performance metrics</div></div>
		<div class="live-pill"><span class="dot"></span>⚡ LIVE</div>
	</div>
	<div class="stats-grid">
		<div class="stat-card"><div class="icon-wrap">🏠</div><div class="val">${D.servers}</div><div class="lbl">Total Servers</div></div>
		<div class="stat-card"><div class="icon-wrap">👥</div><div class="val">${Number(D.users).toLocaleString()}</div><div class="lbl">Total Users</div></div>
		<div class="stat-card"><div class="icon-wrap">⚡</div><div class="val">${D.ping}ms</div><div class="lbl">API Latency</div></div>
		<div class="stat-card"><div class="icon-wrap">💾</div><div class="val">${D.ram}MB</div><div class="lbl">Memory Usage</div></div>
	</div>
</div>

<section class="features-bg" id="features">
	<div class="features-wrap">
		<div class="section-header"><div><h2><span class="glow">EVERYTHING YOU NEED</span></h2><div class="section-sub">Ariyan Bot packs 350+ commands and 93 modules into one powerful bot.</div></div></div>
		<div class="features-grid">${landFeats.map(f=>`<div class="feature-card"><div class="f-icon">${f.icon}</div><h3>${f.t}</h3><p>${f.d}</p></div>`).join('')}</div>
	</div>
</section>

<footer class="footer">© 2026 Ariyan Bot • Made with 💙 by <a href="https://discord.com/users/${D.founderId}" style="color:var(--primary);text-decoration:none">Ariyan</a> • <a href="${D.supportServer}" style="color:var(--text2);text-decoration:none">Support Server</a></footer>`;
}

/* ===== PREMIUM PAGE ===== */
function premiumHTML(){
const pFeats=[
	'Bypass all limits on Anti-Nuke protocols',
	'Advanced AI Girl Chatbot with custom personality',
	'Priority 24/7 technical support',
	'Exclusive premium badges and roles',
	'Unlimited music queue & filters',
	'Custom welcome banners & templates'
];
return `
<nav class="topnav">
	<div class="topnav-brand"><img src="${D.avatar}" onerror="this.style.display='none'" alt=""><span>ARIYAN<br>BOT</span></div>
	<div class="nav-pill"><div class="nav-center">
		<a href="#" onclick="goHome();return false">Home</a>
		<a href="#" onclick="goDash();return false">Dashboard</a>
		<a href="#" onclick="goHome();return false">Status</a>
		<a href="#" onclick="goHome();return false">Features</a>
	</div></div>
	<button class="premium-pill active" onclick="goPremium()">👑 Premium</button>
	<div class="nav-user-icon" onclick="goDash()"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm0 2c-3.33 0-10 1.67-10 5v2h20v-2c0-3.33-6.67-5-10-5z"/></svg></div>
</nav>

<section class="prem-page">
	<div class="prem-badge">👑 ELITE MEMBER</div>
	<h1 class="prem-title">UPGRADE YOUR <span class="prem-green">EXPERIENCE</span></h1>
	<p class="prem-sub">Unlock premium features and take your server to the next level with Ariyan Bot.</p>
	
	<div class="prem-card">
		<div class="prem-ribbon"><span>FREE FOREVER</span></div>
		<h2 class="prem-tier">ARIYAN PREMIUM</h2>
		<div class="prem-price"><span class="prem-dollar">$0</span> <span class="prem-period">/ LIFETIME</span></div>
		<div class="prem-features">${pFeats.map(f=>`<div class="prem-feat"><span class="prem-check">✓</span> ${f}</div>`).join('')}</div>
		<button class="prem-cta" onclick="goDash()">CLAIM PREMIUM ACCESS</button>
	</div>
	
	<p class="prem-staging">ALL PREMIUM FEATURES ARE CURRENTLY FREE FOR ALL USERS 💙</p>
</section>

<footer class="footer">© 2026 Ariyan Bot • Made with 💙 by Ariyan</footer>`;
}

/* ===== DASHBOARD PANEL ===== */
function dashHTML(){
return `<div class="dash-wrap">
	<div class="sidebar">
		<div class="sb-header"><div class="sb-icon"><img src="${D.avatar}" onerror="this.style.display='none'" alt=""></div><div class="sb-brand">Ariyan Bot</div></div>
		<div class="sb-label">Navigation</div>
		<div class="sb-item active" data-p="overview" onclick="navTo('overview')"><span class="si">📊</span>Dashboard</div>
		<div class="sb-item sb-toggle" id="sb-tog" onclick="togSub()"><span class="si">⚙️</span>Settings<span class="arrow">▼</span></div>
		<div class="sb-sub" id="sb-sub">
			<div class="sb-item" data-p="settings" onclick="navTo('settings')">Overview</div>
			<div class="sb-item" data-p="ftoggle" onclick="navTo('ftoggle')">Feature Toggle</div>
			<div class="sb-item" data-p="automod" onclick="navTo('automod')">Automod</div>
		</div>
		<div class="sb-bottom">
			<div class="sb-label">Links</div>
			<div class="sb-item" onclick="window.open('${D.supportServer}','_blank')"><span class="si">💬</span>Support Server</div>
			<div class="sb-item" onclick="window.open('https://discord.com/oauth2/authorize?client_id=${D.botId}&scope=bot%20applications.commands&permissions=8','_blank')"><span class="si">➕</span>Invite Bot</div>
			<div class="sb-item" onclick="goHome()"><span class="si">🏠</span>Back to Home</div>
		</div>
	</div>
	<div class="dash-main">
		<div class="topbar"><div class="topbar-right"><div class="topbar-user"><img src="${D.avatar}" onerror="this.style.display='none'" alt=""><span>Ariyan Bot</span></div></div></div>
		<div class="content-area" id="dash-c"></div>
	</div>
</div>`;}

function overviewHTML(){
return `<div class="page-wrap">
	<h1>📊 Dashboard</h1><div class="page-sub">Overview of Ariyan Bot's performance</div>
	<div class="stats-grid" style="margin-bottom:28px">
		<div class="stat-card"><div class="icon-wrap">🏠</div><div class="val">${D.servers}</div><div class="lbl">Servers</div></div>
		<div class="stat-card"><div class="icon-wrap">👥</div><div class="val">${D.users}</div><div class="lbl">Users</div></div>
		<div class="stat-card"><div class="icon-wrap">⚡</div><div class="val">${D.ping}ms</div><div class="lbl">Latency</div></div>
		<div class="stat-card"><div class="icon-wrap">⏱️</div><div class="val" style="font-size:1.4rem">${D.uptime}</div><div class="lbl">Uptime</div></div>
	</div>
	<div class="grid-2">
		<div class="card"><div class="card-title">🤖 Bot Information</div>
			<div class="info-row"><span class="k">Bot Name</span><span class="v">Ariyan Bot</span></div>
			<div class="info-row"><span class="k">Bot ID</span><span class="v">${D.botId}</span></div>
			<div class="info-row"><span class="k">Runtime</span><span class="v">${D.runtime}</span></div>
			<div class="info-row"><span class="k">Database</span><span class="v">SQLite (aiosqlite)</span></div>
			<div class="info-row"><span class="k">Modules</span><span class="v">${D.cogs} Cogs Loaded</span></div>
			<div class="info-row"><span class="k">Founder</span><span class="v">Ariyan</span></div>
		</div>
		<div class="card"><div class="card-title">⚙️ Configuration</div>
			<div class="info-row"><span class="k">Prefix</span><span class="v">${D.prefix}</span></div>
			<div class="info-row"><span class="k">Language</span><span class="v">Hindi / English</span></div>
			<div class="info-row"><span class="k">Timezone</span><span class="v">${D.timezone}</span></div>
			<div class="info-row"><span class="k">Slash Commands</span><span class="v">${D.slashCommands} Synced</span></div>
			<div class="info-row"><span class="k">AI Engine</span><span class="v">Groq (Llama 3.3)</span></div>
			<div class="info-row"><span class="k">Status</span><span class="v green">● Online</span></div>
		</div>
	</div>
</div>`;}

function settingsHTML(){
return `<div class="page-wrap">
	<h1>⚙️ Settings</h1><div class="page-sub">Configure Ariyan Bot modules</div>
	<span class="badge" style="float:right;margin-top:-40px">Server: ${D.guildName}</span>
	<div class="grid-3">${settCards.map(c=>`<div class="mod-card"><div class="mc-head"><div class="mc-icon ${c.bg}">${c.icon}</div><div><div class="mc-title">${c.t}</div><div class="mc-sub">${c.s}</div></div></div><div class="mc-desc">${c.d}</div><button class="cfg-btn" ${c.pg?`onclick="navTo('${c.pg}')"`:'disabled'}>⚙ Configure</button></div>`).join('')}</div>
</div>`;}

function ftoggleHTML(){
return `<div class="page-wrap">
	<h1>🔘 Feature Toggle</h1><div class="page-sub">Enable or disable Ariyan Bot features</div>
	<span class="back-link" onclick="navTo('settings')">← Back</span>
	<div class="card" style="margin-top:16px"><div class="toggle-list">${featureItems.map(f=>`<div class="toggle-row"><div><h3>${f.t}</h3><p>${f.d}</p></div>${tBtn(f.db)}</div>`).join('')}</div></div>
</div>`;}

function automodHTML(){
return `<div class="page-wrap">
	<h1>🛡️ Automod Settings</h1><div class="page-sub">Configure anti-spam and moderation</div>
	<span class="back-link" onclick="navTo('settings')">← Back</span>
	<div class="grid-2" style="margin-top:16px">
		<div class="card"><div class="card-title">⚙️ Feature Toggles</div><div class="toggle-list">${automodItems.map(f=>`<div class="toggle-row"><div><h3>${f.t}</h3><p>${f.d}</p></div>${tBtn(f.db)}</div>`).join('')}</div></div>
		<div class="card"><div class="card-title">📺 Channel Settings</div>
			<div style="margin-bottom:20px"><div class="field-label">Moderation Log Channel</div><select class="elite-select"><option>Select a channel...</option></select><div class="field-help">Channel where moderation actions will be logged</div></div>
			<div><div class="field-label">Audit Log Channel</div><select class="elite-select"><option>Select a channel...</option></select></div>
		</div>
	</div>
</div>`;}

document.addEventListener('DOMContentLoaded',()=>{render();initSock();});
