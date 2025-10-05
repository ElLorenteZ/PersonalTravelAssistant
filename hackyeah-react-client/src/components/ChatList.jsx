import { useState } from 'react'
import './ChatList.css'

function ChatList({ chats, activeChat, onChatSelect, onNewChat, onDeleteChat, onRenameChat, darkMode, onToggleDarkMode }) {
  const [editingId, setEditingId] = useState(null)
  const [editTitle, setEditTitle] = useState('')

  const handleDoubleClick = (chat) => {
    setEditingId(chat.id)
    setEditTitle(chat.title)
  }

  const handleSaveTitle = (chatId) => {
    if (editTitle.trim()) {
      onRenameChat(chatId, editTitle.trim())
    }
    setEditingId(null)
  }

  const handleKeyDown = (e, chatId) => {
    if (e.key === 'Enter') {
      handleSaveTitle(chatId)
    } else if (e.key === 'Escape') {
      setEditingId(null)
    }
  }

  return (
    <div className="chat-list">
      <div className="chat-list-header">
        <h2>Travel Log</h2>
        <div className="header-buttons">
          <div className="theme-toggle" onClick={onToggleDarkMode}>
            <div className={`toggle-slider ${darkMode ? 'dark' : 'light'}`}>
              {darkMode ? (
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M13 7.5c-.5 3-3 5.5-6.5 5.5C3 13 0 10 0 6.5 0 3.3 2.3.5 5.5 0c-2 1-3 3-3 5 0 3 2.5 5.5 5.5 5.5 2 0 3.7-1 5-2.5z"
                        fill="currentColor"/>
                </svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <circle cx="8" cy="8" r="3" fill="currentColor"/>
                  <path d="M8 1v2M8 13v2M15 8h-2M3 8H1M12.5 12.5l-1.4-1.4M4.9 4.9L3.5 3.5M12.5 3.5l-1.4 1.4M4.9 11.1l-1.4 1.4"
                        stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                </svg>
              )}
            </div>
          </div>
          <button className="new-chat-btn" onClick={onNewChat}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 3v10M3 8h10" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        </div>
      </div>
      <div className="chat-items">
        {chats.map(chat => (
          <div
            key={chat.id}
            className={`chat-item ${activeChat === chat.id ? 'active' : ''}`}
          >
            <div className="chat-item-content" onClick={() => onChatSelect(chat.id)}>
              {editingId === chat.id ? (
                <input
                  type="text"
                  className="chat-title-input"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  onBlur={() => handleSaveTitle(chat.id)}
                  onKeyDown={(e) => handleKeyDown(e, chat.id)}
                  autoFocus
                  onClick={(e) => e.stopPropagation()}
                />
              ) : (
                <h3 onDoubleClick={() => handleDoubleClick(chat)}>{chat.title}</h3>
              )}
              <p>{chat.preview}</p>
            </div>
            <button
              className="delete-chat-btn"
              onClick={(e) => {
                e.stopPropagation()
                onDeleteChat(chat.id)
              }}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M3 4h10M6 4V3a1 1 0 011-1h2a1 1 0 011 1v1M5 4v8a1 1 0 001 1h4a1 1 0 001-1V4"
                      stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ChatList
