// EdgeX Panel - Main JavaScript
class EdgeXPanel {
    constructor() {
        this.apiBase = '/api';
        this.refreshInterval = null;
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadStatus();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Generate Config Button
        const generateBtn = document.getElementById('generate-config');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.generateConfig());
        }

        // Regenerate UUID Button
        const regenerateBtn = document.getElementById('regenerate-uuid');
        if (regenerateBtn) {
            regenerateBtn.addEventListener('click', () => this.regenerateUUID());
        }

        // Copy Config Button
        const copyBtn = document.getElementById('copy-config');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => this.copyConfig());
        }

        // Form inputs
        document.querySelectorAll('.auto-save').forEach(input => {
            input.addEventListener('change', () => this.saveSettings());
        });
    }

    async loadStatus() {
        try {
            const response = await fetch(`${this.apiBase}/status`);
            const data = await response.json();
            this.updateStatusUI(data);
        } catch (error) {
            console.error('Error loading status:', error);
            this.showToast('Failed to load status', 'error');
        }
    }

    updateStatusUI(data) {
        // Update Xray status
        const xrayStatus = document.getElementById('xray-status');
        if (xrayStatus) {
            xrayStatus.textContent = data.xray ? 'Online' : 'Offline';
            xrayStatus.className = `value ${data.xray ? 'online' : 'offline'}`;
        }

        // Update uptime
        const uptime = document.getElementById('uptime');
        if (uptime && data.uptime) {
            uptime.textContent = this.formatUptime(data.uptime);
        }

        // Update active connections
        const connections = document.getElementById('active-connections');
        if (connections) {
            connections.textContent = data.connections || 0;
        }
    }

    async generateConfig() {
        const generateBtn = document.getElementById('generate-config');
        this.showLoading(generateBtn);

        const formData = {
            sni: document.getElementById('sni-input')?.value || 'cloudflare.com',
            host: document.getElementById('host-input')?.value || 'speed.cloudflare.com',
            ws_path: document.getElementById('ws-path-input')?.value || '/ws'
        };

        try {
            const response = await fetch(`${this.apiBase}/generate-config?` + new URLSearchParams(formData));
            const data = await response.json();

            if (data.status === 'success') {
                this.displayConfig(data.config);
                this.showToast('Configuration generated successfully!', 'success');
            } else {
                this.showToast('Failed to generate configuration', 'error');
            }
        } catch (error) {
            console.error('Error generating config:', error);
            this.showToast('Error generating configuration', 'error');
        } finally {
            this.hideLoading(generateBtn);
        }
    }

    async regenerateUUID() {
        const regenerateBtn = document.getElementById('regenerate-uuid');
        this.showLoading(regenerateBtn);

        try {
            const response = await fetch(`${this.apiBase}/admin/uuid/regenerate`, {
                method: 'POST'
            });
            const data = await response.json();
            
            document.getElementById('current-uuid').textContent = data.uuid;
            this.showToast('UUID regenerated successfully!', 'success');
        } catch (error) {
            console.error('Error regenerating UUID:', error);
            this.showToast('Error regenerating UUID', 'error');
        } finally {
            this.hideLoading(regenerateBtn);
        }
    }

    displayConfig(config) {
        // Display config link
        const configDisplay = document.getElementById('config-display');
        const configText = document.getElementById('config-text');
        
        if (configDisplay && configText) {
            configText.textContent = config.link;
            configDisplay.style.display = 'block';
            
            // Generate QR Code
            this.generateQRCode(config.link);
        }

        // Display JSON config
        const jsonDisplay = document.getElementById('json-config');
        if (jsonDisplay && config.json_config) {
            jsonDisplay.textContent = config.json_config;
        }
    }

    generateQRCode(content) {
        const qrContainer = document.getElementById('qrcode');
        if (qrContainer && typeof QRCode !== 'undefined') {
            qrContainer.innerHTML = '';
            new QRCode(qrContainer, {
                text: content,
                width: 256,
                height: 256,
                colorDark: '#1e293b',
                colorLight: '#ffffff',
                correctLevel: QRCode.CorrectLevel.H
            });
        }
    }

    async copyConfig() {
        const configText = document.getElementById('config-text')?.textContent;
        if (configText) {
            try {
                await navigator.clipboard.writeText(configText);
                this.showToast('Configuration copied to clipboard!', 'success');
            } catch (error) {
                // Fallback
                const textarea = document.createElement('textarea');
                textarea.value = configText;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                this.showToast('Configuration copied!', 'success');
            }
        }
    }

    async loadLogs() {
        try {
            const response = await fetch(`${this.apiBase}/logs`);
            const data = await response.json();
            
            const logDisplay = document.getElementById('log-display');
            if (logDisplay && data.logs) {
                logDisplay.innerHTML = data.logs.join('<br>');
                logDisplay.scrollTop = logDisplay.scrollHeight;
            }
        } catch (error) {
            console.error('Error loading logs:', error);
        }
    }

    showLoading(button) {
        if (button) {
            button.disabled = true;
            button.innerHTML = '<span class="spinner"></span> Processing...';
        }
    }

    hideLoading(button) {
        if (button) {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || button.textContent;
        }
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    formatUptime(seconds) {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        const parts = [];
        if (days > 0) parts.push(`${days}d`);
        if (hours > 0) parts.push(`${hours}h`);
        if (minutes > 0) parts.push(`${minutes}m`);
        
        return parts.join(' ') || 'Just started';
    }

    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            this.loadStatus();
            this.loadLogs();
        }, 10000); // Refresh every 10 seconds
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.edgexPanel = new EdgeXPanel();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.edgexPanel) {
        window.edgexPanel.stopAutoRefresh();
    }
});
