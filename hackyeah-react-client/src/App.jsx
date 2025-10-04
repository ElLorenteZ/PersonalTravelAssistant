import { useState, useEffect } from 'react'
import ChatList from './components/ChatList'
import ChatMessages from './components/ChatMessages'
import ChatInput from './components/ChatInput'
import { sendMessage } from './services/chatApi'
import './App.css'

function App() {
  const [chats, setChats] = useState([
    { id: 1, title: 'Planning next trip', preview: 'Looking for recommendations...' }
  ])
  const [activeChat, setActiveChat] = useState(1)
  const [messages, setMessages] = useState([
    // { id: 1, text: 'Hello! I want to plan a trip to Paris', sender: 'user' },
    // { id: 2, text: 'I can help you with that! What would you like to know?', sender: 'bot' }
  ])
  const [isLoading, setIsLoading] = useState(false)
  const [darkMode, setDarkMode] = useState(true)

  useEffect(() => {
    document.body.setAttribute('data-theme', darkMode ? 'dark' : 'light')
  }, [darkMode])

  const handleSend = async (text) => {
    // Add user message
    const userMessage = { id: messages.length + 1, text, sender: 'user' }
    setMessages(prev => [...prev, userMessage])

    setIsLoading(true)
    try {
      // Call API and get response
      const response = await sendMessage(text)

      // Add bot response
      const botMessage = { id: messages.length + 2, text: response, sender: 'bot' }
      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      // Add error message
      const errorMessage = { id: messages.length + 2, text: `Error: ${error.message}`, sender: 'bot' }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleNewChat = () => {
    const newId = chats.length + 1
    setChats([...chats, { id: newId, title: `New Chat ${newId}`, preview: 'Start chatting...' }])
    setActiveChat(newId)
    setMessages([])
  }

  return (
    <div className="app-container">
      <ChatList
        chats={chats}
        activeChat={activeChat}
        onChatSelect={setActiveChat}
        onNewChat={handleNewChat}
        darkMode={darkMode}
        onToggleDarkMode={() => setDarkMode(!darkMode)}
      />
      <div className="chat-area">
        <ChatMessages messages={messages} />
        <ChatInput onSend={handleSend} isLoading={isLoading} />
      </div>
    </div>
  )
}

export default App
