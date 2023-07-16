const URL_ORIGIN = 'https://trakly.atlassian.net';

chrome.sidePanel
    .setPanelBehavior({ openPanelOnActionClick: true })
    .catch((error) => console.error(error));

chrome.tabs.onUpdated.addListener(async (tabId, info, tab) => {
    if (!tab.url) return;
    const url = new URL(tab.url);
    // Enables the side panel on google.com
    if (url.origin === URL_ORIGIN) {
        console.log(url.origin);
        await chrome.sidePanel.setOptions({
            tabId,
            path: 'sidepanel.html',
            enabled: true
        });
    } else {
        // Disables the side panel on all other sites
        await chrome.sidePanel.setOptions({
            tabId,
            enabled: false
        });
    }
});



chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {

    if (request.action === 'sendchat' || request.action === 'sendpage' || request.action === 'analyze') {
        fetch('http://127.0.0.1:5000/' + request.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: request.message })
        })
            .then(response => response.json())
            .then(response => {
                sendResponse({ reply: response.reply });
            })
            .catch(error => {
                sendResponse({ reply: "Error: " + error.message });
            });
    }

    return true;

});