const menuBtn = document.getElementById("menu-btn");
const sidebar = document.getElementById("sidebar");

if (menuBtn) {
    menuBtn.addEventListener("click", () => {
        sidebar.classList.toggle("show");
    });
}

const chatBox = document.getElementById("chat-box");

if (chatBox) {
    chatBox.scrollTop = chatBox.scrollHeight;
}

const chatForm = document.getElementById("chat-form");
const thinkingIndicator = document.getElementById("thinking-indicator");

if (chatForm) {

    chatForm.addEventListener("submit", () => {

        if (thinkingIndicator) {
            thinkingIndicator.style.display = "block";
        }

    });

}

const messageInput = document.getElementById("message-input");

if (messageInput && chatForm) {

    messageInput.addEventListener("keydown", function(event){

        if(event.key === "Enter" && !event.shiftKey){

            event.preventDefault();

            chatForm.submit();
        }

    });

}