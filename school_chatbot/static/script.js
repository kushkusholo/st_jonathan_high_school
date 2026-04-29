// Chat functions
async function sendMessage(message = null) {
    const userInput = document.getElementById('userInput');
    const chatbox = document.getElementById('chatbox');
    
    // Get message from input if not provided
    const msgText = message || userInput.value.trim();
    
    if (!msgText) return;
    
    // Add user message to chat
    addMessageToChat(msgText, 'user');
    userInput.value = '';
    
    // Show typing indicator
    const typingId = showTypingIndicator();
    
    try {
        // Send message to backend
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: msgText })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        if (response.ok) {
            // Add bot message to chat
            addMessageToChat(data.message, 'bot', data.category);
        } else {
            addMessageToChat('Sorry, there was an error processing your request. Please try again.', 'bot');
        }
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator(typingId);
        addMessageToChat('Sorry, I encountered an error. Please try again later.', 'bot');
    }
    
    // Scroll to bottom
    chatbox.scrollTop = chatbox.scrollHeight;
}

function addMessageToChat(message, sender, category = null) {
    const chatbox = document.getElementById('chatbox');
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    // Create content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Parse markdown-like formatting (bullet points, bold, etc.)
    const formattedMessage = message
        .split('\n')
        .map(line => {
            // Bold text enclosed in **
            line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            // Italic text enclosed in __
            line = line.replace(/__(.*?)__/g, '<em>$1</em>');
            return line;
        })
        .join('<br>');
    
    contentDiv.innerHTML = formattedMessage;
    
    // Add category badge if provided
    if (category && category !== 'N/A') {
        const categoryBadge = document.createElement('div');
        categoryBadge.className = 'message-category';
        categoryBadge.textContent = `📌 ${category}`;
        contentDiv.appendChild(categoryBadge);
    }
    
    // Add timestamp
    const timestamp = document.createElement('span');
    timestamp.className = 'timestamp';
    timestamp.textContent = getCurrentTime();
    
    // Append elements
    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timestamp);
    chatbox.appendChild(messageDiv);
    
    // Scroll to bottom
    chatbox.scrollTop = chatbox.scrollHeight;
}

function showTypingIndicator() {
    const chatbox = document.getElementById('chatbox');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.id = 'typingIndicator';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content typing-indicator';
    contentDiv.innerHTML = '<span></span><span></span><span></span>';
    
    messageDiv.appendChild(contentDiv);
    chatbox.appendChild(messageDiv);
    
    chatbox.scrollTop = chatbox.scrollHeight;
    
    return 'typingIndicator';
}

function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
    });
}

// Form submission
document.getElementById('chatForm').addEventListener('submit', (e) => {
    e.preventDefault();
    sendMessage();
});

// Allow Enter key to send message (Shift+Enter for new line)
document.getElementById('userInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Clear chat function
function clearChat() {
    const chatbox = document.getElementById('chatbox');
    chatbox.innerHTML = `
        <div class="message bot-message welcome-message">
            <div class="message-content">
                <p><strong>Welcome to St. Jonathan High School!</strong></p>
                <p>I'm your school assistant, ready to help parents and guardians with information about admissions, fees, academic programs, facilities, and more.</p>
                <p>Feel free to ask any questions about our school. What would you like to know?</p>
            </div>
            <span class="timestamp">Just now</span>
        </div>
    `;
    document.getElementById('userInput').focus();
}

// View all FAQs
async function viewFAQs() {
    const modal = document.getElementById('faqModal');
    const faqList = document.getElementById('faqList');
    
    try {
        const response = await fetch('/api/faqs');
        const faqs = await response.json();
        
        // Clear previous FAQs
        faqList.innerHTML = '';
        
        // Add FAQs to modal
        faqs.forEach((faq, index) => {
            const faqItem = document.createElement('div');
            faqItem.className = 'faq-item';
            
            const categoryBadge = document.createElement('span');
            categoryBadge.className = 'faq-category';
            categoryBadge.textContent = faq.category;
            
            const question = document.createElement('h4');
            question.textContent = faq.question;
            
            const answer = document.createElement('p');
            // Format the answer (replace newlines)
            const formattedAnswer = faq.answer
                .replace(/\n/g, '<br>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            answer.innerHTML = formattedAnswer;
            
            faqItem.appendChild(categoryBadge);
            faqItem.appendChild(question);
            faqItem.appendChild(answer);
            
            // Make FAQ clickable to chat
            faqItem.style.cursor = 'pointer';
            faqItem.addEventListener('click', () => {
                sendMessage(faq.question);
                closeFAQs();
            });
            
            faqList.appendChild(faqItem);
        });
        
        // Show modal
        modal.style.display = 'block';
    } catch (error) {
        console.error('Error loading FAQs:', error);
        faqList.innerHTML = '<p>Error loading FAQs. Please try again.</p>';
    }
}

// Close FAQs modal
function closeFAQs() {
    const modal = document.getElementById('faqModal');
    modal.style.display = 'none';
}

// Close modal when clicking outside
window.addEventListener('click', (event) => {
    const modal = document.getElementById('faqModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});

// Focus input on page load
window.addEventListener('load', () => {
    document.getElementById('userInput').focus();
});

// Toggle info panel on mobile
function toggleInfoPanel() {
    const panel = document.getElementById('infoPanel');
    const toggleBtn = document.getElementById('togglePanel');
    
    if (panel.classList.contains('hidden')) {
        panel.classList.remove('hidden');
        toggleBtn.textContent = '✕';
    } else {
        panel.classList.add('hidden');
        toggleBtn.textContent = '☰';
    }
}

// Add some example quick questions
const quickQuestions = [
    'What are the admission requirements?',
    'What is the school fee structure?',
    'When are the school holidays?',
    'What subjects are offered?',
    'Does the school provide boarding?',
    'What extracurricular activities are available?',
    'What is the school\'s contact information?',
    'Does the school offer scholarships?'
];

// Keyboard shortcuts help
document.addEventListener('keydown', (e) => {
    // Ctrl+? or Cmd+? to show help
    if ((e.ctrlKey || e.metaKey) && e.key === '?') {
        e.preventDefault();
        alert(`
Keyboard Shortcuts:
- Enter: Send message
- Shift+Enter: New line
- Click suggestions: Send preset question
- View All FAQs: See all questions and answers

Visit St. Jonathan High School
📞 +256325516717
📍 Jinja-Kampala Highway, Kampala
        `);
    }
});

// Log page visit
console.log('St. Jonathan High School Parent Portal - Chatbot loaded successfully');
console.log('Available commands: sendMessage(), clearChat(), viewFAQs()');
