const menuBtn = document.getElementById("menu-btn");
const sidebar = document.getElementById("sidebar");
const closeBtn = document.getElementById("close-sidebar");

const micBtn = document.getElementById("mic-btn");
const messageInput = document.getElementById("message-input");

// ======================
// Sidebar
// ======================

if (menuBtn && sidebar) {


menuBtn.addEventListener("click", () => {

    sidebar.classList.add("show");

});


}

if (closeBtn && sidebar) {


closeBtn.addEventListener("click", () => {

    sidebar.classList.remove("show");

});


}

// ======================
// Auto Scroll
// ======================

const chatBox = document.getElementById("chat-box");

if (chatBox) {


chatBox.scrollTop = chatBox.scrollHeight;


}

// ======================
// Thinking Indicator
// ======================

const chatForm = document.getElementById("chat-form");
const thinkingIndicator =
document.getElementById("thinking-indicator");

if (chatForm) {


chatForm.addEventListener("submit", () => {

    if (thinkingIndicator) {

        thinkingIndicator.style.display = "block";

    }

});


}

// ======================
// Enter To Send
// ======================

if (messageInput && chatForm) {


messageInput.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            chatForm.submit();

        }

    }
);


}

// ======================
// Voice Input
// ======================

const SpeechRecognition =
window.SpeechRecognition ||
window.webkitSpeechRecognition;

if (
SpeechRecognition &&
micBtn &&
messageInput
) {


const recognition =
    new SpeechRecognition();

recognition.lang = "en-US";

recognition.onresult = (event) => {

    const text =
        event.results[0][0].transcript;

    messageInput.value = text;

};

recognition.onerror = (event) => {

    console.log(
        "Speech Recognition Error:",
        event.error
    );

};

micBtn.addEventListener(
    "click",
    () => {

        recognition.start();

    }
);


}

// ======================
// Voice Output
// ======================

const speakButtons =
document.querySelectorAll(".speak-btn");

function speakText(text) {


window.speechSynthesis.cancel();

text = text
    .replace(/```[\s\S]*?```/g, "")
    .replace(/`/g, "")
    .replace(/[#*_>|-]/g, "")
    .replace(/\n/g, " ")
    .replace(/\s+/g, " ")
    .trim();

const voices =
    window.speechSynthesis.getVoices();

const chunks =
    text.match(/.{1,200}(\s|$)/g);

if (!chunks) return;

let index = 0;

function speakChunk() {

    if (index >= chunks.length) {

        return;

    }

    const speech =
        new SpeechSynthesisUtterance(
            chunks[index]
        );

    speech.voice = voices.find(
        voice =>
            voice.name ===
            "Google UK English Female"
    );

    speech.lang = "en-US";
    speech.rate = 0.9;
    speech.pitch = 1;

    speech.onend = () => {

        index++;

        speakChunk();

    };

    window.speechSynthesis.speak(
        speech
    );

}

speakChunk();


}

speakButtons.forEach((button) => {


button.addEventListener(
    "click",
    () => {

        speakText(
            button.dataset.text
        );

    }
);


});
