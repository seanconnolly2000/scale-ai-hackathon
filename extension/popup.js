const messageContainer = document.getElementById("message-container");
const userInput = document.getElementById("user-input");
const sendChat = document.getElementById("send-chat");
const analyzeButton = document.getElementById("analyze");

document.addEventListener("DOMContentLoaded", function () {
    sendChat.addEventListener("click", function () {
        const message = userInput.value.trim();
       //var message = document.documentElement.innerHTML;
        if (message !== "") {
            messageContainer.innerHTML += `<p><strong>You:</strong> ${message}</p>`;
            userInput.value = "";
            sendMessage(message);
        }
    });

    userInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            sendChat.click();
        }
    });

    function sendMessage(message) {
        chrome.runtime.sendMessage({ action: 'openpanel' });
         chrome.runtime.sendMessage({ action: "sendchat", message }, function (response) {
             if (response) {
                messageContainer.innerHTML += `<p><strong>AI:</strong> ${response.reply}</p>`;
            }
        });
    }

    analyzeButton.addEventListener("click", function () {
        chrome.runtime.sendMessage({ action: "analyze" }, function (response) {
            if (response) {
                messageContainer.innerHTML = `<p>${response.reply}</p>`;
            }
        });
    });


});
