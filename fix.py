import re

with open('frontend/src/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix CSS
css_addition = """
        /* --- Sidebar Panels --- */
        .sidebar-panel { display: none; flex-direction: column; height: 100%; }
        .sidebar-panel.active { display: flex; }
        .search-container { padding: 12px 16px; border-bottom: 1px solid var(--border); }
        .search-input { width: 100%; padding: 8px 12px; background: var(--bg-base); border: 1px solid var(--border); color: var(--text-main); border-radius: 4px; font-family: var(--ui-font); outline: none; font-size: 13px; }
        .search-input:focus { border-color: var(--accent); }
        .search-results { flex: 1; overflow-y: auto; padding: 8px; }
        .search-result-item { padding: 6px 8px; border-radius: 4px; cursor: pointer; margin-bottom: 2px; display: flex; flex-direction: column; }
        .search-result-item:hover { background: var(--selection); }
        .search-result-name { font-size: 13px; font-weight: 500; display: flex; align-items: center; }
        .search-result-path { font-size: 11px; color: var(--text-muted); font-family: var(--code-font); }
        .settings-container { padding: 16px; flex: 1; overflow-y: auto; }
        .setting-group { margin-bottom: 20px; }
        .setting-label { display: block; font-size: 12px; font-weight: 600; color: var(--text-muted); margin-bottom: 8px; }
        .setting-control { width: 100%; padding: 8px; background: var(--bg-base); border: 1px solid var(--border); color: var(--text-main); border-radius: 4px; font-family: var(--ui-font); font-size: 13px; cursor: pointer; }
"""

spinner_fix = """
        .spinner {
            width: 32px; height: 32px;
            border: 3px solid var(--border);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { 100% { transform: rotate(360deg); } }
"""
content = re.sub(r'\.spinner\s*\{[^}]+\}\s*\.setting-control\s*\{[^}]+\}', spinner_fix, content)

content = content.replace('/* Scrollbar styling */', css_addition + '\n        /* Scrollbar styling */')


# 2. Update Activity Bar to add onclicks
activity_bar_new = """
        <nav class="activity-bar">
            <div class="activity-item active" title="Explorer" onclick="switchSidebarPanel('explorer')"><i class="ph-bold ph-files"></i></div>
            <div class="activity-item" title="Search" onclick="switchSidebarPanel('search')"><i class="ph-bold ph-magnifying-glass"></i></div>
            <div style="flex:1"></div>
            <div class="activity-item" title="Settings" onclick="switchSidebarPanel('settings')"><i class="ph-bold ph-gear"></i></div>
        </nav>
"""
content = re.sub(r'<nav class="activity-bar">.*?</nav>', activity_bar_new, content, flags=re.DOTALL)


# 3. Update Sidebar HTML
sidebar_new = """
        <aside class="sidebar">
            <div id="panel-explorer" class="sidebar-panel active">
                <div class="sidebar-header">
                    <span>Explorer</span>
                    <div class="sidebar-actions">
                        <button class="icon-btn" onclick="scanDirectory()" title="Open Folder"><i class="ph-bold ph-folder-open"></i></button>
                        <button class="icon-btn" onclick="createFile()" title="New File"><i class="ph-bold ph-file-plus"></i></button>
                        <button class="icon-btn" onclick="syncDirectory()" title="Refresh"><i class="ph-bold ph-arrows-clockwise"></i></button>
                    </div>
                </div>
                <div class="path-label-wrap">
                    <div id="path-label">No folder opened</div>
                </div>
                <div id="file-tree">
                    <div style="padding: 10px; font-size: 13px; color: var(--text-muted); text-align: center;">
                        Click the folder icon to open a project.
                    </div>
                </div>
            </div>

            <div id="panel-search" class="sidebar-panel">
                <div class="sidebar-header">
                    <span>Search</span>
                </div>
                <div class="search-container">
                    <input type="text" id="search-input" class="search-input" placeholder="Search files..." oninput="performSearch()">
                </div>
                <div id="search-results" class="search-results"></div>
            </div>

            <div id="panel-settings" class="sidebar-panel">
                <div class="sidebar-header">
                    <span>Settings</span>
                </div>
                <div class="settings-container">
                    <div class="setting-group">
                        <label class="setting-label">Theme</label>
                        <select class="setting-control" id="setting-theme" onchange="applySettings()">
                            <option value="light">Light</option>
                            <option value="dark">Dark</option>
                        </select>
                    </div>
                    <div class="setting-group">
                        <label class="setting-label">Editor Font Size</label>
                        <select class="setting-control" id="setting-fontsize" onchange="applySettings()">
                            <option value="12px">12px</option>
                            <option value="14px" selected>14px</option>
                            <option value="16px">16px</option>
                            <option value="18px">18px</option>
                        </select>
                    </div>
                    <div class="setting-group">
                        <label class="setting-label">Word Wrap</label>
                        <select class="setting-control" id="setting-wrap" onchange="applySettings()">
                            <option value="off">Off</option>
                            <option value="on">On</option>
                        </select>
                    </div>
                </div>
            </div>
        </aside>
"""
content = re.sub(r'<aside class="sidebar">.*?</aside>', sidebar_new, content, flags=re.DOTALL)

# 4. Add Javascript Logic
js_addition = """
        function switchSidebarPanel(panelId) {
            document.querySelectorAll('.activity-item').forEach(item => item.classList.remove('active'));
            document.querySelector(`.activity-item[title="${panelId.charAt(0).toUpperCase() + panelId.slice(1)}"]`).classList.add('active');
            document.querySelectorAll('.sidebar-panel').forEach(panel => panel.classList.remove('active'));
            document.getElementById(`panel-${panelId}`).classList.add('active');
            if (panelId === 'search') document.getElementById('search-input').focus();
        }

        function performSearch() {
            const query = document.getElementById('search-input').value.toLowerCase();
            const resultsContainer = document.getElementById('search-results');
            resultsContainer.innerHTML = '';
            if (!query || !treeData) return;

            const allFiles = [];
            function flatten(node) {
                if (!node.isDir) allFiles.push(node);
                if (node.children) node.children.forEach(flatten);
            }
            flatten(treeData);

            const matched = [];
            allFiles.forEach(file => {
                const nameLower = file.name.toLowerCase();
                let score = fuzzyScore(query, nameLower);
                if (score > 0) matched.push({ file, score });
            });

            matched.sort((a, b) => b.score - a.score);

            matched.forEach(m => {
                const el = document.createElement('div');
                el.className = 'search-result-item';
                let displayPath = m.file.path.replace(root, '').replace(/^\\\\|^\\//, '');
                if (!displayPath) displayPath = '/';
                el.innerHTML = `
                    <div class="search-result-name"><i class="ph-fill ph-file-html" style="margin-right:4px;"></i>${m.file.name}</div>
                    <div class="search-result-path">${displayPath}</div>
                `;
                el.onclick = () => {
                    openEditor(m.file.name, m.file.path);
                    switchSidebarPanel('explorer'); // go back to explorer
                };
                resultsContainer.appendChild(el);
            });
        }

        function fuzzyScore(query, target) {
            let qIdx = 0, tIdx = 0, score = 0, consecutive = 0;
            while (qIdx < query.length && tIdx < target.length) {
                if (query[qIdx] === target[tIdx]) {
                    score += 10 + (consecutive * 5);
                    consecutive++;
                    qIdx++;
                } else {
                    consecutive = 0;
                }
                tIdx++;
            }
            if (qIdx === query.length) {
                if (target.startsWith(query)) score += 50;
                score -= target.length;
                return score;
            }
            return 0;
        }

        function applySettings() {
            const theme = document.getElementById('setting-theme').value;
            const isDark = document.body.classList.contains('dark');
            if ((theme === 'dark' && !isDark) || (theme === 'light' && isDark)) toggleTheme();

            document.getElementById('code-area').style.fontSize = document.getElementById('setting-fontsize').value;
            document.getElementById('code-area').style.whiteSpace = document.getElementById('setting-wrap').value === 'on' ? 'pre-wrap' : 'pre';
        }
"""
content = content.replace('function toggleTheme() {', js_addition + '\n        function toggleTheme() {')

with open('frontend/src/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
