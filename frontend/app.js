const API_URL = "http://localhost:3000";
let token = null;
let currentChat = null;

function showSection(id) {
  document.getElementById("auth-section").style.display = id === "auth" ? "block" : "none";
  document.getElementById("chat-section").style.display = id === "chat" ? "flex" : "none";
}

function login() {
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;
  fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ email, password }),
    credentials: 'include' 
  })
  .then(res => res.json())
  .then(data => {
    token = data.access_token;
    showSection("chat");
    loadChats();
  })
  .catch(console.error);
}

function signup() {
  const username = document.getElementById("signup-username").value;
  const email = document.getElementById("signup-email").value;
  const password = document.getElementById("signup-password").value;
  fetch(`${API_URL}/auth/signup`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ username, email, password }),
    credentials: 'include' 
  }).then(() => alert("Signup complete. Please log in."));
}

function logout() {
  token = null;
  currentChat = null;
  showSection("auth");
}

function createChat() {
  const name = document.getElementById("chat-name").value;
  fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({ chat_name: name }),
    credentials: 'include',
  })
  .then(res => res.json())
  .then(() => loadChats());
}

function loadChats() {
  fetch(`${API_URL}/api/chat/all`, {
    headers: { Authorization: `Bearer ${token}` },
    credentials: 'include',
  })
  .then(res => res.json())
  .then(chats => {
    const list = document.getElementById("chat-list");
    list.innerHTML = "";
    chats.forEach(chat => {
      const li = document.createElement("li");
      li.textContent = chat.chat_name;
      li.onclick = () => {
        currentChat = chat.chat_id;
        document.getElementById("chat-title").textContent = chat.chat_name;
        document.getElementById("summary").textContent = chat.summary || "";
        document.getElementById("messages").innerHTML = "";
      };
      list.appendChild(li);
    });
  });
}

function uploadFile() {
  const fileInput = document.getElementById("file-upload");
  const file = fileInput.files[0];
  if (!file || !currentChat) return;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("chat_id", currentChat);

  fetch(`${API_URL}/api/upload`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
    credentials: 'include' 
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("summary").textContent = data.summary;
  });
}

function sendQuestion() {
  const input = document.getElementById("question-input");
  const question = input.value;
  if (!question || !currentChat) return;

  const ws = new WebSocket(`ws://localhost:3000/ws`);
  ws.onopen = () => {
    ws.send(JSON.stringify({
      type: "question",
      chat_id: currentChat,
      question: question,
    }));
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "answer_chunk") {
      const div = document.createElement("div");
      div.textContent = "AI: " + data.content;
      document.getElementById("messages").appendChild(div);
    }
  };

  const userMsg = document.createElement("div");
  userMsg.textContent = "You: " + question;
  document.getElementById("messages").appendChild(userMsg);
  input.value = "";
}
