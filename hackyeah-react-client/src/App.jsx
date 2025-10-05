import { useState, useEffect } from 'react'
import ChatList from './components/ChatList'
import ChatMessages from './components/ChatMessages'
import ChatInput from './components/ChatInput'
import { sendMessage } from './services/chatApi'
import './App.css'

function App() {
  const [chats, setChats] = useState([
    { id: 1, title: 'New journey', preview: '' }
  ])
  const [activeChat, setActiveChat] = useState(1)
  const [chatMessages, setChatMessages] = useState({
    1: []
  })
  const [isLoading, setIsLoading] = useState(false)
  const [darkMode, setDarkMode] = useState(true)

  const messages = chatMessages[activeChat] || []

  useEffect(() => {
    document.body.setAttribute('data-theme', darkMode ? 'dark' : 'light')
  }, [darkMode])

  const handleSend = async (text) => {
    const currentMessages = chatMessages[activeChat] || []

    // Add user message
    const userMessage = { id: currentMessages.length + 1, text, sender: 'user' }
    setChatMessages(prev => ({
      ...prev,
      [activeChat]: [...currentMessages, userMessage]
    }))

    // Add loading message
    const loadingMessage = { id: currentMessages.length + 2, text: '...', sender: 'bot', isLoading: true }
    setChatMessages(prev => ({
      ...prev,
      [activeChat]: [...prev[activeChat], loadingMessage]
    }))

    setIsLoading(true)
    try {
      // Call API and get response
      const response = await sendMessage(text)

      // Replace loading message with bot response
      setChatMessages(prev => ({
        ...prev,
        [activeChat]: prev[activeChat].slice(0, -1)
      }))
      const botMessage = { id: currentMessages.length + 2, text: response, sender: 'bot' }
      setChatMessages(prev => ({
        ...prev,
        [activeChat]: [...prev[activeChat], botMessage]
      }))
    } catch (error) {
      // Replace loading message with error
      setChatMessages(prev => ({
        ...prev,
        [activeChat]: prev[activeChat].slice(0, -1)
      }))
      const errorMessage = { id: currentMessages.length + 2, text: `Error: ${error.message}`, sender: 'bot' }
      setChatMessages(prev => ({
        ...prev,
        [activeChat]: [...prev[activeChat], errorMessage]
      }))
    } finally {
      setIsLoading(false)
    }
  }

  const handleNewChat = () => {
    const newId = chats.length + 1
    setChats([...chats, { id: newId, title: `New journey ${newId}`, preview: '' }])
    setActiveChat(newId)
    setChatMessages(prev => ({
      ...prev,
      [newId]: []
    }))
  }

  const handleDeleteChat = (chatId) => {
    const updatedChats = chats.filter(chat => chat.id !== chatId)
    setChats(updatedChats)

    // Remove messages for deleted chat
    setChatMessages(prev => {
      const newMessages = { ...prev }
      delete newMessages[chatId]
      return newMessages
    })

    // If deleting the active chat, switch to another chat
    if (activeChat === chatId) {
      if (updatedChats.length > 0) {
        setActiveChat(updatedChats[0].id)
      }
    }
  }

  const handleRenameChat = (chatId, newTitle) => {
    setChats(chats.map(chat =>
      chat.id === chatId ? { ...chat, title: newTitle } : chat
    ))
  }

  return (
    <div className="app-container">
      <ChatList
        chats={chats}
        activeChat={activeChat}
        onChatSelect={setActiveChat}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        onRenameChat={handleRenameChat}
        darkMode={darkMode}
        onToggleDarkMode={() => setDarkMode(!darkMode)}
      />
      <div className="chat-area">
        <ChatMessages messages={messages} isLoading={isLoading} />
        <ChatInput onSend={handleSend} isLoading={isLoading} />
      </div>
    </div>
  )
}

export default App
