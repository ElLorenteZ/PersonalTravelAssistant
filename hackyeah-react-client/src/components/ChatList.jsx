import './ChatList.css'

function ChatList({ chats, activeChat, onChatSelect, onNewChat }) {
  return (
    <div className="chat-list">
      <div className="chat-list-header">
        <h2>Chats</h2>
        <button className="new-chat-btn" onClick={onNewChat}>+</button>
      </div>
      <div className="chat-items">
        {chats.map(chat => (
          <div
            key={chat.id}
            className={`chat-item ${activeChat === chat.id ? 'active' : ''}`}
            onClick={() => onChatSelect(chat.id)}
          >
            <h3>{chat.title}</h3>
            <p>{chat.preview}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ChatList
