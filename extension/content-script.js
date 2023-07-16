// content.js
console.log('Extension Loading.');


chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    var url = window.location.href;
    var title = document.title;
    var body = document.documentElement.innerHTML;
    var doc = { 'url': url, 'title': title, 'body': body }
    sendResponse({ 'doc': doc });
    return true;
});

