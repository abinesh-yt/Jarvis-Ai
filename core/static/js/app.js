const menuBtn = document.getElementById("menu-btn");
const sidebar = document.getElementById("sidebar");

const micBtn = document.getElementById("mic-btn");
const messageInput = document.getElementById("message-input");

console.log("SpeechRecognition:", window.SpeechRecognition);
console.log("webkitSpeechRecognition:", window.webkitSpeechRecognition);


// Mobile Menu
if (menuBtn) {
    menuBtn.addEventListener("click", () => {
        sidebar.classList.toggle("show");
    });
}


// Auto Scroll
const chatBox = document.getElementById("chat-box");

if (chatBox) {
    chatBox.scrollTop = chatBox.scrollHeight;
}


// Thinking Indicator
const chatForm = document.getElementById("chat-form");
const thinkingIndicator = document.getElementById("thinking-indicator");

if (chatForm) {

    chatForm.addEventListener("submit", () => {

        if (thinkingIndicator) {
            thinkingIndicator.style.display = "block";
        }

    });

}


// Enter to Send
if (messageInput && chatForm) {

    messageInput.addEventListener("keydown", function(event) {

        if (event.key === "Enter" && !event.shiftKey) {

            event.preventDefault();

            chatForm.submit();

        }

    });

}


// Voice Input
const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

console.log("Speech:", SpeechRecognition);

if (SpeechRecognition && micBtn && messageInput) {

    const recognition = new SpeechRecognition();

    recognition.lang = "en-US";

    recognition.onstart = () => {
        alert("Listening...");
        console.log("Listening...");
    };

    recognition.onresult = (event) => {

        const text = event.results[0][0].transcript;

        console.log("Result:", text);

        messageInput.value = text;
    };

    recognition.onerror = (event) => {

        console.log("Error:", event.error);

        alert("Error: " + event.error);

    };

    recognition.onend = () => {
        console.log("Recognition ended");
    };

    micBtn.addEventListener("click", () => {

        console.log("Mic clicked");

        recognition.start();

    });

}