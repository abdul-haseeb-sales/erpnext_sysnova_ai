$(document).ready(function() {
    // Only load if user is logged in
    if (frappe.session.user === "Guest") return;

    // Inject HTML for the chat widget
    const chatWidgetHTML = `
        <div id="sysnova-ai-widget">
            <div id="sysnova-ai-btn" class="sysnova-btn-circle">
                <i class="fa fa-comment"></i>
            </div>
            <div id="sysnova-ai-chat-box" class="sysnova-chat-hidden">
                <div class="sysnova-chat-header">
                    <span>Sysnova AI Assistant</span>
                    <button id="sysnova-ai-close-btn">&times;</button>
                </div>
                <div id="sysnova-ai-chat-body">
                    <div class="sysnova-message sysnova-bot-message">
                        Hello! I am Sysnova AI. I can help you search ERPNext database and find files. How can I assist you today?
                    </div>
                </div>
                <div class="sysnova-chat-input-area">
                    <input type="text" id="sysnova-ai-input" placeholder="Type your message..." />
                    <button id="sysnova-ai-send-btn"><i class="fa fa-paper-plane"></i></button>
                </div>
            </div>
        </div>
    `;

    $('body').append(chatWidgetHTML);

    // Toggle Chat Box
    $('#sysnova-ai-btn, #sysnova-ai-close-btn').click(function() {
        $('#sysnova-ai-chat-box').toggleClass('sysnova-chat-hidden');
    });

    // Send Message on Button Click
    $('#sysnova-ai-send-btn').click(function() {
        sendMessage();
    });

    // Send Message on Enter Key
    $('#sysnova-ai-input').keypress(function(e) {
        if (e.which == 13) {
            sendMessage();
        }
    });

    function sendMessage() {
        const inputField = $('#sysnova-ai-input');
        const message = inputField.val().trim();
        if (!message) return;

        // Append User Message
        appendMessage(message, 'user');
        inputField.val('');

        // Append Typing Indicator
        const typingId = appendTypingIndicator();

        // Call Frappe API
        frappe.call({
            method: "erpnext_sysnova_ai.api.chat_with_gemini",
            args: {
                message: message
            },
            callback: function(r) {
                removeTypingIndicator(typingId);
                if (!r.exc && r.message && r.message.status === 'success') {
                    // Gemini uses markdown, simple regex to format bold text (for basic rendering)
                    let replyText = r.message.reply.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                    appendMessage(replyText, 'bot');
                } else {
                    let errorMsg = r.message ? r.message.message : "Something went wrong.";
                    appendMessage("Error: " + errorMsg, 'bot', true);
                }
            }
        });
    }

    function appendMessage(text, sender, isError=false) {
        const chatBody = $('#sysnova-ai-chat-body');
        const msgClass = sender === 'user' ? 'sysnova-user-message' : 'sysnova-bot-message';
        const errorStyle = isError ? 'style="color: red;"' : '';
        
        chatBody.append(`<div class="sysnova-message ${msgClass}" ${errorStyle}>${text}</div>`);
        chatBody.scrollTop(chatBody[0].scrollHeight);
    }

    function appendTypingIndicator() {
        const id = 'typing-' + Date.now();
        $('#sysnova-ai-chat-body').append(`<div id="${id}" class="sysnova-message sysnova-bot-message"><em>Sysnova AI is thinking...</em></div>`);
        return id;
    }

    function removeTypingIndicator(id) {
        $(`#${id}`).remove();
    }
});
